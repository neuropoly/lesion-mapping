%%% Registration WM atlas

%% FA template = JHU-ICBM-FA-1mm.nii.gz , Atlas = JHU-ICBM-labels-1mm.nii.gz

list = sct_tools_ls('RAMRI*');
for ilist = 1:length(list)
    currentfolder = list{ilist};
    subj_name = currentfolder;
    currentfolder = strcat('/Volumes/projects/RAMRI/RAMRI_data/RAMRI_data_WM/', currentfolder, '/Processed_data/');
    cd(currentfolder)
    
    % Participants are first aligned into a common space. The JHU-ICBM-FA template is used as a reference for all subjects.
    
      % Affine transfo on FA
    sct_unix('isct_antsRegistration --dimensionality 3 --transform affine[1] --metric MI[FA.nii.gz,JHU-ICBM-FA-1mm.nii.gz,1,32] --convergence 30x10x5  --shrink-factors 5x3x1 --smoothing-sigmas 0x0x0mm --output [step0,src_regStep0.nii] --verbose 1');
      % Non-linear
    sct_unix('isct_antsRegistration --dimensionality 3 --transform bsplinesyn[0.5,3] --metric MI[FA.nii.gz,JHU-ICBM-FA-1mm.nii.gz,1,32] --convergence 30x10x5  --shrink-factors 5x3x1 --smoothing-sigmas 0x0x0mm --output [step1,src_regStep1.nii] --verbose 1 -r step00GenericAffine.mat');
      % Concat + apply warp to labels
    sct_unix('sct_concat_transfo -d JHU-ICBM-FA-1mm.nii.gz -w step11InverseWarp.nii.gz,-step00GenericAffine.mat -o warp_FA_to_JHU.nii.gz');
    sct_unix('sct_apply_transfo -d JHU-ICBM-labels-1mm.nii.gz -i FA.nii.gz -w warp_FA_to_JHU.nii.gz -o FA_to_JHU.nii.gz -x nn');
      % In order to help the convergence of registration, the Laplacian transform is applied on 3D volumes in order to increase the contrast between white and gray matter
    sct_unix('sct_maths -i FA_to_JHU.nii.gz -laplacian 2 -o FA_l.nii.gz');
    sct_unix('sct_maths -i JHU-ICBM-FA-1mm.nii.gz -laplacian 2 -o JHU_l.nii.gz');
      % The resulted images were registered together using Ants non linear registration tools 
    sct_unix('isct_antsRegistration --dimensionality 3 --transform bsplinesyn[0.5,3] --metric CC[FA_l.nii.gz,JHU_l.nii.gz,1,6] --convergence 10  --shrink-factors 1 --smoothing-sigmas 0mm --output [step2,src_regStep2.nii] --verbose 1');
    sct_unix('sct_apply_transfo -i FA_to_JHU.nii.gz -d JHU-ICBM-labels-1mm.nii.gz -w step20InverseWarp.nii.gz -x linear -o FA_2_JHU_2.nii.gz');
       % The same transformations were then applied to RD
    sct_unix('sct_apply_transfo -d JHU-ICBM-labels-1mm.nii.gz -i RD.nii.gz -w warp_FA_to_JHU.nii.gz -o RD_to_JHU.nii.gz -x nn'); 
    sct_unix('sct_apply_transfo -i RD_to_JHU.nii.gz -d JHU-ICBM-labels-1mm.nii.gz -w step20InverseWarp.nii.gz -x linear -o RD_2_JHU_2.nii.gz');
    
end 

