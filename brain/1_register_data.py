#!/usr/bin/env python
#
# Goal: To warp brain and brainstem atlases to the flair space.
#
# Steps:
# (1) Brain extraction of both T1 and flair imahes
# (2) Register flair image to T1 image
# (3) Register T1 image to MNI_1mm space
# (4) Warp brain and brainstem atlases to the flair space.
#
# Created: 2018-10-01
# Modified: 2018-10-23
# Contributors: Charley Gros

import os
import pandas as pd

from config_file import config


def main(args=None):

    subj_data_df = pd.read_pickle('0_results.pkl')

    path_data = config['path_data']
    center_dct = config["dct_center"]
    path_atlases = config["path_atlases"]
    path_script_brain_extraction = config["path_anima_brain_extraction"]
    current_dir = os.getcwd()

    # loop and run 1_register_data.sh
    reg_subj_lst = []
    for index, row in subj_data_df.iterrows():
        anat_name = center_dct[row.center]['anat']
        if not os.path.isfile(os.path.join(path_data, row.subject, 'brain', anat_name, anat_name+'.nii.gz')):
            anat_name = 't2'

        subj_fold = os.path.join(path_data, row.subject, 'brain')
        flair_mni = os.path.join(subj_fold, anat_name, anat_name + '_mni.nii.gz')
        flair_lesion_mni = os.path.join(subj_fold, anat_name, anat_name + '_lesion_manual_mni.nii.gz')
        flair_brain_mni = os.path.join(subj_fold, anat_name, anat_name + '_brainMask_mni.nii.gz')
        label_folder = os.path.join(subj_fold, anat_name, 'label')
        brain_atlas_reg_path = os.path.join(subj_fold, anat_name, 'label', 'brain.nii.gz')
        if not os.path.isfile(flair_mni) or not os.path.isdir(label_folder) or not os.path.isfile(flair_lesion_mni) or not os.path.isfile(flair_brain_mni):
            print flair_mni
            os.system('./1_register_data.sh ' + subj_fold + ' ' + path_atlases + ' ' + path_script_brain_extraction + ' ' + anat_name)
            os.chdir(current_dir)
        if os.path.isfile(brain_atlas_reg_path):
            reg_subj_lst.append(row.subject)

    subj_data_df = subj_data_df[subj_data_df.subject.isin(reg_subj_lst)]
    subj_data_df.to_pickle('1_results.pkl')

if __name__ == "__main__":
    main()
