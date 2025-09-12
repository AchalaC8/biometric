import pandas as pd
import os

# Get a sorted list of CSV files to ensure chronological order
csv_files = sorted([f for f in os.listdir() if f.endswith('.csv')])

# Check if any CSV files were found
if not csv_files:
    print("No CSV files were found in the current directory.")
else:
    # Extract the month from the first filename to use in the output filename
    # Assumes filenames are in the format "DD-MMM-YYYY.csv"
    try:
        output_month = csv_files[0].split('-')[1]
        output_filename = f'attendance_summary_{output_month}.xlsx'
    except IndexError:
        output_month = "Data"
        output_filename = 'attendance_summary.xlsx'

    attendance_data = []

    # Loop through each CSV file to extract attendance data
    for file_name in csv_files:
        df = pd.read_csv(file_name)
        
        # Check if 'Status' column exists
        if 'Status' in df.columns:
            status_counts = df['Status'].value_counts().to_dict()
            date_label = file_name.replace('.csv', '')
            
            # Store the counts for each day
            attendance_data.append({
                'Day': date_label,
                'Present': status_counts.get('Present', 0),
                'Not Present': status_counts.get('Not Present', 0)
            })

    # Convert the list of dictionaries into a DataFrame
    attendance_df = pd.DataFrame(attendance_data)
    
    # Check if the DataFrame is empty before writing to Excel
    if not attendance_df.empty:
        # Write the DataFrame to an Excel file
        attendance_df.to_excel(output_filename, index=False)
        print(f"Attendance summary has been successfully exported to '{output_filename}'.")
    else:
        print("No attendance data found in the provided CSV files.")
