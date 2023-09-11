
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to PBSFD project! 👋")


# Streamlit app
st.markdown('### **Enter the path for saving the files**')

# User input for the save path
save_path = st.text_input('Path:')
st.write(save_path)
st.session_state.path_for_save = save_path     # Attribute API

# Save the DataFrame when the user clicks the button
#if st.button('Save DataFrame'):
#    try:
#        df.to_csv(save_path, index=False)
#        st.success(f'DataFrame saved to {save_path}')
#    except Exception as e:
#        st.error(f'An error occurred: {str(e)}')
