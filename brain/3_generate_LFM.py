#!/usr/bin/env python
#
# Goal: To generate Lesion Frequency Maps.
#
# Created: 2018-10-28
# Modified: 2019-08-09
# Contributors: Charley Gros

import os
import pandas as pd
import numpy as np
import commands

import sct_utils as sct
from spinalcordtoolbox.image import Image, zeros_like

from config_file import config


TRACTS_LST = ['brain/brain.nii.gz', 'brainstem/brainstem_CST.nii.gz']


def clean_LFM(fname_out, fname_brain):
    img, brain = Image(fname_out), Image(fname_brain)
    brain_data = brain.data
    del brain

    img.data[np.where(brain_data == 0)] = 0

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


def generate_LFM(df, fname_out, fname_out_cst, path_data, dct_center, path_atlases):
    mni_brain = os.path.join(commands.getstatusoutput('echo $FSLDIR')[1], 'data', 'standard', 'MNI152_T1_1mm_brain.nii.gz')

    fname_out_lesion = fname_out.split('_LFM.nii.gz')[0] + '_sumLesion.nii.gz'
    fname_out_brain = fname_out.split('_LFM.nii.gz')[0] + '_sumBrain.nii.gz'
    initialise_sumFile(fname_out_lesion, mni_brain)
    initialise_sumFile(fname_out_brain, mni_brain)

    for index, row in df.iterrows():
        anat_folder = dct_center[row.center]['anat']
        if not os.path.isfile(os.path.join(path_data, row.subject, 'brain', anat_folder, anat_folder+".nii.gz")):
            anat_folder = 't2'

        lesion_path = os.path.join(path_data, row.subject, 'brain', anat_folder, anat_folder+'_lesion_manual_mni.nii.gz')
        brain_path = os.path.join(path_data, row.subject, 'brain', anat_folder, anat_folder+'_brainMask_mni.nii.gz')
        if os.path.isfile(lesion_path) and os.path.isfile(brain_path):
            print row.subject
            add_mask(lesion_path, fname_out_lesion)
            add_mask(brain_path, fname_out_brain)

    sct.run(['sct_maths', '-i', fname_out_lesion,
                         '-div', fname_out_brain,
                         '-o', fname_out])

    clean_LFM(fname_out, mni_brain)
    mask_CST(fname_out, fname_out_cst, [os.path.join(path_atlases, t) for t in TRACTS_LST])


def main(args=None):

    subj_data_df = pd.read_pickle('1_results.pkl')

    path_data = config['path_data']
    dct_center = config['dct_center']
    path_atlases = config['path_atlases']

    path_lfm_fold = os.path.join(config["path_results"], 'LFM')
    if not os.path.isdir(path_lfm_fold):
        os.makedirs(path_lfm_fold)

    for subgroup in ['all', 'rem', 'pro', 'CIS', 'RR', 'SP', 'PP', 'edss_low', 'edss_med', 'edss_high', 'edssPy_low', 'edssPy_med', 'edssPy_high']:
        path_lfm = os.path.join(path_lfm_fold, 'brain_LFM_'+subgroup+'.nii.gz')
        path_lfm_cst = os.path.join(path_lfm_fold, 'brain_LFM_CST_'+subgroup+'.nii.gz')
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
            generate_LFM(lfm_df, path_lfm, path_lfm_cst, path_data, dct_center, path_atlases)

if __name__ == "__main__":
    main()
