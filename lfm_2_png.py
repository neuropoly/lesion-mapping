#!/usr/bin/env python
#
# Goal: To capture axial views of LFMs.
#
# Created: 2018-10-30
# Modified: 2018-10-31
# Contributors: Charley Gros

import os
import numpy as np
import commands
import sys
import matplotlib.pyplot as plt
from skimage.measure import find_contours
from scipy.ndimage.morphology import binary_dilation

from spinalcordtoolbox.image import Image

from brain.config_file import config

path_smatt = '/Volumes/projects/ms_brain_spine/atlases/brain'
path_brainstem = '/Volumes/projects/ms_brain_spine/atlases/brainstem'


def load_data(path, thr_bin=0):
    img = Image(path).change_orientation('RPI')
    data = (img.data > 0).astype(np.int)
    del img
    return data

def load_brain_brainstem_motor():
    # fname_M1_lst = ['Right-M1-S-MATT.nii', 'Left-M1-S-MATT.nii']
    fname_M1_lst = ['brain_M1_R.nii.gz', 'brain_M1_L.nii.gz',
                    'brain_PMv_R.nii.gz', 'brain_PMv_L.nii.gz',
                    'brain_PMd_R.nii.gz', 'brain_PMd_L.nii.gz',
                    'brain_preSMA_R.nii.gz', 'brain_preSMA_L.nii.gz',
                    'brain_S1_R.nii.gz', 'brain_S1_L.nii.gz',
                    'brain_SMA_R.nii.gz', 'brain_SMA_L.nii.gz']
    fname_brainstem_lst = ['brainstem_CST_L.nii.gz', 'brainstem_CST_R.nii.gz']
    BRAMSTEM_ZTOP = 51

    data_M1 = np.sum([load_data(os.path.join(path_smatt, f), thr_bin=0) for f in fname_M1_lst], axis=0)
    data_brainstem = np.sum([load_data(os.path.join(path_brainstem, f), thr_bin=0.01) for f in fname_brainstem_lst], axis=0)

    data_M1[:, :, :BRAMSTEM_ZTOP+1] = 0.0
    data_brainstem[:, :, BRAMSTEM_ZTOP+1:] = 0.0

    data_motor = data_M1 + data_brainstem

    return data_motor


def load_brain_brainstem_M1():
    fname_M1_lst = ['brain_M1_R.nii.gz', 'brain_M1_L.nii.gz']
    fname_brainstem_lst = ['brainstem_CST_L.nii.gz', 'brainstem_CST_R.nii.gz']
    BRAMSTEM_ZTOP = 51

    data_M1 = np.sum([load_data(os.path.join(path_smatt, f), thr_bin=0) for f in fname_M1_lst], axis=0)
    data_brainstem = np.sum([load_data(os.path.join(path_brainstem, f), thr_bin=0.01) for f in fname_brainstem_lst], axis=0)

    data_M1[:, :, :BRAMSTEM_ZTOP+1] = 0.0
    data_brainstem[:, :, BRAMSTEM_ZTOP+1:] = 0.0

    data_motor = data_M1 + data_brainstem

    return data_motor

def rescale_rot(img, rescale):
    img = np.repeat(img, rescale, axis=0)
    img = np.repeat(img, rescale, axis=1)
    img = np.rot90(img)
    return img


def combine_img_w_bkg(img, bkg, cst, rescale, thr, fname_out, color='black', linewidth=4, brain_sc=0):
    i_zero, i_nonzero = np.where(img==0.0), np.nonzero(img)

    img_jet = plt.cm.jet(plt.Normalize(vmin=0, vmax=thr)(img))
    img_jet[i_zero] = 0.0

    bkg_grey = plt.cm.binary_r(plt.Normalize(vmin=np.amin(bkg), vmax=np.amax(bkg))(bkg))

    img_out = np.copy(bkg_grey)
    img_out[i_nonzero] = img_jet[i_nonzero]

    img_out = rescale_rot(img_out, rescale)
    cst = rescale_rot(cst, rescale)

    ratio_shape = img_out.shape[0] * 1. / img_out.shape[1]
    plt.figure(figsize=(10, 10*ratio_shape))
    plt.subplot(1, 1, 1)
    plt.axis("off")
    plt.imshow(img_out, interpolation='nearest', aspect='auto')

    cst_dilated = binary_dilation(cst) if brain_sc else binary_dilation(cst, iterations=3)
    contours = find_contours(cst_dilated, .5)
    for n, contour in enumerate(contours):
        plt.plot(contour[:, 1], contour[:, 0], 'white', linewidth=linewidth)
    for n, contour in enumerate(contours):
        plt.plot(contour[:, 1], contour[:, 0], 'crimson', linewidth=linewidth//2)

    plt.savefig(fname_out, dpi=800)
    plt.close()

def save_colormap(fname_out, cmap='jet'):
    fig = plt.figure(figsize=[10, 1])
    ax = fig.add_subplot(111)

    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    ax.imshow(gradient, aspect='auto', cmap=cmap)

    ax.set_axis_off()
    fig.savefig(fname_out)
    plt.close()


def extract_slices(img, backgroud, cst, z_lst):
    img_lst = [img[:, :, int(z)] for z in z_lst if int(z) in range(img.shape[2])]
    bkg_lst = [backgroud[:, :, int(z)] for z in z_lst if int(z) in range(backgroud.shape[2])]
    cst_lst = [cst[:, :, int(z)] for z in z_lst if int(z) in range(cst.shape[2])]
    pref_lst = ['z'+str(i) for i in z_lst]

    return img_lst, bkg_lst, cst_lst, pref_lst


def load_PAM50_motor():
    path_atlas = os.path.join(commands.getstatusoutput('echo $SCT_DIR')[1], 'data', 'PAM50', 'atlas')

    data = np.sum([load_data(os.path.join(path_atlas, 'PAM50_atlas_'+t+'.nii.gz'), thr_bin=0) for t in ['05', '04', '23', '22']], axis=0)

    return data

def main(lfm_path, brain_spinalcord, thr, ofolder, z_lst):

    img_img = Image(lfm_path).change_orientation('RPI')
    img = img_img.data
    del img_img

    if brain_spinalcord:
        path_pam50 = os.path.join(commands.getstatusoutput('echo $SCT_DIR')[1], 'data', 'PAM50', 'template', 'PAM50_t2.nii.gz')
        img_background = Image(path_pam50)
        backgroud = img_background.data
        del img_background
        x_shape, y_shape, z_shape = backgroud.shape
        x_mean, y_mean = x_shape // 2, y_shape // 2
        backgroud = backgroud[x_mean-25:x_mean+25, y_mean-25:y_mean+25, :]
        img = img[x_mean-25:x_mean+25, y_mean-25:y_mean+25, :]

        cst_mask = load_PAM50_motor()
        cst_mask = cst_mask[x_mean-25:x_mean+25, y_mean-25:y_mean+25, :]

        path_pam50_lvl = os.path.join(commands.getstatusoutput('echo $SCT_DIR')[1], 'data', 'PAM50', 'template', 'PAM50_label_disc.nii.gz')
        img_lvl = Image(path_pam50_lvl)
        data_lvl = img_lvl.data
        del img_lvl

        lvl_z_lst = [np.where(data_lvl == lvl)[2][0] for lvl in np.unique(data_lvl) if lvl in range(1, 9)]

        if int(z_lst[0]) == -1:
            img_lst, bkg_lst, cst_lst = [], [], []
            for lvl_idx in range(len(lvl_z_lst)-1):
                z_bot, z_top = lvl_z_lst[lvl_idx+1], lvl_z_lst[lvl_idx]+1
                z_mid_lvl = (z_top+z_bot) // 2
                img_lst.append(np.mean(img[:, :, z_bot:z_top], axis=2))
                bkg_lst.append(backgroud[:, :, z_mid_lvl])
                cst_lst.append(cst_mask[:, :, z_mid_lvl])
            pref_lst = ['C'+str(i) for i in range(1, 8)]
        else:
            img_lst, bkg_lst, cst_lst, pref_lst = extract_slices(img, backgroud, cst_mask, z_lst)

        linewidth = 10

    else:
        path_mni = os.path.join(commands.getstatusoutput('echo $FSLDIR')[1], 'data', 'standard', 'MNI152_T1_1mm.nii.gz')
        img_background = Image(path_mni).change_orientation('RPI')
        backgroud = img_background.data
        del img_background

        cst_mask = load_brain_brainstem_motor()
        #cst_mask = load_brain_brainstem_M1()

        img_lst, bkg_lst, cst_lst, pref_lst = extract_slices(img, backgroud, cst_mask, z_lst)

        linewidth = 10

    if not os.path.isdir(ofolder):
        os.makedirs(ofolder)

    for img_cur, bkg_cur, cst_cur, pref_cur in zip(img_lst, bkg_lst, cst_lst, pref_lst):
        fname_out_cur = os.path.join(ofolder, pref_cur+'.png')
        img_bkg_cst_cur = combine_img_w_bkg(img_cur, bkg_cur, cst_cur, 4, thr, fname_out_cur, linewidth=linewidth, brain_sc=brain_spinalcord)

    save_colormap(os.path.join(ofolder, 'jet_0_'+str(int(thr*100))+'.png'))

if __name__ == "__main__":
    lfm_path, brain_spinalcord, max_freq, o_folder, z_lst = sys.argv[1:]
    main(lfm_path, int(brain_spinalcord), float(max_freq), o_folder, z_lst.split(','))
