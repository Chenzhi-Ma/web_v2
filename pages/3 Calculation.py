import streamlit as st

from subfolder import Construction_cost_estimation, Direct_damage_estimation, \
    Indirect_damage_estimation, Maintenance_estimation, Co_benefit_estimation, ASTM_indexes_calculation, Calculation,Extra_cost_estimation



# Initialize the current page in session state
if 'shown_page' not in st.session_state:
    st.session_state['shown_page'] = 'Calculation'

# Function to change the current page
def set_page(page_name):
    st.session_state['shown_page'] = page_name

# Define a function for each page that wraps the module function
def show_Calculation():
    Calculation.show()

def show_Construction_cost_estimation():
    Construction_cost_estimation.show()

def show_Maintenance_estimation():
    Maintenance_estimation.show()

def show_Direct_damage_estimation():
    Direct_damage_estimation.show()

def show_Indirect_damage_estimation():
    Indirect_damage_estimation.show()
def show_Extra_cost_estimation():
    Extra_cost_estimation.show()

def show_Co_benefit_estimation():
    Co_benefit_estimation.show()
def show_ASTM_indexes_calculation():
    ASTM_indexes_calculation.show()
# ... define similar functions for the other pages ...

# Sidebar with expanders for navigation
with st.sidebar:

    if st.button("1.Construction cost estimation"):
        set_page("Construction_cost_estimation")
        Current_page="Current page: 1.Construction cost estimation"
        st.session_state.Current_page = Current_page

    if st.button("2.Maintenance estimation"):
        set_page("Maintenance_estimation")
        Current_page = "Current page: 2.Maintenance estimation"
        st.session_state.Current_page = Current_page

    if st.button("3.Direct damage estimation"):
        set_page("Direct_damage_estimation")
        Current_page="Current page: 3.Direct damage estimation"
        st.session_state.Current_page = Current_page

    if st.button("4.Indirect damage estimation"):
        set_page("Indirect_damage_estimation")
        Current_page ="Current page: 4.Indirect damage estimation"
        st.session_state.Current_page = Current_page

    if st.button("5.Extra cost estimation"):
        set_page("Extra_cost_estimation")
        Current_page = "Current page: 5.Extra cost estimation"
        st.session_state.Current_page = Current_page

    if st.button("6.Co benefit estimation"):
        set_page("Co_benefit_estimation")
        Current_page="Current page: 5.Co benefit estimation"
        st.session_state.Current_page = Current_page

    if st.button("7.ASTM indexes calculation"):
        set_page("ASTM_indexes_calculation")
        Current_page ="Current page: 6.ASTM indexes calculation"
        st.session_state.Current_page = Current_page
        # ... add buttons for other calculation subpages ...
    if st.button("Restore saved inputs"):
        set_page("Calculation")
        Current_page ="Current page: home page for calculation"
        st.session_state.Current_page = Current_page
    try:
        # Attempt to use the variable
        _ = st.session_state.Current_page
        # If no error, the variable is defined
        variable_defined = True
    except AttributeError:
        # If an AttributeError is caught, the variable is not defined
        variable_defined = False

    # Now you can use the variable_defined flag to determine if Current_page is defined

    if variable_defined:
        st.write(st.session_state.Current_page)
    else:
        st.write("Please start from step 1")

# Call the function to render the current page
page_name_to_function = {
    'Calculation': show_Calculation,
    'Construction_cost_estimation': show_Construction_cost_estimation,
    'Maintenance_estimation': show_Maintenance_estimation,
    'Direct_damage_estimation': show_Direct_damage_estimation,
    'Indirect_damage_estimation': show_Indirect_damage_estimation,
    'Extra_cost_estimation': show_Extra_cost_estimation,
    'Co_benefit_estimation': show_Co_benefit_estimation,
    'ASTM_indexes_calculation': show_ASTM_indexes_calculation,
    # ... map the rest of your pages ...
}

page_name_to_function[st.session_state['shown_page']]()
