import pandas as pd
import xlsxwriter
from datetime import datetime
import os

def main():
    """
    Reads attendance data from a single CSV file, performs a detailed analysis,
    and exports the results to a single Excel file with multiple sheets.
    """
    try:
        # Prompt the user for the file name
        file_name_input = input("Enter the file name (e.g., 01-Jun-2025): ")
        csv_file_path = f"{file_name_input}.csv"
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: The file '{csv_file_path}' was not found.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        return

    # --- Prepare DataFrames for Excel Sheets ---

    # 1. Overall Attendance Statistics and Daily Summary
    status_counts = df['Status'].value_counts()
    daily_summary_data = {
        'Metric': ['Total Students', 'Present', 'Absent'],
        'Count': [len(df), status_counts.get('Present', 0), status_counts.get('Not Present', 0)]
    }
    daily_summary_df = pd.DataFrame(daily_summary_data)

    # 2. Late Biometric Entry Analysis
    late_punch_time = datetime.strptime('20:45:00', '%H:%M:%S').time()
    late_punches_df = pd.DataFrame()
    if 'Last Punch' in df.columns and 'Status' in df.columns:
        present_students = df[df['Status'] == 'Present'].copy()
        
        # Convert 'Last Punch' to datetime.time objects for comparison
        present_students['Punch Time'] = pd.to_datetime(
            present_students['Last Punch'], 
            format='%H:%M:%S', 
            errors='coerce'
        ).dt.time
        
        # Filter for late punches
        late_punches_df = present_students[present_students['Punch Time'] > late_punch_time].copy()
        if not late_punches_df.empty:
            late_punches_df = late_punches_df[['Student Name', 'Room No.', 'Last Punch']]

    # 3. Not Present Students (Sorted by name)
    absent_students_df = pd.DataFrame()
    if 'Status' in df.columns:
        absent_students_df = df[df['Status'] == 'Not Present'].copy()
        if not absent_students_df.empty:
            absent_students_df = absent_students_df[['Student Name', 'Room No.']]
            absent_students_df.sort_values(by='Student Name', inplace=True)

    # 4. Present Students per Room (Sorted and with names)
    present_per_room_df = pd.DataFrame()
    if 'Status' in df.columns and 'Block' in df.columns and 'Floor' in df.columns and 'Room No.' in df.columns:
        # Group by room and count the number of present students and get their names
        present_per_room_df = df[df['Status'] == 'Present'].groupby(
            ['Block', 'Floor', 'Room No.']
        ).agg(
            Present_Count=('Status', 'size'),
            Present_Names=('Student Name', lambda x: ', '.join(sorted(x)))
        ).reset_index()
        
        # Create a custom sort order for floors
        floor_order = ['FirstFloor', 'SecondFloor', 'ThirdFloor', 'FourthFloor', 'FifthFloor', 'SixthFloor', 'SeventhFloor', 'EighthFloor']
        present_per_room_df['Floor'] = pd.Categorical(present_per_room_df['Floor'], categories=floor_order, ordered=True)
        
        # Sort the DataFrame
        present_per_room_df.sort_values(by=['Block', 'Floor', 'Room No.'], inplace=True)
        
    # 5. Absent Students per Room (Sorted and with names)
    absent_per_room_df = pd.DataFrame()
    if 'Status' in df.columns and 'Block' in df.columns and 'Floor' in df.columns and 'Room No.' in df.columns:
        # Group by room and count the number of absent students and get their names
        absent_per_room_df = df[df['Status'] == 'Not Present'].groupby(
            ['Block', 'Floor', 'Room No.']
        ).agg(
            Absent_Count=('Status', 'size'),
            Absent_Names=('Student Name', lambda x: ', '.join(sorted(x)))
        ).reset_index()
        
        # Apply the same custom sort order for floors
        floor_order = ['FirstFloor', 'SecondFloor', 'ThirdFloor', 'FourthFloor', 'FifthFloor', 'SixthFloor', 'SeventhFloor', 'EighthFloor']
        absent_per_room_df['Floor'] = pd.Categorical(absent_per_room_df['Floor'], categories=floor_order, ordered=True)
        
        # Sort the DataFrame
        absent_per_room_df.sort_values(by=['Block', 'Floor', 'Room No.'], inplace=True)

    # --- Write to Excel File ---
    output_filename = f"{file_name_input}_analysis.xlsx"
    try:
        with pd.ExcelWriter(output_filename, engine='xlsxwriter') as writer:
            daily_summary_df.to_excel(writer, sheet_name='Daily Summary', index=False)
            absent_students_df.to_excel(writer, sheet_name='Students to Notify', index=False)
            late_punches_df.to_excel(writer, sheet_name='Late Biometric Punches', index=False)
            present_per_room_df.to_excel(writer, sheet_name='Present Students per Room', index=False)
            absent_per_room_df.to_excel(writer, sheet_name='Absent Students per Room', index=False)
        
        print(f"Attendance analysis has been successfully exported to '{output_filename}'.")
        print("The file contains the following sheets: 'Daily Summary', 'Students to Notify', 'Late Biometric Punches', 'Present Students per Room', and 'Absent Students per Room'.")
    except ImportError:
        print("\nAn error occurred: The 'xlsxwriter' library is not installed.")
        print("To fix this, please install it by running the following command in your terminal:")
        print("pip install xlsxwriter")
    except Exception as e:
        print(f"\nAn unexpected error occurred while writing to the Excel file: {e}")

if __name__ == "__main__":
    main()
