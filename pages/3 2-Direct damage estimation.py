
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
st.set_page_config(page_title="Direct damage estimation")


with open('database_ori_mat.pkl', 'rb') as f:
    database_ori_mat = pickle.load(f)
with open('totalcost_mat.pkl', 'rb') as f:
    totalcost_mat = pickle.load(f)
default_cost_file = 'unit_cost_data.csv'

# import the matlab file .mat, database_original.mat is a 1*1 struct with 7 fields, inlcude all the original data from 130 simulaitons
database_ori = database_ori_mat['database_original']

# get the detailed original value from rsmeans
costdetails_ori_mat = database_ori['costdetails']
costdetails_ori = costdetails_ori_mat[0, 0]

# the cost multiplier
proportion_ori_mat = database_ori['proportion']
proportion_ori = proportion_ori_mat[0, 0]

# import the building information, include the fire rating, floor area, building type, stories
building_information_ori_mat = database_ori['building_information']
# variable in different columns: 1floor area, 2story, 3perimeter, 4total cost, 5sq. cost, 6fire type in IBC, 7fire type index, 8building type,
# 9beam fire rating in rsmeans, 10column fire rating in rsmeans, 11 IBCbeam, 12 IBC column,
# 13 adjusted column cost,
# 14 adjusted column fire protection cost for 1h, 15 adjusted column fire protection cost for 2h, 16 adjusted column fire protection cost for 3h
building_information_ori = building_information_ori_mat[0, 0]

# the total cost,1 - 2 columns: total cost (original rsmeans value, without adjustment in floor system, column, fire rating), second column is sq.ft cost
# 3 - 4 columns: rsmeans value minus the floor system cost, column system cost
# 5 - 6 columns: value with adjusted floor system and columns, fire rating is based on IBC coding

totalcost_ori = totalcost_mat['totalcost_num']
    # define new vlue in the database




st.header("Economic impact of performance-based structural fire design")


with st.sidebar:
    # Set up the part for user input file
    st.markdown("## **User Input Parameter**")


    Severe_fire_pro = st.number_input("Input probability of severe fire in a compartment (*10-7)", value=0.97)
    Compartment_num = st.number_input("Input number of compartment", value=100)
    study_year = st.number_input("Input study year of the building", value=20)

    fragility_curve_method = st.selectbox(
        'How would you like to define the fragility curves',
        ('Use built-in fragility curves', 'Upload file'))
    if fragility_curve_method =='Use built-in fragility curves':

        fragility_curve = pd.read_csv("fragility curve.csv")
        hazard_intensity = np.asarray(fragility_curve.iloc[:,0])
        fragility_num = st.number_input("Input the index of the built-in fragility curves",step=1, max_value=3, min_value=1)
        upper_bound = (fragility_num) * 5
        lower_bound = (fragility_num - 1) * 5 + 1
        fragility_prob = np.asarray(fragility_curve.iloc[:, lower_bound:upper_bound])
        damage_state_num=4

    if fragility_curve_method =='Upload file':
        uploaded_file_fragility = st.file_uploader("Choose a file with fragility functions 1st column: hazard intensity, 2nd to n-th columns: probability")
        damage_state_num = st.number_input("Input number of damage states", value=1, step=1)


    # Display a text astreamrea for the user to input the array

    damage_state_cost_value = st.text_area("Enter your damage state value (comma-separated):")
    # Process the input and convert it into a NumPy array
    if damage_state_cost_value:
        try:
            input_list = [float(item.strip()) for item in damage_state_cost_value.split(',')]
            damage_state_cost_value = np.array(input_list)
            st.write("Input Array:", damage_state_cost_value)
        except ValueError:
            st.write("Invalid input. Please enter a valid comma-separated list of numbers.")
    else:
        damage_state_cost_value=np.zeros(damage_state_num)



    fire_load_distribution = st.selectbox(
        'How would you like to define the fire load distribution',
        ('Use given distribution (gumbel distribution)', 'Upload file'))
    if fire_load_distribution=='Use given distribution (gumbel distribution)':
        col1, col2 = st.columns(2)
        with col1:
            muq = st.number_input("Input Location parameter", value=420)
        with col2:
            sigmaq = st.number_input("Input scale parameter", value=120)
        # Generate 1000 random numbers from the gumbel distribution
        qfuel = np.random.gumbel(loc=muq, scale=sigmaq,size=1000)

    if fire_load_distribution=='Upload file':
        uploaded_file_fire = st.file_uploader("Choose a file")

    size_fragility = np.shape(hazard_intensity)
    vulnerability_data1 = np.zeros(size_fragility[0])
    vulnerability_data = np.zeros(size_fragility[0])
    for i in range(damage_state_num - 1, 0, -1):
        vulnerability_data1 += np.maximum((-fragility_prob[:, i] + fragility_prob[:, i - 1]),0) * damage_state_cost_value[i-1]

    vulnerability_data = np.maximum(fragility_prob[:, damage_state_num - 1],0) * damage_state_cost_value[damage_state_num - 1] + vulnerability_data1

    damage_value = np.interp(qfuel, hazard_intensity, vulnerability_data)
    damage_value_average=np.average(damage_value)

with st.container():
    st.subheader('Results')
    st.write("---")
    st.write("bar chart, curve of fragility function")

    f1 = plt.figure(figsize=(8, 12), dpi=100)
    # two subplots are adopted
    ax1 = f1.add_subplot(4, 2, 1)
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.4, hspace=0.4)
    ax1.grid(True)
    p1 = ax1.plot(hazard_intensity,fragility_prob,label='DS1')
    ax1.set_xlabel('Fire load (MJ)')
    ax1.set_ylabel('Probability')
    ax1.set_title('Fragility curves')

    ax2 = f1.add_subplot(4, 2, 2)
    ax2.grid(True)
    p2 = ax2.hist(qfuel, bins=20, edgecolor='black')
    ax2.set_xlabel('Fire load (MJ)')
    ax2.set_ylabel('Frequency')
    ax2.set_title('Fire load distribution')

    ax3 = f1.add_subplot(4, 2, 3)
    ax3.grid(True)
    p3 = ax3.hist(damage_value, bins=20, edgecolor='black')
    ax3.set_xlabel('Damage value ($)')
    ax3.set_ylabel('Frequency')
    ax3.set_title('Damage value distribution per severe fire')


    ax4 = f1.add_subplot(4, 2, 4)
    ax4.grid(True)
    p3 = ax4.plot(hazard_intensity,vulnerability_data)
    ax4.set_xlabel('Fire load (MJ)')
    ax4.set_ylabel('Vulnerability ($)')
    ax4.set_title('vulnerability curves')

    st.pyplot(f1)
    Annual_loss=Severe_fire_pro*damage_value_average*10e-7*Compartment_num

    data = {
        'Severe fire frequency per compartment (*10-7)': [Severe_fire_pro],
        'Average loss per severe fire': [damage_value_average],
        'Annual loss': [Annual_loss],
        'Study': [study_year],
        'Study year loss': [Annual_loss*study_year],
    }
    direction_damage_loss = pd.DataFrame(data)
    st.dataframe(direction_damage_loss, use_container_width=True, hide_index=True)
    st.session_state.direction_damage_loss = direction_damage_loss  # Attribute API





    st.write("---")
    st.write("curve of vulnerability function")
    st.write("---")
    st.write("bar chart, fire load in 1000 times")
    st.write("---")
    st.write("bar chart, distribution of loss in 1000 times ")
    st.write("---")
    st.write("table, annual loss ")


