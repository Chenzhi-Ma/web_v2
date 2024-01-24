import streamlit as st
import json
import pandas as pd
import numpy as np
from functions import convert_state_for_json, convert_state_from_json
from io import StringIO

def show():
    st.title('Calculation')
    st.markdown('''
    ---
    ''')
    st.markdown('''
    ## Welcome! This page provides links save and restore the input parameters(session state).
    ''')

    st.markdown('''
    ### Save：
    ''')
    store_inputs = st.checkbox('Do you want to save all the input parameter to the specified path?')



    if store_inputs:
        data_state = convert_state_for_json(st.session_state)
        json_session_state=json.dumps(data_state, indent=4)
        st.download_button(
            label="Download json",
            data=json_session_state,
            file_name='session_state(inputs).json',
        )

    st.markdown('''
    ### Restore：
    ''')
    # Button to trigger loading all session state variables

    uploaded_file=st.file_uploader("Choose a json file that stores all the inputs")

    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            state = convert_state_from_json(data)
            for key, value in state.items():
                st.session_state[key] = value
            st.success("Session state loaded from uploaded file")

            # Display all session state variables in a table
            st.markdown("### Session State Variables")
            session_state_table = pd.DataFrame({
                'Key': st.session_state.keys(),
                'Value': [str(v) for v in st.session_state.values()]  # Convert values to string for display
            })
            st.table(session_state_table)
        except Exception as e:
            st.error(f"Error loading session state: {e}")
