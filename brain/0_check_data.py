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
# Created: 2017-04-01
# Modified: 2018-10-01
# Contributors: Charley Gros, Sara Dupont & Dominique Eden

import os
import pandas as pd
import datetime
import pickle
import numpy as np
from spinalcordtoolbox.image import Image

from config_file import config

DATE_TIME_STG = datetime.datetime.now().strftime("%Y%m%d%H%M")


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
                c_folder = os.path.join(sc_folder, center_dct[center][c][0])
                if os.path.isdir(c_folder):
                    c_img = os.path.join(c_folder, center_dct[center][c][0] + '.nii.gz')
                    c_lesion = os.path.join(c_folder, center_dct[center][c][0] + '_lesion_manual.nii.gz')
                    
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


if __name__ == "__main__":
    main()