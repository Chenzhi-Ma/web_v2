
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
st.set_page_config(page_title="Maintenance estimation")


with open('database_ori_mat.pkl', 'rb') as f:
    database_ori_mat = pickle.load(f)
with open('totalcost_mat.pkl', 'rb') as f:
    totalcost_mat = pickle.load(f)
default_cost_file = 'unit_cost_data.csv'

# import the matlab file .mat, database_original.mat is a 1*1 struct with 7 fields, inlcude all the original data from 130 simulaitons
database_ori = database_ori_mat['database_original']

# get the detailed original value from rsmeans
costdetails_ori_mat = database_ori['costdetails']
costdetails_ori = costdetails_ori_mat[0, 0]

# the cost multiplier
proportion_ori_mat = database_ori['proportion']
proportion_ori = proportion_ori_mat[0, 0]

# import the building information, include the fire rating, floor area, building type, stories
building_information_ori_mat = database_ori['building_information']
# variable in different columns: 1floor area, 2story, 3perimeter, 4total cost, 5sq. cost, 6fire type in IBC, 7fire type index, 8building type,
# 9beam fire rating in rsmeans, 10column fire rating in rsmeans, 11 IBCbeam, 12 IBC column,
# 13 adjusted column cost,
# 14 adjusted column fire protection cost for 1h, 15 adjusted column fire protection cost for 2h, 16 adjusted column fire protection cost for 3h
building_information_ori = building_information_ori_mat[0, 0]

# the total cost,1 - 2 columns: total cost (original rsmeans value, without adjustment in floor system, column, fire rating), second column is sq.ft cost
# 3 - 4 columns: rsmeans value minus the floor system cost, column system cost
# 5 - 6 columns: value with adjusted floor system and columns, fire rating is based on IBC coding

totalcost_ori = totalcost_mat['totalcost_num']
    # define new vlue in the database



st.header("Economic impact of performance-based structural fire design")

construction_cost_df = st.session_state.construction_cost_df
CI = construction_cost_df['Floor'][0] + construction_cost_df['Column'][0]

with st.sidebar:
    st.markdown("## **User Input Parameter**")


    maintenance_cost_method = st.selectbox(
        'How would you like to define maintenance cost',
        ('Constant percentage of total construction cost', 'input own value with respected to year'))

    if maintenance_cost_method == 'Constant percentage of total construction cost':
        maintenance_cost_annually_percentage = st.number_input("Input percentage as initial construction cost",value=3.00)

    if maintenance_cost_method == 'input own value with respected to year':
        uploaded_file_maintenance = st.file_uploader(
            "Choose a file with maintenance cost and year (value in future)")
with st.container():
    st.subheader('Results')
    st.write("---")
    st.write("bar chart, maintenance_cost with respected to year")
    data = {
        'Maintenance_cost': [CI*maintenance_cost_annually_percentage/100],
    }
    Maintenance_cost_df = pd.DataFrame(data)
    st.dataframe(Maintenance_cost_df, use_container_width=True, hide_index=True)
    st.session_state.Maintenance_cost_df = Maintenance_cost_df  # Attribute API

