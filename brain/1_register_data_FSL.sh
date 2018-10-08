#!/bin/bash
#
# Usage:
#   ./1_register_data_FSL.sh <subject_folder>
#
# Example:
#   ./1_register_data_FSL.sh /home/charley/data/brain_spine/processing_data/rennes_20170112_10/
#
# NB: add the flag "-x" after "!/bin/bash" for full verbose of commands.
# Charley Gros 2018-10-07
# modified: 2018-10-07

cd $1

# Bias Field Correction
N4BiasFieldCorrection -i t1/t1.nii.gz -o t1/t1_bias.nii.gz
N4BiasFieldCorrection -i flair/flair.nii.gz -o flair/flair_bias.nii.gz

# Brain Extraction
bet t1/t1_bias t1/t1_brain
bet flair/flair_bias flair/flair_brain

# Intra subject linear registration: Flair --> T1
flirt -in flair/flair_brain -ref t1/t1_brain -out flair/flair_t1 -omat flair/flair2t1.mat -dof 6

# Linear registration of T1 to the MNI152_T1_1mm
flirt -in t1/t1_brain -ref ${FSLDIR}/data/standard/MNI152_T1_1mm_brain -out t1/t1_mni -omat t1/t12mni_affine.mat

# Non Linear registration of T1 to the MNI152_T1_1mm
fnirt --in=t1/t1_brain --ref=${FSLDIR}/data/standard/MNI152_T1_1mm_brain --aff=t1/t12mni_affine.mat --cout=t1/t12mni_nonlinear

# Apply transformations to Flair
applywarp --ref=${FSLDIR}/data/standard/MNI152_T1_1mm_brain --in=flair/flair_brain --warp=t1/t12mni_nonlinear --premat=flair/flair2t1.mat --out=flair/flair_mni

# fslmaths mask_in_functional_space -thr 0.5 -bin mask_in_functional_space



