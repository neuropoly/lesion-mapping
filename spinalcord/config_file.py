#!/usr/bin/env python
#
# This file contains the main hardcoded variables and input paths used for the processing.
#
# Charley Gros 2018-09-20
# Modified: 2018-10-05

import os

config = dict()

config["dct_center"] = {"rennes": ["t2s_inf", "t2s_sup"],
                        "montpellier": ["t2s_inf", "t2s_sup"],
                        "nih": ["t2s"],
                        "bwh": ["t2_ax"],
                        "milan": ["t2s_ax"],
                        "karo": ["t2s"]
                        }

config["path_data"] = "/Volumes/projects/ms_brain_spine/data_processing/"

config["csv_clinicalInfo"] = "/Volumes/projects/ms_brain_spine/clinical_data.csv"

config["path_results"] = "/Volumes/projects/ms_brain_spine/results/"
