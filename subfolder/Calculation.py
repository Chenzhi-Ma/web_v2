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
    ## Welcome!  
    ### This page provides links save and restore current inputs and outputs(session state).
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

    uploaded_file=st.file_uploader("Choose a json file that stores all the current inputs and outputs")

    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            state = convert_state_from_json(data)
            for key, value in state.items():
                st.session_state[key] = value
            st.success("Session state loaded from uploaded file")

            # Display all session state variables in a table
            st.markdown("### Session State Variables")

            session_state_items = [(key, value) if not isinstance(value, pd.DataFrame)
                                   else (key, 'DataFrame with many columns')
                                   for key, value in st.session_state.items()]

            session_state_df = pd.DataFrame(session_state_items, columns=['Key', 'Value'])

            # Display the session state in an interactive table
            st.dataframe(session_state_df)

            # Optionally, display the DataFrame with many columns separately with a header
            if 'large_dataframe' in st.session_state:
                st.write("Large DataFrame:")
                st.dataframe(st.session_state['large_dataframe'])

            st.markdown("### Session states with many columns is shown below:")
            for key, value in st.session_state.items():
                if isinstance(value, pd.DataFrame):
                    st.write(f" **{key}**")
                    st.dataframe(value)  # Display DataFrame with horizontal and vertical scrolling

        except Exception as e:
            st.error(f"Error loading session state: {e}")
