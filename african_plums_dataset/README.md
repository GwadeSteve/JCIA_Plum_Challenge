
# African Plums Dataset

## Overview

The African Plums Dataset is a comprehensive collection of 4,507 annotated images of African plums, collected from various fields in Cameroon. This dataset is tailored for training and evaluating AI models for fruit quality assessment and defect detection. The dataset is organized into six categories based on defect types, and each image is systematically labeled and stored according to its defect type. The dataset is ideal for researchers and developers focusing on agricultural AI applications, particularly in underrepresented regions and for specific crops like African plums.

## Dataset Structure

The dataset is structured as follows:

- **Base Directory**: `african_plums/`
  - Contains six subfolders, each corresponding to a specific defect type.
- **Subfolders**:
  - `bruised/`: Contains 319 images of bruised African plums.
  - `cracked/`: Contains 162 images of cracked African plums.
  - `rotten/`: Contains 720 images of rotten African plums.
  - `spotted/`: Contains 759 images of spotted African plums.
  - `unaffected/`: Contains 1,721 images of unaffected African plums (in good condition).
  - `unripe/`: Contains 826 images of unripe African plums.

### CSV File

The dataset also includes a CSV file (`plums_data.csv`) with three columns:

1. **Image ID**: The identifier for each image, formatted as `<Defect Type>_plum_<number>`. 
   - Example: `bruised_plum_1`, `cracked_plum_15`, etc.
2. **Label**: Indicates the label of the image, with possible values:
   - `defective`: For bruised, cracked, rotten, and spotted categories.
   - `unaffected`: For unaffected plums.
   - `unripe`: For unripe plums.
3. **Defect Type**: Specifies the defect category, corresponding to one of the six defect types:
   - `bruised`, `cracked`, `rotten`, `spotted`, `unaffected`, `unripe`

### Image Format

All images are in PNG format. Each image file name matches its corresponding entry in the CSV file, excluding the file extension.

## Usage

This dataset can be utilized for:

- Training object detection and image classification models for fruit quality assessment.
- Benchmarking AI models designed for agricultural applications.
- Developing automated systems for sorting and grading African plums based on visual characteristics.

### Sample Code

```python
import pandas as pd

# Load the dataset
csv_file = "plums_data.csv"
data = pd.read_csv(csv_file)

# Display the first few rows
print(data.head())
```

## Citation

To ensure proper credit and citation when using this dataset, please cite it as follows:

**Arnaud, [Arnaud Nguembang Fadja]. (2024). African Plums Dataset. Version 1.0. [Kaggle]. DOI: [DOI number].**

