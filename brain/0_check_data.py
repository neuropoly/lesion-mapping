#!/usr/bin/env python
#
# Goal: To check existence of files required for registration, for each subject.
#
# Steps:
# (1) Identifies list of subjects based on entries from config["csv_clinicalInfo"]
# (2) Checks if following files exist and are correct:
#     (Please ensure below organisation / folder structure.)
#     subject_name/
#             brain/
#                     struct/
#                                 struct.nii.gz # raw image
#                     anat/
#                                 anat.nii.gz # raw image
#                                 anat_lesion_manual.nii.gz # lesion mask (binary)
# (3) Creation of pickle '0_results.pkl', saved in current working directory. 
# WARNING: If a file is missing, the subject will be excluded for the remainder of the pipeline.
#
# (4) Custom brain and brainstem atlases for the purpose of this study.
# Save them in config["path_atlases"].
#
# Created: 2017-04-01
# Modified: 2018-10-20
# Contributors: Charley Gros, Sara Dupont & Dominique Eden

import os
import pandas as pd
import datetime
import pickle
import numpy as np
from spinalcordtoolbox.image import Image, zeros_like

from config_file import config

DATE_TIME_STG = datetime.datetime.now().strftime("%Y%m%d%H%M")

BRAINSTEM_DCT = {'CST_R': 'CSTR_Atlas.nii.gz',
                'CST_L': 'CSTL_Atlas.nii.gz',
                'CST': ''}
BRAMSTEM_ZTOP = 63 #51
BRAMSTEM_ZBOT = 8 #14

BRAIN_DCT = {'M1_R': 'Right-M1-S-MATT.nii',
            'M1_L': 'Left-M1-S-MATT.nii',
            'PMd_R': 'Right-PMd-S-MATT.nii',
            'PMd_L': 'Left-PMd-S-MATT.nii',
            'PMv_R': 'Right-PMv-S-MATT.nii',
            'PMv_L': 'Left-PMv-S-MATT.nii',
            'preSMA_R': 'Right-preSMA-S-MATT.nii',
            'preSMA_L': 'Left-preSMA-S-MATT.nii',
            'S1_R': 'Right-S1-S-MATT.nii',
            'S1_L': 'Left-S1-S-MATT.nii',
            'SMA_R': 'Right-SMA-S-MATT.nii',
            'SMA_L': 'Left-SMA-S-MATT.nii'}

def custom_brainstem(ifolder, ofolder, thr):
    cst_r_ifile = os.path.join(ifolder, BRAINSTEM_DCT['CST_R'])
    cst_l_ifile = os.path.join(ifolder, BRAINSTEM_DCT['CST_L'])

    cst_r_ofile = os.path.join(ofolder, 'brainstem_CST_R.nii.gz')
    cst_l_ofile = os.path.join(ofolder, 'brainstem_CST_L.nii.gz')
    cst_ofile = os.path.join(ofolder, 'brainstem_CST.nii.gz')

    cst_r_im, cst_l_im = Image(cst_r_ifile), Image(cst_l_ifile)
    cst_im = zeros_like(cst_r_im)

    cst_r_im.data[:, :, BRAMSTEM_ZTOP+1:] = 0.
    cst_l_im.data[:, :, BRAMSTEM_ZTOP+1:] = 0.
    cst_r_im.data[:, :, :BRAMSTEM_ZBOT] = 0.
    cst_l_im.data[:, :, :BRAMSTEM_ZBOT] = 0.

    cst_r_im.data[cst_r_im.data > thr] = 1.0
    cst_r_im.data[cst_r_im.data <= thr] = 0.0

    cst_l_im.data[cst_l_im.data > thr] = 1.0
    cst_l_im.data[cst_l_im.data <= thr] = 0.0

    cst_im.data = cst_r_im.data + cst_l_im.data
    cst_im.data[cst_im.data > 0.0] = 1.0

    cst_r_im.save(cst_r_ofile)
    cst_l_im.save(cst_l_ofile)
    cst_im.save(cst_ofile)
    del cst_r_im, cst_l_im, cst_im


def custom_brain(ifolder, ofolder):
    ifname_dct = {}
    for roi in BRAIN_DCT:
        ifname_dct[roi] = os.path.join(ifolder, BRAIN_DCT[roi])

    for roi in ifname_dct:
        ofname = os.path.join(ofolder, 'brain_' + roi + '.nii.gz')

        i_im = Image(ifname_dct[roi])
        o_im = zeros_like(i_im)
        o_im.data = i_im.data
        del i_im

        o_im.data[:, :, :BRAMSTEM_ZTOP+1] = 0.0

        o_im.save(ofname)
        del o_im

    sum_roi_im = sum([Image(ifname_dct[roi]).data for roi in ifname_dct])
    i_im = Image(ifname_dct[roi])
    o_im = zeros_like(i_im)
    del i_im

    o_im.data[sum_roi_im > 0.0] = 1.0
    o_im.data[:, :, :BRAMSTEM_ZTOP+1] = 0.0

    o_im.save(os.path.join(ofolder, 'brain.nii.gz'))
    del o_im

def _check_lesion_seg(fname):
    '''Check if the mask is only made of ones.'''
    i = Image(fname)
    check_bool = True
    if not all([True if v in [0, 1] else False for v in np.unique(i.data)]):
        check_bool = False
    del i
    return check_bool


def check_data(path_data, center_dct, subj_data_df):
    '''
    Goal: Identify subjects of interest and check if required files are available and correct.

    Save lists of missing or incrorrect files/folders as pickle files.
    '''
    missing_subject, missing_img, missing_contrast = [], [], []
    missing_lesion, incorrect_lesion = [], []
    excluded_subject = []
    for s, center, idx_s in zip(subj_data_df.subject.values, subj_data_df.center.values, subj_data_df.index.values):
        s_folder = os.path.join(path_data, s)
        if os.path.isdir(s_folder):
            sc_folder = os.path.join(s_folder, 'brain')
            for c in center_dct[center]:
                c_folder = os.path.join(sc_folder, center_dct[center][c])
                if os.path.isdir(c_folder):
                    c_img = os.path.join(c_folder, center_dct[center][c] + '.nii.gz')
                    c_lesion = os.path.join(c_folder, center_dct[center][c] + '_lesion_manual.nii.gz')
                    
                    if not os.path.isfile(c_img):
                        missing_img.append(os.path.abspath(c_img))
                        excluded_subject.append(idx_s)

                    if c == 'anat':
                        if os.path.isfile(c_lesion):
                            if not _check_lesion_seg(c_lesion):
                                incorrect_lesion.append(os.path.abspath(c_lesion))
                                excluded_subject.append(idx_s)
                        else:
                            missing_lesion.append(os.path.abspath(c_lesion))
                            excluded_subject.append(idx_s)

                    
                else:
                    missing_contrast.append(c_folder)
                    excluded_subject.append(idx_s)

        else:
            missing_subject.append(s_folder)
            excluded_subject.append(idx_s)

    stg_lst = ['missing_subject', 'missing_img', 'missing_contrast', 'missing_lesion', 'incorrect_lesion']
    lst_lst = [missing_subject, missing_img, missing_contrast, missing_lesion, incorrect_lesion]
    for stg, lst in zip(stg_lst, lst_lst):
        if len(lst):
            dct = {stg: lst}
            with open(DATE_TIME_STG + '_' + stg + '.pkl', 'wb') as f:
                pickle.dump(dct, f)

    return subj_data_df.drop(subj_data_df.index[list(set(excluded_subject))])

def main(args=None):

    csv_fname = config['csv_clinicalInfo']
    subj_data_df = pd.read_csv(csv_fname)

    path_data = config['path_data']
    center_dct = config["dct_center"]

    subj_check_df = check_data(path_data=path_data,
                                center_dct=center_dct,
                                subj_data_df=subj_data_df)

    subj_check_df.to_pickle('0_results.pkl')

    ofolder = config["path_atlases"]
    if not os.path.isdir(ofolder):
        os.makedirs(ofolder)

    brainstem_atlas_ifolder = config["path_brainstem_folder"]
    brainstem_atlas_ofolder = os.path.join(ofolder, 'brainstem')
    if not os.path.isdir(brainstem_atlas_ofolder):
        os.makedirs(brainstem_atlas_ofolder)
        custom_brainstem(brainstem_atlas_ifolder, brainstem_atlas_ofolder, 0.01)

    brain_atlas_ifolder = config["path_smatt_folder"]
    brain_atlas_ofolder = os.path.join(ofolder, 'brain')
    if not os.path.isdir(brain_atlas_ofolder):
        os.makedirs(brain_atlas_ofolder)
        custom_brain(brain_atlas_ifolder, brain_atlas_ofolder)


if __name__ == "__main__":
    main()