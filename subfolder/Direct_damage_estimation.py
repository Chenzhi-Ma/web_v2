
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt

def show():
    st.title('Direct Damage Estimation')




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
            fragility_num = st.number_input("Input the index of the built-in fragility curves",step=1, max_value=10, min_value=1)
            upper_bound = (fragility_num) * 4+1
            lower_bound = (fragility_num - 1) * 4 + 1
            fragility_prob = np.asarray(fragility_curve.iloc[:, lower_bound:upper_bound])
            damage_state_num=4

        if fragility_curve_method =='Upload file':
            uploaded_file_fragility = st.file_uploader("Choose a file with fragility functions 1st column: hazard intensity, 2nd to n-th columns: probability")
            damage_state_num = st.number_input("Input number of damage states", value=1, step=1)


        # Display a text astreamrea for the user to input the array

        construction_cost_df = st.session_state.construction_cost_df
        CI = construction_cost_df['Floor'][0] + construction_cost_df['Column'][0]

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
            damage_state_cost_value=[1.00*CI,10.00*CI,100.00*CI,1000.00*CI]

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
            qfuel = np.random.gumbel(loc=muq, scale=sigmaq,size=10000)

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
        st.markdown("**parameters for alternative design**")
        #alter_design = st.checkbox('Do you want to get damage cost value for alternative design?')
        if "alter_design" in st.session_state:
            alter_design = st.session_state.alter_design
        else:
            alter_design=[]
        if alter_design:

            fragility_curve_method_alt = st.selectbox(
                'How would you like to define the fragility curves (alt.)',
                ('Use built-in fragility curves', 'Upload file'))

            if fragility_curve_method_alt == 'Use built-in fragility curves':

                fragility_num_alt = st.number_input("Input the index of the built-in fragility curves (alt.)", step=1, max_value=10,min_value=1)

                upper_bound = (fragility_num_alt) * 4+1
                lower_bound = (fragility_num_alt - 1) * 4 + 1
                fragility_prob_alt = np.asarray(fragility_curve.iloc[:, lower_bound:upper_bound])
                damage_state_num = 4

            if fragility_curve_method_alt == 'Upload file':
                uploaded_file_fragility = st.file_uploader(
                    "Choose a file with fragility functions 1st column: hazard intensity, 2nd to n-th columns: probability")
                damage_state_num = st.number_input("Input number of damage states", value=1, step=1)

            # Display a text astreamrea for the user to input the array

            damage_state_cost_value_alt = st.text_area("Enter your damage state value (comma-separated) alt.:")
            # Process the input and convert it into a NumPy array
            if damage_state_cost_value_alt:
                try:
                    input_list = [float(item.strip()) for item in damage_state_cost_value_alt.split(',')]
                    damage_state_cost_value_alt = np.array(input_list)
                    st.write("Input Array:", damage_state_cost_value_alt)
                except ValueError:
                    st.write("Invalid input. Please enter a valid comma-separated list of numbers.")
            else:
                damage_state_cost_value_alt = damage_state_cost_value
            vulnerability_data1_alt = np.zeros(size_fragility[0])
            vulnerability_data_alt = np.zeros(size_fragility[0])
            for i in range(damage_state_num - 1, 0, -1):
                vulnerability_data1_alt += np.maximum((-fragility_prob_alt[:, i] + fragility_prob_alt[:, i - 1]), 0) * \
                                       damage_state_cost_value[i - 1]

            vulnerability_data_alt = np.maximum(fragility_prob_alt[:, damage_state_num - 1], 0) * damage_state_cost_value[
                damage_state_num - 1] + vulnerability_data1_alt

            damage_value_alt = np.interp(qfuel, hazard_intensity, vulnerability_data_alt)
            damage_value_average_alt = np.average(damage_value_alt)


    with st.container():
        st.subheader('Results')
        st.write("---")


        Annual_loss=Severe_fire_pro*damage_value_average*10e-7*Compartment_num

        data = {
            'Average loss per severe fire': [int(damage_value_average)],
            'Annual loss': [int(Annual_loss)],
            'Study year': [int(study_year)],
            'Study year loss': [int(Annual_loss*study_year)],
            'Severe fire frequency per compartment (*10-7)': [int(Severe_fire_pro)],
        }
        direct_damage_loss = pd.DataFrame(data)

        # st.write(" Summary for reference design")

        f1 = plt.figure(figsize=(4, 12), dpi=300)
        # two subplots are adopted
        ax1 = f1.add_subplot(4, 1, 1)
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.4, hspace=0.4)
        ax1.grid(True)
        p1 = ax1.plot(hazard_intensity,fragility_prob,label='DS1')
        ax1.set_xlabel('Fire load (MJ)')
        ax1.set_ylabel('Probability')
        ax1.set_title('Fragility curves')

        ax2 = f1.add_subplot(4, 1, 2)
        ax2.grid(True)
        p2 = ax2.hist(qfuel, bins=20, edgecolor='black')
        ax2.set_xlabel('Fire load (MJ)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Fire load distribution')

        ax3 = f1.add_subplot(4, 1, 3)
        ax3.grid(True)
        p3 = ax3.hist(damage_value, bins=20, edgecolor='black')
        ax3.set_xlabel('Damage value ($)')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Damage value distribution per severe fire')


        ax4 = f1.add_subplot(4, 1, 4)
        ax4.grid(True)
        p3 = ax4.plot(hazard_intensity,vulnerability_data)
        ax4.set_xlabel('Fire load (MJ)')
        ax4.set_ylabel('Vulnerability ($)')
        ax4.set_title('vulnerability curves')

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Results for reference design**")
            st.dataframe(direct_damage_loss, use_container_width=True, hide_index=True)
            st.session_state.direct_damage_loss = direct_damage_loss  # Attribute API
            st.pyplot(f1)

        if alter_design:

            st.write("## results for alternative design")

            Annual_loss_alt = Severe_fire_pro * damage_value_average_alt * 10e-7 * Compartment_num
            data_alt = {

                'Average loss per severe fire': [int(damage_value_average_alt)],
                'Annual loss': [int(Annual_loss_alt)],
                'Study year': [int(study_year)],
                'Study year loss': [int(Annual_loss_alt * study_year)],
                'Severe fire frequency per compartment (*10-7)': [int(Severe_fire_pro)],
            }
            direct_damage_loss_alt = pd.DataFrame(data_alt)
            st.write(" Summary for alternative design")





            f2 = plt.figure(figsize=(4, 12), dpi=300)
            # two subplots are adopted
            ax1 = f2.add_subplot(4, 1, 1)
            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.4, hspace=0.4)
            ax1.grid(True)
            p1 = ax1.plot(hazard_intensity, fragility_prob_alt, label='DS1')
            ax1.set_xlabel('Fire load (MJ)')
            ax1.set_ylabel('Probability')
            ax1.set_title('Fragility curves')


            ax2 = f2.add_subplot(4, 1, 2)
            ax2.grid(True)
            p2 = ax2.hist(qfuel, bins=20, edgecolor='black')
            ax2.set_xlabel('Fire load (MJ)')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Fire load distribution')

            ax3 = f2.add_subplot(4, 1, 3)
            ax3.grid(True)
            p3 = ax3.hist(damage_value_alt, bins=20, edgecolor='black')
            ax3.set_xlabel('Damage value ($)')
            ax3.set_ylabel('Frequency')
            ax3.set_title('Damage value distribution per severe fire')

            ax4 = f2.add_subplot(4, 1, 4)
            ax4.grid(True)
            p3 = ax4.plot(hazard_intensity, vulnerability_data_alt)
            ax4.set_xlabel('Fire load (MJ)')
            ax4.set_ylabel('Vulnerability ($)')
            ax4.set_title('vulnerability curves')
            with col2:
                st.write("**Results for alternative design**")
                st.dataframe(direct_damage_loss_alt, use_container_width=True, hide_index=True)
                st.session_state.direct_damage_loss_alt = direct_damage_loss_alt  # Attribute API
                st.pyplot(f2)








        st.write("---")
        st.write("curve of vulnerability function")
        st.write("---")
        st.write("bar chart, fire load in 1000 times")
        st.write("---")
        st.write("bar chart, distribution of loss in 1000 times ")
        st.write("---")
        st.write("table, annual loss ")


