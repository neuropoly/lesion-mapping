#!/usr/bin/env python
#
# Goal: To quantify lesion characteristics in both brain and brainstem regions.
#
# Measures:
# - tbv [mm3]: total brain volume (brain + brainstem)
# - tlv_* [mm3]: total lesion volume (brain + brainstem)
# - count_*: number of lesions
# - alv_* [mm3]: absolute lesion volume in one of the region of interest listed below
# - nlv_*: alv_* divided by a volume of interest
# - extension_motor (%): volume of lesion in the motor tracts divided by the total volume of lesion in the cord
#
# Regions of interest:
# - brain, brainstem, brain_brainstem: brain, brainstem, and brain+brainstem areas
# - brain_motor, brainstem_motor, brain_brainstem_motor: brain, brainstem, and brain+brainstem motor tracts areas
# - brainstem_CST_R, brainstem_CST_L: corticospinal right and left tracts in the brainstem
# - brain_M1_R, brain_M1_L:
# - brain_PMd_R, brain_PMd_L:
# - brain_PMv_R, brain_PMv_L:
# - brain_preSMA_R, brain_preSMA_L:
# - brain_S1_R, brain_S1_L:
# - brain_SMA_R, brain_SMA_L:
#
# Created: 2018-10-15
# Modified: 2018-10-26
# Contributors: Charley Gros

import os
import numpy as np
import pandas as pd
from skimage.measure import label

from spinalcordtoolbox.image import Image

from config_file import config


def z_brainstem(image_fold):
    brainstem_path = os.path.join(image_fold, 'label', 'brainstem_CST.nii.gz')
    
    brainstem_im = Image(brainstem_path)
    brainstem_im.change_orientation('RPI')
    z_brainstem_lst = list(set(np.where(brainstem_im.data)[2]))
    del brainstem_im

    return np.min(z_brainstem_lst), np.max(z_brainstem_lst)


def convert_nrrd2niigz(fname_in):
    if not os.path.isfile(fname_in):
        brain_mask_nrrd = fname_in.split('.nii.gz')[0] + '.nrrd'
        os.system('animaConvertImage -i '+brain_mask_nrrd+' -o '+fname_in)


def compute_tbv(fname_in):
    convert_nrrd2niigz(fname_in)

    img = Image(fname_in).change_orientation('RPI')
    res_x, res_y, res_z = img.dim[4:7]
    data = img.data
    del img

    data = (data > 0.0).astype(np.int_)
    return np.sum(data) * res_x * res_y * res_z


def compute_lesion_characteristics(img_fold, roi_name=''):
    if roi_name == '':
        mask_path = os.path.join(img_fold, img_fold.split('/')[-1]+'_brainMask.nii.gz')
        convert_nrrd2niigz(mask_path)
    else:
        mask_path = os.path.join(img_fold, 'label', roi_name+'.nii.gz')

    lesion_path = os.path.join(img_fold, img_fold.split('/')[-1]+'_lesion_manual.nii.gz')

    mask_im = Image(mask_path).change_orientation('RPI')
    lesion_im = Image(lesion_path).change_orientation('RPI')

    if roi_name == '':
        z_min, _ = z_brainstem(img_fold)
        mask_data = mask_im.data[:, :, z_min:]
        lesion_data = lesion_im.data[:, :, z_min:]
    else:
        mask_data, lesion_data = mask_im.data, lesion_im.data

    res_x, res_y, res_z = lesion_im.dim[4:7]
    del mask_im, lesion_im

    lesion_data = lesion_data * mask_data

    count = label((lesion_data > 0).astype(np.int), neighbors=8, return_num=True)[1]
    tlv = np.sum(lesion_data) * res_x * res_y * res_z
    mask_vol = np.sum(mask_data) * res_x * res_y * res_z
    nlv = tlv * 1.0 / mask_vol
    return count, tlv, nlv


def main():

    subj_data_df = pd.read_pickle('1_results.pkl')

    path_data = config['path_data']
    center_dct = config["dct_center"]
    path_results_pkl = os.path.join(config["path_results"], 'brain_brainstem_results.pickle')
    path_results_csv = os.path.join(config["path_results"], 'brain_brainstem_results.csv')

    roi_lst = ['', '_brain_motor',
            '_brainstem_CST', '_brainstem_CST_R', '_brainstem_CST_L',
            '_brain_M1_R', '_brain_M1_L', '_brain_PMd_R', '_brain_PMd_L',
            '_brain_PMv_R', '_brain_PMv_L', '_brain_preSMA_R', '_brain_preSMA_L',
            '_brain_S1_R', '_brain_S1_L', '_brain_SMA_R', '_brain_SMA_L']
    atlas_pref_lst = ['', 'brain', 'brainstem_CST', 'brainstem_CST_R', 'brainstem_CST_L',
                    'brain_M1_R', 'brain_M1_L', 'brain_PMd_R', 'brain_PMd_L',
                    'brain_PMv_R', 'brain_PMv_L', 'brain_preSMA_R', 'brain_preSMA_L',
                    'brain_S1_R', 'brain_S1_L', 'brain_SMA_R', 'brain_SMA_L']

    for index, row in subj_data_df.iterrows():
        subj_fold = os.path.join(path_data, row.subject, 'brain')

        # tbv
        t1_fold = os.path.join(subj_fold, center_dct[row.center]["struct"])
        t1_brain_mask_nii = os.path.join(t1_fold, center_dct[row.center]["struct"]+'_brainMask.nii.gz')
        subj_data_df.loc[index, 'tbv'] = compute_tbv(t1_brain_mask_nii)

        flair_fold = os.path.join(subj_fold, center_dct[row.center]["anat"])
        
        # lesion count, TLV, NLV        
        for roi, atlas_pref in zip(roi_lst, atlas_pref_lst):
            count_cur, tlv_cur, nlv_cur = compute_lesion_characteristics(flair_fold, roi_name=atlas_pref)
            subj_data_df.loc[index, 'count'+roi] = count_cur
            if roi == '':
                subj_data_df.loc[index, 'tlv'] = tlv_cur
            else:
                subj_data_df.loc[index, 'alv'+roi] = tlv_cur
            subj_data_df.loc[index, 'nlv'+roi] = nlv_cur

        # extension
        if subj_data_df.loc[index, 'tlv']:
            subj_data_df.loc[index, 'extension_motor'] = (subj_data_df.loc[index, 'alv_brain_motor']+subj_data_df.loc[index, 'alv_brainstem_CST']) * 100. / subj_data_df.loc[index, 'tlv']
    
    subj_data_df.to_csv(path_results_csv)
    subj_data_df.to_pickle(path_results_pkl)

if __name__ == "__main__":
    main()