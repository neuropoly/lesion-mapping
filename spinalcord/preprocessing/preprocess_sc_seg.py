#
# Preprocessing SC: run sct_deepseg_sc on T1 (follow-up) spinalcord data
#
# Usage: python preprocessT1_sc_seg.py <input_folder> <T1_foldername>
#
# Example: python preprocessT1_sc_seg.py ../data_processing M24
#

import os
import sys

def run_main(ifolder, t1_name):

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

                    if os.path.isdir(c_fold):
                        if os.path.isfile(s_fname):
                            print(s+'/'+c+ 'already segmented.')
                        else:
                            print('Segmentation of: ' + s+'/'+c)

                            c_algo = 't2s' if c.startswith('t2s') else 't2'

                            cmd = 'sct_deepseg_sc -i ' + i_fname
                            cmd += ' -c ' + c_algo
                            cmd += ' -ofolder ' + c_fold
                            cmd += ' -v 0'
                            os.system(cmd)

    print('\n------ END ------\n')


if __name__ == '__main__':
    ifolder, t1folder = sys.argv[1:]
    run_main(ifolder, t1folder)
