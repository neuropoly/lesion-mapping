#!/usr/bin/env python
#
# Goal: To check existence of files required for registration, for each subject.
#
# Steps:
# (1) Identifies list of subjects based on entries from config["csv_clinicalInfo"]
# (2) Checks if following files exist:
#     (Please ensure below organisation / folder structure.)
#     subject_name/
#             spinalcord/
#                     contrast_ax/
#                                 contrast_ax.nii.gz # raw image
#                                 contrast_ax_seg_manual.nii.gz # spinal cord mask (binary)
#                                 contrast_ax_lesion_manual.nii.gz # lesion mask (binary)
#                                 labels_disc.nii.gz # disc label
#                     contrast_sag/
#                                 contrast_sag.nii.gz # raw image
#                                 contrast_sag_seg_manual.nii.gz # spinal cord mask (binary)
#                                 contrast_sag_lesion_manual.nii.gz # lesion mask (binary)
#                                 labels_disc.nii.gz # disc label
# (3) Creation of pickle '0_results_datetime.pkl', saved in current working directory. 
# WARNING: If a file is missing, the subject will be excluded for the remainder of the pipeline. 
#
# Created: 2017-04-01
# Modified: 2018-09-20
# Contributors: Charley Gros, Sara Dupont & Dominique Eden
