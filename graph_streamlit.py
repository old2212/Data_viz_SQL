import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import RendererAgg
import time
from datetime import datetime

#connect to the SQL database
connection = sqlite3.connect('bce.db')


## QUESTION 2

#query tables : Which percentage of the companies are under which Status?
sql_query_Q2 = pd.read_sql_query ('''
                               SELECT count(EnterpriseNumber), Status
                               FROM enterprise
                               ''', connection)
#Create dataframe
df_Q2 = pd.DataFrame(sql_query_Q2)
score_active_ent = df_Q2.iat[0,0]

#Display the number of active company

st.markdown(f"<h1 style='text-align: center; color: blue;'>The number of active enterprise is :  </h1>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align: center; color: lightblue;'>{score_active_ent} </h1>", unsafe_allow_html=True)


## QUESTION 1

#connect to the SQL database
connection = sqlite3.connect('bce.db')
#query tables
sql_query_Q1T1 = pd.read_sql_query ('''
                                SELECT count(EnterpriseNumber) as Total_Enterprise, Description
                                FROM enterprise
                                INNER JOIN code ON enterprise.JuridicalForm = code.Code
                                WHERE code.Language = 'FR' AND code.Category = 'JuridicalForm'
                                Group by Description
                                Order by count(EnterpriseNumber) DESC;
                                ''', connection)

#Create a dataframe 1 to prepare graph input
df_Q1T1 = pd.DataFrame(sql_query_Q1T1, columns = ['Total_Enterprise', 'Description'])

df_Q1T1_most_frequent = df_Q1T1.iloc[:6,:]
data = [{'Description':'Autres','Total_Enterprise':df_Q1T1['Total_Enterprise'][6:].sum()}]
data_df = pd.DataFrame(data)
df_Q1T1 = pd.concat([df_Q1T1_most_frequent, data_df])

# Pie chart, where the slices will be ordered and plotted counter-clockwise:
fig1, ax1 = plt.subplots()
ax1.pie(df_Q1T1['Total_Enterprise'], labels = df_Q1T1['Description'], autopct='%1.1f%%')
# plt.show()
st.pyplot(fig1)

### Question 3

#query tables : Which percentage of the companies are which type of entreprise?
sql_query_Q3T1 = pd.read_sql_query ('''
                               SELECT count(EnterpriseNumber), TypeOfEnterprise
                               FROM enterprise
                               Group by TypeOfEnterprise
                               ''', connection)

sql_query_Q3T2 = pd.read_sql_query ('''
                               SELECT *
                               FROM code
                               WHERE Language=="FR" AND Category=="TypeOfEnterprise"
                               ''', connection)

df_Q3T1 = pd.DataFrame(sql_query_Q3T1)
df_Q3T1.rename(columns = {'TypeOfEnterprise':'Code'}, inplace = True)
df_Q3T2 = pd.DataFrame(sql_query_Q3T2)
df_Q3 = pd.merge(df_Q3T1, df_Q3T2, on='Code')
df_Q3 = df_Q3[["count(EnterpriseNumber)", "Description"]]

# Pie chart, where the slices will be ordered and plotted counter-clockwise:
labels = df_Q3["Description"]
sizes = df_Q3["count(EnterpriseNumber)"]

fig3, ax3 = plt.subplots()
ax3.pie(sizes, labels=labels, autopct='%1.1f%%',
        shadow=False, startangle=90)
ax3.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

st.pyplot(fig3)

### QUESTION 4

df_Q4M2008 = pd.read_csv("mapping_sector_2008.csv")
sql_query_Q4T1 = pd.read_sql_query ('''
                               SELECT EnterpriseNumber, StartDate, NaceCode
                               FROM enterprise
                               INNER JOIN activity ON enterprise.EnterpriseNumber = activity.EntityNumber
                               WHERE NaceVersion==2008
                               ''',connection)

df_Q4T1 = pd.DataFrame(sql_query_Q4T1)
df_Q4T1["NaceCode"] = df_Q4T1.NaceCode.str[:2].astype(int)
# df_Q4T1["StartDate"] = df_Q4T1.StartDate.str[:10].replace('-','', regex=True)
df_Q4M2008 = pd.read_csv("mapping_sector_2008.csv")
sql_query_Q4T1 = pd.read_sql_query ('''
                               SELECT EnterpriseNumber, StartDate, NaceCode
                               FROM enterprise
                               INNER JOIN activity ON enterprise.EnterpriseNumber = activity.EntityNumber
                               WHERE NaceVersion==2008
                               ''',connection)
#DATA CLEANING : FIrst two digit extract and age caclulation
df_Q4T1 = pd.DataFrame(sql_query_Q4T1)
df_Q4T1["NaceCode"] = df_Q4T1.NaceCode.str[:2].astype(int)

today = datetime.today()

df_Q4T1["StartDate"] = pd.to_datetime(df_Q4T1["StartDate"], errors='coerce')
df_Q4T1['age'] = df_Q4T1["StartDate"].apply(
               lambda x: today.year - x.year - 
               ((today.month, today.day) < (x.month, x.day)))

df_Q4M2008.code_sector.astype(int)
dict_M2008 = df_Q4M2008.set_index('code_sector').to_dict()['title_sector']
df_Q4T1["sector"] = df_Q4T1["NaceCode"].map(dict_M2008)
df_Q4T1 = df_Q4T1.groupby("sector").agg({"age":"mean"})
df_Q4T1= df_Q4T1.sort_values(by=['age'], inplace=True)

fig, ax = plt.subplots()
ax.bar(df_Q4T1['sector'], df_Q4T1['age'])
plt.xticks(rotation=30, ha='right')
st.pyplot(fig)