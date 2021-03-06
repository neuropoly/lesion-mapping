#!/bin/bash
#
# Usage:
#   ./1_register_data.sh <subject_folder> <atlas_folder> <anima_brainExtraction_folder>
#
# Example:
#   ./1_register_data.sh /home/charley/data/brain_spine/processing_data/rennes_20170112_10/ /home/charley/data/brain_spine/atlases/ /home/charley/code/Anima-Scripts-Public/brain_extraction/
#
# NB: add the flag "-x" after "!/bin/bash" for full verbose of commands.
# Charley Gros 2018-10-07
# modified: 2018-10-23

cd $1

if [ ! -f $4/mni2$4.xml ]; then
	# Brain extraction of T1 image
	python $3animaAtlasBasedBrainExtraction.py -i t1/t1.nii.gz
	animaConvertImage -i t1/t1_masked.nrrd -o t1/t1_brain.nii.gz

	# Brain extraction of FLAIR image
	python $3animaAtlasBasedBrainExtraction.py -i $4/$4.nii.gz
	animaConvertImage -i $4/$4_masked.nrrd -o $4/$4_brain.nii.gz

	# Intra subject linear registration: Flair --> T1
	animaPyramidalBMRegistration -r t1/t1_brain.nii.gz -m $4/${4}_brain.nii.gz -o ${4}/${4}_t1.nii.gz -O ${4}/${4}2t1.txt

	# Rigid registration of T1 to the MNI152_T1_1mm: T1_rig
	animaPyramidalBMRegistration -r ${FSLDIR}/data/standard/MNI152_T1_1mm_brain.nii.gz -m t1/t1_brain.nii.gz -o t1/t1_mni_rig.nii.gz -O t1/t12mni_rig.txt

	# Affine registration of T1_rig to the MNI152_T1_1mm: T1_aff
	animaPyramidalBMRegistration -r ${FSLDIR}/data/standard/MNI152_T1_1mm_brain.nii.gz -m t1/t1_mni_rig.nii.gz --ot 2 -o t1/t1_mni_aff.nii.gz -O t1/t12mni_aff.txt

	# Non Linear registration of T1 to the MNI152_T1_1mm: T1_nonlin
	animaDenseSVFBMRegistration -r ${FSLDIR}/data/standard/MNI152_T1_1mm_brain.nii.gz -m t1/t1_mni_aff.nii.gz -o t1/t1_mni_nonlin.nii.gz -O t1/t12mni_nonlin.nii.gz

	# Concatenate the transformation from the flair space to the MNI space
	animaTransformSerieXmlGenerator -i $4/${4}2t1.txt -i t1/t12mni_rig.txt -i t1/t12mni_aff.txt -i t1/t12mni_nonlin.nii.gz -o $4/${4}2mni.xml

	# Apply the transformations
	animaApplyTransformSerie -i $4/$4_brain.nii.gz -g ${FSLDIR}/data/standard/MNI152_T1_1mm_brain.nii.gz -t ${4}/${4}2mni.xml -o $4/${4}_mni.nii.gz

	# Compute the inverse transformation: from MNI space to flair space
	animaTransformSerieXmlGenerator -i t1/t12mni_nonlin.nii.gz -i t1/t12mni_aff.txt -i t1/t12mni_rig.txt -i $4/${4}2t1.txt -I 1 -I 2 -I 3 -I 4 -o $4/mni2${4}.xml
fi

if [ ! -d $4/label ]; then
	mkdir $4/label
	# Warp atlas to flair space
	for f in $2brain/*.nii.gz ; do
		animaApplyTransformSerie -g $4/$4_brain.nii.gz -i ${f} -t $4/mni2${4}.xml -n linear -o $4/label/$(basename "$f")
	done
	for f in $2brainstem/*.nii.gz ; do
		animaApplyTransformSerie -g $4/$4_brain.nii.gz -i ${f} -t $4/mni2${4}.xml -n linear -o $4/label/$(basename "$f")
	done
fi

if [ ! -f $4/$4_brainMask_mni.nii.gz ]; then
	# Warp the lesion mask from flair to MNI space
	animaApplyTransformSerie -i $4/$4_lesion_manual.nii.gz -g ${FSLDIR}/data/standard/MNI152_T1_1mm_brain.nii.gz -t $4/${4}2mni.xml -n linear -o $4/$4_lesion_manual_mni.nii.gz
	# Warp the brain mask from flair to MNI space
	animaApplyTransformSerie -i $4/$4_brainMask.nii.gz -g ${FSLDIR}/data/standard/MNI152_T1_1mm_brain.nii.gz -t $4/${4}2mni.xml -n linear -o $4/$4_brainMask_mni.nii.gz
fi
