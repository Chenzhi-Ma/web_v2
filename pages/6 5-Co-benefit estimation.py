
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
st.set_page_config(page_title="Co-benefit estimation")

st.header("Economic impact of performance-based structural fire design")

with st.sidebar:
    # Set up the part for user input file
    if "alter_design" in st.session_state:
        alter_design = st.session_state.alter_design
    else:
        alter_design = []

    st.markdown("## **User Input Parameter**")
    rent_loss_selection = []
    rent_loss_selection = st.checkbox("run the rent loss analysis")
    rent_loss = 0
    rent_loss_alt = 0
    if rent_loss_selection:
        building_basic_information = st.session_state.building_basic_information
        Affect_area = building_basic_information['Total area'][0]

        # labor_hour_unit = st.number_input("Input labor hour needed for sq.ft fire protection")
        Unit_rent_loss = st.number_input("Input rent loss per month per sq.ft", value=0.005 * 24 * 30)
        number_crew = st.number_input("Input number of crew G-2 working on applying fire protection on steelwork",
                                      value=1, step=1)
        Cure_time = st.number_input("Input hours needed to cure the fire protection on steelwork (hr)", value=72,
                                    step=1)
        per_rented=st.number_input("Input the percentage of area that has been rented",
                                      value=0.50)
        #Affect_area = st.number_input("Input the affected area by the delayed construction schedule",
                                     # value=Affect_area)

        construction_cost_df = st.session_state.construction_cost_df
        total_labor_hour = construction_cost_df['Floor'][2] + construction_cost_df['Column'][2]
        rent_loss = (total_labor_hour / number_crew + Cure_time) * Unit_rent_loss / 24 / 30 * Affect_area*per_rented

        # alter_design = st.checkbox('Do you want to get indirect damage cost value for alternative design?')
        #st.markdown("**parameters for alternative design**")
        # alter_design = st.checkbox('Do you want to get damage cost value for alternative design?')
        if alter_design:

            construction_cost_df_alt = st.session_state.construction_cost_df_alt
            total_labor_hour_alt = construction_cost_df_alt['Floor'][2] + construction_cost_df_alt['Column'][2]
            rent_loss_alt = (total_labor_hour_alt / number_crew + Cure_time) * Unit_rent_loss / 24 / 30 * Affect_area*per_rented
            cobenefits_value_alt = 0



    st.write('---')
    cobenefits_method = st.selectbox(
        'How would you like to define other potential co-benefit',
        ('input own value','Default method' ))
    cobenefits_value=0
    if cobenefits_method == 'Default method':
        st.write("you select default method")
    if cobenefits_method == 'input own value':
        cobenefits_value = st.number_input("Input co-benefits")

    if alter_design:
        if cobenefits_method == 'Default method':
            st.write("you select default method")
        if cobenefits_method == 'input own value':
            cobenefits_value_alt = st.number_input("Input co-benefits (alt.)")


with st.container():
    st.subheader('Results')
    st.write("---")
    data = {
        'rent loss': [int(rent_loss)],
        'Cobenefit': [cobenefits_value],
    }
    cobenefits_value_df = pd.DataFrame(data)

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Results for reference design**")

        st.dataframe(cobenefits_value_df, use_container_width=True, hide_index=True)
        st.session_state.Cobenefits_value = Cobenefits_value_df  # Attribute API

    if alter_design:
        with col2:
            st.write("**Results for alternative design**")
            data = {
                'rent loss': [int(rent_loss_alt)],
                'Cobenefit': [cobenefits_value_alt],
            }
            cobenefits_value_alt_df = pd.DataFrame(data)

            st.dataframe(cobenefits_value_alt_df, use_container_width=True, hide_index=True)
            st.session_state.Cobenefits_value_alt = Cobenefits_value_alt_df  # Attribute API


