
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
def show():
    st.title('Co benefit estimation')

    st.header("Economic impact of performance-based structural fire design")

    with st.sidebar:
        # Set up the part for user input file
        if "alter_design" in st.session_state:
            alter_design = st.session_state.alter_design
        else:
            alter_design = []





        st.markdown("## **User Input Parameter**")

        option_analysis_type = st.session_state.option_analysis_type
        if st.checkbox("Reset to default parameter (Co-benefit)",value=False):
            option_analysis_type='Start a new analysis'
            st.write('**The restored input parameter would not be applied**')



        rent_loss_selection = st.checkbox("run the rent loss analysis",value=True)
        rent_loss = 0
        rent_loss_alt = 0

        if rent_loss_selection:
            building_parameter_original = st.session_state.building_parameter_original
            Affect_area = building_parameter_original['Total area'][0]

            if option_analysis_type == 'Start a new analysis':
                Unit_rent_loss_saved = 3.60
                number_crew_saved = 2
                Cure_time_saved=72
                per_rented_saved=0.5
            elif option_analysis_type == 'Load session variables':
                if 'rent_estimation_related' in st.session_state:
                    rent_estimation_related = st.session_state.rent_estimation_related
                    Unit_rent_loss_saved = rent_estimation_related.at[
                        0, 'Unit rent rate']
                    number_crew_saved = rent_estimation_related.at[
                        0, 'Number of crew needed']
                    Cure_time_saved = rent_estimation_related.at[
                        0, 'Cure time needed']
                    per_rented_saved = rent_estimation_related.at[
                        0, 'Percentage affected']
                else:
                    Unit_rent_loss_saved = 3.60
                    number_crew_saved = 2
                    Cure_time_saved=72
                    per_rented_saved=0.5

                if 'indirect_damage_alt' in st.session_state:
                    indirect_damage_alt = st.session_state.indirect_damage_alt
                    indirect_damage_loss_alt_saved = indirect_damage_alt.at[
                        0, 'Indirect damage loss alt.']
                else:
                    indirect_damage_loss_alt_saved = 0




            # labor_hour_unit = st.number_input("Input labor hour needed for sq.ft fire protection")
            Unit_rent_loss = st.number_input("Input rent rate month per sq.ft", value=Unit_rent_loss_saved)
            number_crew = st.number_input("Input number of crew G-2 working on applying fire protection on steelwork",
                                          value=number_crew_saved, step=1)
            Cure_time = st.number_input("Input hours needed to cure the fire protection on steelwork (hr)", value=Cure_time_saved,
                                        step=1)
            per_rented=st.number_input("Input the percentage of area that has been rented",
                                          value=per_rented_saved)
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
                Cobenefits_value_alt = 0


        st.write('---')
        cobenefits_method = st.selectbox(
            'How would you like to define other potential co-benefit',
            ('input own value','Default method' ))
        Cobenefits_value=0
        if cobenefits_method == 'Default method':
            st.write("you select default method")
        if cobenefits_method == 'input own value':
            Cobenefits_value = st.number_input("Input co-benefits")

        if alter_design:
            if cobenefits_method == 'Default method':
                st.write("you select default method")
            if cobenefits_method == 'input own value':
                Cobenefits_value_alt = st.number_input("Input co-benefits (alt.)")


    with st.container():
        st.subheader('Results')
        st.write("---")
        data = {
            'rent loss': [int(rent_loss)],
            'Cobenefit': [Cobenefits_value],
        }
        Cobenefits_value_df = pd.DataFrame(data)





        if rent_loss_selection:
            data = {
                'Unit rent rate': [Unit_rent_loss],
                'Number of crew needed': [number_crew],
                'Cure time needed': [Cure_time],
                'Percentage affected': [per_rented],
            }
            rent_estimation_related = pd.DataFrame(data)
            st.session_state.rent_estimation_related = rent_estimation_related  # Attribute API


        col1, col2 = st.columns(2)
        with col1:
            st.write("**Results for reference design**")

            st.dataframe(Cobenefits_value_df, use_container_width=True, hide_index=True)
            st.session_state.Cobenefits_value_df = Cobenefits_value_df  # Attribute API
        if alter_design:
            with col2:
                st.write("**Results for alternative design**")
                data = {
                    'rent loss': [int(rent_loss_alt)],
                    'Cobenefit': [Cobenefits_value_alt],
                }
                Cobenefits_value_alt_df = pd.DataFrame(data)

                st.dataframe(Cobenefits_value_alt_df, use_container_width=True, hide_index=True)
                st.session_state.Cobenefits_value_df_alt = Cobenefits_value_alt_df  # Attribute API


