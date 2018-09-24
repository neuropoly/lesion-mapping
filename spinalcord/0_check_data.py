#!/usr/bin/env python
#
# Goal: To check existence of files required for registration, for each subject.
#
# Steps:
# (1) Identifies list of subjects based on entries from config["csv_clinicalInfo"]
# (2) Checks if following files exist and are correct:
#     (Please ensure below organisation / folder structure.)
#     subject_name/
#             spinalcord/
#                     contrast_ax/
#                                 contrast_ax.nii.gz # raw image
#                                 contrast_ax_seg_manual.nii.gz # spinal cord mask (binary)
#                                 contrast_ax_lesion_manual.nii.gz # lesion mask (binary)
#                                 labels_disc.nii.gz # disc label
#                     contrast_sag/
#                                 contrast_sag.nii.gz # raw image
#                                 contrast_sag_seg_manual.nii.gz # spinal cord mask (binary)
#                                 contrast_sag_lesion_manual.nii.gz # lesion mask (binary)
#                                 labels_disc.nii.gz # disc label
# (3) Creation of pickle '0_datetime_results.pkl', saved in current working directory. 
# WARNING: If a file is missing, the subject will be excluded for the remainder of the pipeline. 
#
# Created: 2017-04-01
# Modified: 2018-09-20
# Contributors: Charley Gros, Sara Dupont & Dominique Eden

import os
import pandas as pd
import datetime
import pickle
import numpy as np
from skimage.measure import label
from spinalcordtoolbox.image import Image

from config_file import config


def _check_sc_seg(fname):
    '''Check if the mask is only made of ones and only one connected object.'''
    i = Image(fname)
    check_bool = True
    if not all([True if v in [0, 1] else False for v in np.unique(i.data)]):
        check_bool = False
    if label(i.data, return_num=True)[1] != 1:
        check_bool = False
    del i
    return check_bool


def _check_lesion_seg(fname):
    '''Check if the mask is only made of ones.'''
    i = Image(fname)
    check_bool = True
    if not all([True if v in [0, 1] else False for v in np.unique(i.data)]):
        check_bool = False
    del i
    return check_bool


def _check_disc_label(fname):
    '''Check if the mask is only made of 2 voxels.'''
    i = Image(fname)
    check_bool = True
    if len(np.where(i.data)[0]) != 2:
        check_bool = False
    del i
    return check_bool


def check_data(path_data, center_dct, subj_data_df):
    '''
    Goal: Identify subjects of interest and check if required files are available and correct.

    Save lists of missing or incrorrect files/folders as pickle files.
    '''
    missing_subject, missing_img, missing_contrast = [], [], []
    missing_sc, missing_lesion, missing_incorrect_labels = [], [], []
    incorrect_sc, incorrect_lesion = [], []
    for s, center in zip(subj_data_df.subject.values, subj_data_df.center.values):
        s_folder = os.path.join(path_data, s)
        if os.path.isdir(s_folder):
            sc_folder = os.path.join(s_folder, 'spinalcord')
            c_lst = [cc for orient in center_dct[center] for cc in center_dct[center][orient]]
            for c in c_lst:
                c_folder = os.path.join(sc_folder, c)
                if os.path.isdir(c_folder):
                    c_img = os.path.join(c_folder, c + '.nii.gz')
                    c_seg = os.path.join(c_folder, c + '_seg_manual.nii.gz')
                    c_lesion = os.path.join(c_folder, c + '_lesion_manual.nii.gz')
                    c_labels = os.path.join(c_folder, 'labels_disc.nii.gz')
                    
                    if not os.path.isfile(c_img):
                        missing_img.append(os.path.abspath(c_img))
                        
                    if os.path.isfile(c_seg):
                        if not _check_sc_seg(c_seg):
                            incorrect_sc.append(os.path.abspath(c_seg))
                    else:
                        missing_sc.append(os.path.abspath(c_seg))

                    if os.path.isfile(c_lesion):
                        if not _check_lesion_seg(c_lesion):
                            incorrect_lesion.append(os.path.abspath(c_lesion))               
                    else:
                        missing_lesion.append(os.path.abspath(c_lesion))

                    if os.path.isfile(c_labels):
                        if not _check_disc_label(c_labels):
                            missing_incorrect_labels.append(os.path.abspath(c_labels))
                    else:
                        missing_incorrect_labels.append(os.path.abspath(c_labels))
                    
                else:
                    missing_contrast.append(c_folder)
        else:
            missing_subject.append(s_folder)

    date_time_stg = datetime.datetime.now().strftime("%Y%m%d%H%M")
    stg_lst = ['missing_subject', 'missing_img', 'missing_contrast', 'missing_sc', 'missing_lesion', 'missing_incorrect_labels', 'incorrect_sc', 'incorrect_lesion']
    lst_lst = [missing_subject, missing_img, missing_contrast, missing_sc, missing_lesion, missing_incorrect_labels, incorrect_sc, incorrect_lesion]
    for stg, lst in zip(stg_lst, lst_lst):
        if len(lst):
            dct = {stg: lst}
            with open(date_time_stg + '_' + stg + '.pkl', 'wb') as f:
                pickle.dump(dct, f)

def main(args=None):

    csv_fname = config['csv_clinicalInfo']
    subj_data_df = pd.read_csv(csv_fname)

    path_data = config['path_data']
    center_dct = config["dct_center"]

    subj_check_df = check_data(path_data=path_data,
                                center_dct=center_dct,
                                subj_data_df=subj_data_df)


if __name__ == "__main__":
    main()