# ms_brain_spine
Project about quantification of MS lesions in the brain + spinal cord

## Dependencies
- [Spinal Cord Toolbox (SCT)](https://github.com/neuropoly/spinalcordtoolbox)

SCT is used for all preprocessing steps of the spinal cord data, including cord segmentation, registration into the template space, and lesion load quantification.

Version [v.3.2.4](https://github.com/neuropoly/spinalcordtoolbox/releases/v3.2.4) and above.

- [Anima-Public](https://github.com/Inria-Visages/Anima-Public)

Anima-Public is used for registrating brain data to the MNI space.

Version [v.3.1](https://github.com/Inria-Visages/Anima-Public/tree/v3.1) and above.

- [Anima-Scripts-Public](https://github.com/Inria-Visages/Anima-Scripts-Public)

Anima-Scripts-Public is used for extracting the brain.

Version [v.1.0](https://github.com/Inria-Visages/Anima-Scripts-Public/tree/v1.0) and above.


## Dataset structure
The dataset should be arranged in a structured fashion, as the following:
~~~
- subject_name/
	- brain/
		- anat/
			- anat.nii.gz # raw image
			- anat_lesion_manual.nii.gz # lesion mask (binary)
		- struct/
			- struct.nii.gz
	- spinalcord/
	    - image_ax/
			- image_ax.nii.gz # raw image
			- image_ax_seg_manual.nii.gz # spinal cord mask (binary)
			- image_ax_lesion_manual.nii.gz # lesion mask (binary)
			- labels_disc.nii.gz # disc label (2 labels, i.e. 2 voxels)
			- labels_vert.nii.gz # vertebral label (2 labels, i.e. voxels, mid body), non-compulsory
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

### Clinical and demographic information
Please save the clinical and demographic information of the dataset into a `csv` file, with the following columns for each subject:
- `center`: center of acquisition
- `subject`: subject folder name
- `age`: age of the subject (year)
- `gender`: gender of the subject: either `F` for female or `M` for male
- `disease_dur`: disease duration of the subject (year)
- `edss`: EDSS score of the subject (float between 0 and 10)
- `phenotype`: phenotype of the subject: `CIS`, `RR`, `SP` or `PP`

### Brain processing

- Go into brain scripts folder
~~~
cd brain
~~~

#### Set parameters
Edit [config_file.py](brain/config_file.py) according to your needs, then save the file.
- `dct_center`: indicate for each center, the folder names of your structural image (see `struct` in the `Dataset structure` section, e.g. `anat.nii.gz`) and your anatomical image (`anat`, e.g. `flair.nii.gz`)
- `path_data`: folder path where your data is stored (see also `Dataset structure` section)
- `csv_clinicalInfo`: path towards the csv containing the clinical information of the dataset
- `path_results`: folder path where to save the results

#### Check data
Check data availability and integrity:
~~~
python 0_check_data.py
~~~
This script will loop across the subjects listed in the csv file `csv_clinicalInfo` and check the availaibility and integrity of the files used for the processing. If some files are missing or incorrect, one or more of the following files will be output in the current directory (where `datetime` indicates the date and time of the end of the running of `0_check_data`):
- `datetime_missing_subject.pkl`: if the folder of a subject listed in the csv file is not present in the dataset.
- `datetime_missing_contrast.pkl`: if the image folder of a subject listed in the `dct_center` dictionary is not present in the dataset.
- `datetime_missing_img.pkl`: if a raw image is missing in the dataset.
- `datetime_missing_lesion.pkl`: if a lesion segmentation is missing in the dataset for a `anat` image.
- `datetime_incorrect_lesion.pkl`: if a lesion segmentation is incorrect in the dataset (i.e. not binary) for a `anat` image.
To display the missing files or to correct / generate the missing or incorrect label files, please run:
~~~
python missing_incorrect_files.py datetime_*.pkl
~~~
for instance:
~~~
python missing_incorrect_files.py 201809201152_incorrect_lesion.pkl
~~~

#### Register data to the MNI152_T1_1mm space
Register data by running:
~~~
python 1_register_data.py
~~~
This script XXX

### Spinal cord processing

- Go into spinal cord scripts folder
~~~
cd spinalcord
~~~

#### Set parameters
Edit [config_file.py](spinalcord/config_file.py) according to your needs, then save the file.
- `dct_center`: indicate for each center, the folder names of your axial image(s) (see `image_ax` in the `Dataset structure` section)
- `path_data`: folder path where your data is stored (see also `Dataset structure` section)
- `csv_clinicalInfo`: path towards the csv containing the clinical information of the dataset
- `path_results`: folder path where to save the results

#### Check data
Check data availability and integrity:
~~~
python 0_check_data.py
~~~
This script will loop across the subjects listed in the csv file `csv_clinicalInfo` and check the availaibility and integrity of the files used for the processing. If some files are missing or incorrect, one or more of the following files will be output in the current directory (where `datetime` indicates the date and time of the end of the running of `0_check_data`):
- `datetime_missing_subject.pkl`: if the folder of a subject listed in the csv file is not present in the dataset.
- `datetime_missing_contrast.pkl`: if the image folder of a subject listed in the `dct_center` dictionary is not present in the dataset.
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

#### Register data to the PAM50 template
Register data to the PAM50 template [REF] then warp the template and the white matter atlas [REF] back to the subject space:
~~~
python 1_register_data.py
~~~

#### Quantify lesion characteristics
Quantify lesion characteristics in the entire cord as well as in the corticospinal tracts:
~~~
python 2_quantify.py
~~~

Measures:
- csa [mm2]: mean cross-sectional area of the cord
- tlv [mm3]: total lesion volume in the entire cord
- count_*: number of lesions in the entire cord or in one of the region of interest listed below (e.g. count_VCST_R)
- nlv_*: TLV divided by a volume of interest (e.g. entire cord or one of the region of interest listed below)
- alv_* [mm3]: absolute lesion volume in one of the region of interest listed below (e.g. alv_VCST_R)
- extension_CST (%): volume of lesion in the corticospinal tracts divided by the total volume of lesion in the cord

Regions of interest:
- VCST_R, VCST_L: ventral corticospinal right and left tracts
- LCST_R, LCST_L : lateral corticospinal right and left tracts
- CST: corticospinal tracts

## Licence
This repository is under a MIT licence.

