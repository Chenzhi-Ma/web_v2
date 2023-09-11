
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
st.set_page_config(page_title="ASTM index calculation")


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

with st.sidebar:
    st.markdown("## **User Input Parameter**")
    astm_index_method = st.selectbox(
        'How would you like to input cost value (present value)',
        ('Based on previous data','type value', 'upload file with given format'))

    if astm_index_method == 'Based on previous data':
        construction_cost_df=st.session_state.construction_cost_df
        CI=construction_cost_df['Floor'][0]+construction_cost_df['Column'][0]
        direction_damage_loss=st.session_state.direction_damage_loss
        DD=direction_damage_loss['Study year loss']
        indirect_damage_loss_df=st.session_state.indirect_damage_loss_df
        ID=indirect_damage_loss_df['indirect_damage_loss']
        Maintenance_cost_df=st.session_state.Maintenance_cost_df   # Attribute API
        CM=Maintenance_cost_df['Maintenance_cost']
        Cobenefits_value_df=st.session_state.Cobenefits_value_df    # Attribute API
        CB=Cobenefits_value_df['Cobenefits_value']
        pvlcc = CI + DD + ID+CM - CB





    if astm_index_method == 'type value':

        CI_alt = st.number_input("Input initial construction cost for alternative design")
        CI_ref = st.number_input("Input initial construction cost for reference design")
        DD_alt = st.number_input("Input direct damage loss for alternative design")
        DD_ref = st.number_input("Input direct damage loss cost for reference design")
        ID_alt = st.number_input("Input indirect damage loss for alternative design")
        ID_ref = st.number_input("Input indirect damage loss cost for reference design")
        CM_alt = st.number_input("Input maintenance cost for alternative design")
        CM_ref = st.number_input("Input maintenance cost  for reference design")
        CB_alt = st.number_input("Input co-benefit for alternative design")
        CB_ref = st.number_input("Input co-benefit cost for reference design")

        net_b = DD_ref + ID_ref-CB_ref - DD_alt - ID_alt + CB_alt
        net_c = -CI_ref - CM_ref + CI_alt + CM_alt
        pvlcc = [0, 0]  # Initialize the list

        pvlcc[0] = CI_ref + CM_ref + DD_ref + ID_ref - CB_ref
        pvlcc[1] = CI_ref + CM_ref + DD_alt + ID_alt - CB_alt

        bcr = net_b / net_c
        pnv = net_b - net_c


    if astm_index_method == 'upload file with given format':
        astm_index_method_file = st.file_uploader(
            "Choose a file with all the cost data")

with st.container():
    st.subheader('Results')
    st.write("---")
    st.write("BCR,LCC,PNV of provided design values")


    st.session_state.PVLCC = pvlcc  # Attribute API
    st.markdown("### present value life cycle cost of given fire design")
    data = {
        "PVLCC": [pvlcc],
    }
    PVLCC_df = pd.DataFrame(data)
    st.dataframe(pvlcc, use_container_width=True, hide_index=True)

