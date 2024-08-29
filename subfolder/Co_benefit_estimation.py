
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
def show():
    st.title('Co-benefit estimation')

    st.header("Economic impact of performance-based structural fire design")

    fragility_parameter_original = st.session_state.fragility_parameter_original
    building_parameter_original = st.session_state.building_parameter_original

    df_cost_df=st.session_state.df_cost_cci
    Affect_area = df_cost_df['Total floor area (thousand sq.ft)'][0]*1000

    Compartment_area_saved = fragility_parameter_original.at[0, 'Estimated area of the fire compartment']
    Compartment_num=round(Affect_area/Compartment_area_saved)

    df_cci = st.session_state.df_cci

    cci_total = df_cci['CCI - Other Components'][0]
    cci_fire_protection = df_cci['CCI - Fire Protection Total'][0]
    print(cci_total, 1234)



    Severe_fire_pro=fragility_parameter_original.at[0,'Probability of severe fire']
    study_year = fragility_parameter_original.at[0,'Study year']

    if "environment_impact" in st.session_state:
        environment_impact = st.session_state.environment_impact
    else:
        environment_impact = []

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

        rent_loss_selection = st.checkbox("Run the rent loss analysis",value=True)
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

            print(total_labor_hour,rent_loss)

            # alter_design = st.checkbox('Do you want to get indirect damage cost value for alternative design?')
            #st.markdown("**parameters for alternative design**")
            # alter_design = st.checkbox('Do you want to get damage cost value for alternative design?')

        uploaded_file_cost=st.session_state.uploaded_file_cost
        value = np.asarray(uploaded_file_cost.iloc[2:5, 33])
        SFRM_volume = value
        value = np.asarray(uploaded_file_cost.iloc[2, 31])
        beam_unit_material_cost = float(value)
        GWP_material = np.asarray(uploaded_file_cost.iloc[7:11, 25:27])
        GWP_density = np.asarray(uploaded_file_cost.iloc[7:11, 27])
        beam_sfrm_unit_volume=float(SFRM_volume[0])


        construction_cost_df_updated = st.session_state.construction_cost_df
        fire_parameter_original = st.session_state.fire_parameter_original   # Attribute API
        fire_material_floor = fire_parameter_original.at[0,'Beam fire protection material']
        fire_material_column = fire_parameter_original.at[0, 'Column fire protection material']
        beam_f_density=float(GWP_density[fire_material_floor-1])
        column_f_density=float(GWP_density[fire_material_column-1])
        beam_f_gwp=int(GWP_material[fire_material_floor-1,1])
        column_f_gwp=int(GWP_material[fire_material_column-1,1])

        if environment_impact:
            unit_cost_data=st.session_state.uploaded_file_cost
            environmental_impact_table = np.asarray(unit_cost_data.iloc[2:25, 38:41], float)
            environmental_impact_name = np.asarray(unit_cost_data.iloc[2:25, 36])
            environmental_impact_unit = np.asarray(unit_cost_data.iloc[2:25, 37])
            GWP_analysis_type = st.selectbox(
                "Analysis type",
                ('Default value','Input own value'),
            )
            if GWP_analysis_type == 'Input own value':
                col1, col2 = st.columns(2)
                with col1:
                    beam_f_density = st.number_input("Input beam fire protection density pcf", value=20)
                with col2:
                    column_f_density = st.number_input("Input column fire protection density pcf", value=20)

                col1, col2 = st.columns(2)
                with col1:
                    beam_f_gwp = st.number_input("Input beam fire protection global warming (kg CO2 eq) per 1000kg unit material", value=500)
                with col2:
                    column_f_gwp = st.number_input("Input column fire protection global warming (kg CO2 eq) per 1000kg unit material", value=500)



            total_sfrm_cost_original = construction_cost_df_updated.at[0, 'Floor']/cci_fire_protection/beam_unit_material_cost*beam_sfrm_unit_volume*\
                                       beam_f_density*0.4536/1000*beam_f_gwp+\
                                       construction_cost_df_updated.at[0, 'Column']/cci_fire_protection/beam_unit_material_cost*beam_sfrm_unit_volume*\
                                       column_f_density*0.4536/1000*column_f_gwp

            ei_cost = st.session_state.ei_cost
            content_cost = ei_cost['Average content loss per sever fire'][0]
            steel_cost = ei_cost['Average steel loss per sever fire'][0]
            concrete_cost = ei_cost['Average concrete loss per sever fire'][0]



            CPI_inflation_till_now = st.number_input("Input the CPI inflation from 2013 till now(https://www.bls.gov/data/inflation_calculator.htm)", value=1.36)

            content_ei=content_cost/cci_total/CPI_inflation_till_now*environmental_impact_table[:,0]
            steel_ei=steel_cost/cci_total/CPI_inflation_till_now*environmental_impact_table[:,1]
            concrete_ei=concrete_cost/cci_total/CPI_inflation_till_now*environmental_impact_table[:,2]

            namep1 = pd.DataFrame({
                'Impact name': [environmental_impact_name]
            })

            namep2 = pd.DataFrame({
                'Unit': [environmental_impact_unit]
            })
            row_names = namep1['Impact name'][0] + '-' + namep2['Unit'][0]
            Total_envir=np.array(content_ei,dtype=int)+np.array(steel_ei,dtype=int)+np.array(concrete_ei,dtype=int)
            environmental_impact_df = pd.DataFrame({
                'Total(Per severe fire)': Total_envir,
                'Total(Annual)': np.array(Total_envir * Severe_fire_pro * 1e-9 * Affect_area,dtype=int),
                'Total(Study year)': np.array(Total_envir * Severe_fire_pro * 1e-9 * Affect_area * study_year,dtype=int),
                'Content': np.array(content_ei,dtype=int),
                'Steel': np.array(steel_ei,dtype=int),
                'Conrete': np.array(concrete_ei,dtype=int)
            }, index=row_names)

            st.session_state.environmental_impact_df=environmental_impact_df


        if alter_design:
            st.markdown('---')
            st.markdown('### Parameter for alternative design:')
            number_crew_reinf = st.number_input("Input number of Rodmen (reinf.) ",
                                                value=8, step=1)
            construction_cost_df_alt = st.session_state.construction_cost_df_alt
            extra_cost_df = st.session_state.extra_cost_df
            extra_labor = extra_cost_df['Extra labor alt. (hour)'][0]
            total_labor_hour_alt = construction_cost_df_alt['Floor'][2] + construction_cost_df_alt['Column'][2]
            rent_loss_alt = (total_labor_hour_alt / number_crew + Cure_time+extra_labor*2/number_crew_reinf) * Unit_rent_loss / 24 / 30 * Affect_area*per_rented


            Cobenefits_value_alt = 0
            construction_cost_df_updated_alt = st.session_state.construction_cost_df_alt
            fire_parameter_alt = st.session_state.fire_parameter_original   # Attribute API
            fire_material_floor_alt = fire_parameter_alt.at[0,'Beam fire protection material']
            fire_material_column_alt = fire_parameter_alt.at[0, 'Column fire protection material']

            beam_f_density_alt = float(GWP_density[fire_material_floor_alt - 1])
            column_f_density_alt = float(GWP_density[fire_material_column_alt - 1])
            beam_f_gwp_alt = int(GWP_material[fire_material_floor_alt - 1, 1])
            column_f_gwp_alt = int(GWP_material[fire_material_column_alt - 1, 1])

            if environment_impact:
                if GWP_analysis_type == 'Input own value':
                    col1, col2 = st.columns(2)
                    with col1:
                        beam_f_density_alt = st.number_input("Input beam fire protection density for alt. pcf", value=20)
                    with col2:
                        column_f_density_alt = st.number_input("Input column fire protection density for alt. pcf", value=20)
                    col1, col2 = st.columns(2)
                    with col1:
                        beam_f_gwp_alt = st.number_input("Input beam fire protection global warming (kg CO2 eq) per 1000kg unit material for alt.", value=500)
                    with col2:
                        column_f_gwp_alt = st.number_input("Input column fire protection global warming (kg CO2 eq) per 1000kg unit material for alt.", value=500)


                total_sfrm_cost_alt = construction_cost_df_updated_alt.at[0, 'Floor']/cci_fire_protection/beam_unit_material_cost*beam_sfrm_unit_volume*\
                                           beam_f_density_alt*0.4536/1000*beam_f_gwp_alt+\
                                           construction_cost_df_updated_alt.at[0, 'Column']/cci_fire_protection/beam_unit_material_cost*beam_sfrm_unit_volume*\
                                           column_f_density_alt*0.4536/1000*column_f_gwp_alt

                ei_cost_alt = st.session_state.ei_cost_alt

                content_cost_alt = ei_cost_alt['Average content loss per sever fire'][0]
                steel_cost_alt = ei_cost_alt['Average steel loss per sever fire'][0]
                concrete_cost_alt = ei_cost_alt['Average concrete loss per sever fire'][0]



                content_ei_alt = content_cost_alt /cci_total / CPI_inflation_till_now * environmental_impact_table[:, 0]
                steel_ei_alt = steel_cost_alt /cci_total/ CPI_inflation_till_now * environmental_impact_table[:, 1]
                concrete_ei_alt = concrete_cost_alt /cci_total/ CPI_inflation_till_now * environmental_impact_table[:, 2]

                namep1 = pd.DataFrame({
                    'Impact name': [environmental_impact_name]
                })

                namep2 = pd.DataFrame({
                    'Unit': [environmental_impact_unit]
                })
                row_names = namep1['Impact name'][0] + '-' + namep2['Unit'][0]
                Total_envir_alt=np.array(content_ei_alt, dtype=int) + np.array(steel_ei_alt, dtype=int) + np.array(concrete_ei_alt,dtype=int)


                environmental_impact_df_alt = pd.DataFrame({
                    'Total(Per severe fire)': Total_envir_alt,
                    'Total(Annual)': np.array(Total_envir_alt*Severe_fire_pro * 1e-9 * Affect_area,dtype=int),
                    'Total(Study year)': np.array(Total_envir_alt * Severe_fire_pro * 1e-9 * Affect_area * study_year,dtype=int),
                    'Content': np.array(content_ei_alt, dtype=int),
                    'Steel': np.array(steel_ei_alt, dtype=int),
                    'Conrete': np.array(concrete_ei_alt, dtype=int)
                }, index=row_names)

                st.session_state.environmental_impact_df_alt = environmental_impact_df_alt


        st.write('---')
        cobenefits_method = st.selectbox(
            'How would you like to define other potential co-benefit',
            ('Default method' ,'input own value'))
        Cobenefits_value=0
        if cobenefits_method == 'Default method':
            st.write("you select default method")
            Cobenefits_value = 0
        if cobenefits_method == 'input own value':
            Cobenefits_value = st.number_input("Input co-benefits")

        if alter_design:

            if cobenefits_method == 'Default method':
                st.write("you select default method")
                Cobenefits_value_alt=0
            if cobenefits_method == 'input own value':
                Cobenefits_value_alt = st.number_input("Input co-benefits (alt.)")


    with st.container():
        st.subheader('Results')
        st.write("---")
        data = {
            'Rent loss': [int(rent_loss)],
            'Cobenefit': [int(Cobenefits_value)],
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
            if environment_impact:
                data_sfrm_co2 = pd.DataFrame ({
                    'Greenhouse gas(CO_2) from SFRM (kg)': [int(total_sfrm_cost_original)],
                })
                st.dataframe(data_sfrm_co2,hide_index=True)
                st.session_state.co2_sfrm = data_sfrm_co2  # Attribute API
        if environment_impact:
            st.write("**Full environment impact for reference design**")
            st.dataframe(environmental_impact_df, use_container_width=True, hide_index=False)


        if alter_design:
            with col2:
                st.write("**Results for alternative design**")
                data = {
                    'Rent loss': [int(rent_loss_alt)],
                    'Cobenefit': [int(Cobenefits_value_alt)],

                }
                Cobenefits_value_alt_df = pd.DataFrame(data)

                st.dataframe(Cobenefits_value_alt_df, use_container_width=True, hide_index=True)
                st.session_state.Cobenefits_value_df_alt = Cobenefits_value_alt_df  # Attribute API
                if environment_impact:
                    data_sfrm_co2_alt = {
                        'Greenhouse gas(CO_2) from SFRM alt. (kg)': [int(total_sfrm_cost_alt)]
                    }
                    data_sfrm_co2_alt=pd.DataFrame(data_sfrm_co2_alt)
                    st.dataframe(data_sfrm_co2_alt,hide_index=True)
                    st.session_state.co2_sfrm_alt = data_sfrm_co2_alt  # Attribute API

            if environment_impact:
                st.write("**Full environment impact for alternative design**")
                st.dataframe(environmental_impact_df_alt, use_container_width=True, hide_index=False)


