#
# Preprocessing SC: run sct_register_multimodal on T1 (followup) spinalcord data
#
# Usage: python preprocessT1_sc_reg.py <input_folder> <T1_foldername>
#
# Example: python preprocessT1_sc_reg.py ../data_processing M24
#

import os
import sys

LABELS_SUFFIX = ['3_6', '3_4' ,'5_7' ,'1_3' ,'1_2' ,'4_6']
PARAMS_REG = 'step=0,type=label,dof=Tx_Ty_Tz_Sz:step=1,type=seg,algo=affine,metric=MeanSquares:step=2,type=seg,algo=slicereg,metric=MeanSquares:step=3,type=im,algo=syn,metric=MI,iter=5,shrink=2'

def _find_labels_fname(folder):
	for l in LABELS_SUFFIX:
		fname = os.path.join(folder, 'labels_disc_'+l+'.nii.gz')
		if os.path.isfile(fname):
			break
	return fname, l


def run_main(ifolder, t1_name):

    missing_files = []
    # loop over subjects
    for s in os.listdir(ifolder):
        s_fold = os.path.join(ifolder, s)
        if os.path.isdir(s_fold):
            t1_fold = os.path.join(s_fold, 'spinalcord', t1_name)
            if os.path.isdir(t1_fold):
                # loop over SC contrasts
                for c in os.listdir(t1_fold):
                    c_fold = os.path.join(t1_fold, c)
                    i_fname = os.path.join(t1_fold, c, c+'.nii.gz')
                    s_fname = os.path.join(t1_fold, c, c+'_seg.nii.gz')
                    l_fname, suffix = _find_labels_fname(os.path.join(t1_fold, c))

                    if not os.path.isdir(c_fold):
                        continue

                    if all(os.path.isfile(f) for f in [i_fname, s_fname, l_fname]):
                        c_ref_fold = os.path.join(s_fold, 'spinalcord', 'M0', c)
                        i_ref_fname = os.path.join(c_ref_fold, c+'.nii.gz')
                        s_ref_fname = os.path.join(c_ref_fold, c+'_seg_manual.nii.gz')
                        l_ref_fname = os.path.join(c_ref_fold, 'labels_disc_'+suffix+'.nii.gz')

                        if all(os.path.isfile(f) for f in [i_ref_fname, s_ref_fname, l_ref_fname]):
                            print('\nRegistration of: '+c_fold)
                            cmd = 'sct_register_multimodal -i '+i_fname
                            cmd += ' -iseg '+s_fname
                            cmd += ' -ilabel '+l_fname
                            cmd += ' -d '+i_ref_fname
                            cmd += ' -dseg '+s_ref_fname
                            cmd += ' -dlabel '+l_ref_fname
                            cmd += ' -param '+PARAMS_REG
                            cmd += ' -ofolder '+os.path.join(c_ref_fold, t1_name)
                            os.system(cmd)

                        else:
                            print('\nMissing files for: '+c_ref_fold)
                            missing_files.append(c_ref_fold)
                    else:
                        print('\nMissing files for: '+c_fold)
                        missing_files.append(c_fold)

    print('\nMissing files in the following folders: ')
    print('\n\t'+'\n\t'.join(missing_files))
    print('\n------ END ------\n')


if __name__ == '__main__':
    ifolder, t1folder = sys.argv[1:]
    run_main(ifolder, t1folder)
