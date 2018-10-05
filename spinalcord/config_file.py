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
                        "lyon": ["t2s"]
                        }

config["path_data"] = "/home/charley/data/brain_spine/data_processing/"

config["csv_clinicalInfo"] = "/home/charley/data/brain_spine/clinical_data.csv"

config["path_results"] = "/home/charley/data/brain_spine/results/"