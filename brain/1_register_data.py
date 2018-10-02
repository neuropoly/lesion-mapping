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

DATE_TIME_STG = datetime.datetime.now().strftime("%Y%m%d%H%M")

def main(args=None):

    subj_data_df = pd.read_pickle('0_results.pkl')

    path_data = config['path_data']

    # loop and run 1_register_data.sh


if __name__ == "__main__":
    main()