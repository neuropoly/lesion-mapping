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
#                     image_ax/
#                                 image_ax.nii.gz # raw image
#                                 image_ax_seg_manual.nii.gz # spinal cord mask (binary)
#                                 image_ax_lesion_manual.nii.gz # lesion mask (binary)
#                                 labels_disc.nii.gz # disc label
#                                 labels_vert.nii.gz # vertebral label, non-compulsory
# (3) Creation of pickle '0_results.pkl', saved in current working directory. 
# WARNING: If a file is missing, the subject will be excluded for the remainder of the pipeline. 
#
# Created: 2017-04-01
# Modified: 2018-10-05
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


def _check_label(fname):
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
    excluded_subject = []
    for s, center, idx_s in zip(subj_data_df.subject.values, subj_data_df.center.values, subj_data_df.index.values):
        s_folder = os.path.join(path_data, s)
        if os.path.isdir(s_folder):
            sc_folder = os.path.join(s_folder, 'spinalcord')
            for c in center_dct[center]:
                c_folder = os.path.join(sc_folder, c)
                if os.path.isdir(c_folder):
                    c_img = os.path.join(c_folder, c + '.nii.gz')
                    c_seg = os.path.join(c_folder, c + '_seg_manual.nii.gz')
                    c_lesion = os.path.join(c_folder, c + '_lesion_manual.nii.gz')
                    c_labels = os.path.join(c_folder, 'labels_disc.nii.gz')
                    c_labels_vert = os.path.join(c_folder, 'labels_vert.nii.gz')
                    if not os.path.isfile(c_img):
                        missing_img.append(os.path.abspath(c_img))
                        excluded_subject.append(idx_s)
                        
                    if os.path.isfile(c_seg):
                        if not _check_sc_seg(c_seg):
                            incorrect_sc.append(os.path.abspath(c_seg))
                            excluded_subject.append(idx_s)
                    else:
                        missing_sc.append(os.path.abspath(c_seg))
                        excluded_subject.append(idx_s)

                    if os.path.isfile(c_lesion):
                        if not _check_lesion_seg(c_lesion):
                            incorrect_lesion.append(os.path.abspath(c_lesion))
                            excluded_subject.append(idx_s)               
                    else:
                        missing_lesion.append(os.path.abspath(c_lesion))
                        excluded_subject.append(idx_s)

                    if not os.path.isfile(c_labels) and not os.path.isfile(c_labels_vert):
                        missing_incorrect_labels.append(os.path.abspath(c_labels))
                        excluded_subject.append(idx_s)
                    else:
                        c_labels = c_labels if os.path.isfile(c_labels) else c_labels_vert
                        if not _check_label(c_labels):
                            missing_incorrect_labels.append(os.path.abspath(c_labels))
                            excluded_subject.append(idx_s)
                    
                else:
                    missing_contrast.append(c_folder)
                    excluded_subject.append(idx_s)
        else:
            missing_subject.append(s_folder)
            excluded_subject.append(idx_s)

    date_time_stg = datetime.datetime.now().strftime("%Y%m%d%H%M")
    stg_lst = ['missing_subject', 'missing_img', 'missing_contrast', 'missing_sc', 'missing_lesion', 'missing_incorrect_labels', 'incorrect_sc', 'incorrect_lesion']
    lst_lst = [missing_subject, missing_img, missing_contrast, missing_sc, missing_lesion, missing_incorrect_labels, incorrect_sc, incorrect_lesion]
    for stg, lst in zip(stg_lst, lst_lst):
        if len(lst):
            dct = {stg: lst}
            with open(date_time_stg + '_' + stg + '.pkl', 'wb') as f:
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


if __name__ == "__main__":
    main()