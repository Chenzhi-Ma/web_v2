import streamlit as st
import json
import pandas as pd
import numpy as np
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

    def convert_state_for_json(state):
        serializable_state = {}
        for key, value in state.items():
            if isinstance(value, pd.DataFrame):
                # Convert DataFrame to a JSON string
                serializable_state[key] = value.to_json(orient='split')
            elif isinstance(value, np.bool_):
                # Convert NumPy boolean to Python boolean
                serializable_state[key] = bool(value)
            else:
                serializable_state[key] = value
        return serializable_state

    if store_inputs:
        file_path = st.session_state.path_for_save + 'session_state.json'
        try:
            with open(file_path, 'w') as file:
                data = convert_state_for_json(st.session_state)
                json.dump(data, file, indent=4)
            st.success(f"Session state saved to {file_path}")
        except Exception as e:
            st.error(f"Error saving session state: {e}")

    st.markdown('''
    ### Restore：
    ''')

    # Button to trigger loading all session state variables

    uploaded_file=st.file_uploader("Choose a json file that stores all the inputs")

    def convert_state_from_json(serialized_state):
        original_state = {}
        for key, value in serialized_state.items():
            if isinstance(value, str):
                try:
                    # Use StringIO to wrap the JSON string
                    str_io = StringIO(value)
                    original_state[key] = pd.read_json(str_io, orient='split')
                except ValueError:
                    # If the conversion fails, keep the value as a string
                    original_state[key] = value
            else:
                original_state[key] = value
        return original_state

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
