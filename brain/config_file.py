#!/usr/bin/env python
#
# This file contains the main hardcoded variables and input paths used for the processing.
#
# Charley Gros 2018-09-20
# Modified: 2018-10-26

config = dict()

config["dct_center"] = {"rennes": {"struct": "t1",
                                    "anat": "flair"},
                        "montpellier": {"struct": "t1",
                                    "anat": "flair"},
                        "lyon": {"struct": "t1",
                                    "anat": "flair"}
                        }

config["path_data"] = "/home/charley/data/brain_spine/data_processing/"

config["csv_clinicalInfo"] = "/home/charley/data/brain_spine/clinical_data.csv"

config["path_results"] = "/home/charley/data/brain_spine/results/"

config["path_anima_brain_extraction"] = "/home/charley/code/Anima-Scripts-Public/brain_extraction/"

config["path_smatt_folder"] = "/home/charley/Documents/anne/SMATT_website/"
config["path_brainstem_folder"] = "/home/charley/Documents/anne/Brainstem23BundleAtlas/"
config["path_atlases"] = "/home/charley/data/brain_spine/atlases/"