
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
def show():
    st.title('Extra cost estimation')

    st.header("Economic impact of performance-based structural fire design")

    building_parameter_original = st.session_state.building_parameter_original
    Affect_area = building_parameter_original['Total area'][0]

    unit_cost_data = st.session_state.uploaded_file_cost
    welded_wire_table = unit_cost_data.iloc[26:35, 15:19]
    welded_wire_name = welded_wire_table.iloc[1:,0].tolist()
    welded_wire_labor=np.asarray(welded_wire_table.iloc[1:, 2], float)
    welded_wire_cost = np.asarray(welded_wire_table.iloc[1:, 3], float)
    #welded_wire_table = np.asarray(unit_cost_data.iloc[28:36, 16:19], float)

    with st.sidebar:
        # Set up the part for user input file
        st.markdown("## **User Input Parameter**")

        option_analysis_type = st.session_state.option_analysis_type
        if st.checkbox("Reset to default parameter (Extra cost)",value=False):
            option_analysis_type='Start a new analysis'
            st.write('**The restored input parameter would not be applied**')
        extra_cost_saved = 0
        if "alter_design" in st.session_state:
            alter_design = st.session_state.alter_design
        else:
            alter_design=[]

        if alter_design:
            extra_cost_method = st.selectbox(
                f'Method to measure extra cost of **alternative design**',
                ('Default method','Input own value'))



            if option_analysis_type == 'Start a new analysis':
                extra_cost_saved = 0
            elif option_analysis_type == 'Load session variables':
                if 'extra_cost_df' in st.session_state:
                    extra_cost_df = st.session_state.extra_cost_df
                    extra_cost_saved = extra_cost_df.at[
                        0, 'Extra cost alt.']
                else:
                    extra_cost_saved = 0

            if extra_cost_method == 'Input own value':
                extra_cost=st.number_input("Input estimated extra cost",value=extra_cost_saved)
                extra_labor=st.number_input("Input estimated extra labor",value=0.0)
            if extra_cost_method == 'Default method':
                option_rebar = st.selectbox(
                    "Input welded wire mesh for alternative design",
                    welded_wire_name,
                )
                selected_index = welded_wire_name.index(option_rebar)
                extra_cost=Affect_area/100*(welded_wire_cost[selected_index]-welded_wire_cost[0])
                extra_labor=Affect_area/100*(welded_wire_labor[selected_index]-welded_wire_labor[0])

                # alter_design = st.checkbox('Do you want to get indirect damage cost value for alternative design?')

    with st.container():

        st.subheader('Results')
        st.write("---")

        if alter_design:
            data = {
                'Extra cost alt.': [int(extra_cost)],
                'Extra labor alt. (hour)': [int(extra_labor)]
            }
            extra_cost_df = pd.DataFrame(data)
            st.dataframe(extra_cost_df, use_container_width=True, hide_index=True)
            st.session_state.extra_cost_df = extra_cost_df  # Attribute API
        else:
            st.markdown("### Extra cost is not needed when the alternative design is not activated")

