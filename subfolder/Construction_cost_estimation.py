
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from io import StringIO

import json
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost,update_session_state
import matplotlib.pyplot as plt
def show():
    st.title('Construction cost estimation')

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

    def Modify_database():

        st.header("Economic impact of performance-based structural fire design")



        with (st.sidebar):

            st.markdown("## **User Input Parameters**")
            option_analysis_type = st.selectbox(
                "Analysis type",
                ('Load session variables','Start a new analysis'),
            )
            if option_analysis_type=='Start a new analysis':
                if st.button('clear all saved session state'):
                    keys_to_keep = ['path_for_save','shown_page','Current_page']
                    # Delete all session state variables except for the specified key(s)
                    for key in list(st.session_state.keys()):
                        if key not in keys_to_keep:
                            del st.session_state[key]

            st.session_state.option_analysis_type=option_analysis_type

            st.markdown("---")

            option_analysis_type = st.session_state.option_analysis_type

            if st.checkbox("Reset to default parameter (Construction cost)", value=False):
                option_analysis_type = 'Start a new analysis'
                st.write('**The restored input parameter would not be applied**')

            # Set up the input for Column Type selected by users
            if option_analysis_type == 'Start a new analysis':
                BI_saved = 1
            else:
                if 'BI' in st.session_state:
                    BI_saved=st.session_state.BI
                else:
                    BI_saved=1

            # BI = BI_saved
            BI = st.number_input("Input Building index (start from 1)",value=BI_saved, step=1)

            st.session_state.BI = BI  # Attribute API
            # Set up the basic non-editable building parameter
            building_index = BI
            Building_type = int(building_information_ori[building_index - 1][8])
            total_story = int(building_information_ori[building_index - 1][2])
            bound = [0, 20, 35, 60, 70, 85, 95, 120, 130]
            #index bound
            low_limit = bound[Building_type - 1]
            up_limit = bound[Building_type]
            #story and area bound
            low_limit_area=min(building_information_ori[low_limit:up_limit,1])
            up_limit_area = max(building_information_ori[low_limit:up_limit, 1])

            low_limit_story = min(building_information_ori[low_limit:up_limit, 2])
            up_limit_story = max(building_information_ori[low_limit:up_limit, 2])


            # default building parameter
            total_floor_area_inp = building_information_ori[building_index - 1][1]  # sq.ft

            story_height_inp = 10  # ft
            bay_total_load_default = [0.115, 0.115, 0.080, 0.08, 0.08, 0.08, 0.08, 0.08]
            bayload_inp = bay_total_load_default[Building_type - 1]  # kips
            baysize1_inp = 20  # ft
            baysize2_inp = 25  # ft

            # Set up the inputs for Material Properties
            Building_para_modi = st.checkbox('Modify default building parameter')

            if option_analysis_type == 'Start a new analysis':
                Building_para_modi_saved = Building_para_modi
            elif option_analysis_type == 'Load session variables':
                if 'building_parameter_original' in st.session_state:
                    building_parameter_original_saved=st.session_state.building_parameter_original
                    Building_para_modi_saved=building_parameter_original_saved.at[0, 'Modify default building parameter']
                    story_height_inp=building_parameter_original_saved.at[0, 'Story height']
                    #total_floor_area_inp=building_parameter_original_saved.at[0,  'Total area']
                    bayload_inp=building_parameter_original_saved.at[0,    'Bay load']
                    total_story = building_parameter_original_saved.at[0,  'Building stories']
                    baysize1_inp = building_parameter_original_saved.at[0, 'Bay size1']
                    baysize2_inp = building_parameter_original_saved.at[0, 'Bay size2']
                else:
                    Building_para_modi_saved = Building_para_modi

            Building_para_modi=Building_para_modi_saved

            if Building_para_modi:
                col1,col2 = st.columns(2)
                with col1:
                    story_height_inp = st.number_input("story height",value=story_height_inp, step=1)
                with col2:
                    total_floor_area_inp = st.number_input("total floor area (sq.ft)",value=total_floor_area_inp)
                if total_floor_area_inp<low_limit_area or total_floor_area_inp>up_limit_area:
                    st.write("Warning: ")
                    st.write(f"The total floor area is out of the range in the database, the results on fire safety measures except passive fire protection on steelworks might not be applicable. "
                                  f"Min:{low_limit_area} Max:{up_limit_area}")

                col1, col2 = st.columns(2)
                with col1:
                    bayload_inp = st.number_input("bay total load (lbf)",value=int(bayload_inp*1000),step=1)/1000
                with col2:
                    total_story = st.number_input("Building storys",value=int(total_story), step=1)

                if total_story<low_limit_story or total_story>up_limit_story:
                    st.write("Warning: ")
                    st.write(f"The total story is out of the range in the database, the results on fire safety measures except passive fire protection on steelworks might not be applicable. "
                                  f"Min:{low_limit_story} Max:{up_limit_story}")

                col1, col2 = st.columns(2)
                with col1:
                    baysize1_inp = st.number_input("bay size x direction (ft)",value=baysize1_inp, step=1)
                with col2:
                    baysize2_inp = st.number_input("bay size y direction (ft)",value=baysize2_inp, step=1)


            column_fire_rating_inp = int(building_information_ori[building_index - 1][12])
            Beam_fire_rating_inp = int(building_information_ori[building_index - 1][11])
            fire_protection_material_column_inp = 1

            fire_protection_material_beam_inp = 1
            fire_protection_percentage_column_inp = 1
            fire_protection_percentage_beam_inp = 1


            fire_design_para_modi = st.checkbox('Modify default fire design paramter')

            if option_analysis_type == 'Start a new analysis':
                fire_design_para_modi_saved = fire_design_para_modi
            elif option_analysis_type == 'Load session variables':
                if 'fire_parameter_original' in st.session_state:
                    fire_parameter_original_saved = st.session_state.fire_parameter_original
                    fire_design_para_modi_saved=fire_parameter_original_saved.at[0, 'Modify fire design parameter']
                    Beam_fire_rating_inp = fire_parameter_original_saved.at[0, 'Beam fire rating']
                    column_fire_rating_inp = fire_parameter_original_saved.at[0, 'Column fire rating']
                    fire_protection_material_beam_inp = fire_parameter_original_saved.at[0, 'Beam fire protection material']
                    fire_protection_material_column_inp = fire_parameter_original_saved.at[0, 'Column fire protection material']
                    fire_protection_percentage_beam_inp = fire_parameter_original_saved.at[0, 'Beam fire protection percentage']
                    fire_protection_percentage_column_inp = fire_parameter_original_saved.at[0, 'Column fire protection percentage']
                else:
                    fire_design_para_modi_saved = fire_design_para_modi

            fire_design_para_modi=fire_design_para_modi_saved

            if fire_design_para_modi:

                col1,col2 = st.columns(2)
                with col2:
                    column_fire_rating_inp = st.number_input("Column fire rating (hr)",min_value=0,max_value=4,value=int(column_fire_rating_inp), step=1)
                with col1:
                    Beam_fire_rating_inp = st.number_input("Beam fire rating (hr)",min_value=0,max_value=4,value=Beam_fire_rating_inp, step=1)
                col1, col2 = st.columns(2)
                with col2:
                    fire_protection_material_column_inp = st.number_input("Input column fire protection material",min_value=1,
                                                                          value=fire_protection_material_column_inp, step=1)
                with col1:
                    fire_protection_material_beam_inp = st.number_input("Input beam fire protection material",min_value=1,
                                                                        value=fire_protection_material_beam_inp, step=1)
                col1, col2 = st.columns(2)
                with col2:
                    fire_protection_percentage_column_inp = st.number_input("Input column fire protection percentage",
                                                                            value=float(fire_protection_percentage_column_inp),min_value=0.00, max_value=1.00,step=0.01)
                with col1:
                    fire_protection_percentage_beam_inp = st.number_input("Input beam fire protection percentage",
                                                                          value=float(fire_protection_percentage_beam_inp),min_value=0.00, max_value=1.00,step=0.01)

            fire_cost_para_modi = st.checkbox('Modify default fire protection cost value')

            if fire_cost_para_modi:
                uploaded_file_cost = st.file_uploader("Choose a file cost value ")
                st.write("Remark: csv format, base on the sample file, only change the value, can add value for new fire protection material")
            else:
                uploaded_file_cost = default_cost_file

            data_frame = pd.read_csv(uploaded_file_cost)
            st.session_state.uploaded_file_cost=data_frame

            # get the column cost arrays
            column_tabular = np.asarray(data_frame.iloc[0:15, 0:8], float)
            # get the indices for different fire protection materials
            row_indices_column = [i + 12 + fire_protection_material_column_inp * 6 for i in range(0, 4)]
            # get the numerical value for given fire protection materials
            column_fire_cost_tabular = np.asarray(data_frame.iloc[row_indices_column, 0:7], float)


            # get the indices for different fire protection materials for beams
            row_indices_beam = [i - 8 + fire_protection_material_beam_inp * 10 for i in range(0, 8)]

            beam_fire_cost_tabular = np.asarray(data_frame.iloc[row_indices_beam, 9:14], float)

            beam_fire_labor_tabular = np.asarray(data_frame.iloc[0:5, 26:33])
            # sf material labor hour
            unit_labor_beam=float(beam_fire_labor_tabular[2,6])
            print(beam_fire_labor_tabular)
            unit_material_fireprotection = float(beam_fire_labor_tabular[2, 5])
            unit_labor_fluted_deck=beam_fire_labor_tabular[3,6]
            unit_material_fluted_deck = beam_fire_labor_tabular[3, 5]
            #
            print(unit_material_fireprotection)

            # beam fire cost at different fire rating with given building index
            beam_fire_cost = beam_fire_cost_tabular[Building_type - 1][2:5]

            floor_default_composite = [20.65, 20.65, 19.99, 19.99, 19.99, 19.99, 19.99, 19.99]
            fireprotectionbeam_default = [0.86, 0.86, 0.79, 0.79, 0.79, 0.79, 0.79, 0.79]

            # fireprotectionbeam_default_material = [0.523,0.523,0.483,0.483,0.483,0.483,0.483,0.483]


            floor_composite = floor_default_composite[Building_type - 1]
            fireprotectionbeam_ori = fireprotectionbeam_default[Building_type - 1]


            column_cost, column_protection_cost, floor_load_max,column_protection_labor = column_cost_calculation(total_floor_area_inp, total_story, baysize1_inp, baysize2_inp,
                                                              bayload_inp,story_height_inp, column_tabular, column_fire_cost_tabular,fire_protection_percentage_column_inp,
                                                                                          unit_material_fireprotection,unit_labor_beam)

            if fire_protection_material_column_inp!=1:
                column_protection_labor=column_protection_labor*0

            floor_cost, floor_protection_cost,floor_protection_labor = floor_system_cost(total_floor_area_inp, floor_composite, beam_fire_cost,
                                                                  fireprotectionbeam_ori,fire_protection_percentage_beam_inp,
                                                                                   unit_material_fireprotection,unit_labor_beam)
            if fire_protection_material_beam_inp!=1:
                floor_protection_labor=floor_protection_labor*0

            total_cost = totalcost_ori[building_index - 1][2] + floor_cost + column_cost + column_protection_cost[
                column_fire_rating_inp - 1] + floor_protection_cost[Beam_fire_rating_inp - 1]
            total_cost_sqft = total_cost / total_floor_area_inp

            if floor_load_max>1000:
                st.write ("Warning: ")
                st.write ("The floor load is over the max column loading capacity (1000 kips), if want to continue, "
                          "please use user-defined column cost and capacity data")


            Interpolation_agree = st.checkbox('Enable interpolation when the default building parameter is changed')
            if Interpolation_agree:
                partition_cost, Sprinkler_cost, Fire_pump_cost, Alarm_cost, Ceiling_cost = fire_service_cost(total_floor_area_inp,
                                                                                                             total_story,
                                                                                                             building_information_ori,
                                                                                                             building_index)
            else:
                partition_cost, Sprinkler_cost, Fire_pump_cost, Alarm_cost, Ceiling_cost = [0,0,0,0,0]
            st.write("---")
            alter_design = st.checkbox('Do you want to specify fire design parameters for alternative design?')

            Beam_fire_rating_inp_alt = Beam_fire_rating_inp
            column_fire_rating_inp_alt = column_fire_rating_inp
            fire_protection_material_beam_inp_alt = fire_protection_material_beam_inp
            fire_protection_material_column_inp_alt = fire_protection_material_column_inp
            fire_protection_percentage_beam_inp_alt = fire_protection_percentage_beam_inp
            fire_protection_percentage_column_inp_alt = fire_protection_percentage_column_inp

            if option_analysis_type == 'Start a new analysis':
                alter_design_saved = alter_design
            elif option_analysis_type == 'Load session variables':
                if 'fire_parameter_alt' in st.session_state:
                    fire_parameter_alt_saved = st.session_state.fire_parameter_alt
                    alter_design_saved=fire_parameter_alt_saved.at[0, 'active alternative design']
                    Beam_fire_rating_inp_alt = fire_parameter_alt_saved.at[0, 'Beam fire rating alt.']
                    column_fire_rating_inp_alt = fire_parameter_alt_saved.at[0, 'Column fire rating alt.']
                    fire_protection_material_beam_inp_alt = fire_parameter_alt_saved.at[0, 'Beam fire protection material alt.']
                    fire_protection_material_column_inp_alt = fire_parameter_alt_saved.at[0, 'Column fire protection material alt.']
                    fire_protection_percentage_beam_inp_alt = fire_parameter_alt_saved.at[0,  'Beam fire protection percentage alt.']
                    fire_protection_percentage_column_inp_alt = fire_parameter_alt_saved.at[0, 'Column fire protection percentage alt.']
                else:
                    alter_design_saved = alter_design

            alter_design=alter_design_saved

            if alter_design:
                col1,col2 = st.columns(2)
                with col2:
                    column_fire_rating_inp_alt = st.number_input("Column fire rating alt. (hr)",min_value=0,max_value=4,
                                                                 value=column_fire_rating_inp_alt, step=1)
                with col1:
                    Beam_fire_rating_inp_alt = st.number_input("Beam fire rating alt. (hr)",min_value=0,max_value=4,
                                                               value=Beam_fire_rating_inp_alt, step=1)
                col1, col2 = st.columns(2)
                with col2:
                    fire_protection_material_column_inp_alt = st.number_input("Input column fire protection material alt.",min_value=1,
                                                                              value=fire_protection_material_column_inp_alt, step=1)
                with col1:
                    fire_protection_material_beam_inp_alt = st.number_input("Input beam fire protection material alt.",min_value=1,
                                                                            value=fire_protection_material_beam_inp_alt, step=1)
                col1, col2 = st.columns(2)
                with col2:
                    fire_protection_percentage_column_inp_alt = st.number_input("Input column fire protection percentage alt.",
                                                                                value=float(fire_protection_percentage_column_inp_alt),min_value=0.00, max_value=1.00,step=0.01)
                with col1:
                    fire_protection_percentage_beam_inp_alt = st.number_input("Input beam fire protection percentage alt.",
                                                                              value=float(fire_protection_percentage_beam_inp_alt),min_value=0.00, max_value=1.00,step=0.01)

                row_indices_column = [i + 12 + fire_protection_material_column_inp_alt * 6 for i in range(0, 4)]
                # get the numerical value for given fire protection materials
                column_fire_cost_tabular_alt = np.asarray(data_frame.iloc[row_indices_column, 0:7], float)

                # get the indices for different fire protection materials for beams
                row_indices_beam = [i - 8 + fire_protection_material_beam_inp_alt * 10 for i in range(0, 8)]

                beam_fire_cost_tabular_alt = np.asarray(data_frame.iloc[row_indices_beam, 9:14], float)
                beam_fire_cost_alt = beam_fire_cost_tabular_alt[Building_type - 1][2:5]

                column_cost_alt, column_protection_cost_alt, floor_load_max_alt, column_protection_labor_alt= column_cost_calculation(total_floor_area_inp, total_story, baysize1_inp, baysize2_inp,
                                                                  bayload_inp,story_height_inp, column_tabular, column_fire_cost_tabular_alt,fire_protection_percentage_column_inp_alt
                                                                                                           ,unit_material_fireprotection,unit_labor_beam)
                if fire_protection_material_column_inp_alt != 1:
                    column_protection_labor_alt = column_protection_labor_alt * 0

                floor_cost_alt, floor_protection_cost_alt,floor_protection_labor_alt = floor_system_cost(total_floor_area_inp, floor_composite, beam_fire_cost_alt,
                                                                      fireprotectionbeam_ori,fire_protection_percentage_beam_inp_alt
                                                                              ,unit_material_fireprotection,unit_labor_beam)
                if fire_protection_material_beam_inp_alt != 1:
                    floor_protection_labor_alt = floor_protection_labor_alt * 0

                total_cost_alt = totalcost_ori[building_index - 1][2] + floor_cost + column_cost + column_protection_cost[
                    column_fire_rating_inp_alt - 1] + floor_protection_cost[Beam_fire_rating_inp_alt - 1]

        with st.container():
            st.markdown(
                '**Note: detailed building design and fire design can be found on page "Explore construction cost database"**')
            st.subheader('Results')
            cci_consider = st.checkbox('Consider city cost index', value=False)
            if cci_consider:
                #cci_df = pd.read_csv('city_cost_index.csv')
                cci_df = pd.read_csv('city_cost_index_unit_cost_level.csv',encoding='latin-1')

                state_name = st.selectbox('Select the state', cci_df['State'].unique())
                # Filter cities based on the selected state
                filtered_cities = cci_df[cci_df['State'] == state_name]['City']
                # Select city from the filtered list
                city_name = st.selectbox('Select the city', filtered_cities)
                # Get the index of the selected city
                city_index = cci_df[(cci_df['State'] == state_name) & (cci_df['City'] == city_name)].index[0]

                cci_other = cci_df['TOTAL'].iloc[city_index] / 100
                cci_fire_mat = cci_df['MAT07'].iloc[city_index] / 100
                cci_fire_ins = cci_df['INST07'].iloc[city_index] / 100
                cci_fire_tot = cci_df['TOTAL07'].iloc[city_index] / 100

                cci_rebar_mat = cci_df['MAT0320'].iloc[city_index] / 100
                cci_rebar_ins = cci_df['INST0320'].iloc[city_index] / 100
                cci_rebar_tot = cci_df['TOTAL0320'].iloc[city_index] / 100

                # cci_fire_total = cci_df['TOTAL_B10'].iloc[city_index]/100
                bare_mat=float(beam_fire_labor_tabular[2, 1])
                bare_labor=float(beam_fire_labor_tabular[2, 2])

                cci_fire_total = cci_fire_mat * bare_mat / (bare_mat+bare_labor) + cci_fire_ins * bare_labor / (bare_mat+bare_labor)
                # st.markdown(f"City name: {city_name},"
                #             f"CCI for fire protection material: {cci_df['MAT_B10'].iloc[city_index]}%, CCI for fire protection installation: {cci_fire_ins * 100}%,"
                #             f"CCI for fire protection: {int(cci_fire_total * 100)}%,CCI for other components: {cci_other * 100}%,")
                # Creating the DataFrame
                df_cci = pd.DataFrame({
                    'City Name': [city_name],
                    'CCI - Fire Protection Material': [cci_fire_mat],
                    'CCI - Fire Protection Installation': [cci_fire_ins],
                    'CCI - Fire Protection Total': [cci_fire_total],
                    'CCI - Rebar Material': [cci_rebar_mat],
                    'CCI - Rebar Installation': [cci_rebar_ins],
                    'CCI - Rebar Total': [cci_rebar_tot],
                    'CCI - Other Components': [cci_other]
                })


                st.session_state.df_cci = df_cci  # Attribute API

                # Displaying the DataFrame in Streamlit
                st.dataframe(df_cci, height=100, hide_index=True)
            else:
                cci_fire_mat = 1
                cci_fire_ins = 1
                cci_other = 1
                cci_fire_total = cci_fire_mat * 0.5 / 1.16 + cci_fire_ins * 0.66 / 1.16

            st.write("---")

            data = {
                'Modify default building parameter': [Building_para_modi],
                'Story height': [int(story_height_inp)],
                'Total area': [int(total_floor_area_inp)],
                'Bay load': [bayload_inp],
                'Building stories': [total_story],
                'Bay size1': [baysize1_inp],
                'Bay size2': [baysize2_inp],
            }
            building_parameter_original = pd.DataFrame(data)
            st.session_state.building_parameter_original = building_parameter_original  # Attribute API

            data = {
                'Modify fire design parameter': [fire_design_para_modi],
                'Beam fire rating': [Beam_fire_rating_inp],
                'Column fire rating': [column_fire_rating_inp],
                'Beam fire protection material': [fire_protection_material_beam_inp],
                'Column fire protection material': [fire_protection_material_column_inp],
                'Beam fire protection percentage': [fire_protection_percentage_beam_inp],
                'Column fire protection percentage': [fire_protection_percentage_column_inp],
            }
            fire_parameter_original = pd.DataFrame(data)
            st.session_state.fire_parameter_original = fire_parameter_original  # Attribute API

            if alter_design:
                data = {
                    'active alternative design': [alter_design],
                    'Beam fire rating alt.': [Beam_fire_rating_inp_alt],
                    'Column fire rating alt.': [column_fire_rating_inp_alt],
                    'Beam fire protection material alt.': [fire_protection_material_beam_inp_alt],
                    'Column fire protection material alt.': [fire_protection_material_column_inp_alt],
                    'Beam fire protection percentage alt.': [fire_protection_percentage_beam_inp_alt],
                    'Column fire protection percentage alt.': [fire_protection_percentage_column_inp_alt],
                }
                fire_parameter_alt = pd.DataFrame(data)
                st.session_state.fire_parameter_alt = fire_parameter_alt  # Attribute API

            #define the size of the figure
            f1 = plt.figure(figsize=(6, 6), dpi=200)
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.4, hspace=0.4)

            f2 = plt.figure(figsize=(6, 6), dpi=200)
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.4, hspace=0.4)

            f3 = plt.figure(figsize=(6, 6), dpi=200)
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.4, hspace=0.4)

            # two subplots are adopted
            ax1 = f1.add_subplot(2, 1, 1)
            ax1.grid(True)
            column_fire_cost_given_rate=column_protection_cost[column_fire_rating_inp - 1]
            floor_protection_cost_given_rate=floor_protection_cost[Beam_fire_rating_inp - 1]
            cost_value_original=[floor_protection_cost_given_rate*cci_fire_total,column_fire_cost_given_rate*cci_fire_total,partition_cost,Sprinkler_cost,Fire_pump_cost,Alarm_cost,Ceiling_cost]
            p1=ax1.bar([1,2,3,4,5,6,7], cost_value_original,width=0.4,edgecolor=[1,0,0])
            ax1.set_xticks([1,2,3,4,5,6,7],('Beams','Columns','Partition','Sprinkler', 'Fire pump', 'Alarm', 'Ceiling'))
            ax1.set_ylabel('Cost ($)')
            ax1.set_title('Fire service cost')
            p1[0].set_color([0,0.5,1])
            p1[0].set_edgecolor([0,0,1])
            p1[1].set_color([0,0.5,1])
            p1[1].set_edgecolor([0,0,1])

            # make the y axis can be shown on right side
            ax2 = ax1.twinx()
            cost_value_original_multiplier=[floor_protection_cost_given_rate*cci_fire_total, column_fire_cost_given_rate*cci_fire_total, partition_cost, Sprinkler_cost,
                          Fire_pump_cost, Alarm_cost, Ceiling_cost]/total_cost
            p2 = ax2.bar([1, 2, 3, 4, 5, 6, 7],
                         cost_value_original_multiplier,width=0.2,edgecolor=[1,0,0])
            ax2.set_ylabel('Cost multiplier', color='red')
            ax2.tick_params(axis='y', labelcolor='red')
            p2[0].set_color([0,0.5,1])
            p2[0].set_edgecolor([0,0,1])
            p2[1].set_color([0,0.5,1])
            p2[1].set_edgecolor([0,0,1])

            #ax1.set_yticks(np.linspace(0, max([floor_protection_cost_given_rate, column_fire_cost_given_rate, partition_cost, Sprinkler_cost,
            #              Fire_pump_cost, Alarm_cost, Ceiling_cost]), 6))
            #ax2.set_yticks(np.linspace(0, max([floor_protection_cost_given_rate, column_fire_cost_given_rate, partition_cost, Sprinkler_cost,
            #              Fire_pump_cost, Alarm_cost, Ceiling_cost]/total_cost), 6))

            # show the table that lists the updated cost data
            column_fire_labor_given_rate = column_protection_labor[column_fire_rating_inp - 1]
            floor_protection_labor_given_rate = floor_protection_labor[Beam_fire_rating_inp - 1]


            data = {
                '': ['Cost ($)',"Cost multiplier","Labor hour"],
                'Floor': [int(floor_protection_cost_given_rate*cci_fire_total),floor_protection_cost_given_rate/total_cost,int(floor_protection_labor_given_rate)],
                'Column': [int(column_fire_cost_given_rate*cci_fire_total),column_fire_cost_given_rate/total_cost,int(column_fire_labor_given_rate)],
                'Partition': [int(partition_cost),partition_cost/total_cost,0],
                'Sprinkler': [int(Sprinkler_cost),Sprinkler_cost/total_cost,0],
                'Fire pump': [int(Fire_pump_cost),Fire_pump_cost/total_cost,0],
                'Alarm': [int(Alarm_cost),Alarm_cost/total_cost,0],
                'Ceiling': [int(Ceiling_cost),Ceiling_cost/total_cost,0],
            }
            construction_cost_df_updated = pd.DataFrame(data)

            ax3 = f1.add_subplot(2, 1, 2)
            ax3.grid(True)
            labor_hour_original = [floor_protection_labor_given_rate, column_fire_labor_given_rate]
            p3 = ax3.bar([1, 2],
                         labor_hour_original, width=0.4, edgecolor=[1, 0, 0])
            ax3.set_xticks([1, 2], ('Beams', 'Columns'))
            ax3.set_ylabel('Labor hour (hr)')
            ax3.set_title('Labor hour needed for crew G2')

            if alter_design:
                st.session_state.alter_design = alter_design  # Attribute API

                column_fire_cost_given_rate = column_protection_cost_alt[column_fire_rating_inp_alt - 1]
                floor_protection_cost_given_rate = floor_protection_cost_alt[Beam_fire_rating_inp_alt - 1]
                column_fire_labor_given_rate = column_protection_labor_alt[column_fire_rating_inp_alt - 1]
                floor_protection_labor_given_rate = floor_protection_labor_alt[Beam_fire_rating_inp_alt - 1]



                data = {
                    '': ['Cost ($)',"Cost multiplier","Labor hour"],
                    'Floor': [int(floor_protection_cost_given_rate*cci_fire_total),floor_protection_cost_given_rate/total_cost,int(floor_protection_labor_given_rate)],
                    'Column': [int(column_fire_cost_given_rate*cci_fire_total),column_fire_cost_given_rate/total_cost,int(column_fire_labor_given_rate)],
                    'Partition': [int(partition_cost),partition_cost/total_cost,0],
                    'Sprinkler': [int(Sprinkler_cost),Sprinkler_cost/total_cost,0],
                    'Fire pump': [int(Fire_pump_cost),Fire_pump_cost/total_cost,0],
                    'Alarm': [int(Alarm_cost),Alarm_cost/total_cost,0],
                    'Ceiling': [int(Ceiling_cost),Ceiling_cost/total_cost,0],
                }
                construction_cost_df_updated_alt = pd.DataFrame(data)


                ax4 = f2.add_subplot(2, 1, 1)
                ax4.grid(True)
                cost_value_alt=[floor_protection_cost_given_rate*cci_fire_total, column_fire_cost_given_rate*cci_fire_total, partition_cost, Sprinkler_cost,
                              Fire_pump_cost, Alarm_cost, Ceiling_cost]
                p4 = ax4.bar([1, 2, 3, 4, 5, 6, 7],
                             cost_value_alt, width=0.4, edgecolor=[1, 0, 0])
                ax4.set_xticks([1, 2, 3, 4, 5, 6, 7],
                               ('Beams', 'Columns', 'Partition', 'Sprinkler', 'Fire pump', 'Alarm', 'Ceiling'))
                ax4.set_ylabel('Cost ($)')
                ax4.set_title('Fire service cost (Alternative design)')
                p4[0].set_color([0, 0.5, 1])
                p4[0].set_edgecolor([0, 0, 1])
                p4[1].set_color([0, 0.5, 1])
                p4[1].set_edgecolor([0, 0, 1])

                # make the y axis can be shown on right side
                ax5 = ax4.twinx()
                cost_value_alt_multiplier=[floor_protection_cost_given_rate*cci_fire_total, column_fire_cost_given_rate*cci_fire_total, partition_cost, Sprinkler_cost,
                              Fire_pump_cost, Alarm_cost, Ceiling_cost] / total_cost
                p5 = ax5.bar([1, 2, 3, 4, 5, 6, 7],
                             cost_value_alt_multiplier, width=0.2, edgecolor=[1, 0, 0])
                ax5.set_ylabel('Cost multiplier', color='red')
                ax5.tick_params(axis='y', labelcolor='red')
                p5[0].set_color([0, 0.5, 1])
                p5[0].set_edgecolor([0, 0, 1])
                p5[1].set_color([0, 0.5, 1])
                p5[1].set_edgecolor([0, 0, 1])

                ax6 = f2.add_subplot(2, 1, 2)
                ax6.grid(True)
                labor_hour_alt=[floor_protection_labor_given_rate, column_fire_labor_given_rate]
                p6 = ax6.bar([1, 2],
                             labor_hour_alt, width=0.4,
                             edgecolor=[1, 0, 0])
                ax6.set_xticks([1, 2], ('Beams', 'Columns'))
                ax6.set_ylabel('Labor hour (hr)')
                ax6.set_title('Labor hour needed for crew G2')

                max_cost_value=1.1*max(cost_value_original+cost_value_alt)
                max_cost_value_multiplier = 1.1*max(np.maximum(np.array(cost_value_original_multiplier), np.array(cost_value_alt_multiplier)))

                max_labor_hour=1.1* max(labor_hour_original+ labor_hour_alt)

                ax1.set_ylim(0, max_cost_value)
                ax4.set_ylim(0, max_cost_value)

                ax2.set_ylim(0, max_cost_value_multiplier)
                ax5.set_ylim(0, max_cost_value_multiplier)

                ax3.set_ylim(0, max_labor_hour)
                ax6.set_ylim(0, max_labor_hour)



            ax7 = f3.add_subplot(2, 1, 1)

            p7 = ax7.bar([1, 2, 3, 4, 5, 6, 7],
                         building_information_ori[building_index-1, [19, 20, 21, 22, 23, 24, 25]],width=0.4,edgecolor=[1,0,0])

            ax7.set_ylabel('Cost ($))', color='black')
            ax7.tick_params(axis='y', labelcolor='black')
            p7[0].set_color([0,0.5,1])
            p7[0].set_edgecolor([0,0,1])
            p7[1].set_color([0,0.5,1])
            p7[1].set_edgecolor([0,0,1])
            ax7.set_xticks([1,2,3,4,5,6,7],('Beams','Columns','Partition','Sprinkler', 'Fire pump', 'Alarm', 'Ceiling'))
            ax7.set_ylabel('Cost ($)')
            ax7.set_title('Original fire safety measures cost')


            ax8 = ax7.twinx()
            p8 = ax8.bar([1, 2, 3, 4, 5, 6, 7],
                         building_information_ori[building_index-1, [19, 20, 21, 22, 23, 24, 25]]/building_information_ori[building_index-1, 4],width=0.2,edgecolor=[1,0,0])

            ax8.set_ylabel('Cost multiplier', color='red')
            ax8.tick_params(axis='y', labelcolor='red')
            p8[0].set_color([0,0.5,1])
            p8[0].set_edgecolor([0,0,1])
            p8[1].set_color([0,0.5,1])
            p8[1].set_edgecolor([0,0,1])
            ax8.grid(True)


            # show the table that lists the original cost data
            totalcost_orig=int(totalcost_ori[building_index - 1][2])
            data = {
                '': ['Cost ($)',"Cost multiplier"],
                'Floor': [int(building_information_ori[building_index-1, 19]),float(building_information_ori[building_index-1,19])/totalcost_orig],
                'Column': [int(building_information_ori[building_index-1, 20]),float(building_information_ori[building_index-1, 20])/totalcost_orig],
                'Partition': [int(building_information_ori[building_index-1, 21]),float(building_information_ori[building_index-1, 21])/totalcost_orig],
                'Sprinkler': [int(building_information_ori[building_index-1, 22]),float(building_information_ori[building_index-1, 22])/totalcost_orig],
                'Fire pump': [int(building_information_ori[building_index-1, 23]),float(building_information_ori[building_index-1, 23])/totalcost_orig],
                'Alarm': [int(building_information_ori[building_index-1, 24]),float(building_information_ori[building_index-1, 24])/totalcost_orig],
                'Ceiling': [int(building_information_ori[building_index-1, 25]),float(building_information_ori[building_index-1, 25])/totalcost_orig],
            }
            construction_cost_df_original = pd.DataFrame(data, index=[0,1])


            col1, col2 = st.columns(2)
            with col1:

                df_cost={
                    '': ['With CCI', "Without CCI"],
                    'Total Construction Cost (thousand $)': [int(total_cost*cci_other/1000),int(total_cost/1000)],
                    'Total Construction Cost per sq.ft ($)': [int(total_cost_sqft*cci_other),int(total_cost_sqft)],
                    'Total floor area (thousand sq.ft) for fire protection': [int(total_floor_area_inp/1000),int(total_floor_area_inp/1000)],
                    'Total floor area (thousand sq.ft) for other components': [int(building_information_ori[building_index - 1][1]/1000),int(building_information_ori[building_index - 1][1]/1000)],
                    'Total story': int(total_story),
                }

                #df_cost_df = pd.DataFrame(list(df_cost.items()), columns=['Description', 'Value','Value2'])
                df_cost_df = pd.DataFrame(df_cost, index=[0, 1])
                st.markdown('**Updated cost data with user-defined cost value**')
                st.dataframe(construction_cost_df_updated, use_container_width=True, hide_index=True)

                st.dataframe(df_cost_df, use_container_width=True, hide_index=True)

                st.session_state.construction_cost_df = construction_cost_df_updated  # Attribute API
                st.pyplot(f1)
            if alter_design:
                with col2:
                    df_cost_alt = {
                        '': ['With CCI', "Without CCI"],
                        'Total Construction Cost (thousand $)': [int(total_cost_alt*cci_other/1000),int(total_cost_alt/1000),],
                        'Total Construction Cost per sq.ft (thousand $)': [int(total_cost_alt*cci_other/total_floor_area_inp),int(total_cost_alt/total_floor_area_inp)],
                        'Total floor area (thousand sq.ft)': [int(total_floor_area_inp/1000),int(total_floor_area_inp/1000)],
                        'Total floor area (thousand sq.ft) for other components': [int(building_information_ori[building_index - 1][1]/1000),
                                                                                   int(building_information_ori[building_index - 1][1]/1000)],
                        'Total story': [int(total_story),int(total_story)],
                    }
                    #df_cost_df_alt = pd.DataFrame(list(df_cost_alt.items()), columns=['Description', 'Value'])
                    df_cost_df_alt = pd.DataFrame(df_cost, index=[0, 1])

                    st.markdown('**Alternative design**')
                    st.dataframe(construction_cost_df_updated_alt,use_container_width=True,hide_index=True)
                    st.dataframe(df_cost_df_alt, use_container_width=True,hide_index=True)

                    st.session_state.construction_cost_df_alt = construction_cost_df_updated_alt  # Attribute API
                    st.pyplot(f2)

            st.markdown('**Original cost data**')
            st.dataframe(construction_cost_df_original,use_container_width=True,hide_index=True)
            df_cost_orig = {
                'Total Construction Cost (thousand $)': int(totalcost_orig/1000),
                'Total Construction Cost per sq.ft ($)': int(
                    totalcost_orig / building_information_ori[building_index - 1][1]),
                'Total floor area (thousand sq.ft)': int(building_information_ori[building_index - 1][1] / 1000),
                'Total floor area (thousand sq.ft) for other components': int(
                    building_information_ori[building_index - 1][1] / 1000),
                'Total story': int(total_story),
            }
            #df_cost_orig_df = pd.DataFrame(list(df_cost_orig.items()), columns=['Description', 'Value'])
            #st.dataframe(df_cost_orig_df, use_container_width=True, hide_index=True)

            st.session_state.construction_cost_df_original = construction_cost_df_original  # Attribute API

            st.pyplot(f3)


            Download = st.checkbox('Do you want to download the detailed member cost')
            if Download:
                cost_save_tocsv = construction_cost_df_updated.to_csv(index=False)
               # cost_save_tocsv_string_io = StringIO(cost_save_tocsv)
                # Create a download button
                st.download_button(
                    label="Download CSV",
                    data=cost_save_tocsv,
                    file_name='user_updated_costdetail.csv',
                    mime='text/csv',
                )
                # savepath=st.session_state.path_for_save+'user_updated_costdetail.csv'
                # construction_cost_df_updated.to_csv(savepath, index=False)
                #st.success(f"Data successfully saved to {savepath}")

    def User_defined_building():
        import pandas as pd
        import numpy as np
        from functions import get_wd_ratio, get_fireprotection_thickness,calculate_fireprotection_cost
        st.header("Economic impact of performance-based structural fire design")
        para_fireprotection=np.zeros([5,2])

        # Set up the second section on the left part
        with (st.sidebar):
            # Set up the part for user input file
            st.markdown("## **User Input File**")
            uploaded_file = st.file_uploader("Choose a csv file")
            if uploaded_file:
                Thickness_method = st.selectbox(
                    'How would you like to calculate the protection thickness',
                    ('Ignore the thickness, use RSMeans default thickness','Use thickness adjust equation', 'Thickness is given'))

                Cost_method = st.selectbox('What unit cost value you like to use',('RSMeans default value','User defined equation'))

                if Cost_method == 'User defined equation':
                    col1, col2 = st.columns(2)
                    with col1:
                        para_fireprotection[4, 0] = st.number_input("Unit fire protection cost for metal deck, material 1, per sf.")
                    with col2:
                        para_fireprotection[4, 1] = st.number_input(
                            "Unit fire protection cost for metal deck, material 2, per sf.")
                    No_material = st.selectbox(
                        'How many fire protection material do you have',
                        ('1', '2','3','4'))
                    if No_material=='1':
                        col1, col2 = st.columns(2)
                        with col1:
                            para_fireprotection[0,0] = st.number_input("Cost equation parameter a for material 1")
                        with col2:
                            para_fireprotection[0,1] = st.number_input("Cost equation parameter b for material 1")

                    elif No_material=='2':
                        col1, col2 = st.columns(2)
                        with col1:
                            para_fireprotection[0,0] = st.number_input("Cost equation parameter a for material 1")
                        with col2:
                            para_fireprotection[0,1] = st.number_input("Cost equation parameter b for material 1")
                        col1, col2 = st.columns(2)
                        with col1:
                            para_fireprotection[1,0] = st.number_input("Cost equation parameter a for material 2")
                        with col2:
                            para_fireprotection[1,1] = st.number_input("Cost equation parameter b for material 2")
                    elif No_material=='3':
                        col1, col2 = st.columns(2)
                        with col1:
                            para_fireprotection[0,0] = st.number_input("Cost equation parameter a for material 1")
                        with col2:
                            para_fireprotection[0,1] = st.number_input("Cost equation parameter b for material 1")
                        col1, col2 = st.columns(2)
                        with col1:
                            para_fireprotection[1,0] = st.number_input("Cost equation parameter a for material 2")
                        with col2:
                            para_fireprotection[1,1] = st.number_input("Cost equation parameter b for material 2")
                        col1, col2 = st.columns(2)
                        with col1:
                            para_fireprotection[2,0] = st.number_input("Cost equation parameter a for material 3")
                        with col2:
                            para_fireprotection[2,1] = st.number_input("Cost equation parameter b for material 3")

                    elif No_material=='4':
                        col1, col2 = st.columns(2)
                        with col1:
                            para_fireprotection[0,0] = st.number_input("Cost equation parameter a for material 1")
                        with col2:
                            para_fireprotection[0,0] = st.number_input("Cost equation parameter b for material 1")
                        col1, col2 = st.columns(2)
                        with col1:
                            para_fireprotection[1,0] = st.number_input("Cost equation parameter a for material 2")
                        with col2:
                            para_fireprotection[1,1] = st.number_input("Cost equation parameter b for material 2")
                        col1, col2 = st.columns(2)
                        with col1:
                            para_fireprotection[2,0] = st.number_input("Cost equation parameter a for material 3")
                        with col2:
                            para_fireprotection[2,1] = st.number_input("Cost equation parameter b for material 3")
                        col1, col2 = st.columns(2)
                        with col1:
                            para_fireprotection[3,0] = st.number_input("Cost equation parameter a for material 4")
                        with col2:
                            para_fireprotection[3,1] = st.number_input("Cost equation parameter b for material 4")


                else:
                    para_fireprotection = [
                        [18.59, 0.4126],  # 1 for sfrm
                        [170.7, 4.654], #2 for intumescent
                        [0,0],
                        [0,0],
                        [2.54]  # price for metal deck, per sf. per inch thickness
                    ]

                # input of this function
                material_constant_index = 1

                # import user input file
                user_input = pd.read_csv(uploaded_file)
                # member type
                # 1 is beam, 2 is column, 3 hss member (assume hss cannot be used for beams), 4 metal deck
                member_shape_index_inp = np.asarray(user_input.iloc[:, 0])
                # enclose type
                # case a: 3 sides, case b: 4 sides, case c: box 3 sides, case d: box 4 sides
                enclose_type_inp = np.asarray(user_input.iloc[:, 1])
                # member shape, w16*31 or others
                member_shape_inp = np.asarray(user_input.iloc[:, 2])
                # member number of a specific size
                member_num_inp = np.asarray(user_input.iloc[:, 3])
                # member length of a specific size (inch)
                member_length_inp = np.asarray(user_input.iloc[:, 4])
                # member fire protection thickness, user input value
                member_fire_thick_inp = np.asarray(user_input.iloc[:, 6])
                # member fire rating, user input value
                member_fire_rating_inp = np.asarray(user_input.iloc[:, 7])

                # member fire protection material, user input value
                member_fire_material_inp = np.asarray(user_input.iloc[:, 8])

                # reference member thickness, input
                reference_t = [3 / 8, 13 / 16, 5 / 4];
                # reference member w/d ratio, input
                reference_wd = 0.819
                # material constant, input
                c1_inp = [1.05, 0.86, 1.25, 1.25, 1.01, 0.95]
                c2_inp = [0.61, 0.97, 0.53, 0.25, 0.66, 0.45]

                # total number of members
                num_member = np.shape(member_shape_index_inp)[0]
                # initialize the variables
                member_wholeline = []
                notfound_index = []
                member_parameter_ori = []

                # import the relationship between w/d and thickness of intumescent
                intumescent_thickness = pd.read_csv('intumescent coating.csv')
                intumescent_thick_wd_inp = np.asarray(intumescent_thickness.iloc[:, 3:])
                # member_parameter_wd=[0] * num_member
                member_parameter_wd = np.zeros([num_member])
                member_parameter_peri = np.zeros([num_member])
                member_parameter_surf = np.zeros([num_member])
                # member_parameter output: thickness, cost
                member_parameter_thick = np.zeros([num_member])
                member_unit_price = np.zeros([num_member])
                member_price = np.zeros([num_member])
                member_unit_labor= np.zeros([num_member])
                member_labor = np.zeros([num_member])
                thickness_record= np.zeros([num_member])
                for i in range(0, num_member ):
                    text = member_shape_inp[i]
                    text = text.replace("*", "×")

                    # Find the last occurrence of "×" using rfind()
                    last_multiplication_index = max(text.rfind("*"), text.rfind("×"))
                    # Extract characters before the last "×"
                    input_size1 = text[:last_multiplication_index]
                    input_size2 = text[(last_multiplication_index):]
                    content, notfound_lable = get_wd_ratio(input_size1, input_size2)
                    if notfound_lable != 'found':
                        notfound_index.append(i)

                    member_parameter_ori = np.asarray(content[1:])
                    # print(3 * (enclose_type_inp[i] - 1) + 1,member_parameter_ori[3 * (enclose_type_inp[i] - 1) + 1])
                    member_parameter_wd[i] = member_parameter_ori[3 * (enclose_type_inp[i] - 1) + 1]
                    member_parameter_peri[i] = member_parameter_ori[3 * (enclose_type_inp[i] - 1)]
                    member_parameter_surf[i] = member_parameter_ori[3 * (enclose_type_inp[i] - 1) + 2]

                    # target member w/d ratio
                    wd1 = member_parameter_wd[i]
                    wd2 = reference_wd
                    c1 = c1_inp[material_constant_index - 1];
                    c2 = c2_inp[material_constant_index - 1];
                    # print(member_fire_rating_inp[i])
                    t2 = reference_t[member_fire_rating_inp[i] - 1]
                    if Thickness_method == 'Use thickness adjust equation':
                        member_parameter_thick[i] = get_fireprotection_thickness(wd1, member_fire_rating_inp[i],
                                                                             member_fire_material_inp[i],
                                                                             member_shape_index_inp[i], wd2, t2, c1, c2,
                                                                             intumescent_thick_wd_inp)
                        member_unit_price[i]=calculate_fireprotection_cost(member_parameter_thick[i],para_fireprotection,
                                                                           member_parameter_peri[i],member_fire_material_inp[i],member_shape_index_inp[i])
                        member_price[i]=member_unit_price[i]*member_num_inp[i]*member_length_inp[i]/12
                        thickness_record[i] = member_parameter_thick[i]

                    elif Thickness_method == 'Thickness is given':
                        member_unit_price[i] = calculate_fireprotection_cost(member_fire_thick_inp[i], para_fireprotection,
                                                                             member_parameter_peri[i],member_fire_material_inp[i],member_shape_index_inp[i])
                        member_price[i]=member_unit_price[i]*member_num_inp[i]*member_length_inp[i]/12
                        thickness_record[i]=member_fire_thick_inp[i]


                    elif Thickness_method == 'Ignore the thickness, use RSMeans default thickness':
                        default_cost_input = pd.read_csv(default_cost_file)
                        rsmean_default_beam_cost = np.asarray(default_cost_input.iloc[6:24, 15:24])
                        vector_values = np.arange(1, 7) - 1
                        # Perform element-wise operations
                        result = vector_values * 3 + member_fire_rating_inp[i] - 1
                        fire_protection_cost = [float(rsmean_default_beam_cost[i1, member_fire_material_inp[i]+1]) for i1 in result]
                        exposed_perimeter_inp = [float(rsmean_default_beam_cost[i1, 6]) for i1 in result]
                        labor_inp = [float(rsmean_default_beam_cost[i1, 8]) for i1 in result]
                        m_material, b_material = np.polyfit(exposed_perimeter_inp, fire_protection_cost, 1)
                        m_labor, b_labor = np.polyfit(exposed_perimeter_inp, labor_inp, 1)
                        member_unit_price[i]=m_material*member_parameter_peri[i]+b_material
                        member_unit_labor[i]=m_labor*member_parameter_peri[i]+b_labor

                        member_price[i]=member_unit_price[i]*member_num_inp[i]*member_length_inp[i]/12
                        member_labor[i] = member_unit_labor[i] * member_num_inp[i] * member_length_inp[i]/12
                        thickness_record[i]=0


                total_fire_protection_cost = sum(member_price)
                total_fire_protection_cost_material1=0
                total_fire_protection_cost_material2=0
                total_fire_protection_cost_material3=0
                total_fire_protection_cost_material4=0

                total_fire_protection_cost_member1 = 0
                total_fire_protection_cost_member2 = 0
                total_fire_protection_cost_member3 = 0
                total_fire_protection_cost_member4 = 0



                for i in range(0, num_member ):
                    if member_fire_material_inp[i]==1:
                        total_fire_protection_cost_material1+=member_price[i]
                    elif member_fire_material_inp[i]==2:
                        total_fire_protection_cost_material2 += member_price[i]
                    elif member_fire_material_inp[i] == 3:
                        total_fire_protection_cost_material3 += member_price[i]
                    elif member_fire_material_inp[i] == 4:
                        total_fire_protection_cost_material4 += member_price[i]

                    if member_shape_index_inp[i] == 1:
                        total_fire_protection_cost_member1 += member_price[i]
                    elif member_shape_index_inp[i] == 2:
                        total_fire_protection_cost_member2 += member_price[i]
                    elif member_shape_index_inp[i] == 3:
                        total_fire_protection_cost_member3 += member_price[i]
                    elif member_shape_index_inp[i] == 4:
                        total_fire_protection_cost_member4 += member_price[i]


            alter_design = st.checkbox('Do you want to specify fire design parameters for alternative design?')


        with st.container():
            st.markdown('**Note: detailed building design and fire design can be found on page "Explore construction cost database"**')


            st.subheader('Results')
            st.write("---")
            if uploaded_file==None:
                st.markdown("**Please upload input file**")


                # summary the results we got
            value_material = [total_fire_protection_cost_material1, total_fire_protection_cost_material2,
                      total_fire_protection_cost_material3, total_fire_protection_cost_material4]
            value_member = [total_fire_protection_cost_member1, total_fire_protection_cost_member2,
                      total_fire_protection_cost_member3, total_fire_protection_cost_member4]





            f1 = plt.figure(figsize=(8, 12), dpi=100)
            # two subplots are adopted
            ax1 = f1.add_subplot(3, 2, 1)
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.4, hspace=0.4)

            ax1.grid(True)
            p1 = ax1.bar([i for i in range(1, num_member+1)],np.log10(member_price),width=0.4,edgecolor=[1,0,0])
            ax1.set_xlabel('Member index')
            ax1.set_ylabel('log10(Cost ($))')
            ax1.set_title('Passive fire protection cost')


            ax2 = f1.add_subplot(3, 2, 2)
            ax2.grid(True)
            p2 = ax2.bar([i for i in range(1, num_member+1)],member_price,width=0.4,edgecolor=[1,0,0])
            ax2.set_xlabel('Member index')
            ax2.set_ylabel('Cost ($)')
            ax2.set_title('Passive fire protection cost')



            ax4 = f1.add_subplot(3, 2, 4)
            ax4.grid(True)
            #p4 = ax4.bar([1], total_fire_protection_cost, width=0.4, edgecolor=[1, 0, 0])
            # Categories or labels for the bars (you can customize these)
            categories = ['1', '2', '3', '4']
            # Define colors for each value
            value_colors = ['blue', 'green', 'orange', 'red']
            # Create a figure and axis
            # Create a stacked bar with each value having a different color
            bottom = 0
            bars = ax4.bar(categories, value_material, color=value_colors)
            # for bar, value in zip(bars, values):
            # ax.annotate(str(value), xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
            #          xytext=(5, 0), textcoords='offset points', va='center')

            for value, color, label in zip(value_material, value_colors, categories):
                ax4.bar('Total cost', value, bottom=bottom, color=color, label=label)
                bottom += value
            # Add labels and a title
            ax4.set_ylabel('Cost ($)')
            ax4.set_xlabel('Material')
            ax4.set_title('Total passive fire protection cost')




            # Create a custom legend
            handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in value_colors]
            ax4.legend(handles, categories)
            # Add labels and a legend



            ax5 = f1.add_subplot(3, 2, 5)
            ax5.grid(True)
            bottom = 0
            bars = ax5.bar(categories, value_member, color=value_colors)
            # for bar, value in zip(bars, values):
            # ax.annotate(str(value), xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
            #          xytext=(5, 0), textcoords='offset points', va='center')

            for value, color, label in zip(value_member, value_colors, categories):
                ax5.bar('Total cost', value, bottom=bottom, color=color, label=label)
                bottom += value
            # Add labels and a title
            ax5.set_ylabel('Cost ($)')
            ax5.set_xlabel('Member (1 for beam, 2 for column, 4 for metal deck)')
            ax5.set_title('Total passive fire protection cost')




            if Thickness_method == 'Ignore the thickness, use RSMeans default thickness':


                ax3 = f1.add_subplot(3, 2, 3)
                ax3.grid(True)
                p3 = ax3.bar([i for i in range(1, num_member+1)],member_labor,width=0.4,edgecolor=[1,0,0])
                ax3.set_ylabel('Labor hour (hr)')
                ax3.set_title('Labor hour needed for different members')


            st.pyplot(f1)

            data = {
                '': ['Cost ($)'],
                'Floor': [value_member[0]+value_member[3]],
                'Column': [value_member[1]],
                'Partition': [0],
                'Sprinkler': [0],
                'Fire pump': [0],
                'Alarm': [0],
                'Ceiling': [0],
            }

            construction_cost_df = pd.DataFrame(data, index=[0, 1])
            st.session_state.construction_cost_df = construction_cost_df  # Attribute API
            data_array=[member_price,member_labor,thickness_record]


            construction_cost_detail = pd.DataFrame(data_array, index=['Construction cost', 'Labor hour (1 crew)', 'Member thickness'])
            st.session_state.construction_cost_detail = construction_cost_detail  # Attribute API

            st.session_state.construction_cost_detail

            Download = st.checkbox('Do you want to download the detailed member cost and labor')


            if Download:
                savepath=st.session_state.path_for_save+'userinput_costdetail.csv'
                construction_cost_detail.to_csv(savepath, index=False)
                st.success(f"Data succesfully saved to {savepath}")


    page_names_to_funcs = {
        'Construction cost estimation: Modify database': Modify_database,
        "Construction cost estimation: User defined building": User_defined_building,
    }

    demo_name = st.sidebar.selectbox("Choose a sub tool", page_names_to_funcs.keys())
    page_names_to_funcs[demo_name]()





