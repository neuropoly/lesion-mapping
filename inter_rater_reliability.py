#!/usr/bin/env python
#
# These functions were used to evaluate the inter-rater reliability of the lesion segmentation in the study:
# Eden et al., "Spatial distribution of multiple sclerosis lesions in the cervical spinal cord", manuscript under revision (submitted to Brain, 2018).
#

import numpy as np
from scipy import ndimage
import spinalcordtoolbox.image as msct_image

def compute_lesion_wise_metrics(mask_rater, mask_consensus, threshold_overlap=0.5):
    '''
    This function compute the lesion-wise sensitivity and precision
    between the mask of a rater and the consensus reading mask.

    Input:
        - mask_rater [numpy.array]: manual segmentation mask of one rater
        - mask_rater [numpy.array]: consensus reading mask obtained considering all raters' masks
        - threshold_overlap [float]: value between 0. and 1.
            A candidate lesion was considered as correctly detected (i.e. true positive)
            when the rater segmentation connected-voxels overlapped with more than
            [threshold_overlap] of the consensus reading segmentation voxels, otherwise
            it was considered as incorrectly detected (i.e. false positive). If a lesion 
            of the consensus reading had an insufficient overlap (<[threshold_overlap])
            with the rater segmentation voxels, then we defined it as not-detected
            (i.e. false negative).

    Output:
        - sensitivity [float]: value between 0. and 1., defined as the ratio of true positive lesions
            by the sum of true positive and false negative lesions.
        - precision [float]: value between 0. and 1., defined as the ratio of true positive lesions
            by the sum of true and false positive lesions.
    '''
    # label each individual lesion of both input masks
    labels, nb_les = {}, {}
    labels['rater'], nb_les['rater'] = ndimage.label(mask_rater)
    labels['consensus'], nb_les['consensus'] = ndimage.label(mask_consensus)
    
    # create a matrix (1xnb_les['rater']), filled with ones
    found_rater = np.ones(nb_les['rater'], np.int16)

    # initialize the number of true positive, false positive, and false negative
    tp, fp, fn = 0, 0, 0

    # loop across the lesions of the consensus mask
    for i in range(1, nb_les['consensus'] + 1):
        # measure the voxel size of the current lesion
        lesion_size = np.sum(mask_consensus[labels['consensus'] == i])

        # extract the labels of the rater lesions
        # which overlap with the current lesion from the consensus mask
        rater_lesions_list = np.unique(labels['rater'][labels['consensus'] == i])

        # measure the voxel size of the overlap between the rater segmentation
        # and the current lesion from the consensus mask
        nb_overlap = mask_rater[labels['consensus'] == i].sum()

        if nb_overlap >= threshold_overlap * lesion_size:  # if the overlap is sufficient
            tp += 1
            for rater_lesion in rater_lesions_list:
                if rater_lesion != 0:
                    found_rater[rater_lesion - 1] = 0  # this rater lesion is not a false positive
        else:  # if the overlap is unsufficient
            fn += 1

    for i in range(1, nb_les['rater'] + 1):
        if found_rater[i - 1] == 1:  # if this rater lesion did not overlap with the consensus mask
            fp += 1

    sensitivity, precision = None, None
    if tp + fn != 0:
        sensitivity = tp * 1. / (tp + fn)
    if tp + fp != 0:
        precision = tp * 1. / (tp + fp)

    return sensitivity, precision


def compute_dice_coefficient(mask_rater, mask_consensus):
    '''
    This function compute the Dice coefficient
    between the mask of a rater and the consensus reading mask.

    Input:
        - mask_rater [numpy.array]: manual segmentation mask of one rater
        - mask_rater [numpy.array]: consensus reading mask obtained considering all raters' masks

    Output:
        - dice [float]: value between 0. and 1., defined as in "Measures of the Amount of Ecologic
        Association Between Species", Lee R. Dice (1945).
    '''
    mask_rater = mask_rater.astype(np.bool)
    mask_consensus = mask_consensus.astype(np.bool)

    intersection = np.count_nonzero(mask_rater & mask_consensus)

    size_i1 = np.count_nonzero(mask_rater)
    size_i2 = np.count_nonzero(mask_consensus)

    try:
        dice = 2. * intersection / float(size_i1 + size_i2)
    except ZeroDivisionError:
        dice = None

    return dice


def generate_consensus_reading(fname_raterMasks_lst, threshold=0.5, fname_out='./consensus_reading.nii.gz'):
    '''
    This function generate a consensus reading mask from several segmentation mask of the same raw image.
    In the generated mask, 1 indicates that this voxel is part of the consensus reading, 0 otherwise.

    Input:
        - fname_raterMasks_lst [list]: list of nifti binary mask filenames.
            Note that they are suspected to all have the same size,
            since they are all the mask of the same raw image.
        - threshold [float]: value between 0. and 1.
            A voxel is labelled 1 in the output consensus mask
            if [threshold] of the raters segmented this voxel as lesion.
        - fname_out [string]: filename of the consensus reading mask generated.
    '''
    # compute the number of agreement needed to consider a voxel as part of the consensus reading mask
    threshold_n = int(threshold * len(fname_raterMasks_lst))
                
    # Sum all the rater segmentations
    data_sum = np.sum(np.asarray([msct_image.Image(fname_raterMask).data for fname_raterMask in fname_raterMasks_lst]), axis=0)
                
    # Threshold the resulting array according to the threshold
    data_thresh = np.zeros(data_sum.shape)
    data_thresh[np.where(data_sum >= threshold_n)] = 1

    # Save the resulting array as Image in the related ofolder
    im_consensus = msct_image.zeros_like(msct_image.Image(fname_raterMasks_lst[0]), dtype=np.uint8)
    im_consensus.data = data_thresh
    im_consensus.save(fname_out)