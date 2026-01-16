import pandas as pd
import csv
from difflib import SequenceMatcher, unified_diff
import sys

class ElementDeltaFinder:
    """
    A comprehensive tool to find element-wise (character-level) differences 
    between two columns in CSV files.
    """
    
    def __init__(self, csv_file, column1, column2):
        """
        Initialize the delta finder
        
        Parameters:
        - csv_file: Path to CSV file
        - column1: Name of first column
        - column2: Name of second column
        """
        self.csv_file = csv_file
        self.column1 = column1
        self.column2 = column2
        self.df = None
        self.results = None
        self.load_data()
    
    def load_data(self):
        """Load and validate CSV file"""
        try:
            self.df = pd.read_csv(self.csv_file)
            print(f"✓ Loaded CSV: {self.csv_file}")
            print(f"  Rows: {len(self.df)}, Columns: {len(self.df.columns)}")
            
            if self.column1 not in self.df.columns or self.column2 not in self.df.columns:
                print(f"\n✗ Error: Columns not found!")
                print(f"  Looking for: '{self.column1}' and '{self.column2}'")
                print(f"  Available: {list(self.df.columns)}")
                sys.exit(1)
                
        except Exception as e:
            print(f"✗ Error loading CSV: {e}")
            sys.exit(1)
    
    @staticmethod
    def typecast_to_string(value):
        """Typecast value to string, handling None and empty values"""
        if pd.isna(value):
            return ""
        return str(value).strip()
    
    def get_diff_visualization(self, str1, str2, context_chars=20):
        """
        Create a visual representation of character differences
        """
        if str1 == str2:
            return "NO DIFFERENCE"
        
        # Character-by-character comparison
        diff_visual = []
        len1, len2 = len(str1), len(str2)
        max_len = max(len1, len2)
        
        changes = []
        for i, (c1, c2) in enumerate(zip(str1, str2)):
            if c1 != c2:
                changes.append(f"[Pos {i}: '{c1}' → '{c2}']")
        
        # Handle length differences
        if len1 != len2:
            if len1 > len2:
                changes.append(f"[Deletion at end: '{str1[len2:]}' removed]")
            else:
                changes.append(f"[Insertion at end: '{str2[len1:]}' added]")
        
        return " | ".join(changes) if changes else "IDENTICAL"
    
    def analyze(self):
        """Perform the delta analysis"""
        
        # Typecast both columns to strings
        self.df[self.column1] = self.df[self.column1].apply(self.typecast_to_string)
        self.df[self.column2] = self.df[self.column2].apply(self.typecast_to_string)
        
        results_list = []
        
        for idx, row in self.df.iterrows():
            val1 = row[self.column1]
            val2 = row[self.column2]
            
            # Record all rows (both matching and different)
            diff_visualization = self.get_diff_visualization(val1, val2)
            has_difference = val1 != val2
            
            results_list.append({
                'row_index': idx,
                f'{self.column1}': val1,
                f'{self.column2}': val2,
                'has_delta': 'YES' if has_difference else 'NO',
                'delta_length_diff': len(val1) - len(val2),
                'delta_visualization': diff_visualization,
                'value1_length': len(val1),
                'value2_length': len(val2)
            })
        
        self.results = pd.DataFrame(results_list)
        return self.results
    
    def get_summary(self):
        """Get statistical summary of deltas"""
        if self.results is None:
            return None
        
        total_rows = len(self.results)
        rows_with_delta = len(self.results[self.results['has_delta'] == 'YES'])
        rows_without_delta = total_rows - rows_with_delta
        
        summary = {
            'total_rows': total_rows,
            'rows_with_differences': rows_with_delta,
            'rows_without_differences': rows_without_delta,
            'difference_percentage': (rows_with_delta / total_rows * 100) if total_rows > 0 else 0,
            'avg_length_difference': self.results['delta_length_diff'].abs().mean(),
            'max_length_difference': self.results['delta_length_diff'].abs().max(),
            'min_length_difference': self.results['delta_length_diff'].abs().min()
        }
        
        return summary
    
    def print_summary(self):
        """Print formatted summary"""
        summary = self.get_summary()
        
        print(f"\n{'='*90}")
        print(f"DELTA ANALYSIS SUMMARY")
        print(f"{'='*90}")
        print(f"File: {self.csv_file}")
        print(f"Column 1: {self.column1}")
        print(f"Column 2: {self.column2}")
        print(f"{'-'*90}")
        print(f"Total Rows:                    {summary['total_rows']}")
        print(f"Rows with Differences (Delta): {summary['rows_with_differences']} ({summary['difference_percentage']:.1f}%)")
        print(f"Rows without Differences:      {summary['rows_without_differences']} ({100-summary['difference_percentage']:.1f}%)")
        print(f"{'-'*90}")
        print(f"Average Length Difference:     {summary['avg_length_difference']:.2f} characters")
        print(f"Max Length Difference:         {summary['max_length_difference']} characters")
        print(f"Min Length Difference:         {summary['min_length_difference']} characters")
        print(f"{'='*90}\n")
    
    def print_differences(self, limit=None):
        """Print detailed differences"""
        differences_only = self.results[self.results['has_delta'] == 'YES']
        
        if len(differences_only) == 0:
            print("\n✓ No differences found!\n")
            return
        
        print(f"\n{'='*90}")
        print(f"DETAILED DIFFERENCES (showing {min(limit or len(differences_only), len(differences_only))} of {len(differences_only)})")
        print(f"{'='*90}\n")
        
        for idx, row in differences_only.head(limit).iterrows():
            print(f"Row [{row['row_index']}]:")
            print(f"  {self.column1} ({row['value1_length']} chars): {row[self.column1]}")
            print(f"  {self.column2} ({row['value2_length']} chars): {row[self.column2]}")
            print(f"  Delta: {row['delta_visualization']}")
            print()
    
    def export_results(self, output_file):
        """Export results to CSV"""
        self.results.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
        print(f"✓ Results exported to: {output_file}")
    
    def get_differences_only(self):
        """Return only rows with differences"""
        return self.results[self.results['has_delta'] == 'YES']


# USAGE EXAMPLES
if __name__ == "__main__":
    
    # Example 1: Compare Claim ID vs ehr_source_identifier
    print("\n" + "█"*90)
    print("EXAMPLE 1: Comparing Claim ID vs ehr_source_identifier")
    print("█"*90)
    
    # Try to find the encounters file with Claim ID column
    import os
    csv_files = [
        '152888_93814841974029258281_encounters-results.csv',
        'encounters-results.csv',
        '152888_7359011417695536902_appointments-results.csv'
    ]
    
    found_file = None
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            found_file = csv_file
            break
    
    if found_file:
        finder1 = ElementDeltaFinder(
            found_file,
            'Claim ID',
            'ehr_source_identifier'
        )
        
        finder1.analyze()
        finder1.print_summary()
        finder1.print_differences(limit=15)
        finder1.export_results('claim_id_vs_ehr_source_identifier_deltas.csv')
    else:
        print("✗ Could not find encounters CSV file with 'Claim ID' column")
    
    
    # Example 2: Uncomment to compare other columns
    # print("\n" + "█"*90)
    # print("EXAMPLE 2: Comparing Appointment Status vs Billing Status")
    # print("█"*90)
    # 
    # finder2 = ElementDeltaFinder(
    #     'appointment_report_12_26_2025.csv',
    #     'Appointment Status',
    #     'Billing Status'
    # )
    # 
    # finder2.analyze()
    # finder2.print_summary()
    # finder2.print_differences(limit=10)
    # finder2.export_results('status_deltas.csv')
