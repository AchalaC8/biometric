<h1>Attendance Analysis Script</h1>
<p>A utility for processing and visualizing attendance data from CSV files.</p>

<section>
<p>This Python script uses the <code>pandas</code> and <code>matplotlib</code> libraries to analyze attendance data from a CSV file. It calculates various statistics and generates a pie chart to visualize the overall attendance status.</p>
</section>

<div>
<div>
<h2>Features</h2>
<ul>
<li><strong>Total Students:</strong> Counts and prints the total number of students in the dataset.</li>
<li><strong>Attendance Status:</strong> Displays a count of "Present" vs. "Not Present" students.</li>
<li><strong>Floor and Room Breakdown:</strong> Shows the number of students on each floor and in each room.</li>
<li><strong>Visual Attendance Summary:</strong> Creates a pie chart showing the percentage of "Present" and "Not Present" students.</li>
</ul>
</div>

<div>
    <h2>Prerequisites</h2>
    <p>To run this script, you need to have Python installed along with the following libraries:</p>
    <ul>
        <li><code>pandas</code></li>
        <li><code>matplotlib</code></li>
    </ul>
    <p>You can install these dependencies using <code>pip</code>:</p>
    <div>
        <pre>pip install pandas matplotlib</pre>
    </div>
</div>

<div>
    <h2>How to Use</h2>
    <ol>
        <li><strong class="font-semibold">Prepare your data:</strong> Ensure your attendance data is in a CSV file with the following columns:
            <ul>
                <li><code>Status</code> (must contain values like `Present` and `Not Present`)</li>
                <li><code>Floor</code></li>
                <li><code>Room No.</code></li>
                <li>Other columns can be present but will not be used in the analysis.</li>
            </ul>
        </li>
        <li><strong class="font-semibold">Run the script:</strong> Open a terminal or command prompt, navigate to the directory where the script is saved, and run the script with the <code>python</code> command:
            <div>
                <pre>python your_script_name.py</pre>
            </div>
        </li>
        <li><strong class="font-semibold">Enter the filename:</strong> The script will prompt you to "enter the file name". Type the name of your CSV file (e.g., <code>attendance_data.csv</code>) and press Enter.</li>
        <li><strong class="font-semibold">View the output:</strong> The script will print the analysis results to the console and display the pie chart in a separate window.</li>
    </ol>
</div>

<div>
    <h2>Example</h2>
    <p>Assuming you have a CSV file named <code>01-Jun-2025.csv</code>, the script's output would look similar to this:</p>
    <div>
        <pre>
enter the file nameattendance_data.csv
Total students
100
Count of Present vs Not Present
Status
Present         75
Not Present     25
Name: count, dtype: int64
Students per floor
Floor
ThirdFloor      30
SecondFloor     25
FourthFloor     25
FifthFloor      20
Name: count, dtype: int64
Students per room
Room No.
302    5
204    4
307    3
...
Name: count, dtype: int64</pre>
</div>
<p>The pie chart will appear in a new window, similar to the one below, showing the Present and Not Present percentages. </p>
</div>

</div>
