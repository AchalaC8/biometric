import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

# Get a sorted list of CSV files to ensure chronological order
csv_files = sorted([f for f in os.listdir() if f.endswith('.csv')])

# Extract the month from the first filename to name the graph
if csv_files:
    month = csv_files[0].split('-')[1]
    graph_filename = f'attendance_graph_{month}.png'
else:
    # Fallback name if no files are found
    month = 'Data'
    graph_filename = 'attendance_graph.png'
    
attendance_data = []

# Loop through each CSV file to extract attendance data
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

    plt.savefig(graph_filename)
