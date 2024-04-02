
# Import the necessary packages

import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to PBSFD project! 👋")

# Streamlit app

if st.button(f"Click to show the saved path"):
    st.markdown('**All the downloaded files would be stored at the default path you specified in the browser**')

# upload images

# Convert DataFrame to CSV string

# Display the image based on the file path

st.markdown('''
## Purpose 
This project will quantify the economic impact of alternative, performance-based designs for structural 
performance in fire of composite steel-framed buildings. Experiments at the NIST NFRL are supporting the development 
of new methods to quantify the structural performance in fire, however, wide adoption for design of these engineering 
methods in lieu of the current prescriptive fire protection rules require economic data to highlight possible benefits. 
By providing cost assessment and evaluation of case studies to complement forthcoming design methods, the project 
will contribute to support new provisions in building codes for a more efficient use of resources in the U.S. construction industry.
''')

st.markdown('''
# Source code:  
## [Github](https://github.com/Chenzhi-Ma/web_v2)
''' )


# Save the DataFrame when the user clicks the button
#if st.button('Save DataFrame'):
#    try:
#        df.to_csv(save_path, index=False)
#        st.success(f'DataFrame saved to {save_path}')
#    except Exception as e:
#        st.error(f'An error occurred: {str(e)}')
