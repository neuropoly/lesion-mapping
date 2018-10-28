#!/usr/bin/env python
#
# Goal: To generate Lesion Frequency Maps.
#
# Created: 2018-10-28
# Modified: 2018-10-28
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

    path_lfm = os.path.join(path_lfm_fold, 'brain_LFM.nii.gz')
    path_lfm_cst = os.path.join(path_lfm_fold, 'brain_LFM_CST.nii.gz')
    if not os.path.isfile(path_lfm) or not os.path.isfile(path_lfm_cst):
        generate_LFM(subj_data_df, path_lfm, path_lfm_cst, path_data, dct_center, path_atlases)

if __name__ == "__main__":
    main()