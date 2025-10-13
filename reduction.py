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
# Added multiple formats to handle various file name date styles
DATE_FORMATS = ['%d-%B-%Y', '%d-%b-%Y', '%d-%B%Y', '%d-%b%Y'] 

# --- Helper Function for Sorting ---
def sort_by_room_details(data_df: pd.DataFrame, floor_order: list) -> pd.DataFrame:
    """
    Helper function to sort DataFrame by Block, Floor (custom order), and Room No.
    """
    if not data_df.empty and all(col in data_df.columns for col in ['Block', 'Floor', 'Room No.']):
        data_df['Floor'] = pd.Categorical(data_df['Floor'], categories=floor_order, ordered=True)
        # Ensure Room No is string for consistent sorting if needed, though pandas handles mixed types well usually
        data_df.sort_values(by=['Block', 'Floor', 'Room No.'], inplace=True)
    return data_df

# --- Helper Function for Grouping Files by Month (Used for Monthly Graph) ---
def group_files_by_month(csv_files: list) -> dict:
    """
    Groups a list of CSV file names into a dictionary where the key is 'Month-Year' (e.g., 'Jul-2025')
    and the value is a list of file names belonging to that month, sorted by date.
    """
    monthly_groups = {}
    
    for file_name in csv_files:
        date_part = file_name.replace('.csv', '')
        date_obj = None
        
        # Try multiple formats
        for fmt in DATE_FORMATS:
            try:
                date_obj = datetime.strptime(date_part, fmt)
                break
            except ValueError:
                continue
        
        if date_obj:
            month_year_key = date_obj.strftime('%b-%Y')
            
            if month_year_key not in monthly_groups:
                monthly_groups[month_year_key] = []
            monthly_groups[month_year_key].append(file_name)
    
    # Sort files within each month by date
    final_monthly_groups = {}
    for month, files in monthly_groups.items():
        sortable_list = []
        for file_name in files:
            date_part = file_name.replace('.csv', '')
            date_obj_sort = None
            
            for fmt in DATE_FORMATS:
                try:
                    date_obj_sort = datetime.strptime(date_part, fmt)
                    break
                except ValueError:
                    continue
            
            if date_obj_sort:
                sortable_list.append((date_obj_sort, file_name))
        
        sortable_list.sort(key=lambda x: x[0])
        final_monthly_groups[month] = [file[1] for file in sortable_list]
        
    return final_monthly_groups

# --- Core Function for Daily Analysis (Restored) ---
def analyze_attendance(df: pd.DataFrame) -> dict:
    """
    Performs a detailed analysis of the attendance DataFrame for a single day.
    """
    required_cols = {'Status', 'Student Name', 'Room No.'}
    if not required_cols.issubset(df.columns):
        st.error("Missing required columns for daily analysis: 'Status', 'Student Name', 'Room No.'.")
        return {} 

    output_dfs = {}
    status_counts = df['Status'].value_counts()
    daily_summary_data = {
        'Metric': ['Total Students', 'Present', 'Absent'],
        'Count': [len(df), status_counts.get('Present', 0), status_counts.get('Not Present', 0)]
    }
    output_dfs['Daily Summary'] = pd.DataFrame(daily_summary_data)

    late_punch_time = datetime.strptime(LATE_PUNCH_TIME_STR, '%H:%M:%S').time()
    
    if 'Last Punch' in df.columns:
        present_students = df[df['Status'] == 'Present'].copy()
        
        present_students['Punch Time'] = pd.to_datetime(
            present_students['Last Punch'],
            format='%H:%M:%S',
            errors='coerce'
        ).dt.time
        
        late_punches_df = present_students[present_students['Punch Time'].astype(str) > str(late_punch_time)].copy()
        
        output_dfs['Late Biometric Punches'] = late_punches_df[['Student Name', 'Room No.', 'Last Punch']]
    else:
        output_dfs['Late Biometric Punches'] = pd.DataFrame(columns=['Student Name', 'Room No.', 'Last Punch'])

    absent_students_df = df[df['Status'] == 'Not Present'].copy()
    output_dfs['Students to Notify'] = absent_students_df[['Student Name', 'Room No.']].sort_values(by='Student Name')

    if {'Block', 'Floor', 'Room No.'}.issubset(df.columns):
        
        present_per_room_df = df[df['Status'] == 'Present'].groupby(
            ['Block', 'Floor', 'Room No.']
        ).agg(
            Present_Count=('Status', 'size'),
            Present_Names=('Student Name', lambda x: ', '.join(sorted(x)))
        ).reset_index()
        output_dfs['Present Students per Room'] = sort_by_room_details(present_per_room_df, FLOOR_ORDER)

        absent_per_room_df = df[df['Status'] == 'Not Present'].groupby(
            ['Block', 'Floor', 'Room No.']
        ).agg(
            Absent_Count=('Status', 'size'),
            Absent_Names=('Student Name', lambda x: ', '.join(sorted(x)))
        ).reset_index()
        output_dfs['Absent Students per Room'] = sort_by_room_details(absent_per_room_df, FLOOR_ORDER)

    return output_dfs

# --- Helper Function for Excel Export ---
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
        st.error("Please ensure the 'xlsxwriter' library is installed for Excel export.")
        return None

# --- Core Function for Monthly Graph ---
def create_monthly_graph(month_key: str, csv_files_in_month: list):
    """
    Analyzes CSV files for a SINGLE month to create an attendance graph.
    """
    try:
        attendance_data = []

        for file_name in csv_files_in_month:
            df = pd.read_csv(file_name)
            if 'Status' in df.columns:
                status_counts = df['Status'].value_counts().to_dict()
                
                day_label = file_name.replace('.csv', '')
                date_part = file_name.replace('.csv', '')
                
                # Get the day part for the x-axis label
                date_obj = None
                for fmt in DATE_FORMATS:
                    try:
                        date_obj = datetime.strptime(date_part, fmt)
                        day_label = date_obj.strftime('%d')
                        break
                    except ValueError:
                        continue
                
                if date_obj is None:
                    st.warning(f"Could not parse date from filename: {file_name}. Skipping.")
                    continue

                attendance_data.append({
                    'Day': day_label,
                    'Present': status_counts.get('Present', 0),
                    'Not Present': status_counts.get('Not Present', 0),
                    'Date_Sort': date_obj # Use this for internal sorting
                })

        attendance_df = pd.DataFrame(attendance_data).sort_values(by='Date_Sort').reset_index(drop=True)

        if not attendance_df.empty:
            
            fig, ax = plt.subplots(figsize=(12, 7))
            bar_width = 0.35
            x = np.arange(len(attendance_df['Day']))
            
            # Colors for better visibility
            colors = {'Present': '#4CAF50', 'Not Present': '#F44336'}
            
            ax.bar(x - bar_width/2, attendance_df['Present'], bar_width, label='Present', color=colors['Present'])
            ax.bar(x + bar_width/2, attendance_df['Not Present'], bar_width, label='Not Present', color=colors['Not Present'])
            
            # Styling
            ax.set_xlabel('Day of Month', fontsize=12)
            ax.set_ylabel('Number of Students', fontsize=12)
            ax.set_title(f'Daily Attendance Trend for {month_key}', fontsize=14)
            ax.set_xticks(x)
            ax.set_xticklabels(attendance_df['Day'], rotation=0)
            ax.legend()
            ax.grid(axis='y', linestyle='--', alpha=0.6)
            plt.tight_layout()
            
            return fig
        else:
            return None
    except Exception as e:
        st.error(f"An error occurred while creating the graph: {e}")
        return None

# --- NEW: Function to collect all unique location details across all files ---
@st.cache_data
def collect_unique_location_details(csv_files: list) -> tuple:
    """
    Scans all CSV files to get unique Block, Floor, and Room No.
    """
    unique_blocks = set()
    unique_floors = set()
    unique_rooms = set()
    
    required_cols = {'Block', 'Floor', 'Room No.'}
    
    for file_name in csv_files:
        try:
            df = pd.read_csv(file_name)
            if all(col in df.columns for col in required_cols):
                unique_blocks.update(df['Block'].dropna().unique())
                unique_floors.update(df['Floor'].dropna().unique())
                
                # Convert Room No. to string before collecting to handle mixed types consistently
                room_nos = df['Room No.'].dropna().astype(str).unique()
                unique_rooms.update(room_nos)
        except Exception:
            continue
            
    # Sort floors according to the defined FLOOR_ORDER
    sorted_floors = [f for f in FLOOR_ORDER if f in unique_floors]
    for f in sorted(list(unique_floors)): # Add any non-standard floors alphabetically
        if f not in sorted_floors:
            sorted_floors.append(f)
            
    # Sort blocks and rooms alphabetically
    sorted_blocks = sorted(list(unique_blocks))
    sorted_rooms = sorted(list(unique_rooms)) # Keeps them as strings for filtering

    return sorted_blocks, sorted_floors, sorted_rooms


# --- Core Function for Reduction Days Report (formerly Cumulative Absence) ---
def calculate_reduction_days(csv_files: list, floor_order: list, 
                                 selected_blocks: list, selected_floors: list, 
                                 selected_rooms: list) -> pd.DataFrame:
    """
    Analyzes multiple CSV files to calculate the total number of days a student was absent (Reduction Days) 
    and applies location filters.
    """
    all_absences = []
    student_details = {}  

    for file_name in csv_files:
        try:
            df = pd.read_csv(file_name)
        except Exception:
            continue

        required_cols = ['Employee Code', 'Status', 'Student Name', 'Block', 'Floor', 'Room No.']
        if all(col in df.columns for col in required_cols):
            
            # Collect student details (including Block/Floor/Room for filtering later)
            for _, row in df[required_cols].drop_duplicates().iterrows():
                student_details[row['Employee Code']] = {
                    'Student Name': row['Student Name'],
                    'Block': row['Block'],
                    'Floor': row['Floor'],
                    'Room No.': str(row['Room No.']) # Ensure Room No. is string for consistent merge/filter
                }

            absent_df = df[df['Status'] == 'Not Present'].copy()
            if not absent_df.empty:
                absent_df['Absence_Count'] = 1
                all_absences.append(absent_df[['Employee Code', 'Absence_Count']])

    if not all_absences:
        # Renamed column header
        return pd.DataFrame(columns=['Student Name', 'Block', 'Floor', 'Room No.', 'Reduction Days'])

    cumulative_absence_df = pd.concat(all_absences)
    total_absences = cumulative_absence_df.groupby('Employee Code')['Absence_Count'].sum().reset_index()
    
    # --- RENAME: Column header changed to "Reduction Days" ---
    total_absences.rename(columns={'Absence_Count': 'Reduction Days'}, inplace=True)

    details_df = pd.DataFrame.from_dict(student_details, orient='index').reset_index().rename(columns={'index': 'Employee Code'})
    
    final_df = pd.merge(details_df, total_absences, on='Employee Code', how='left').fillna(0)
    
    final_df['Reduction Days'] = final_df['Reduction Days'].astype(int)
    
    # Filter only students who have absences recorded
    final_df = final_df[final_df['Reduction Days'] > 0].copy()


    # --- NEW: Apply Multi-Select Filtering ---
    # Convert Room No. in the DataFrame to string for consistent filtering
    final_df['Room No.'] = final_df['Room No.'].astype(str)

    # 1. Block Filter
    if selected_blocks and selected_blocks != ['All']:
        final_df = final_df[final_df['Block'].isin(selected_blocks)]
        
    # 2. Floor Filter
    if selected_floors and selected_floors != ['All']:
        final_df = final_df[final_df['Floor'].isin(selected_floors)]
        
    # 3. Room No. Filter (Filter list is already strings)
    if selected_rooms and selected_rooms != ['All']:
        final_df = final_df[final_df['Room No.'].isin(selected_rooms)]
        
    # --- END NEW FILTERING ---

    # Final column selection and sorting
    final_df = final_df[['Student Name', 'Block', 'Floor', 'Room No.', 'Reduction Days']]

    final_df = sort_by_room_details(final_df, floor_order)
    
    return final_df.reset_index(drop=True)


# --- Streamlit App Entry Point (Refactored) ---
def app():
    st.set_page_config(layout="wide")
    st.title("Attendance Analysis Dashboard")

    all_csv_files = sorted([f for f in os.listdir() if f.endswith('.csv')])
    monthly_file_groups = group_files_by_month(all_csv_files)
    
    month_options = sorted(monthly_file_groups.keys(), key=lambda x: datetime.strptime(x, '%b-%Y'), reverse=True)
    
    # Prepare hierarchical data for Daily Analysis selector
    daily_selection_data = {} 
    for file_name in all_csv_files:
        date_part = file_name.replace('.csv', '')
        date_obj = None
        for fmt in DATE_FORMATS:
            try:
                date_obj = datetime.strptime(date_part, fmt)
                break
            except ValueError:
                continue
        
        if date_obj:
            year = date_obj.strftime('%Y')
            month_key = date_obj.strftime('%b') 
            display_day = date_obj.strftime('%d (%a)')
            
            if year not in daily_selection_data:
                daily_selection_data[year] = {}
            if month_key not in daily_selection_data[year]:
                daily_selection_data[year][month_key] = []
            
            daily_selection_data[year][month_key].append((date_obj, display_day, file_name))
            
    for year in daily_selection_data:
        for month in daily_selection_data[year]:
            daily_selection_data[year][month].sort(key=lambda x: x[0], reverse=True)
            
    selected_file = None 
    
    # Get unique location details for filtering the Reduction Days report
    unique_blocks, unique_floors, unique_rooms = collect_unique_location_details(all_csv_files)


    # ------------------------------------------------
    # SIDEBAR: Controls
    # ------------------------------------------------
    with st.sidebar:
        st.header("Analysis Controls")
        
        # --- RENAME: Analysis Type Radio Button Updated ---
        analysis_type = st.radio(
            "Select Analysis Type",
            ('Daily Attendance Report', 'Monthly Attendance Graph', 'Reduction Days Report')
        )
        st.markdown("---")

        selected_blocks, selected_floors, selected_rooms = None, None, None

        if analysis_type == 'Daily Attendance Report':
            st.subheader("Daily Report Date")
            
            all_years = sorted(daily_selection_data.keys(), reverse=True)
            
            if all_years:
                # 1. Year Selector
                selected_year = st.selectbox(
                    "Select Year:",
                    options=all_years,
                    index=0,
                    key="daily_year_select"
                )

                # 2. Month Selector
                months_in_year = sorted(daily_selection_data.get(selected_year, {}).keys(), key=lambda x: datetime.strptime(x, '%b'))
                
                if months_in_year:
                    selected_month = st.selectbox(
                        "Select Month:",
                        options=months_in_year,
                        index=len(months_in_year) - 1,
                        key="daily_month_select"
                    )

                    # 3. Day/Date Selector (File Name)
                    files_in_month_data = daily_selection_data.get(selected_year, {}).get(selected_month, [])
                    
                    display_dates = [f[1] for f in files_in_month_data]
                    file_map = {f[1]: f[2] for f in files_in_month_data}
                    
                    selected_display_date = st.selectbox(
                        "Select Day:",
                        options=display_dates,
                        index=0,
                        key="daily_day_select",
                        help="Select a day's report. The format is DD (Weekday)."
                    )
                    
                    selected_file = file_map.get(selected_display_date)

                else:
                    st.warning("No files found for selected year.")
            else:
                st.warning("No valid attendance files found.")
                
            st.markdown("---")
        
        elif analysis_type == 'Monthly Attendance Graph':
            st.subheader("Monthly Graph Selector")
            selected_month_key = st.selectbox(
                "Choose Month-Year for the trend graph:",
                options=month_options,
                index=0 if month_options else None,
                help="Generates a bar chart showing Present vs. Absent trends across all days in the selected month."
            )
            st.markdown("---")

        # --- NEW: Multi-select Filters for Reduction Days Report ---
        elif analysis_type == 'Reduction Days Report':
            st.subheader("Filter Location Details")
            
            # Add 'All' option to defaults
            block_options = ['All'] + unique_blocks
            floor_options = ['All'] + unique_floors
            room_options = ['All'] + unique_rooms

            selected_blocks = st.multiselect(
                "Select Block(s)", 
                options=block_options, 
                default=['All'],
                help="Select one or more blocks to include in the report."
            )
            
            selected_floors = st.multiselect(
                "Select Floor(s)", 
                options=floor_options, 
                default=['All'],
                help="Select one or more floors to include in the report."
            )

            selected_rooms = st.multiselect(
                "Select Room No(s)", 
                options=room_options, 
                default=['All'],
                help="Select one or more room numbers to include in the report."
            )
            st.markdown("---")


    # ------------------------------------------------
    # MAIN CONTENT: Reports
    # ------------------------------------------------

    if not all_csv_files:
        st.error("No CSV files found in the directory. Please upload attendance files to run the analysis.")
        return

    # --- 1. Daily Attendance Report ---
    if analysis_type == 'Daily Attendance Report' and selected_file:
        # ... (Daily report display logic remains the same) ...
        st.header(f"Detailed Daily Attendance Report: {selected_file.replace('.csv', '')}")

        try:
            df = pd.read_csv(selected_file)
            analysis_results = analyze_attendance(df)

            if analysis_results:
                
                # --- Daily Summary ---
                st.subheader("Daily Summary")
                st.dataframe(analysis_results['Daily Summary'], hide_index=True)
                
                # --- Late Biometric Punches ---
                st.subheader("Late Biometric Punches (Punch after 8:45 PM)")
                if not analysis_results['Late Biometric Punches'].empty:
                    st.dataframe(analysis_results['Late Biometric Punches'], hide_index=True)
                else:
                    st.info("No late biometric punches recorded after 8:45 PM for present students.")

                # --- Absent Students ---
                st.subheader("Students to Notify (Not Present)")
                if not analysis_results['Students to Notify'].empty:
                    st.dataframe(analysis_results['Students to Notify'], hide_index=True)
                else:
                    st.success("All students are present!")
                
                st.markdown("---")
                
                # --- Per Room Analysis ---
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Present Students per Room")
                    st.dataframe(analysis_results['Present Students per Room'], hide_index=True)
                    
                with col2:
                    st.subheader("Absent Students per Room")
                    st.dataframe(analysis_results['Absent Students per Room'], hide_index=True)

                # --- Daily Download Button ---
                excel_buffer = generate_excel_file(analysis_results)
                if excel_buffer:
                    st.download_button(
                        label="Download Full Daily Report (Excel)",
                        data=excel_buffer,
                        file_name=f"Daily_Analysis_{selected_file.replace('.csv', '')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        help="Downloads all tables above into a single Excel file with multiple sheets."
                    )
            else:
                st.error("Could not run analysis. Check if the file has data and correct column headers.")

        except Exception as e:
            st.error(f"Error loading or analyzing file {selected_file}: {e}")

    elif analysis_type == 'Daily Attendance Report' and not selected_file:
         st.warning("Please ensure valid attendance files are uploaded and select a date.")


    # --- 2. Monthly Attendance Graph ---
    elif analysis_type == 'Monthly Attendance Graph' and selected_month_key:
        # ... (Monthly graph display logic remains the same) ...
        st.header(f"Monthly Attendance Trend: {selected_month_key}")
        
        files_for_month = monthly_file_groups.get(selected_month_key, [])
        if files_for_month:
            with st.spinner(f"Generating graph for {selected_month_key} from {len(files_for_month)} daily reports..."):
                fig = create_monthly_graph(selected_month_key, files_for_month)
                if fig:
                    st.pyplot(fig)
                else:
                    st.warning(f"No valid attendance data found for {selected_month_key} to generate the graph.")
        else:
            st.warning(f"No files found for the selected month: {selected_month_key}.")


    # --- 3. Reduction Days Report ---
    elif analysis_type == 'Reduction Days Report':
        # --- RENAME: Header changed to "Reduction Days Report" ---
        st.header("Reduction Days Report")
        
        with st.spinner('Calculating total reduction days across all files and applying filters...'):
            # --- UPDATED: Passing filter selections to the calculation function ---
            cumulative_df = calculate_reduction_days(
                all_csv_files, 
                FLOOR_ORDER,
                selected_blocks,
                selected_floors,
                selected_rooms
            )
        
        if not cumulative_df.empty:
            # st.success(f"Displaying Reduction Days for {len(cumulative_df)} students based on selected filters.") <-- REMOVED THIS LINE
            
            st.dataframe(cumulative_df, hide_index=True)
            
            # --- Cumulative Download Button ---
            # --- RENAME: Excel sheet name updated ---
            cumulative_dfs = {'Reduction Days': cumulative_df}
            excel_file_cumulative = generate_excel_file(cumulative_dfs)
            
            if excel_file_cumulative:
                st.download_button(
                    label="Download Reduction Days Report (Excel)",
                    data=excel_file_cumulative,
                    file_name="Reduction_Days_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            # Check if filtering resulted in zero results, or if there were no initial absences
            if (selected_blocks and selected_blocks != ['All']) or \
               (selected_floors and selected_floors != ['All']) or \
               (selected_rooms and selected_rooms != ['All']):
                st.info("No students with recorded Reduction Days match the current location filters.")
            else:
                st.info("No students were marked as 'Not Present' across all files, resulting in zero Reduction Days.")

    # Display status if no file options are available
    if not all_csv_files and analysis_type != 'Reduction Days Report':
        st.warning("No CSV files found to perform the analysis. Please ensure your attendance files are available.")


if __name__ == "__main__":
    app()
