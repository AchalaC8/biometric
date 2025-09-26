import pandas as pd
import xlsxwriter
from datetime import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import io

# --- Constants for Configuration ---
LATE_PUNCH_TIME_STR = '20:45:00'
FLOOR_ORDER = [
    'FirstFloor', 'SecondFloor', 'ThirdFloor', 'FourthFloor',
    'FifthFloor', 'SixthFloor', 'SeventhFloor', 'EighthFloor'
]

def analyze_attendance(df: pd.DataFrame) -> dict:
    """
    Performs a detailed analysis of the attendance DataFrame.

    Args:
        df: A pandas DataFrame containing the attendance data.

    Returns:
        A dictionary where keys are sheet names and values are the
        corresponding DataFrames to be exported.
    """
    # Validate required columns for analysis
    required_cols = {'Status', 'Student Name', 'Room No.'}
    if not required_cols.issubset(df.columns):
        st.error(f"Error: The following required columns are missing for detailed analysis: {', '.join(required_cols - set(df.columns))}")
        return {}

    # Initialize a dictionary to hold all output DataFrames
    output_dfs = {}

    # --- 1. Overall Attendance Statistics and Daily Summary ---
    status_counts = df['Status'].value_counts()
    daily_summary_data = {
        'Metric': ['Total Students', 'Present', 'Absent'],
        'Count': [len(df), status_counts.get('Present', 0), status_counts.get('Not Present', 0)]
    }
    output_dfs['Daily Summary'] = pd.DataFrame(daily_summary_data)

    # --- 2. Late Biometric Entry Analysis ---
    late_punch_time = datetime.strptime(LATE_PUNCH_TIME_STR, '%H:%M:%S').time()
    if 'Last Punch' in df.columns:
        present_students = df[df['Status'] == 'Present'].copy()
        
        # Convert 'Last Punch' to datetime.time objects for comparison
        present_students['Punch Time'] = pd.to_datetime(
            present_students['Last Punch'],
            format='%H:%M:%S',
            errors='coerce'
        ).dt.time
        
        # Filter for late punches and select relevant columns
        late_punches_df = present_students[present_students['Punch Time'] > late_punch_time].copy()
        output_dfs['Late Biometric Punches'] = late_punches_df[['Student Name', 'Room No.', 'Last Punch']]
    else:
        st.warning("Warning: 'Last Punch' column not found. Skipping late punch analysis.")
        output_dfs['Late Biometric Punches'] = pd.DataFrame(columns=['Student Name', 'Room No.', 'Last Punch'])

    # --- 3. Not Present Students (Sorted by name) ---
    absent_students_df = df[df['Status'] == 'Not Present'].copy()
    output_dfs['Students to Notify'] = absent_students_df[['Student Name', 'Room No.']].sort_values(by='Student Name')

    # Check for Block, Floor, and Room No. columns for per-room analysis
    if {'Block', 'Floor', 'Room No.'}.issubset(df.columns):
        
        def sort_by_room_details(data_df):
            """Helper function to sort by Block, Floor, and Room No."""
            if not data_df.empty:
                # Apply the custom sort order for floors
                data_df['Floor'] = pd.Categorical(data_df['Floor'], categories=FLOOR_ORDER, ordered=True)
                data_df.sort_values(by=['Block', 'Floor', 'Room No.'], inplace=True)
            return data_df

        # --- 4. Present Students per Room (Sorted and with names) ---
        present_per_room_df = df[df['Status'] == 'Present'].groupby(
            ['Block', 'Floor', 'Room No.']
        ).agg(
            Present_Count=('Status', 'size'),
            Present_Names=('Student Name', lambda x: ', '.join(sorted(x)))
        ).reset_index()
        output_dfs['Present Students per Room'] = sort_by_room_details(present_per_room_df)

        # --- 5. Absent Students per Room (Sorted and with names) ---
        absent_per_room_df = df[df['Status'] == 'Not Present'].groupby(
            ['Block', 'Floor', 'Room No.']
        ).agg(
            Absent_Count=('Status', 'size'),
            Absent_Names=('Student Name', lambda x: ', '.join(sorted(x)))
        ).reset_index()
        output_dfs['Absent Students per Room'] = sort_by_room_details(absent_per_room_df)
    else:
        st.warning("Warning: 'Block', 'Floor', or 'Room No.' columns not found. Skipping per-room analysis.")

    return output_dfs

def generate_excel_file(output_dfs: dict) -> io.BytesIO:
    """
    Exports all analysis DataFrames to a single Excel file in-memory.

    Args:
        output_dfs: A dictionary of DataFrames to export.

    Returns:
        A BytesIO object containing the Excel file.
    """
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for sheet_name, df in output_dfs.items():
                if not df.empty:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    df_empty = pd.DataFrame([['No data to display.']], columns=['Info'])
                    df_empty.to_excel(writer, sheet_name=sheet_name, index=False)
        output.seek(0)
        return output
    except ImportError:
        st.error("Error: The 'xlsxwriter' library is not installed. Please install it with 'pip install xlsxwriter'.")
        return None

def create_monthly_graph(csv_files: list):
    """
    Analyzes multiple CSV files to create a monthly attendance graph.
    
    Args:
        csv_files: A list of CSV file names.
    """
    try:
        attendance_data = []

        for file_name in csv_files:
            df = pd.read_csv(file_name)
            if 'Status' in df.columns:
                status_counts = df['Status'].value_counts().to_dict()
                date_label = file_name.replace('.csv', '')
                attendance_data.append({
                    'Day': date_label,
                    'Present': status_counts.get('Present', 0),
                    'Not Present': status_counts.get('Not Present', 0)
                })

        attendance_df = pd.DataFrame(attendance_data)
        if not attendance_df.empty:
            month = csv_files[0].split('-')[1] if csv_files else 'Data'
            fig, ax = plt.subplots(figsize=(12, 7))
            bar_width = 0.35
            x = np.arange(len(attendance_df['Day']))
            ax.bar(x - bar_width/2, attendance_df['Present'], bar_width, label='Present', color='green')
            ax.bar(x + bar_width/2, attendance_df['Not Present'], bar_width, label='Not Present', color='red')
            ax.set_xlabel('Day', fontsize=12)
            ax.set_ylabel('Number of Students', fontsize=12)
            ax.set_title(f'Present vs Not Present Students for {month}', fontsize=14)
            ax.set_xticks(x)
            ax.set_xticklabels(attendance_df['Day'], rotation=45, ha='right')
            ax.legend()
            plt.tight_layout()
            return fig
        else:
            st.info("No attendance data found to create a monthly graph.")
            return None
    except (ImportError, ModuleNotFoundError):
        st.error("Error: The 'matplotlib' or 'numpy' library is not installed. Please install them with 'pip install matplotlib numpy'.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while creating the graph: {e}")
        return None

def app():
    """
    Main Streamlit application logic.
    """
    st.title("Attendance Analysis Dashboard")
    st.write("This app provides a detailed analysis of daily attendance data and generates a monthly summary graph.")

    # Part 1: Single-day analysis and Excel export
    st.header("Daily Attendance Report")
    file_name_input = st.text_input("Enter the file name (e.g., 01-Jun-2025):", value="01-Jun-2025")
    
    if st.button("Generate Report"):
        if not file_name_input:
            st.warning("Please enter a file name.")
        else:
            csv_file_path = f"{file_name_input}.csv"
            if not os.path.exists(csv_file_path):
                st.error(f"Error: The file '{csv_file_path}' was not found.")
            else:
                try:
                    df = pd.read_csv(csv_file_path)
                    analysis_results = analyze_attendance(df)
                    if analysis_results:
                        excel_file = generate_excel_file(analysis_results)
                        if excel_file:
                            st.success(f"Analysis for '{file_name_input}.csv' is complete.")
                            st.download_button(
                                label="Download Excel Report",
                                data=excel_file,
                                file_name=f"{file_name_input}_analysis.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                            # Display dataframes in the app
                            for sheet_name, df_result in analysis_results.items():
                                st.subheader(f"{sheet_name}")
                                st.dataframe(df_result)
                except Exception as e:
                    st.error(f"An unexpected error occurred during single-day analysis: {e}")

    # Part 2: Monthly graph generation
    st.header("Monthly Attendance Summary")
    csv_files = sorted([f for f in os.listdir() if f.endswith('.csv')])
    
    if csv_files:
        st.info(f"Found {len(csv_files)} CSV files. Generating a monthly graph...")
        fig = create_monthly_graph(csv_files)
        if fig:
            st.pyplot(fig)
    else:
        st.info("No CSV files found in the current directory to generate a monthly graph.")

if __name__ == "__main__":
    app()
