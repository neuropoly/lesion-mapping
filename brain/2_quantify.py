#!/usr/bin/env python
#
# Goal: To quantify lesion characteristics.
#
# Steps:
#		1. Custom brain and brainstem atlases for the purpose of this study.
#
# XXX
#
# Created: 2018-10-18
# Modified: 2018-10-18
# Contributors: Charley Gros


import os
import numpy as np

from spinalcordtoolbox.image import Image, zeros_like

from config_file import config

BRAINSTEM_DCT = {'CST_R': 'CSTR_Atlas.nii.gz',
				'CST_L': 'CSTL_Atlas.nii.gz',
				'CST': ''}
BRAMSTEM_ZTOP = 51

BRAIN_DCT = {'M1_R': 'Right-M1-S-MATT.nii',
			'M1_L': 'Left-M1-S-MATT.nii',
			'PMd_R': 'Right-PMd-S-MATT.nii',
			'PMd_L': 'Left-PMd-S-MATT.nii',
			'PMv_R': 'Right-PMv-S-MATT.nii',
			'PMv_L': 'Left-PMv-S-MATT.nii',
			'preSMA_R': 'Right-preSMA-S-MATT.nii',
			'preSMA_L': 'Left-preSMA-S-MATT.nii',
			'S1_R': 'Right-S1-S-MATT.nii',
			'S1_L': 'Left-S1-S-MATT.nii',
			'SMA_R': 'Left-SMA-S-MATT.nii',
			'SMA_L': 'Right-SMA-S-MATT.nii'}


def custom_brainstem(ifolder, ofolder):
	cst_r_ifile = os.path.join(ifolder, BRAINSTEM_DCT['CST_R'])
	cst_l_ifile = os.path.join(ifolder, BRAINSTEM_DCT['CST_L'])

	cst_r_ofile = os.path.join(ofolder, 'brainstem_CST_R.nii.gz')
	cst_l_ofile = os.path.join(ofolder, 'brainstem_CST_L.nii.gz')
	cst_ofile = os.path.join(ofolder, 'brainstem_CST.nii.gz')

	cst_r_im, cst_l_im = Image(cst_r_ifile), Image(cst_l_ifile)
	cst_im = zeros_like(cst_r_im)

	cst_r_im.data[:, :, BRAMSTEM_ZTOP+1:] = 0.
	cst_l_im.data[:, :, BRAMSTEM_ZTOP+1:] = 0.

	cst_im.data = cst_r_im.data + cst_l_im.data
	cst_im.data[cst_im.data > 1.0] = 1.0
	
	cst_r_im.save(cst_r_ofile)
	cst_l_im.save(cst_l_ofile)
	cst_im.save(cst_ofile)
	del cst_r_im, cst_l_im, cst_im


def custom_brain(ifolder, ofolder):
	ifname_dct = {}
	for roi in BRAIN_DCT:
		ifname_dct[roi] = os.path.join(ifolder, BRAIN_DCT[roi])

	sum_roi_im = sum([Image(ifname_dct[roi]).data for roi in ifname_dct])

	for roi in ifname_dct:
		ofname = os.path.join(ofolder, 'brain_' + roi + '.nii.gz')

		i_im = Image(ifname_dct[roi])
		o_im = zeros_like(i_im)
		o_im.data = i_im.data
		del i_im

		o_im.data[:, :, :BRAMSTEM_ZTOP+1] = 0.
		o_im.data = np.divide(o_im.data * 1., sum_roi_im)

		o_im.save(ofname)
		del o_im


def main():
	ofolder = config["path_atlases"]
	if not os.path.isdir(ofolder):
		os.makedirs(ofolder)

	brainstem_atlas_ifolder = config["path_brainstem_folder"]
	brainstem_atlas_ofolder = os.path.join(ofolder, 'brainstem')
	if not os.path.isdir(brainstem_atlas_ofolder):
		os.makedirs(brainstem_atlas_ofolder)
		custom_brainstem(brainstem_atlas_ifolder, brainstem_atlas_ofolder)

	brain_atlas_ifolder = config["path_smatt_folder"]
	brain_atlas_ofolder = os.path.join(ofolder, 'brain')
	if not os.path.isdir(brain_atlas_ofolder):
		os.makedirs(brain_atlas_ofolder)
		custom_brain(brain_atlas_ifolder, brain_atlas_ofolder)



if __name__ == "__main__":
    main()