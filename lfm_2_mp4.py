#!/usr/bin/env python
#
# Goal: To generate Lesion Frequency Maps.
#
# Created: 2018-10-27
# Modified: 2018-10-27
# Contributors: Charley Gros

import os
import numpy as np
import commands
import sys

# import sct_utils as sct
from spinalcordtoolbox.image import Image#, zeros_like

# from config_file import config

import matplotlib.pyplot as plt
import matplotlib.animation as anim
 
class AnimatedGif:
    def __init__(self, size=(640, 480)):
        self.fig = plt.figure()
        self.fig.set_size_inches(size[0] / 100, size[1] / 100)
        self.size_x = size[0]
        self.size_y = size[1]
        ax = self.fig.add_axes([0, 0, 1, 1], frameon=False, aspect=1)
        ax.set_xticks([])
        ax.set_yticks([])
        self.images = []
 
    def add(self, image, label=''):
        plt_im = plt.imshow(image, cmap='Greys', vmin=0, vmax=1, animated=True)
        plt_txt = plt.text(self.size_x * 3 // 4, self.size_y - 10, label, color='red')
        self.images.append([plt_im, plt_txt])
 
    def save(self, filename):
        animation = anim.ArtistAnimation(self.fig, self.images)
        animation.save(filename, writer='imagemagick', fps=10)


def combine_img_w_bkg(img, bkg, rescale):
    i_zero, i_nonzero = np.where(img==0.0), np.nonzero(img)

    img_jet = plt.cm.jet(plt.Normalize(vmin=np.amin(img), vmax=np.amax(img))(img))
    img_jet[i_zero] = 0.0

    bkg_grey = plt.cm.binary_r(plt.Normalize(vmin=np.amin(bkg), vmax=np.amax(bkg))(bkg))

    img_out = np.copy(bkg_grey)
    img_out[i_nonzero] = img_jet[i_nonzero]
    img_out = np.repeat(img_out, rescale, axis=0)
    img_out = np.repeat(img_out, rescale, axis=1)
    img_out = np.rot90(img_out)
    
    return img_out

def main(img_path, brain_spinalcord, sagittal_coronal_axial):

    img_img = Image(img_path).change_orientation('RPI')
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

        path_pam50_lvl = os.path.join(commands.getstatusoutput('echo $SCT_DIR')[1], 'data', 'PAM50', 'template', 'PAM50_levels.nii.gz')
        img_lvl = Image(path_pam50_lvl)
        z_top = np.max(list(set(np.where(img_lvl.data == 1)[2]))) + 1
        z_bottom = np.min(list(set(np.where(img_lvl.data == 7)[2])))
        del img_lvl

        backgroud = backgroud[:, :, z_bottom:z_top]
        img = img[:, :, z_bottom:z_top]
        if sagittal_coronal_axial == 0:
            idx_lst = range(x_mean-25, x_mean+25)
        elif sagittal_coronal_axial == 1:
            idx_lst = range(y_mean-25, y_mean+25)
        else:
            idx_lst = range(z_bottom, z_top)

        rescale = 4
    else:
        path_mni = os.path.join(commands.getstatusoutput('echo $FSLDIR')[1], 'data', 'standard', 'MNI152_T1_1mm.nii.gz')
        img_background = Image(path_mni).change_orientation('RPI')
        backgroud = img_background.data
        del img_background

        BRAMSTEM_ZBOT = 14
        backgroud = backgroud[:, :, BRAMSTEM_ZBOT:]
        img = img[:, :, BRAMSTEM_ZBOT:]

        rescale = 2

        idx_lst = range(1, backgroud.shape[sagittal_coronal_axial]+1)

    img_lst = np.split(img, img.shape[sagittal_coronal_axial], axis=sagittal_coronal_axial)
    bkg_lst = np.split(backgroud, img.shape[sagittal_coronal_axial], axis=sagittal_coronal_axial)

    animated_gif = AnimatedGif(size=(float(img_lst[0].mean(axis=sagittal_coronal_axial).shape[0])*rescale,
                                    float(img_lst[0].mean(axis=sagittal_coronal_axial).shape[1])*rescale))
    for img_cur, bkg_cur, idx_cur in zip(img_lst, bkg_lst, idx_lst):
        img_bkg_cur = combine_img_w_bkg(img_cur.mean(axis=sagittal_coronal_axial),
                                        bkg_cur.mean(axis=sagittal_coronal_axial),
                                        rescale)
        animated_gif.add(img_bkg_cur, label=str(idx_cur))

    fname_out = 'spinalcord_' if brain_spinalcord else 'brain_'
    if sagittal_coronal_axial == 1:
        fname_out += 'cor.mp4'
    elif sagittal_coronal_axial == 2:
        fname_out += 'ax.mp4'
    else:
        fname_out += 'sag.mp4'
    animated_gif.save(str(fname_out))

 

if __name__ == "__main__":
    img_path, brain_spinalcord, sagittal_coronal_axial = sys.argv[1:]
    main(img_path, int(brain_spinalcord), int(sagittal_coronal_axial))