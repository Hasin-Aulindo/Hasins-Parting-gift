import pandas as pd
import sys
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Read both CSV files
file1 = pd.read_csv('appointment_report_12_26_2025.csv')
file2 = pd.read_csv('152888_7359011417695536902_appointments-results.csv')

# Standardize the key columns for comparison
# File 1 uses: Patient, Doctor, Date of Service
# File 2 uses: Patient, Doctor, Date of Service (with different date format)

# Function to normalize doctor names
def normalize_doctor(name):
    # Remove title (Dr., Dr, etc.)
    name = re.sub(r'^dr\.?\s+', '', name, flags=re.IGNORECASE).strip()
    # Convert to uppercase for comparison
    return name.upper()

# Function to normalize patient names
def normalize_patient(name):
    return name.upper().strip()

# Standardize date format for file1
file1['Date of Service'] = pd.to_datetime(file1['Date of Service']).dt.date

# Standardize date format for file2
file2['Date of Service'] = pd.to_datetime(file2['Date of Service']).dt.date

# Normalize names in both files
file1['Doctor_normalized'] = file1['Doctor'].apply(normalize_doctor)
file1['Patient_normalized'] = file1['Patient'].apply(normalize_patient)

file2['Doctor_normalized'] = file2['Doctor'].apply(normalize_doctor)
file2['Patient_normalized'] = file2['Patient'].apply(normalize_patient)

# Create composite keys for matching
file1['key'] = file1['Patient_normalized'] + '|' + file1['Doctor_normalized'] + '|' + file1['Date of Service'].astype(str)
file2['key'] = file2['Patient_normalized'] + '|' + file2['Doctor_normalized'] + '|' + file2['Date of Service'].astype(str)

# Function to find best fuzzy match
def find_best_match(key, choices, cutoff=97):
    """Find best match using fuzzy matching with threshold"""
    matches = process.extractBests(key, choices, scorer=fuzz.token_set_ratio, score_cutoff=cutoff, limit=1)
    if matches:
        return matches[0][0], matches[0][1]  # Return matched key and score
    return None, 0

# Find rows in file1 but not in file2 (Deletions)
file2_keys_set = set(file2['key'])
unmatched_file1 = []

for idx, row in file1.iterrows():
    key1 = row['key']
    if key1 not in file2_keys_set:
        # Try fuzzy matching
        best_match, score = find_best_match(key1, list(file2_keys_set), cutoff=97)
        if best_match is None:
           
            unmatched_file1.append(idx)

deleted_rows = file1.iloc[unmatched_file1].copy()


file1_keys_set = set(file1['key'])
unmatched_file2 = []

for idx, row in file2.iterrows():
    key2 = row['key']
    if key2 not in file1_keys_set:
        
        best_match, score = find_best_match(key2, list(file1_keys_set), cutoff=97)
        if best_match is None:
            
            unmatched_file2.append(idx)

added_rows = file2.iloc[unmatched_file2].copy()


delta_report = []


for idx, row in deleted_rows.iterrows():
    delta_report.append({
        'Change Type': 'DELETED',
        'Patient': row['Patient'],
        'Doctor': row['Doctor'],
        'Date of Service': row['Date of Service'],
        'Appointment Status': row['Appointment Status'],
        'Details': f"Record removed from file 2"
    })

# Add added records
for idx, row in added_rows.iterrows():
    delta_report.append({
        'Change Type': 'ADDED',
        'Patient': row['Patient'],
        'Doctor': row['Doctor'],
        'Date of Service': row['Date of Service'],
        'Appointment Status': '',
        'Details': f"New record in file 2"
    })

# Create DataFrame from delta report
if delta_report:
    delta_df = pd.DataFrame(delta_report)
    
    # Save to CSV
    output_file = 'deltas.csv'
    delta_df.to_csv(output_file, index=False)
    
    print(f"Delta report generated: {output_file}")
    print(f"Total deltas found: {len(delta_df)}")
    print(f"  - Deleted: {len(deleted_rows)}")
    print(f"  - Added: {len(added_rows)}")
    print("\nDelta Summary:")
    print(delta_df.to_string())
else:
    print("No deltas found between the two files.")
