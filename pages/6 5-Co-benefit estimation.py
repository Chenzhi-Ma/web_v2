
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
    st.markdown("## **User Input Parameter**")
    cobenefits_method = st.selectbox(
        'How would you like to define cobenefits cost',
        ('input own value','Default method' ))
    cobenefits_value=0
    if cobenefits_method == 'Default method':
        st.write("you select default method")
    if cobenefits_method == 'input own value':
        cobenefits_value = st.number_input("Input co-benefits")

    alter_design = st.checkbox('Do you want to get co-benefit cost for alternative design?')

    if alter_design:
        cobenefits_value_alt = 0
        if cobenefits_method == 'Default method':
            st.write("you select default method")
        if cobenefits_method == 'input own value':
            cobenefits_value_alt = st.number_input("Input co-benefits (alt.)")

with st.container():
    st.subheader('Results')
    st.write("---")
   # st.write("cobenefits_value")
    data = {
        'Cobenefit': [cobenefits_value],
    }
    Cobenefits_value_df = pd.DataFrame(data)


    col1, col2 = st.columns(2)
    with col1:
        st.write("**Results for reference design**")

        st.dataframe(Cobenefits_value_df, use_container_width=True, hide_index=True)
        st.session_state.Cobenefits_value_df = Cobenefits_value_df  # Attribute API

    if alter_design:
        with col2:
            st.write("**Results for alternative design**")

            data = {
                'Cobenefit': [cobenefits_value_alt],
            }
            Cobenefits_value_df_alt = pd.DataFrame(data)
            st.dataframe(Cobenefits_value_df_alt, use_container_width=True, hide_index=True)
            st.session_state.Cobenefits_value_df_alt = Cobenefits_value_df_alt  # Attribute API







