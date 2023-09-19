
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
st.set_page_config(page_title="Indirect damage estimation")


st.header("Economic impact of performance-based structural fire design")

with st.sidebar:
    # Set up the part for user input file
    st.markdown("## **User Input Parameter**")

    indirect_damage_method = st.selectbox(
        'Method to calculate indirect damage',
        ('Default method','input own value'))

    indirect_damage_loss=0
    if indirect_damage_method == 'input own value':
        indirect_damage_loss=st.number_input("Input indirect damage loss")

    building_basic_information = st.session_state.building_basic_information
    Affect_area = building_basic_information['Total area'][0]
    if indirect_damage_method == 'Default method':
        print(1)
        # alter_design = st.checkbox('Do you want to get indirect damage cost value for alternative design?')
    st.markdown("**parameters for alternative design**")
    #alter_design = st.checkbox('Do you want to get damage cost value for alternative design?')

    if "alter_design" in st.session_state:
        alter_design = st.session_state.alter_design
    else:
        alter_design=[]

    if alter_design:
        indirect_damage_loss_alt = 0
        if indirect_damage_method == 'input own value (alt.)':
            indirect_damage_loss_alt = st.number_input("Input indirection damage loss (alt.)")

        if indirect_damage_method == 'Considering the rent loss (alt.)':
            print(1)



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


