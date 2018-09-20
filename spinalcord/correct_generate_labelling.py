#!/usr/bin/env python
#
# This script helps at the generation or correction of groundtruths.
#
# Charley Gros 2018-09-18
# Modified: 2018-09-18

import os
import sys
import pickle
import sct_utils as sct

def _generate_disc_labels(lst):
	'''Generate intervertebral disc labels.'''
	stg = '\n\nMissing or Incorrect files: ' + str(len(lst)) + '\n'
	msg = 'Click to put 2 labels at the posterior edge of the intervertebral discs (e.g. label 3 corresponds to disc C2-C3).'
	msg += ' Choose your 2 label values as far away as possible on the image.'
	for l in lst:
		print os.path.dirname(l) + '\n'
		fname_img = os.path.dirname(l) + '/' + l.split('/')[-2] + '.nii.gz'
		sct.run(['sct_label_utils', '-i', fname_img, '-create-viewer', '3,4,5,6', '-msg', msg, '-o', l])


def _visualize_incorrect_segmentation(lst):
	'''Open incorrect segmentations with FSLeyes.'''
	stg = '\n\nIncorrect files: ' + str(len(lst)) + '\n\n'
	stg += 'Please correct the segmentations and save them as *_seg_manual.nii.gz and *_lesion_manual.nii.gz for the spinal cord and lesion segmentation, respectively.'
	stg += '\n'
	print stg
	for l in lst:
		print os.path.dirname(l) + '\n'
		fname_img = os.path.dirname(l) + '/' + l.split('/')[-2] + '.nii.gz'
		os.system(' '.join(['fsleyes', fname_img, l, '-cm Red']))


def _display_missing_files(dct):
	'''Print the missing files in the terminal.'''
	stg = '\n\nMissing files: ' + str(len(dct[dct.keys()[0]])) + '\n\n' + '\n'.join(dct[dct.keys()[0]])
	print stg


def run_main(fname_pickle):
	dct = pickle.load(open(fname_pickle,"rb"))

	if dct.keys()[0] == 'missing_incorrect_labels':
		_generate_disc_labels(dct[dct.keys()[0]])
	elif dct.keys()[0] in ['incorrect_lesion', 'incorrect_sc']:
		_visualize_incorrect_segmentation(dct[dct.keys()[0]])
	else:
		_display_missing_files(dct)


if __name__ == '__main__':
	path_pickle = sys.argv[1]
	run_main(path_pickle)
