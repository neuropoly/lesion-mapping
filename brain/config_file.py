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
                        "nih": {"struct": "t1",
                                    "anat": "flair"},
                        "milan": {"struct": "t1",
                                    "anat": "t2"},
                        "bwh": {"struct": "t1",
                                    "anat": "flair"},
                        "karo": {"struct": "t1",
                                    "anat": "flair"}}

config["path_data"] = "/Volumes/projects/ms_brain_spine/data_processing/"

config["csv_clinicalInfo"] = "/Volumes/projects/ms_brain_spine/clinical_data.csv"

config["path_results"] = "/Volumes/projects/ms_brain_spine/results/"

config["path_anima_brain_extraction"] = "/Users/anne/Anima-Scripts-Public/brain_extraction/"

config["path_smatt_folder"] = "/Volumes/projects/ms_brain_spine/download_atlases/SMATT_website/"
config["path_brainstem_folder"] = "/Volumes/projects/ms_brain_spine/download_atlases/Brainstem23BundleAtlas/"
config["path_atlases"] = "/Volumes/projects/ms_brain_spine/atlases/"
