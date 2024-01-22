import streamlit as st

from subfolder import Construction_cost_estimation, Direct_damage_estimation, \
    Indirect_damage_estimation, Maintenance_estimation, Co_benefit_estimation, ASTM_indexes_calculation, Calculation



# Initialize the current page in session state
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Calculation'

# Function to change the current page
def set_page(page_name):
    st.session_state['current_page'] = page_name

# Define a function for each page that wraps the module function
def show_Calculation():
    Calculation.show()

def show_Construction_cost_estimation():
    Construction_cost_estimation.show()

def show_Direct_damage_estimation():
    Direct_damage_estimation.show()

def show_Indirect_damage_estimation():
    Indirect_damage_estimation.show()

def show_Maintenance_estimation():
    Maintenance_estimation.show()

def show_Co_benefit_estimation():
    Co_benefit_estimation.show()
def show_ASTM_indexes_calculation():
    ASTM_indexes_calculation.show()
# ... define similar functions for the other pages ...

# Sidebar with expanders for navigation
with st.sidebar:

    if st.button("1.Construction cost estimation"):
        set_page("Construction_cost_estimation")
    if st.button("2.Direct_damage_estimation"):
        set_page("Direct_damage_estimation")
    if st.button("3.Indirect_damage_estimation"):
        set_page("Indirect_damage_estimation")
    if st.button("4.Maintenance_estimation"):
        set_page("Maintenance_estimation")
    if st.button("5.Co_benefit_estimation"):
        set_page("Co_benefit_estimation")
    if st.button("6.ASTM_indexes_calculation"):
        set_page("ASTM_indexes_calculation")

        # ... add buttons for other calculation subpages ...

    # ... add any other buttons or expanders for navigation ...

# Call the function to render the current page
page_name_to_function = {
    'Calculation': show_Calculation,
    'Construction_cost_estimation': show_Construction_cost_estimation,
    'Direct_damage_estimation': show_Direct_damage_estimation,
    'Indirect_damage_estimation': show_Indirect_damage_estimation,
    'Maintenance_estimation': show_Maintenance_estimation,
    'Co_benefit_estimation': show_Co_benefit_estimation,
    'ASTM_indexes_calculation': show_ASTM_indexes_calculation,
    # ... map the rest of your pages ...
}

page_name_to_function[st.session_state['current_page']]()
