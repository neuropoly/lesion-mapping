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
import numpy as np
import commands

import sct_utils as sct
from spinalcordtoolbox.image import Image

from config_file import config

PARAM_REG = 'step=1,type=seg,algo=centermass,metric=MeanSquares,slicewise=1:step=2,type=seg,algo=bsplinesyn,metric=MeanSquares,slicewise=1,iter=3'

def register_to_template(img_path, sc_path, contrast, label_path, label_flag, ofolder, qc_folder):

    registration_status = 1

    try:
        sct.run(['sct_register_to_template', '-i', img_path,
                                            '-s', sc_path,
                                            '-c', contrast,
                                            label_flag, label_path,
                                            '-param', PARAM_REG,
                                            '-ofolder', ofolder,
                                            '-qc', qc_folder])
    except:
        im_ana, im_seg = Image(img_path), Image(sc_path)
        im_seg_new = im_ana.copy() # copy hdr --> segmentation
        im_seg_new.data = im_seg.data
        im_seg_new.save(sc_path)

        im_labels = Image(label_path)
        im_labels_new = im_ana.copy() # copy hdr --> labels
        im_labels_new.data = im_labels.data 
        im_labels_new.change_type(type='uint8')
        im_labels_new.save(label_path)

        try: # re-run
            sct.run(['sct_register_to_template', '-i', img_path,
                                                '-s', sc_path,
                                                '-c', contrast,
                                                label_flag, label_path,
                                                '-param', PARAM_REG,
                                                '-ofolder', ofolder,
                                                '-qc', qc_folder])
        except:
            registration_status = 0
            sct.printv('ERROR: Could not complete registration for anat. --> template! Path: %s' % img_path)

    return registration_status


def warp_template(dest_img, warping_field, ofolder, qc_folder):

    sct.run(['sct_warp_template', '-d', dest_img,
                                    '-w', warping_field,
                                    '-ofolder', ofolder,
                                    '-qc', qc_folder])


def exist_gap(lvl_filename_lst):
    lvl_lvl_lst = [list(np.unique(Image(filename).data)) for filename in lvl_filename_lst]
    lvl_lst = list(set([int(l) for sublist in lvl_lvl_lst for l in sublist]))
    return sorted(lvl_lst) !=  range(min(lvl_lst), max(lvl_lst)+1)


def merge_images_in_template(fname_out, subj_fold, img_lst, mask_suffixe):
    mask_lst = [os.path.join(subj_fold, img_suff, img_suff+'_'+mask_suffixe) for img_suff in img_lst]
    warp_lst = [os.path.join(subj_fold, img_suff, 'warp_anat2template.nii.gz') for img_suff in img_lst]
    dest = os.path.join(commands.getstatusoutput('echo $SCT_DIR')[1], 'data/PAM50/template/PAM50_t2.nii.gz')

    sct.run(['sct_merge_images', '-i', ','.join(mask_lst),
                        '-d', dest,
                        '-w', ','.join(warp_lst),
                        '-o', fname_out])

    return 1 if os.path.isfile(fname_out) else 0


def main(args=None):

    subj_data_df = pd.read_pickle('0_results.pkl')

    path_data = config['path_data']
    center_dct = config["dct_center"]
    path_qc = os.path.join(config["path_results"], 'qc')

    excluded_subject, gap_subject_lst = [], []
    for index, row in subj_data_df.iterrows():
        image_lst = center_dct[row.center]
        subj_fold = os.path.join(path_data, row.subject, 'spinalcord')

        if os.path.isdir(subj_fold):
            reg_status = 1
            subj_fold_qc = os.path.join(path_data, row.subject, row.subject+'_spinalcord') # Used to have the subject name in the QC
            os.rename(subj_fold, subj_fold_qc)
            for img_prefixe in image_lst:
                img_fold = os.path.join(subj_fold_qc, img_prefixe)
                if os.path.isdir(img_fold):
                    img_path = os.path.join(img_fold, img_prefixe + '.nii.gz')
                    sc_path = os.path.join(img_fold, img_prefixe + '_seg_manual.nii.gz')
                    label_path = os.path.join(img_fold, 'labels_disc.nii.gz')
                    label_flag = '-ldisc'
                    if not os.path.isfile(label_path):
                        label_path = os.path.join(img_fold, 'labels_vert.nii.gz')
                        label_flag = '-l'
                    contrast = img_prefixe.split('_')[0]

                    out_path = os.path.join(img_fold, 'template2anat.nii.gz')
                    if not os.path.isfile(out_path):
                        print row.subject, img_prefixe
                        reg_status = register_to_template(img_path,
                                                            sc_path,
                                                            contrast,
                                                            label_path,
                                                            label_flag,
                                                            img_fold,
                                                            path_qc)
                        
                    atlas_path = os.path.join(img_fold, 'label')
                    warping_field_path = os.path.join(img_fold, 'warp_template2anat.nii.gz')
                    if not os.path.isdir(atlas_path) and os.path.isfile(warping_field_path):
                        warp_template(img_path,
                                        warping_field_path,
                                        atlas_path,
                                        path_qc)
                        if not os.path.isdir(atlas_path):
                            reg_status = 0

            if exist_gap([os.path.join(subj_fold_qc, img_prefixe, 'label', 'template', 'PAM50_levels.nii.gz') for img_prefixe in image_lst]):
                gap_subject_lst.append(row.subject)

            lesion_mask_path = os.path.join(subj_fold_qc, 'lesion_mask_template.nii.gz')
            cord_mask_path = os.path.join(subj_fold_qc, 'cord_mask_template.nii.gz')
            if not os.path.isfile(lesion_mask_path):
                reg_status = merge_images_in_template(lesion_mask_path,
                                                        subj_fold_qc,
                                                        image_lst,
                                                        'lesion_manual.nii.gz')
            if not os.path.isfile(cord_mask_path):
                reg_status = merge_images_in_template(cord_mask_path,
                                                        subj_fold_qc,
                                                        image_lst,
                                                        'seg_manual.nii.gz')

            os.rename(subj_fold_qc, subj_fold)
            if not reg_status:
                excluded_subject.append(index)

    subj_data_df = subj_data_df.drop(subj_data_df.index[excluded_subject])
    subj_data_df.to_pickle('1_results.pkl')

    if len(gap_subject_lst):
        print '\n\nPlease check the following subjects, where we detected a gap in terms of vertebral distribution after registration on the PAM50 template.'
        print '\n\t- '.join(gap_subject_lst)

if __name__ == "__main__":
    main()
