import pandas as pd
import csv
from difflib import SequenceMatcher

def typecast_to_string(value):
    """
    Typecast any value to string
    """
    return str(value) if value is not None else ""

def find_character_differences(str1, str2):
    """
    Find character-level differences between two strings
    Returns a list of differences with positions
    """
    differences = []
    matcher = SequenceMatcher(None, str1, str2)
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            differences.append({
                'type': tag,  # 'replace', 'insert', 'delete'
                'position_str1': f"{i1}-{i2}",
                'position_str2': f"{j1}-{j2}",
                'from_str1': str1[i1:i2],
                'to_str2': str2[j1:j2]
            })
    
    return differences

def compare_columns(csv_file, column1, column2, output_file=None):
    """
    Compare two columns in a CSV file as strings and report differences
    
    Parameters:
    - csv_file: Path to CSV file
    - column1: Name of first column to compare
    - column2: Name of second column to compare
    - output_file: Optional path to save results as CSV
    
    Returns:
    - DataFrame with differences
    """
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Check if columns exist
    if column1 not in df.columns or column2 not in df.columns:
        print(f"Error: Column '{column1}' or '{column2}' not found in CSV")
        print(f"Available columns: {list(df.columns)}")
        return None
    
    # Typecast both columns to strings
    df[column1] = df[column1].apply(typecast_to_string)
    df[column2] = df[column2].apply(typecast_to_string)
    
    # Find differences
    differences_list = []
    
    for idx, row in df.iterrows():
        val1 = row[column1]
        val2 = row[column2]
        
        # Skip if both are empty
        if val1.strip() == "" and val2.strip() == "":
            continue
        
        # If values are different, record the difference
        if val1 != val2:
            char_diffs = find_character_differences(val1, val2)
            
            differences_list.append({
                'row_index': idx,
                'column1_name': column1,
                'column1_value': val1,
                'column2_name': column2,
                'column2_value': val2,
                'are_different': 'YES',
                'difference_count': len(char_diffs),
                'difference_details': str(char_diffs) if char_diffs else "Complete replacement"
            })
        else:
            differences_list.append({
                'row_index': idx,
                'column1_name': column1,
                'column1_value': val1,
                'column2_name': column2,
                'column2_value': val2,
                'are_different': 'NO',
                'difference_count': 0,
                'difference_details': "No differences"
            })
    
    # Create results DataFrame
    results_df = pd.DataFrame(differences_list)
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"DELTA ANALYSIS: {column1} vs {column2}")
    print(f"{'='*80}")
    print(f"Total rows analyzed: {len(df)}")
    print(f"Rows with differences: {len(results_df[results_df['are_different'] == 'YES'])}")
    print(f"Rows without differences: {len(results_df[results_df['are_different'] == 'NO'])}")
    print(f"\n{'='*80}\n")
    
    # Save to output file if specified
    if output_file:
        results_df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
        print(f"Results saved to: {output_file}\n")
    
    return results_df

def print_differences_summary(results_df, show_all=False):
    """
    Print a summary of differences
    """
    print("\nDIFFERENCES SUMMARY:")
    print("="*80)
    
    differences_only = results_df[results_df['are_different'] == 'YES']
    
    if len(differences_only) == 0:
        print("✓ No differences found between columns!")
        return
    
    if show_all or len(differences_only) <= 10:
        for idx, row in differences_only.iterrows():
            print(f"\nRow {row['row_index']}:")
            print(f"  Column: {row['column1_name']}")
            print(f"    Value 1: {row['column1_value']}")
            print(f"  Column: {row['column2_name']}")
            print(f"    Value 2: {row['column2_value']}")
            print(f"  Differences: {row['difference_details']}")
            print(f"  {'─'*76}")
    else:
        print(f"Showing first 10 of {len(differences_only)} differences:\n")
        for idx, row in differences_only.head(10).iterrows():
            print(f"Row {row['row_index']}: '{row['column1_value']}' → '{row['column2_value']}'")


# USAGE EXAMPLE
if __name__ == "__main__":
    # Example 1: Compare Claim ID and ehr_source_identifier from appointments CSV
    print("EXAMPLE 1: Comparing appointments data")
    results1 = compare_columns(
        'appointment_report_12_26_2025.csv',
        'Patient',
        'Doctor',
        'appointment_deltas.csv'
    )
    
    if results1 is not None:
        print_differences_summary(results1)
    
    # Example 2: You can uncomment and modify for other files
    # results2 = compare_columns(
    #     '152888_7359011417695536902_appointments-results.csv',
    #     'column_name_1',
    #     'column_name_2',
    #     'output_deltas.csv'
    # )
