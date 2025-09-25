<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attendance Analysis Script</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f3f4f6;
            color: #1f2937;
        }
    </style>
</head>
<body class="p-8">

    <div class="max-w-4xl mx-auto bg-white shadow-xl rounded-lg p-8 space-y-8">

        <header class="text-center pb-4 border-b border-gray-200">
            <h1 class="text-4xl font-extrabold text-gray-900 mb-2">Attendance Analysis Script</h1>
            <p class="text-lg text-gray-600">A utility for processing and visualizing attendance data from CSV files.</p>
        </header>

        <section>
            <p class="text-gray-700 leading-relaxed text-base">This Python script uses the <code class="bg-gray-100 px-1 py-0.5 rounded-md text-sm font-semibold text-gray-800">pandas</code> and <code class="bg-gray-100 px-1 py-0.5 rounded-md text-sm font-semibold text-gray-800">matplotlib</code> libraries to analyze attendance data from a CSV file. It calculates various statistics and generates a pie chart to visualize the overall attendance status.</p>
        </section>

        <div class="space-y-6">
            <div class="bg-gray-50 rounded-lg p-6">
                <h2 class="text-2xl font-bold text-gray-800 mb-4">Features</h2>
                <ul class="list-disc list-inside space-y-2 text-gray-700 leading-relaxed">
                    <li><strong class="font-semibold">Total Students:</strong> Counts and prints the total number of students in the dataset.</li>
                    <li><strong class="font-semibold">Attendance Status:</strong> Displays a count of "Present" vs. "Not Present" students.</li>
                    <li><strong class="font-semibold">Floor and Room Breakdown:</strong> Shows the number of students on each floor and in each room.</li>
                    <li><strong class="font-semibold">Visual Attendance Summary:</strong> Creates a pie chart showing the percentage of "Present" and "Not Present" students.</li>
                </ul>
            </div>

            <div class="bg-gray-50 rounded-lg p-6">
                <h2 class="text-2xl font-bold text-gray-800 mb-4">Prerequisites</h2>
                <p class="text-gray-700 leading-relaxed mb-4">To run this script, you need to have Python installed along with the following libraries:</p>
                <ul class="list-disc list-inside space-y-2 text-gray-700 leading-relaxed">
                    <li><code class="bg-gray-100 px-1 py-0.5 rounded-md text-sm font-semibold text-gray-800">pandas</code></li>
                    <li><code class="bg-gray-100 px-1 py-0.5 rounded-md text-sm font-semibold text-gray-800">matplotlib</code></li>
                </ul>
                <p class="text-gray-700 leading-relaxed mt-4">You can install these dependencies using <code class="bg-gray-100 px-1 py-0.5 rounded-md text-sm font-semibold text-gray-800">pip</code>:</p>
                <div class="bg-gray-800 text-white rounded-lg p-4 font-mono text-sm mt-2">
                    <pre>pip install pandas matplotlib</pre>
                </div>
            </div>

            <div class="bg-gray-50 rounded-lg p-6">
                <h2 class="text-2xl font-bold text-gray-800 mb-4">How to Use</h2>
                <ol class="list-decimal list-inside space-y-4 text-gray-700 leading-relaxed">
                    <li><strong class="font-semibold">Prepare your data:</strong> Ensure your attendance data is in a CSV file with the following columns:
                        <ul class="list-disc list-inside ml-6 mt-2 space-y-1">
                            <li><code class="bg-gray-100 px-1 py-0.5 rounded-md text-sm font-semibold text-gray-800">Status</code> (must contain values like `Present` and `Not Present`)</li>
                            <li><code class="bg-gray-100 px-1 py-0.5 rounded-md text-sm font-semibold text-gray-800">Floor</code></li>
                            <li><code class="bg-gray-100 px-1 py-0.5 rounded-md text-sm font-semibold text-gray-800">Room No.</code></li>
                            <li>Other columns can be present but will not be used in the analysis.</li>
                        </ul>
                    </li>
                    <li><strong class="font-semibold">Run the script:</strong> Open a terminal or command prompt, navigate to the directory where the script is saved, and run the script with the <code class="bg-gray-100 px-1 py-0.5 rounded-md text-sm font-semibold text-gray-800">python</code> command:
                        <div class="bg-gray-800 text-white rounded-lg p-4 font-mono text-sm mt-2">
                            <pre>python your_script_name.py</pre>
                        </div>
                    </li>
                    <li><strong class="font-semibold">Enter the filename:</strong> The script will prompt you to "enter the file name". Type the name of your CSV file (e.g., <code class="bg-gray-100 px-1 py-0.5 rounded-md text-sm font-semibold text-gray-800">attendance_data.csv</code>) and press Enter.</li>
                    <li><strong class="font-semibold">View the output:</strong> The script will print the analysis results to the console and display the pie chart in a separate window.</li>
                </ol>
            </div>

            <div class="bg-gray-50 rounded-lg p-6">
                <h2 class="text-2xl font-bold text-gray-800 mb-4">Example</h2>
                <p class="text-gray-700 leading-relaxed mb-4">Assuming you have a CSV file named <code class="bg-gray-100 px-1 py-0.5 rounded-md text-sm font-semibold text-gray-800">attendance_data.csv</code>, the script's output would look similar to this:</p>
                <div class="bg-gray-800 text-white rounded-lg p-4 font-mono text-sm mt-2 space-y-2">
                    <pre class="whitespace-pre-wrap"><code>enter the file nameattendance_data.csv
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
Name: count, dtype: int64</code></pre>
                </div>
                <p class="text-gray-700 leading-relaxed mt-4">The pie chart will appear in a new window, similar to the one below, showing the `Present` and `Not Present` percentages. </p>
            </div>
        </div>
    </div>

</body>
</html>
