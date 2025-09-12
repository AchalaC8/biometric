import pandas as pd
import matplotlib.pyplot as plt
import zipfile,os
bio_zip=zipfile.ZipFile("ac_bio","w")
j=1
for i in os.listdir():
    if(i.endswith('.csv')):
        print("Day",j,"analysis")
        a=pd.read_csv(i)
    
        print('Total students')
        print(len(a))
        print('Count of Present vs Not Present')
        print(a['Status'].value_counts())

        print('Students per floor')
        print(a['Floor'].value_counts())

        print('Students per room')
        print(a['Room No.'].value_counts())
        print("\n\n\n")
        j+=1
        a['Status'].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'lightcoral'])
        plt.title('Overall Attendance')
        plt.ylabel('')
        plt.show()


input()
