#!/usr/bin/env python3

import os
import subprocess
import argparse
import sys

def run_command(cmd, error_message="Command execution failed"):
    """ Run a shell command and check if it was successful """
    print(f"Executing command: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {error_message}\n{result.stderr}")
        sys.exit(1)
    return result.stdout

def check_conda_env():
    """ Check if the correct conda environment is activated """
    result = subprocess.run("echo $CONDA_DEFAULT_ENV", shell=True, capture_output=True, text=True)
    current_env = result.stdout.strip()
    if current_env != "sword2":
        print(f"⚠️ Warning: The current conda environment is `{current_env}`. Please activate the `sword2` environment!")
        sys.exit(1)

def main(input_pdb, output_dir):
    """ Main function to run all steps """
    check_conda_env()
    
    os.makedirs(output_dir, exist_ok=True)

    # 2. Create SWORD2 folder
    sword_dir = f"{output_dir}/sword2"
    os.makedirs(sword_dir, exist_ok=True)

    # 3. Run SWORD2 domain segmentation
    print("🔹 Running SWORD2 domain segmentation...")
    run_command(f"./SWORD2/SWORD2.py -i {input_pdb} -o {sword_dir}", "SWORD2 failed to run, please check the path.")

    # 4. Perform SWORD mapping
    mapping_file = f"{sword_dir}/{os.path.basename(input_pdb).replace('.pdb', '_A')}/mapping_auth_resnums.txt"
    sword_txt = f"{sword_dir}/{os.path.basename(input_pdb).replace('.pdb', '_A')}/sword.txt"
    output_mapping = f"{sword_dir}/{os.path.basename(input_pdb).replace('.pdb', '_A')}/sword_mapping.txt"

    print("🔹 Performing SWORD mapping...")
    run_command(f"python script/step02_mapping.py {mapping_file} {sword_txt} {output_mapping}", "SWORD mapping failed.")

    # 5. Run DALI alignment
    dali_dir = f"{output_dir}/{os.path.basename(input_pdb).replace('.pdb', '')}"
    os.makedirs(dali_dir, exist_ok=True)
    
    print("🔹 Running DALI alignment...")
    run_command(f"bash script/step04_run_dali_and_organize.sh {input_pdb} {dali_dir}", "DALI run failed.")

    # 6. Perform DALI mapping
    print("🔹 Performing DALI mapping...")
    run_command(f"python script/step05_map_molA_domains.py {dali_dir} rcsb_cas12_domain.position.txt", "DALI mapping failed.")
    
    # 7. Run Foldseek alignment
    foldseek_output = f"{output_dir}/foldseek_res.m8"
    
    print("🔹 Running Foldseek alignment...")
    run_command(f"./foldseek/bin/foldseek easy-search {input_pdb} local_database/ {foldseek_output} tmp", "Foldseek run failed.")

    # 8. Foldseek mapping
    foldseek_mapped_output = f"{output_dir}/foldseek_mapped_output.csv"
    
    print("🔹 Performing Foldseek result mapping...")
    run_command(f"python script/step02_pdb_mapping_m8.py {input_pdb} {foldseek_output} {foldseek_mapped_output}", "Foldseek result mapping failed.")

    # 9. Generate domain matrix
    print("🔹 Generating domain matrix...")
    run_command(f"python script/step03_domain_matrix.py {dali_dir}/molA2_domain_mapping.txt {output_mapping} {foldseek_mapped_output} {dali_dir}", "Domain matrix generation failed.")

    # 10. Filter SWORD results
    sword_filtered_output = f"{output_dir}/{os.path.basename(input_pdb).replace('.pdb', '_cleaned_sword_result.txt')}"
    
    print("🔹 Filtering SWORD results...")
    run_command(f"python script/step07_filter_sword.py {output_dir}/{os.path.basename(input_pdb).replace('.pdb', '_annotated_sword_result.txt')} {sword_filtered_output}", "SWORD filtering failed.")

    # 11. Window annotation
    window_annotated_output = f"{output_dir}/{os.path.basename(input_pdb).replace('.pdb', '_window_annoted.txt')}"
    
    print("🔹 Performing window annotation...")
    run_command(f"python script/windows_annotion.py {sword_filtered_output} {output_dir}/{os.path.basename(input_pdb).replace('.pdb', '_domain_annotation_matrix.csv')} {window_annotated_output}", "Window annotation failed.")

    # 12. WED window annotation
    wed_window_annotated_output = f"{output_dir}/{os.path.basename(input_pdb).replace('.pdb', '_WED_window_annoted.txt')}"
    
    print("🔹 Performing WED window annotation...")
    run_command(f"python script/WED_windows_annotion.py {sword_filtered_output} {output_dir}/{os.path.basename(input_pdb).replace('.pdb', '_domain_annotation_matrix.csv')} {wed_window_annotated_output}", "WED window annotation failed.")

    print("✅ All tasks completed! Outputs are saved in:", output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CAS12FAM analysis tool")
    parser.add_argument("-i", "--input", required=True, help="Input PDB file")
    parser.add_argument("-o", "--output", required=True, help="Output directory")

    args = parser.parse_args()
    main(args.input, args.output)