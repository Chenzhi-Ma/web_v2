
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
st.set_page_config(page_title="Indirect damage estimation")


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
    # Set up the part for user input file
    st.markdown("## **User Input Parameter**")

    indirect_damage_method = st.selectbox(
        'How would you like to define unit labor hour of fire protection',
        ('Considering the rent loss','input own value'))
    indirect_damage_loss=0
    if indirect_damage_method == 'input own value':
        indirect_damage_loss=st.number_input("Input indirection damage loss")

    building_basic_information = st.session_state.building_basic_information
    Affect_area = building_basic_information['Total area'][0]
    if indirect_damage_method == 'Considering the rent loss':
        #labor_hour_unit = st.number_input("Input labor hour needed for sq.ft fire protection")
        Unit_rent_loss = st.number_input("Input rent loss per month per sq.ft",value=0.005*24*30)
        number_crew=st.number_input("Input number of crew G-2 working on applying fire protection on steelwork",value=1,step=1)
        Cure_time = st.number_input("Input hours needed to cure the fire protection on steelwork (hr)",value=72,step=1)
        Affect_area = st.number_input("Input the affected area by the delayed construction schedule", value=Affect_area)

        construction_cost_df=st.session_state.construction_cost_df
        total_labor_hour=construction_cost_df['Floor'][2]+construction_cost_df['Column'][2]
        indirect_damage_loss=(total_labor_hour/number_crew+Cure_time)*Unit_rent_loss/24/30*Affect_area

    alter_design = st.checkbox('Do you want to get indirect damage cost value for alternative design?')
    if alter_design:
        indirect_damage_method = st.selectbox(
            'How would you like to define unit labor hour of fire protection',
            ( 'Considering the rent loss (alt.)','input own value (alt.)'))
        indirect_damage_loss_alt = 0
        if indirect_damage_method == 'input own value (alt.)':
            indirect_damage_loss_alt = st.number_input("Input indirection damage loss (alt.)")

        if indirect_damage_method == 'Considering the rent loss (alt.)':
            construction_cost_df_alt = st.session_state.construction_cost_df_alt
            total_labor_hour_alt = construction_cost_df_alt['Floor'][2] + construction_cost_df_alt['Column'][2]
            indirect_damage_loss_alt = (total_labor_hour_alt / number_crew + Cure_time) * Unit_rent_loss / 24 / 30 * Affect_area






with st.container():

    st.subheader('Results')
    st.write("---")
    data = {
        'indirect damage loss': [int(indirect_damage_loss)],
    }
    indirect_damage_loss_df = pd.DataFrame(data)




    col1, col2 = st.columns(2)
    with col1:
        st.write("**Results for reference design**")

        st.dataframe(indirect_damage_loss_df, use_container_width=True, hide_index=True)
        st.session_state.indirect_damage_loss_df = indirect_damage_loss_df  # Attribute API

    if alter_design:
        with col2:
            st.write("**Results for alternative design**")
            data = {
                'indirect damage loss': [int(indirect_damage_loss_alt)],
            }
            indirect_damage_loss_df_alt = pd.DataFrame(data)

            st.dataframe(indirect_damage_loss_df_alt, use_container_width=True, hide_index=True)
            st.session_state.indirect_damage_loss_df_alt = indirect_damage_loss_df_alt  # Attribute API


