
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
def show():
    st.title('Indirect damage estimation')


    st.header("Economic impact of performance-based structural fire design")

    with st.sidebar:
        # Set up the part for user input file
        st.markdown("## **User Input Parameter**")
        option_analysis_type = st.session_state.option_analysis_type

        if st.checkbox("Reset to default parameter (Indirect damage)",value=False):
            option_analysis_type = 'Start a new analysis'
            st.write('**The restored input parameter would not be applied**')


        indirect_damage_method = st.selectbox(
            'Method to calculate indirect damage',
            ('Input own value','Default method'))

        if option_analysis_type == 'Start a new analysis':
            indirect_damage_loss_saved=0
            indirect_damage_loss_alt_saved = 0
        elif option_analysis_type == 'Load session variables':
            if 'indirect_damage_original' in st.session_state:
                indirect_damage_original = st.session_state.indirect_damage_original
                indirect_damage_loss_saved = indirect_damage_original.at[
                    0, 'Indirect damage loss']
            else:
                indirect_damage_loss_saved=0

            if 'indirect_damage_alt' in st.session_state:
                indirect_damage_alt = st.session_state.indirect_damage_alt
                indirect_damage_loss_alt_saved = indirect_damage_alt.at[
                    0, 'Indirect damage loss alt.']
            else:
                indirect_damage_loss_alt_saved=0


        if indirect_damage_method == 'Input own value':
           indirect_damage_loss=st.number_input("Input indirect damage loss",value=indirect_damage_loss_saved)

        building_parameter_original = st.session_state.building_parameter_original
        if indirect_damage_method == 'Default method':
            print(1)
            # alter_design = st.checkbox('Do you want to get indirect damage cost value for alternative design?')
        st.markdown("**Parameters for alternative design**")
        #alter_design = st.checkbox('Do you want to get damage cost value for alternative design?')

        if "alter_design" in st.session_state:
            alter_design = st.session_state.alter_design
        else:
            alter_design=[]




        if alter_design:

            if indirect_damage_method == 'Input own value':
                indirect_damage_loss_alt = st.number_input("Input indirection damage loss (alt.)",value=indirect_damage_loss_alt_saved)
            if indirect_damage_method == 'Considering the rent loss (alt.)':
                print(1)



    with st.container():

        st.subheader('Results')
        st.write("---")
        data = {
            'indirect damage loss': [int(indirect_damage_loss)],
        }
        indirect_damage_loss_df = pd.DataFrame(data)

        data = {
            'Indirect damage loss': [int(indirect_damage_loss)],
        }
        indirect_damage_original = pd.DataFrame(data)
        st.session_state.indirect_damage_original = indirect_damage_original  # Attribute API

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

            data = {
                'Indirect damage loss alt.': [int(indirect_damage_loss)],
            }
            indirect_damage_alt = pd.DataFrame(data)
            st.session_state.indirect_damage_alt = indirect_damage_alt  # Attribute API

