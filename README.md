Attendance Analysis Script
This Python script uses the pandas and matplotlib libraries to analyze attendance data from a CSV file. It calculates various statistics and generates a pie chart to visualize the overall attendance status.

Features
Total Students: Counts and prints the total number of students in the dataset.

Attendance Status: Displays a count of "Present" vs. "Not Present" students.

Floor and Room Breakdown: Shows the number of students on each floor and in each room.

Visual Attendance Summary: Creates a pie chart showing the percentage of "Present" and "Not Present" students.

Prerequisites
To run this script, you need to have Python installed along with the following libraries:

pandas

matplotlib

You can install these dependencies using pip:

pip install pandas matplotlib

How to Use
Prepare your data: Ensure your attendance data is in a CSV file with the following columns:

Status (must contain values like Present and Not Present)

Floor

Room No.

Other columns can be present but will not be used in the analysis.

Run the script: Open a terminal or command prompt, navigate to the directory where the script is saved, and run the script with the python command:

python your_script_name.py

Enter the filename: The script will prompt you to "enter the file name". Type the name of your CSV file (e.g., attendance_data.csv) and press Enter.

View the output: The script will print the analysis results to the console and display the pie chart in a separate window.

Example
Assuming you have a CSV file named attendance_data.csv, the script's output would look similar to this:

enter the file nameattendance_data.csv
Total students
100
Count of Present vs Not Present
Status
Present        75
Not Present    25
Name: count, dtype: int64
Students per floor
Floor
ThirdFloor     30
SecondFloor    25
FourthFloor    25
FifthFloor     20
Name: count, dtype: int64
Students per room
Room No.
302    5
204    4
307    3
...
Name: count, dtype: int64

The pie chart will appear in a new window, similar to the one below, showing the Present and Not Present percentages.
