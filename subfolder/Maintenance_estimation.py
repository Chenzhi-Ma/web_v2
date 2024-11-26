
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
def show():
    st.title('Maintenance estimation')


    st.header("Economic impact of performance-based structural fire design")

    with st.sidebar:
        st.markdown("## **User Input Parameter**")
        study_year_saved=50
        maintenance_cost_annually_percentage_saved=3.00
        discount_rate_saved=3.00
        maintenance_cost_annually_percentage_saved_alt=3.00
        option_analysis_type = st.session_state.option_analysis_type


        if st.checkbox("Reset to default parameter (Maintenance)",value=False):
            option_analysis_type='Start a new analysis'
            st.write('**The restored input parameter would not be applied**')




        if option_analysis_type == 'Load session variables':
            if 'maintenance_input_original' in st.session_state:
                maintenance_input_original = st.session_state.maintenance_input_original
                maintenance_cost_annually_percentage_saved=maintenance_input_original.at[0, 'Percentage as initial construction cost']
                discount_rate_saved=maintenance_input_original.at[0, 'Input the discount rate']
                study_year_saved=maintenance_input_original.at[0, 'Study year']
            if 'maintenance_input_alt' in st.session_state:
                maintenance_input_alt = st.session_state.maintenance_input_alt
                maintenance_cost_annually_percentage_saved_alt = maintenance_input_alt.at[
                    0, 'Percentage as initial construction cost for alt.']

        study_year = st.number_input("Input study year of the building", value=study_year_saved)
        maintenance_cost_method = st.selectbox(
            'How would you like to define maintenance cost',
            ('Constant percentage of total construction cost', 'input own value with respected to year'))

        if maintenance_cost_method == 'Constant percentage of total construction cost':
            maintenance_cost_annually_percentage = st.number_input("Input percentage as initial construction cost",value=maintenance_cost_annually_percentage_saved)/100
            discount_rate = st.number_input("Input the discount rate",value=discount_rate_saved)/100
            #study_year=st.number_input("Input the study year (building lifetime)",value=50, step=1)


        if maintenance_cost_method == 'Input own value with respected to year':
            uploaded_file_maintenance = st.file_uploader(
                "Choose a file with maintenance cost and year (value in future)")

        #alter_design = st.checkbox('Do you want to get maintenance cost for alternative design?')
        st.markdown("**parameters for alternative design**")
        #alter_design = st.checkbox('Do you want to get damage cost value for alternative design?')

        if "alter_design" in st.session_state:
            alter_design = st.session_state.alter_design
        else:
            alter_design=[]

        if alter_design:
            if maintenance_cost_method == 'Constant percentage of total construction cost':
                maintenance_cost_annually_percentage_alt = st.number_input("Input percentage as initial construction cost (alt.)",
                                                                           value=maintenance_cost_annually_percentage_saved_alt)/100
            if maintenance_cost_method == 'input own value with respected to year':
                uploaded_file_maintenance = st.file_uploader(
                    "Choose a file with maintenance cost and year (value in future)")


    with st.container():
        st.subheader('Results')
        st.write("---")

        data = {
            'Percentage as initial construction cost': [maintenance_cost_annually_percentage*100],
            'Input the discount rate': [discount_rate*100],
            'Study year': [study_year],
        }
        maintenance_input_original = pd.DataFrame(data, index=[0, 1])
        st.session_state.maintenance_input_original = maintenance_input_original  # Attribute API

        #st.write("bar chart, maintenance_cost with respected to year")
        construction_cost_df = st.session_state.construction_cost_df
        CI = construction_cost_df['Floor'][0] #+ construction_cost_df['Column'][0]
        maintenance_cost_total=CI*maintenance_cost_annually_percentage/discount_rate*(1-np.exp(-discount_rate*study_year))
        data = {
            'Maintenance cost': [int(maintenance_cost_total)],
        }
        Maintenance_cost_df = pd.DataFrame(data)


        col1, col2 = st.columns(2)
        with col1:
            st.write("**Results for reference design**")

            st.dataframe(Maintenance_cost_df, use_container_width=True, hide_index=True)
            st.session_state.Maintenance_cost_df = Maintenance_cost_df  # Attribute API

        if alter_design:
            with col2:
                st.write("**Results for alternative design**")
                construction_cost_df_alt = st.session_state.construction_cost_df_alt
                CI_alt = construction_cost_df_alt['Floor'][0] #+ construction_cost_df_alt['Column'][0]
                maintenance_cost_total_alt = CI_alt * maintenance_cost_annually_percentage_alt/ discount_rate * (
                            1 - np.exp(-discount_rate * study_year))
                data = {
                    'Maintenance cost': [int(maintenance_cost_total_alt)],
                }
                maintenance_cost_total_alt = pd.DataFrame(data)
                st.dataframe(maintenance_cost_total_alt, use_container_width=True, hide_index=True)
                st.session_state.maintenance_cost_total_alt = maintenance_cost_total_alt  # Attribute API

                data = {
                    'Percentage as initial construction cost for alt.': [maintenance_cost_annually_percentage_alt*100],
                }
                maintenance_input_alt = pd.DataFrame(data, index=[0, 1])
                st.session_state.maintenance_input_alt = maintenance_input_alt  # Attribute API




