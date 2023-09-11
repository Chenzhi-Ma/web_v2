
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
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

with st.container():
    st.subheader('Results')
    st.write("---")
    st.write("cobenefits_value")
    data = {
        'Cobenefits_value': [cobenefits_value],
    }
    Cobenefits_value_df = pd.DataFrame(data)
    st.dataframe(Cobenefits_value_df, use_container_width=True, hide_index=True)
    st.session_state.Cobenefits_value_df = Cobenefits_value_df  # Attribute API


