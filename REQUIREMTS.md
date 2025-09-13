    <h1 class="section-header">Project Requirements: Automated Attendance Notification System</h1>

    <p>This document outlines the functional and non-functional requirements for the Automated Attendance Notification System.</p>

    <h2>1. Functional Requirements</h2>

    <h3>1.1 Data Processing</h3>
    <ul>
        <li><strong>RF-1.1.1:</strong> The system SHALL read daily attendance data from a CSV file.</li>
        <li><strong>RF-1.1.2:</strong> The system SHALL dynamically identify the correct CSV file for the current day based on a consistent naming convention (e.g., `DD-Mon-YYYY.csv`).</li>
        <li><strong>RF-1.1.3:</strong> The system SHALL be able to parse data with the following columns: `Employee Code`, `Student Name`, `Block`, `Floor`, `Room No.`, `Last Punch`, `Punch Records`, and `Status`.</li>
    </ul>

    <h3>1.2 Absentee Identification</h3>
    <ul>
        <li><strong>RF-1.2.1:</strong> The system SHALL accurately identify all students with a `Status` of "Not Present".</li>
        <li><strong>RF-1.2.2:</strong> The system SHALL also identify students who have `Last Punch` after a specified time threshold (e.g., 8:45 PM) as "Late".</li>
    </ul>

    <h3>1.3 Reporting</h3>
    <ul>
        <li><strong>RF-1.3.1:</strong> The system SHALL generate an Excel file (`.xlsx`) containing multiple sheets for different reports.</li>
        <li><strong>RF-1.3.2:</strong> The Excel file SHALL include a sheet named "Daily Summary" with a count of total students, present students, absent students, and late students.</li>
        <li><strong>RF-1.3.3:</strong> The Excel file SHALL include a sheet named "Students to Notify" listing the details of all absent students.</li>
        <li><strong>RF-1.3.4:</strong> The Excel file SHALL include a sheet named "Late Biometric Punches" listing students who checked in late.</li>
        <li><strong>RF-1.3.5:</strong> The Excel file SHALL include a sheet named "Present Students per Room" listing the names of present students, sorted by Block, Floor, and Room.</li>
        <li><strong>RF-1.3.6:</strong> The Excel file SHALL include a sheet named "Absent Students per Room" listing the names of absent students, sorted by Block, Floor, and Room.</li>
    </ul>

    <h3>1.4 Notification</h3>
    <ul>
        <li><strong>RF-1.4.1:</strong> The system SHALL send an automated notification to each student identified as "Not Present".</li>
        <li><strong>RF-1.4.2:</strong> The system SHALL support integration with a third-party messaging API (e.g., Twilio) for sending SMS or email alerts.</li>
        <li><strong>RF-1.4.3:</strong> The notification content SHALL be configurable and include relevant details such as the student's name and a reminder message.</li>
    </ul>

    <hr>

    <h2>2. Non-Functional Requirements</h2>

    <h3>2.1 Performance</h3>
    <ul>
        <li><strong>RN-2.1.1:</strong> The system SHALL process and generate the reports within 30 seconds for a file containing up to 500 records.</li>
    </ul>

    <h3>2.2 Reliability and Availability</h3>
    <ul>
        <li><strong>RN-2.2.1:</strong> The system SHALL be scheduled to run once daily at a specific, predetermined time (e.g., 8:45 PM).</li>
        <li><strong>RN-2.2.2:</strong> The system SHALL handle cases where the daily CSV file is not present without crashing, and instead, log an appropriate message.</li>
    </ul>

    <h3>2.3 Security</h3>
    <ul>
        <li><strong>RN-2.3.1:</strong> The system SHALL handle sensitive API keys and credentials securely.</li>
        <li><strong>RN-2.3.2:</strong> The system SHALL protect student data (e.g., phone numbers, names) by ensuring it is not publicly exposed in logs or reports beyond what is necessary for the intended function.</li>
    </ul>

    <h3>2.4 Usability</h3>
    <ul>
        <li><strong>RN-2.4.1:</strong> The system SHALL not require manual intervention after the initial setup.</li>
        <li><strong>RN-2.4.2:</strong> The output reports SHALL be clearly organized and easy for administrators to understand.</li>
    </ul>

    <h3>2.5 Maintainability</h3>
    <ul>
        <li><strong>RN-2.5.1:</strong> The code SHALL be well-documented with comments explaining the purpose of functions and key logic.</li>
        <li><strong>RN-2.5.2:</strong> The code structure SHALL be modular, allowing for easy updates or feature additions (e.g., changing the notification provider).</li>
    </ul>
