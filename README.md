# **Cas12fam: Cas12 Family Annotation Method**
Cas12fam (**Cas12 Family Annotation Method**) is a **protein domain annotation tool** specifically designed for **Cas12 protein families**.  
It integrates **structure prediction and alignment techniques** to generate accurate domain annotations, leveraging tools such as **SWORD2, DALI, and Foldseek**.

## **Features**
- 🧬 **Cas12-specific domain annotation**: Tailored for Cas12 family proteins.
- 🔬 **Structure-based analysis**: Uses **DALI, and Foldseek** to identify domains.
- 🚀 **High-speed & accuracy**: Efficiently processes **PDB structures** to generate **domain annotations**.

## **Installation**

To run Cas12fam, you need to install several dependencies:

1. **Sword2**: SWORD2 is a powerful partitioning algorithm designed to provide multiple domain assignments for a given protein structure. You can obtain this tool from the [Sword2 GitHub repository](https://github.com/DSIMB/SWORD2).
2. **DALI**: DALI is a protein structure alignment tool that compares 3D structures of proteins.  You can access and install this tool from the [DALI server website](http://ekhidna2.biocenter.helsinki.fi/dali/).
3. **Foldseek**: A fast and sensitive protein structure alignment tool that supports large-scale protein structure set comparisons, monomer and multimer searches, as well as clustering. Foldseek can be installed from the [Foldseek GitHub repository](https://github.com/steineggerlab/foldseek).

## Usage
### 1. Activate Sword2 Environment

First, you need to activate the `Sword2` environment. Assuming you have installed [Sword2](https://github.com/DSIMB/SWORD2) following the instructions, activate it using:
```
conda activate sword2
```
### 2.  Run Cas12fam

To run the Cas12fam tool, provide the input PDB file and specify the output directory. For example:
```
python cas12fam.py -i input.pdb -o outputdir
```
### **Arguments**
* `-i input.pdb`:  **Input file**. Provide the path to a PDB file (Protein Data Bank format) that contains the molecular structure to be processed. The PDB file must be **a single-chain cas12 protein structure**. Ensure that the file exists, is accessible, and is properly formatted.
* `-o outputdir`, outputdir: Output directory. Specify the directory where the processed results should be saved. If the directory doesn't exist, it will be created.
### **Example**
```
python cas12fam.py -i example/5u34_A.pdb -o 5u34
```
## Output

- `{output_dir}/sword2/{input_pdb}_A/`  
  **SWORD2 segmented domains**, including:
  - `{input_pdb}_A.pdb` → The segmented domains in **PDB format**.
  - `sword_mapping.txt` → **Mapping between original PDB and SWORD2 segments**.

### **2. DALI Structural Alignment**
- `{output_dir}/{input_pdb}/`  
  - **DALI compares the input PDB structure against a global Cas12 database**.
  - `molA2_domain_mapping.txt`: **DALI Mapping**. This file contains the domain mapping results from DALI.
  
### **3. Foldseek Structural Comparison**
- `{output_dir}/foldseek_res.m8` → **Foldseek alignment results** (comparison with individual domains from a local database).
- `{output_dir}/foldseek_mapped_output.csv` → **Mapped Foldseek results**.
  
### **4. Domain Matrix**
- `{dali_dir}/domain_matrix.csv`  
  This file contains a matrix representation of the **domain annotation results**, generated using **DALI** and **Foldseek**.  
  - **Columns (X-axis):** Represent the amino acids in the input PDB file. The first column corresponds to the first amino acid, the second column to the second amino acid, and so on.  
  - **Rows (Y-axis):** Represent **18 domains**, which correspond to structural classifications identified through DALI and Foldseek.  
  - Each cell in the matrix indicates whether a specific amino acid in the input structure belongs to a particular domain.

* `{output_dir}/{input_pdb}_cleaned_sword_result.txt`: **Filtered SWORD2 Results**. This file contains the SWORD2 results after filtering, which include domain annotations, improved sequence-structure mappings, and cleaned results for further analysis.

* `{output_dir}/{input_pdb}_window_annoted.txt`: **Window Annotation**. This file contains window-based annotations of the RuvC domains in the PDB file. It provides detailed annotations based on the windowing method for the domains.

* `{output_dir}/{input_pdb}_WED_window_annoted.txt`: **WED Window Annotation**. Similar to the window annotation, this file contains the **WED window annotation** based on a different algorithm. It provides additional insights into the domain's structure and its biological function.

### **5. Final Domain Annotation**
- `{output_dir}/{input_pdb}_cleaned_sword_result.txt`:  
  - **Filtered SWORD2 results**, containing **domain segmentation and annotation** after refinement.  
  - This file provides a **cleaned version** of SWORD2's domain mapping, improving accuracy by removing potential errors and inconsistencies.  

- `{output_dir}/{input_pdb}_window_annoted.txt`:  
  - **Window-based domain annotation** using a specific annotation method.  
  - This file contains window-based annotations of the RuvC domains in the PDB file. It provides detailed annotations based on the windowing method for the domains.

- `{output_dir}/{input_pdb}_WED_window_annoted.txt`:  
  - **WED-based domain annotation**, providing an alternative annotation strategy.  
  - Similar to the window annotation, this file contains the **WED window annotation** based on a different algorithm. 

This integration provides a comprehensive view of the protein's domain structure, enhancing confidence in functional predictions.
