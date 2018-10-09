#!/bin/bash
#
# Usage:
#   ./1_register_data_anima.sh <subject_folder>
#
# Example:
#   ./1_register_data_anima.sh /home/charley/data/brain_spine/processing_data/rennes_20170112_10/
#
# NB: add the flag "-x" after "!/bin/bash" for full verbose of commands.
# Charley Gros 2018-10-07
# modified: 2018-10-07

PATH_ANIMA_SCRIPT="/home/charley/code/Anima-Scripts-Public/brain_extraction/"

cd $1

# Brain extraction of T1 image
python ${PATH_ANIMA_SCRIPT}animaAtlasBasedBrainExtraction.py t1/t1.nii.gz
animaConvertImage -i t1/t1_masked.nrrd -o t1/t1_brain.nii.gz

# Brain extraction of FLAIR image
python ${PATH_ANIMA_SCRIPT}animaAtlasBasedBrainExtraction.py flair/flair.nii.gz
animaConvertImage -i flair/flair_masked.nrrd -o flair/flair_brain.nii.gz

# Intra subject linear registration: Flair --> T1
animaPyramidalBMRegistration -r t1/t1_brain.nii.gz -m flair/flair_brain.nii.gz -o flair/flair_t1.nii.gz -O flair/flair2t1.txt

# Rigid registration of T1 to the MNI152_T1_1mm: T1_rig
animaPyramidalBMRegistration -r ${FSLDIR}/data/standard/MNI152_T1_1mm_brain.nii.gz -m t1/t1_brain.nii.gz -o t1/t1_mni_rig.nii.gz -O t1/t12mni_rig.txt

# # Affine registration of T1_rig to the MNI152_T1_1mm: T1_aff
animaPyramidalBMRegistration -r ${FSLDIR}/data/standard/MNI152_T1_1mm_brain.nii.gz -m t1/t1_mni_rig.nii.gz --ot 2 -o t1/t1_mni_aff.nii.gz -O t1/t12mni_aff.txt

# Non Linear registration of T1 to the MNI152_T1_1mm: T1_nonlin
animaDenseSVFBMRegistration -r ${FSLDIR}/data/standard/MNI152_T1_1mm_brain.nii.gz -m t1/t1_mni_aff.nii.gz -o t1/t1_mni_nonlin.nii.gz -O t1/t12mni_nonlin.nii.gz

# Concatenate the transformation from the flair space to the MNI space
animaTransformSerieXmlGenerator -i flair/flair2t1.txt -i t1/t12mni_rig.txt -i t1/t12mni_aff.txt -i t1/t12mni_nonlin.nii.gz -o flair/flair2mni.xml

# Apply the transformations
animaApplyTransformSerie -i flair/flair_brain.nii.gz -g ${FSLDIR}/data/standard/MNI152_T1_1mm_brain.nii.gz -t flair/flair2mni.xml -o flair/flair_mni.nii.gz