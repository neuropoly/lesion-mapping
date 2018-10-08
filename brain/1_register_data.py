#!/usr/bin/env python
#
# Goal: To register the anat image into the MNI152_T1_1mm space.
#
# Steps:
# (1) 
#
# Created: 2018-10-01
# Modified: 2018-10-01
# Contributors: Charley Gros

import os
import pandas as pd

from config_file import config


def main(args=None):

    subj_data_df = pd.read_pickle('0_results.pkl')

    path_data = config['path_data']
    center_dct = config["dct_center"]
    current_dir = os.getcwd()

    # loop and run 1_register_data.sh
    for index, row in subj_data_df.iterrows():
    	anat_name = center_dct[row.center]['anat']
    	subj_fold = os.path.join(path_data, row.subject, 'brain')
    	flair_mni = os.path.join(subj_fold, anat_name, anat_name + '_mni.nii.gz')
    	if not os.path.isfile(flair_mni):
    		print flair_mni
    		os.system('./1_register_data_anima.sh ' + subj_fold)
    		os.chdir(current_dir)


if __name__ == "__main__":
    main()