#!/usr/bin/env python
#
# Goal: To register the axial image into the PAM50 space.
#
# Steps:
# (1) 
#
# Created: 2018-10-01
# Modified: 2018-10-01
# Contributors: Charley Gros

import os
import pandas as pd

import sct_utils as sct
from spinalcordtoolbox.image import Image

from config_file import config

PARAM_REG = 'step=1,type=seg,algo=centermassrot,metric=MeanSquares:step=2,type=seg,algo=bsplinesyn,shrink=8,metric=MeanSquares:step=3,type=seg,algo=bsplinesyn,shrink=4,metric=MeanSquares:step=4,type=im,algo=bsplinesyn,metric=MI,iter=5,shrink=1'

def register_to_template(img_path, sc_path, contrast, label_path, label_flag):

    registration_status = 1

    try:
        sct.run(['sct_register_to_template', '-i', img_path,
                                            '-s', sc_path,
                                            '-c', contrast,
                                            label_flag, label_path,
                                            '-param', PARAM_REG,
                                            '-v', '2'])
    except:
        im_ana, im_seg = Image(img_path), Image(sc_path)
        im_seg_new = im_ana.copy() # copy hdr --> segmentation
        im_seg_new.data = im_seg.data
        im_seg_new.save(sc_path)

        im_labels = Image(label_path)
        im_labels_new = im_ana.copy() # copy hdr --> labels
        im_labels_new.data = im_labels.data 
        im_labels_new.changeType(type='uint8')
        im_labels_new.save(label_path)

        try: # re-run
            sct.run(['sct_register_to_template', '-i', img_path,
                                                '-s', sc_path,
                                                '-c', contrast,
                                                label_flag, label_path,
                                                '-param', PARAM_REG,
                                                '-v', '2'])
        except:
            registration_status = 0
            sct.printv('ERROR: Could not complete registration for anat. --> template! Path: %s' % img_path)
    
    return registration_status


def main(args=None):

    subj_data_df = pd.read_pickle('0_results.pkl')

    path_data = config['path_data']
    center_dct = config["dct_center"]
    current_dir = os.getcwd()

    excluded_subject = []
    for index, row in subj_data_df.iterrows():
        image_lst = center_dct[row.center]
        subj_fold = os.path.join(path_data, row.subject, 'spinalcord')
        if os.path.isdir(subj_fold):
            for img_prefixe in image_lst:
                img_fold = os.path.join(subj_fold, img_prefixe)
                if os.path.isdir(subj_fold):
                    img_path = os.path.join(img_fold, img_prefixe + '.nii.gz')
                    sc_path = os.path.join(img_fold, img_prefixe + '_seg_manual.nii.gz')
                    label_path = os.path.join(img_fold, 'labels_disc.nii.gz')
                    label_flag = '-ldisc'
                    if not os.path.isfile(label_path):
                        label_path = os.path.join(img_fold, 'labels_vert.nii.gz')
                        label_flag = '-l'
                    contrast = img_prefixe.split('_')[0]

                    out_path = os.path.join(img_fold, 'anat2template.nii.gz')
                    if not os.path.isfile(out_path):
                        print img_path
                        os.chdir(img_fold)
                        reg_status = register_to_template(img_path,
                                                            sc_path,
                                                            contrast,
                                                            label_path,
                                                            label_flag)
                        os.chdir(current_dir)

                        if not reg_status:
                            excluded_subject.append(index)

    subj_data_df = subj_data_df.drop(subj_data_df.index[excluded_subject])
    subj_data_df.to_pickle('1_results.pkl')

if __name__ == "__main__":
    main()