import pandas as pd
import matplotlib.pyplot as plt

a=pd.read_csv(input("enter the file name")+".csv")

print('Total students')
print(len(a))
print('Count of Present vs Not Present')
print(a['Status'].value_counts())

print('Students per floor')
print(a['Floor'].value_counts())

print('Students per room')
print(a['Room No.'].value_counts())

a['Status'].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'lightcoral'])
plt.title('Overall Attendance')
plt.ylabel('')
plt.show()

input()

