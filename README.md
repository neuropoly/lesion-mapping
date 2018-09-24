# ms_brain_spine
Project about quantification of MS lesions in the brain + spinal cord

## Dependencies
- [Spinal Cord Toolbox (SCT)](https://github.com/neuropoly/spinalcordtoolbox)

SCT is used for all preprocessing steps, including spinal cord segmentation, registration of all images on the template space, lesion load quantification.

Version [v.3.2.4](https://github.com/neuropoly/spinalcordtoolbox/releases/v3.2.4) and above.

## Dataset structure
The dataset should be arranged in a structured fashion, as the following:
~~~
- subject_name/
	- brain/
		- flair/
			- flair.nii.gz
		- t1/
			- t1.nii.gz
	- spinalcord/
	    - contrast_ax/
			- contrast_ax.nii.gz # raw image
			- contrast_ax_seg_manual.nii.gz # spinal cord mask (binary)
			- contrast_ax_lesion_manual.nii.gz # lesion mask (binary)
			- labels_disc.nii.gz # disc label (2 labels, i.e. 2 voxels)
	    - contrast_sag/
			- contrast_sag.nii.gz # raw image
			- contrast_sag_seg_manual.nii.gz # spinal cord mask (binary)
			- contrast_sag_lesion_manual.nii.gz # lesion mask (binary)
			- labels_disc.nii.gz # disc label (2 labels, i.e. 2 voxels)
    - ...
~~~

## How to run

- Download (or `git clone`) this repository:
~~~
git clone https://github.com/neuropoly/ms_brain_spine
~~~

- Use SCT python
~~~
source sct_launcher
~~~

### Spinal cord processing

- Edit [config_file.py](spinalcord/config_file.py) according to your needs, then save the file.
	- `dct_center`: indicate for each center, the folder names of your axial image (see `contrast_ax` in the `Dataset structure` section) and your sagittal image (`contrast_sag`)
	- `path_data`: folder path where your data is stored (see also `Dataset structure` section)
	- `csv_clinicalInfo`: path towards the csv containing the clinical information of the dataset, with the following columns for each subject:
		- `center`: center of acquisition
		- `subject`: subject folder name
		- `age`: age of the subject (year)
		- `gender`: gender of the subject: either `F` for female or `M` for male
		- `disease_dur`: disease duration of the subject (year)
		- `edss`: EDSS score of the subject (float between 0 and 10)
		- `phenotype`: phenotype of the subject: `CIS`, `RR`, `SP` or `PP`
	- `path_results`: folder path where to save the results

- Check data availability and integrity:
~~~
python 0_check_data.py
~~~
This script will loop across the subjects listed in the csv file `csv_clinicalInfo` and check the availaibility and integrity of the files used for the processing. If some files are missing or incorrect, one or more of the following files will be output in the current directory (where `datetime` indicates the date and time of the end of the running of `0_check_data`):
		- `datetime_missing_subject.pkl`: if the folder of a subject listed in the csv file is not present in the dataset.
		- `datetime_missing_contrast.pkl`: if the contrast folder of a subject listed in the `dct_center` dictionary is not present in the dataset.
		- `datetime_missing_img.pkl`: if a raw image is missing in the dataset.
		- `datetime_missing_sc.pkl`: if a spinal cord segmentation is missing in the dataset.
		- `datetime_missing_lesion.pkl`: if a lesion segmentation is missing in the dataset.
		- `datetime_missing_incorrect_labels.pkl`: if a label file of the discs is missing or incorrect (i.e. more than two voxels labeled in the mask) in the dataset.
		- `datetime_incorrect_sc.pkl`: if a spinal cord segmentation is incorrect in the dataset (i.e. not binary and/or several connected objects).
		- `datetime_incorrect_lesion.pkl`: if a lesion segmentation is incorrect in the dataset (i.e. not binary).
To display the missing files or to correct / generate the missing or incorrect label files, please run:
~~~
python correct_generate_labelling.py datetime_*.pkl
~~~
for instance:
~~~
python correct_generate_labelling.py 201809201152_incorrect_sc.pkl
~~~


## Licence
This repository is under a MIT licence.

