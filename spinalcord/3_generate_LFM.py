#!/usr/bin/env python
#
# Goal: To generate Lesion Frequency Maps.
#
# Created: 2018-10-27
# Modified: 2019-08-09
# Contributors: Charley Gros

import os
import pandas as pd
import numpy as np
import commands

import sct_utils as sct
from spinalcordtoolbox.image import Image, zeros_like

from config_file import config


TRACTS_LST = ['PAM50_atlas_05.nii.gz', 'PAM50_atlas_04.nii.gz', 'PAM50_atlas_23.nii.gz', 'PAM50_atlas_22.nii.gz']


def clean_LFM(fname_out, fname_cord, fname_lvl):
    img, cord, lvl = Image(fname_out), Image(fname_cord), Image(fname_lvl)
    cord_data, lvl_data = cord.data, lvl.data
    del cord, lvl

    img.data[np.where(cord_data == 0)] = 0
    z_top = np.max(list(set(np.where(lvl_data == 1)[2]))) + 1
    z_bottom = np.min(list(set(np.where(lvl_data == 7)[2])))
    img.data[:, :, :z_bottom] = 0
    img.data[:, :, z_top:] = 0
    img.data[np.isnan(img.data)]=0.0
    img.data[img.data>1.0]=0.0

    img.save(fname_out)
    del img


def initialise_sumFile(fname_out, fname_standard):
    img_out = zeros_like(Image(fname_standard))
    img_out.save(fname_out)
    del img_out


def add_mask(fname_new, fname_out):
    img_new, img_in = Image(fname_new), Image(fname_out)
    img_out = zeros_like(img_in)
    img_out.data = img_new.data + img_in.data
    del img_new, img_in
    img_out.save(fname_out)
    del img_out


def mask_CST(fname_LFM, fname_LFM_CST, mask_lst):
    img_lfm = Image(fname_LFM)
    img_cst = zeros_like(img_lfm)
    img_cst.data = img_lfm.data
    del img_lfm

    cst_mask_data = np.sum([Image(mask_fname).data for mask_fname in mask_lst], axis=0)
    cst_mask_data = (cst_mask_data > 0.0).astype(np.int_)

    img_cst.data[np.where(cst_mask_data == 0.0)] = 0.0
    img_cst.save(fname_LFM_CST)


def generate_LFM(df, fname_out, fname_out_cst, path_data):
    path_pam50 = os.path.join(commands.getstatusoutput('echo $SCT_DIR')[1], 'data/PAM50/')
    pam50_cord = os.path.join(path_pam50, 'template', 'PAM50_cord.nii.gz')
    pam50_lvl = os.path.join(path_pam50, 'template', 'PAM50_levels.nii.gz')

    fname_out_lesion = fname_out.split('_LFM.nii.gz')[0] + '_sumLesion.nii.gz'
    fname_out_cord = fname_out.split('_LFM.nii.gz')[0] + '_sumCord.nii.gz'
    initialise_sumFile(fname_out_lesion, pam50_cord)
    initialise_sumFile(fname_out_cord, pam50_cord)

    for index, row in df.iterrows():
        lesion_path = os.path.join(path_data, row.subject, 'spinalcord', 'lesion_mask_template.nii.gz')
        cord_path = os.path.join(path_data, row.subject, 'spinalcord', 'cord_mask_template.nii.gz')
        if os.path.isfile(lesion_path) and os.path.isfile(cord_path):
            print row.subject
            add_mask(lesion_path, fname_out_lesion)
            add_mask(cord_path, fname_out_cord)

    sct.run(['sct_maths', '-i', fname_out_lesion,
                         '-div', fname_out_cord,
                         '-o', fname_out])

    clean_LFM(fname_out, pam50_cord, pam50_lvl)
    mask_CST(fname_out, fname_out_cst, [os.path.join(path_pam50, 'atlas', t) for t in TRACTS_LST])


def main(args=None):

    subj_data_df = pd.read_pickle('1_results.pkl')

    path_data = config['path_data']
    path_lfm_fold = os.path.join(config["path_results"], 'LFM')
    if not os.path.isdir(path_lfm_fold):
        os.makedirs(path_lfm_fold)

    for subgroup in ['all', 'rem', 'pro', 'CIS', 'RR', 'SP', 'PP', 'edss_low', 'edss_med', 'edss_high', 'edssPy_low', 'edssPy_med', 'edssPy_high']:
        path_lfm = os.path.join(path_lfm_fold, 'spinalcord_LFM_'+subgroup+'.nii.gz')
        path_lfm_cst = os.path.join(path_lfm_fold, 'spinalcord_LFM_CST_'+subgroup+'.nii.gz')
        if subgroup == 'all':
            lfm_df = subj_data_df
        elif subgroup == 'pro':
            lfm_df = subj_data_df[subj_data_df.phenotype.isin(['PP', 'SP'])]
        elif subgroup == 'rem':
            lfm_df = subj_data_df[subj_data_df.phenotype.isin(['CIS', 'RR'])]
        elif subgroup in ['CIS', 'RR', 'SP', 'PP']:
            lfm_df = subj_data_df[subj_data_df.phenotype == subgroup]
        elif subgroup.startswith('edss_'):
            if subgroup.endswith('low'):
                lfm_df = subj_data_df[subj_data_df.edss_M0 <= 2.5]
            elif subgroup.endswith('high'):
                lfm_df = subj_data_df[subj_data_df.edss_M0 >= 6.0]
            elif subgroup.endswith('med'):
                lfm_df = subj_data_df[(subj_data_df.edss_M0 < 6.0) & (subj_data_df.edss_M0 > 2.5)]
        elif subgroup.startswith('edssPy_'):
            if subgroup.endswith('low'):
                lfm_df = subj_data_df[subj_data_df.edss_py_M0 < 1.0]
            elif subgroup.endswith('high'):
                lfm_df = subj_data_df[subj_data_df.edss_py_M0 >= 3.0]
            elif subgroup.endswith('med'):
                lfm_df = subj_data_df[(subj_data_df.edss_py_M0 < 3.0) & (subj_data_df.edss_py_M0 >= 1.0)]

        if not os.path.isfile(path_lfm) or not os.path.isfile(path_lfm_cst):
            print('\nGenerating the LFM with '+subgroup+' subjects ('+str(len(lfm_df.index))+').')
            generate_LFM(lfm_df, path_lfm, path_lfm_cst, path_data)


if __name__ == "__main__":
    main()
