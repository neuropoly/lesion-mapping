#!/usr/bin/env python
#
# Goal: To quantify lesion characteristics.
#
# Measures:
# - csa [mm2]: mean cross-sectional area of the cord
# - tlv [mm3]: total lesion volume in the entire cord
# - count_*: number of lesions in the entire cord or in one of the region of interest listed below (e.g. count_VCST_R)
# - nlv_*: TLV divided by a volume of interest (e.g. entire cord or one of the region of interest listed below)
# - alv_* [mm3]: absolute lesion volume in one of the region of interest listed below (e.g. alv_VCST_R)
# - extension_CST (%): volume of lesion in the corticospinal tracts divided by the total volume of lesion in the cord
#
# Regions of interest:
# - VCST_R, VCST_L: ventral corticospinal right and left tracts
# - LCST_R, LCST_L : lateral corticospinal right and left tracts
# - CST: corticospinal tracts
#
# Created: 2018-10-15
# Modified: 2018-10-15
# Contributors: Charley Gros

import os
import pandas as pd
import numpy as np
from skimage.measure import label

import sct_utils as sct
from spinalcordtoolbox.image import Image

from config_file import config

TRACTS_DCT = {'LCST-R': 'PAM50_atlas_05.nii.gz',
                'LCST-L': 'PAM50_atlas_04.nii.gz',
                'VCST-R': 'PAM50_atlas_23.nii.gz',
                'VCST-L': 'PAM50_atlas_22.nii.gz'}


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


def compute_mean_csa(z_dct):
    csa_lst_lst = []
    for img_fold, z_min, z_max in zip(z_dct['img_fold_path'], z_dct['z_min'], z_dct['z_max']):
        csa_pickle = os.path.join(img_fold, 'csa', 'csa_per_slice.pickle')

        if not os.path.isfile(csa_pickle):
            sc_path = os.path.join(img_fold, img_fold.split('/')[-1] + '_seg_manual.nii.gz')
            sct.run(['sct_process_segmentation', '-i', sc_path, '-p', 'csa', '-ofolder', os.path.join(img_fold, 'csa')])

        csa_pd = pd.read_pickle(csa_pickle)
        csa_lst = csa_pd[csa_pd['Slice (z)'].isin(range(z_min, z_max+1))]['CSA (mm^2)'].values
        csa_lst_lst.append(csa_lst)

    return np.mean([csa for sublst in csa_lst_lst for csa in sublst])


def compute_lesion_characteristics(z_dct, roi_name=''):
    count_lst, tlv_lst, sc_vol_lst = [], [], []
    for img_fold, z_min, z_max in zip(z_dct['img_fold_path'], z_dct['z_min'], z_dct['z_max']):
        sc_im = Image(os.path.join(img_fold, img_fold.split('/')[-1] + '_seg_manual.nii.gz')).change_orientation('RPI')
        lesion_im = Image(os.path.join(img_fold, img_fold.split('/')[-1] + '_lesion_manual.nii.gz')).change_orientation('RPI')

        sc_data = sc_im.data[:, :, z_min:z_max+1]
        lesion_data = lesion_im.data[:, :, z_min:z_max+1]
        res_x, res_y, res_z = lesion_im.dim[4:7]

        roi_path = os.path.join(img_fold, 'label', 'atlas', roi_name)
        if os.path.isfile(roi_path):
            roi_im = Image(roi_path).change_orientation('RPI')
            roi_data = roi_im.data[:, :, z_min:z_max+1]
            sc_data = (sc_data * roi_data)
            lesion_data = (lesion_data * roi_data)
            lesion_threshold_indices = lesion_data > 0            
            lesion_data[lesion_threshold_indices] = 1
            sc_threshold_indices = sc_data > 0
            sc_data[sc_threshold_indices] = 1
            
            del roi_im

        count_lst.append(label((lesion_data > 0).astype(np.int), neighbors=8, return_num=True)[1])
        tlv_lst.append(np.sum(lesion_data) * res_x * res_y * res_z)
        sc_vol_lst.append(np.sum(sc_data) * res_x * res_y * res_z)

        del sc_im, lesion_im

    count, tlv, sc_vol = sum(count_lst), sum(tlv_lst), sum(sc_vol_lst)

    return count, tlv, sc_vol


def main(args=None):

    subj_data_df = pd.read_pickle('1_results.pkl')

    path_data = config['path_data']
    center_dct = config["dct_center"]
    path_results_pkl = os.path.join(config["path_results"], 'spinalcord_results.pickle')
    path_results_csv = os.path.join(config["path_results"], 'spinalcord_results.csv')

    for index, row in subj_data_df.iterrows():
        image_lst = center_dct[row.center]
        subj_fold = os.path.join(path_data, row.subject, 'spinalcord')

        z_dct = z_to_include(image_lst, subj_fold)
        print row.subject

        # csa
        subj_data_df.loc[index, 'csa_sc'] = compute_mean_csa(z_dct)

        # lesion count, TLV, NLV
        subj_data_df.loc[index, 'count_sc_full'], subj_data_df.loc[index, 'tlv_sc_full'], subj_data_df.loc[index, 'vol_sc_full'] = compute_lesion_characteristics(z_dct, roi_name='')

        # Per tract: lesion count, ALV, NLV
        for tract in TRACTS_DCT:
            subj_data_df.loc[index, 'count_sc_'+tract], subj_data_df.loc[index, 'alv_sc_'+tract], subj_data_df.loc[index, 'vol_sc_'+tract] = compute_lesion_characteristics(z_dct, roi_name=TRACTS_DCT[tract])

    subj_data_df.to_csv(path_results_csv)
    subj_data_df.to_pickle(path_results_pkl)

if __name__ == "__main__":
    main()
