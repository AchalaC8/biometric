import pandas as pd
import matplotlib.pyplot as plt
import os
j=1
for i in os.listdir():
    if(i.endswith('.csv')):
        print("Day",j,"analysis")
        a=pd.read_csv(i)

        print('Count of Present vs Not Present')
        print(a['Status'].value_counts())

        print('Total students')
        print(len(a))

        print('Students per floor')
        print(a['Floor'].value_counts())

        print('Students per room')
        print(a['Room No.'].value_counts())

        j+=1
input()
