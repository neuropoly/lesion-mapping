#!/usr/bin/env python
#
# Goal: To quantify lesion characteristics.
#
# Steps:
# (1) 
#
# Created: 2018-10-15
# Modified: 2018-10-15
# Contributors: Charley Gros

import os
import pandas as pd
import numpy as np

import sct_utils as sct
from spinalcordtoolbox.image import Image

from config_file import config

def z_slice_levels(levels_path):
    levels_im = Image(levels_path)
    levels_im.change_orientation('RPI')

    lvl_dct = {}
    for lvl in list(np.unique(levels_im.data)):
        if lvl:
            lvl_dct[lvl] = list(set(np.where(levels_im.data == lvl)[2]))
    del levels_im

    return lvl_dct

def z_to_include(image_lst, subj_fold):
    if len(image_lst) == 1:
        img_fold_path = os.path.join(subj_fold, image_lst[0])
        levels_path = os.path.join(img_fold_path, 'label', 'template', 'PAM50_levels.nii.gz')
        lvl_z_dct = z_slice_levels(levels_path)
        z_dct = {'img_fold_path': [img_fold_path],
                    'z_min': [np.min(lvl_z_dct[np.max(lvl_z_dct.keys())])],
                    'z_max': [np.max(lvl_z_dct[np.min(lvl_z_dct.keys())])],
                }

    elif len(image_lst) == 2:
        img1_fold_path = os.path.join(subj_fold, image_lst[0])
        img2_fold_path = os.path.join(subj_fold, image_lst[1])
        levels1_path = os.path.join(img1_fold_path, 'label', 'template', 'PAM50_levels.nii.gz')
        levels2_path = os.path.join(img2_fold_path, 'label', 'template', 'PAM50_levels.nii.gz')

        lvl_z_dct1 = z_slice_levels(levels1_path)
        lvl_z_dct2 = z_slice_levels(levels2_path)

        lvl_intersection = list(set(lvl_z_dct1.keys()) & set(lvl_z_dct2.keys()))

        if len(lvl_intersection):
            if np.min(lvl_z_dct1.keys()) < np.min(lvl_z_dct2.keys()):
                for lvl_rm in lvl_intersection:
                    lvl_z_dct2 = removekey(lvl_z_dct2, lvl_rm)
            else:
                for lvl_rm in lvl_intersection:
                    lvl_z_dct1 = removekey(lvl_z_dct1, lvl_rm)

        z_dct = {'img_fold_path': [img1_fold_path, img2_fold_path],
                    'z_min': [np.min(lvl_z_dct1[np.max(lvl_z_dct1.keys())]), np.min(lvl_z_dct2[np.max(lvl_z_dct2.keys())])],
                    'z_max': [np.max(lvl_z_dct1[np.min(lvl_z_dct1.keys())]), np.max(lvl_z_dct2[np.min(lvl_z_dct2.keys())])],
                }

    return z_dct

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r


def main(args=None):

    subj_data_df = pd.read_pickle('1_results.pkl')

    path_data = config['path_data']
    center_dct = config["dct_center"]
    path_results_pkl = os.path.join(config["path_results"], 'results.pickle')
    path_results_csv = os.path.join(config["path_results"], 'results.csv')

    for index, row in subj_data_df.iterrows():
        image_lst = center_dct[row.center]
        subj_fold = os.path.join(path_data, row.subject, 'spinalcord')

        z_dct = z_to_include(image_lst, subj_fold)

        # csa

        # lesion count

        # ALV

        # NLV

        # TLV

        # Extension


if __name__ == "__main__":
    main()