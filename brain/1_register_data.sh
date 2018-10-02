# BET
bet t1/t1 t1/t1_brain
bet flair/flair flair/flair_brain

# Register flair to t1 image
flirt -in flair/flair_brain -ref t1/t1_brain -out flair/flair_t1 -omat flair/flair2t1.mat -dof 6

# Register t1 image to MNI152_T1_1mm_brain space, in two steps
# 1 -- FLIRT
flirt -in t1/t1_brain -ref ${FSLDIR}/data/standard/MNI152_T1_1mm_brain -out t1/t1_mni -omat t1/t12mni_affine.mat
# 2 -- FNIRT
fnirt --in=t1/t1_brain --ref=${FSLDIR}/data/standard/MNI152_T1_1mm_brain --aff=t1/t12mni_affine.mat --cout=t1/t12mni_nonlinear

# Wrap flair image to MNI152_T1_1mm_brain space by using the transformations previously computed
applywarp --ref=${FSLDIR}/data/standard/MNI152_T1_1mm_brain --in=flair/flair_brain --warp=t1/t12mni_nonlinear --premat=flair/flair2t1.mat --out=flair/flair_mni

# Wrap lesion mask to MNI152_T1_1mm_brain space