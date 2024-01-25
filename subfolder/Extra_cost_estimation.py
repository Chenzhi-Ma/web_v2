
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

    with st.sidebar:
        # Set up the part for user input file
        st.markdown("## **User Input Parameter**")

        option_analysis_type = st.session_state.option_analysis_type
        if st.checkbox("Reset to default parameter (Extra cost)",value=False):
            option_analysis_type='Start a new analysis'
            st.write('**The restored input parameter would not be applied**')

        if "alter_design" in st.session_state:
            alter_design = st.session_state.alter_design
        else:
            alter_design=[]

        if alter_design:
            extra_cost_method = st.selectbox(
                f'Method to measure extra cost of **alternative design**',
                ('Input own value','Default method'))
            extra_cost_saved=0

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

            if extra_cost_method == 'Default method':
                print(1)
                # alter_design = st.checkbox('Do you want to get indirect damage cost value for alternative design?')

    with st.container():

        st.subheader('Results')
        st.write("---")

        if alter_design:
            data = {
                'Extra cost alt.': [int(extra_cost)],
            }
            extra_cost_df = pd.DataFrame(data)
            st.dataframe(extra_cost_df, use_container_width=True, hide_index=True)
            st.session_state.extra_cost_df = extra_cost_df  # Attribute API
        else:
            st.markdown("### Extra cost is not needed when the alternative design is not activated")

