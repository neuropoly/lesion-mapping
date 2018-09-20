import os

config = dict()

config["center_dct"] = {"rennes": {"ax": ["t2s_inf", "t2s_sup"],
                                    "sag": ["t2_sag_cerv"]},
                        "montpellier": {"ax": ["t2s_inf", "t2s_sup"],
                                    "sag": ["t2_sag_cerv"]},
                        "lyon": {"ax": ["t2s"],
                                    "sag": ["t2_sag"]}
                        }

config["path_data"] = "/home/charley/data/brain_spine/data_processing/"

config["csv_clinicalInfo"] = "/home/charley/data/brain_spine/clinical_data.csv"

config["path_results"] = "/home/charley/data/brain_spine/results/"