
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
st.set_page_config(page_title="Construction cost estimation")


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

# Import the necessary packages
import streamlit as st
import pandas as pd

# Set up the header
st.header("Economic impact of performance-based structural fire design")
with st.sidebar:
    # Set up the part for user input file
    st.markdown("## **User Input Parameter**")
    BT = st.number_input("Input Building type", value=1, step=1)

with st.container():
    st.subheader('Results')
    st.write("---")

    with st.expander('Database Summary'):
        st.write("Building information summary")
        bound = [0, 20, 35, 60, 70, 85, 95, 120, 130]
        low_limit = bound[BT-1]
        up_limit = bound[BT]
        Building_informaiton_df = pd.DataFrame(building_information_ori[low_limit:up_limit,[0,1,2,4,5,6,8,11,12]],
                                               columns=['Index','Area (sq.ft)', '# story', 'Total cost ($)', 'sq.ft cost ($)','IBC fire type'
                                                        ,'Building type','beam fire rating','column fire rating'])
        pd.set_option('display.float_format', '{:.2f}'.format)
        st.dataframe(data = Building_informaiton_df,use_container_width=True,hide_index=True)
        st.write("---")
        st.write("Fire service cost summary")
        Fire_service_cost_df = pd.DataFrame(building_information_ori[low_limit:up_limit,[0,19,20,21,22,23,24,25]],
                                            columns=['Index','Floor','Column','Partition','Sprinkler','Fire pump','Alarm','Ceiling'])
        pd.set_option('display.float_format', '{:.2f}'.format)
        st.dataframe(data = Fire_service_cost_df,use_container_width=True,hide_index=True)

    st.write("---")
    st.subheader('Fire protection cost multiplier summary')
    # columns = ["Floor system", "Column"]
    columns = ['Floor system','Column','Partition','Sprinkler','Fire pump','Alarm systems','ceiling']
    chartdata=pd.DataFrame(proportion_ori[low_limit:up_limit, 0:7],
                           columns = ['Floor system','Column','Partition','Sprinkler','Fire pump','Alarm systems','ceiling'])
    st.bar_chart(chartdata, width=0, height=0)

    chartdata=pd.DataFrame(proportion_ori[:, 0:7],
                           columns = ['Floor system','Column','Partition','Sprinkler','Fire pump','Alarm systems','ceiling'])

    st.bar_chart(chartdata, width=0, height=0)
    st.write("---")
    st.subheader('Fire protection cost value summary')
    chartdata_value=pd.DataFrame(costdetails_ori[low_limit:up_limit, 0:7],
                                 columns = ['Floor system','Column','Partition','Sprinkler','Fire pump','Alarm systems','ceiling'])
    st.bar_chart(chartdata_value, width=0, height=0)

    chartdata_value=pd.DataFrame(costdetails_ori[:, 0:7],
                                 columns = ['Floor system','Column','Partition','Sprinkler','Fire pump','Alarm systems','ceiling'])
    st.bar_chart(chartdata_value, width=0, height=0)

