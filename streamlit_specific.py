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

# --- Helper Function for Sorting ---
def sort_by_room_details(data_df: pd.DataFrame, floor_order: list) -> pd.DataFrame:
    """
    Helper function to sort DataFrame by Block, Floor (custom order), and Room No.
    """
    if not data_df.empty and all(col in data_df.columns for col in ['Block', 'Floor', 'Room No.']):
        # Apply the custom sort order for floors
        data_df['Floor'] = pd.Categorical(data_df['Floor'], categories=floor_order, ordered=True)
        data_df.sort_values(by=['Block', 'Floor', 'Room No.'], inplace=True)
    return data_df

def analyze_attendance(df: pd.DataFrame) -> dict:
    """
    Performs a detailed analysis of the attendance DataFrame for a single day.
    """
    # Validate required columns for analysis
    required_cols = {'Status', 'Student Name', 'Room No.'}
    if not required_cols.issubset(df.columns):
        st.error(f"Error: The following required columns are missing for detailed analysis: {', '.join(required_cols - set(df.columns))}")
        return {}

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
        
        present_students['Punch Time'] = pd.to_datetime(
            present_students['Last Punch'],
            format='%H:%M:%S',
            errors='coerce'
        ).dt.time
        
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
        
        # --- 4. Present Students per Room (Sorted and with names) ---
        present_per_room_df = df[df['Status'] == 'Present'].groupby(
            ['Block', 'Floor', 'Room No.']
        ).agg(
            Present_Count=('Status', 'size'),
            Present_Names=('Student Name', lambda x: ', '.join(sorted(x)))
        ).reset_index()
        output_dfs['Present Students per Room'] = sort_by_room_details(present_per_room_df, FLOOR_ORDER)

        # --- 5. Absent Students per Room (Sorted and with names) ---
        absent_per_room_df = df[df['Status'] == 'Not Present'].groupby(
            ['Block', 'Floor', 'Room No.']
        ).agg(
            Absent_Count=('Status', 'size'),
            Absent_Names=('Student Name', lambda x: ', '.join(sorted(x)))
        ).reset_index()
        output_dfs['Absent Students per Room'] = sort_by_room_details(absent_per_room_df, FLOOR_ORDER)
    else:
        st.warning("Warning: 'Block', 'Floor', or 'Room No.' columns not found. Skipping per-room analysis.")

    return output_dfs

def generate_excel_file(output_dfs: dict) -> io.BytesIO:
    """
    Exports all analysis DataFrames to a single Excel file in-memory.
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
    """
    try:
        attendance_data = []

        for file_name in csv_files:
            df = pd.read_csv(file_name)
            if 'Status' in df.columns:
                status_counts = df['Status'].value_counts().to_dict()
                # Dynamically set date label from filename
                date_label = file_name.replace('.csv', '') 
                attendance_data.append({
                    'Day': date_label,
                    'Present': status_counts.get('Present', 0),
                    'Not Present': status_counts.get('Not Present', 0)
                })

        attendance_df = pd.DataFrame(attendance_data)
        if not attendance_df.empty:
            # Dynamically determine the month from the first file found
            try:
                # Assuming filename format is DD-MMM-YYYY.csv
                month = csv_files[0].split('-')[1] 
            except IndexError:
                month = 'Data' # Fallback if filename format is unexpected
            
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
    except (ImportError, ModuleNotFoundError) as e:
        st.error(f"Error: A required library (matplotlib/numpy) is missing: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while creating the graph: {e}")
        return None

def calculate_cumulative_absence(csv_files: list, floor_order: list) -> pd.DataFrame:
    """
    Analyzes multiple CSV files to calculate the total number of days a student was absent.
    """
    all_absences = []
    student_details = {} 

    for file_name in csv_files:
        try:
            df = pd.read_csv(file_name)
        except Exception:
            continue

        # Check for all required columns (Employee Code is crucial for unique student tracking)
        required_cols = ['Employee Code', 'Status', 'Student Name', 'Block', 'Floor', 'Room No.']
        if all(col in df.columns for col in required_cols):
            
            # Store/update student details
            for _, row in df[required_cols].drop_duplicates().iterrows():
                student_details[row['Employee Code']] = {
                    'Student Name': row['Student Name'],
                    'Block': row['Block'],
                    'Floor': row['Floor'],
                    'Room No.': row['Room No.']
                }

            # Filter for absent students and assign a count of 1 for the day
            absent_df = df[df['Status'] == 'Not Present'].copy()
            if not absent_df.empty:
                absent_df['Absence_Count'] = 1
                all_absences.append(absent_df[['Employee Code', 'Absence_Count']])

    if not all_absences:
        return pd.DataFrame(columns=['Student Name', 'Block', 'Floor', 'Room No.', 'Number of Reduction Days'])

    # Combine all absence records and aggregate by Employee Code
    cumulative_absence_df = pd.concat(all_absences)
    total_absences = cumulative_absence_df.groupby('Employee Code')['Absence_Count'].sum().reset_index()
    total_absences.rename(columns={'Absence_Count': 'Number of Reduction Days'}, inplace=True)

    # Convert student details dictionary to a DataFrame for merging
    details_df = pd.DataFrame.from_dict(student_details, orient='index').reset_index().rename(columns={'index': 'Employee Code'})
    
    # Merge counts with student details
    final_df = pd.merge(details_df, total_absences, on='Employee Code', how='left').fillna(0)
    
    # Filter only students who were absent (count > 0)
    final_df['Number of Reduction Days'] = final_df['Number of Reduction Days'].astype(int)
    final_df = final_df[final_df['Number of Reduction Days'] > 0]

    # Select, rename and sort the final columns
    final_df = final_df[['Student Name', 'Block', 'Floor', 'Room No.', 'Number of Reduction Days']]

    # Apply the custom sorting
    final_df = sort_by_room_details(final_df, floor_order)
    
    # Cache the result in Streamlit's session state to avoid recalculation
    st.session_state['cumulative_df'] = final_df
    
    return final_df.reset_index(drop=True)

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds Streamlit filter controls (Block, Floor, Room No.) to the sidebar 
    and filters the DataFrame accordingly.
    """
    st.sidebar.header("Filter Cumulative Report")

    # 1. Block Filter
    blocks = ['All'] + sorted(df['Block'].unique().tolist())
    selected_block = st.sidebar.selectbox("Filter by Building Block", blocks)
    
    filtered_df = df.copy()
    if selected_block != 'All':
        filtered_df = filtered_df[filtered_df['Block'] == selected_block]

    # 2. Floor Filter
    # Only show floors relevant to the current filtered block
    # Use .cat.categories.intersection(filtered_df['Floor'].unique()) for categorical data
    current_floors_set = filtered_df['Floor'].cat.categories.intersection(filtered_df['Floor'].unique()).tolist()
    # Sort floors based on the global FLOOR_ORDER
    current_floors_sorted = sorted(current_floors_set, key=lambda x: FLOOR_ORDER.index(x) if x in FLOOR_ORDER else 99)
    current_floors = ['All'] + current_floors_sorted
    selected_floor = st.sidebar.selectbox("Filter by Floor", current_floors)

    if selected_floor != 'All':
        filtered_df = filtered_df[filtered_df['Floor'] == selected_floor]

    # 3. Room No. Filter
    # Only show rooms relevant to the current filtered block and floor
    current_rooms = ['All'] + sorted(filtered_df['Room No.'].unique().tolist())
    selected_room = st.sidebar.selectbox("Filter by Room No.", current_rooms)

    if selected_room != 'All':
        filtered_df = filtered_df[filtered_df['Room No.'] == selected_room]
        
    st.sidebar.markdown("---")
    st.sidebar.info(f"Showing {len(filtered_df)} of {len(df)} records.")

    return filtered_df

def app():
    """
    Main Streamlit application logic.
    """
    # Ensure wide mode for Streamlit
    st.set_page_config(layout="wide")
    
    st.title("Attendance Analysis Dashboard")
    st.write("This app provides a detailed analysis of daily attendance data and generates a monthly summary graph.")

    # Check/Initialize session state for the cumulative report
    if 'cumulative_df' not in st.session_state:
        st.session_state['cumulative_df'] = pd.DataFrame()

    # Part 1: Single-day analysis and Excel export
    st.header("Daily Attendance Report")
    file_name_input = st.text_input("Enter the file name (e.g., 01-Jun-2025):", value="01-Jun-2025")
    
    if st.button("Generate Daily Report"):
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
                                label="Download Daily Excel Report",
                                data=excel_file,
                                file_name=f"{file_name_input}_analysis.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                            # Display dataframes in the app
                            with st.expander("Show Daily Analysis Tables"):
                                for sheet_name, df_result in analysis_results.items():
                                    st.subheader(f"{sheet_name}")
                                    st.dataframe(df_result)
                except Exception as e:
                    st.error(f"An unexpected error occurred during single-day analysis: {e}")

    # Part 2: Monthly graph generation and Cumulative Absence Report
    st.header("Monthly Attendance Summary")
    
    csv_files = sorted([f for f in os.listdir() if f.endswith('.csv')])
    
    if csv_files:
        st.info(f"Found {len(csv_files)} CSV files: {', '.join(csv_files[:3])}...")
        
        # Monthly Graph
        st.subheader("Monthly Attendance Graph")
        fig = create_monthly_graph(csv_files)
        if fig:
            st.pyplot(fig)
        
        # --- Cumulative Absence Report ---
        st.subheader("Number of Reduction Days Per Student")
        
        # PRIMARY BUTTON: Used to trigger the calculation and populate the session state
        calculate_button = st.button("Generate Cumulative Absence Report", key="calculate_main")
        
        # Check if the button was pressed OR if data already exists in the session state
        if calculate_button or not st.session_state['cumulative_df'].empty:
            
            # Recalculate only if the button was pressed
            if calculate_button:
                with st.spinner('Calculating total absence days across all files...'):
                    # The function calculates AND saves the result to session_state
                    cumulative_df_original = calculate_cumulative_absence(csv_files, FLOOR_ORDER)
            
            cumulative_df_original = st.session_state['cumulative_df']

            if not cumulative_df_original.empty:
                st.success("Cumulative Absence Report calculated successfully. Use the sidebar to filter.")
                
                # --- APPLY FILTERS ---
                # This function is run on every rerun, allowing the filters to work interactively
                filtered_df = apply_filters(cumulative_df_original)

                # --- DISPLAY ---
                st.dataframe(filtered_df)
                
                # --- DOWNLOAD BUTTON ---
                cumulative_dfs = {'Number of Reduction Days': filtered_df}
                excel_file_cumulative = generate_excel_file(cumulative_dfs)
                
                if excel_file_cumulative:
                    st.download_button(
                        label="Download Filtered Excel Report",
                        data=excel_file_cumulative,
                        file_name="Monthly_Reduction_Days_Filtered_Report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.info("No students were marked as 'Not Present' across all files.")
    else:
        st.info("No CSV files found in the current directory to generate a monthly graph or cumulative report.")

if __name__ == "__main__":
    app()
