
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import math
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt

def show():
    st.title('Direct Damage Estimation')




    st.header("Economic impact of performance-based structural fire design")


    with (st.sidebar):
        # Set up the part for user input file
        st.markdown("## **User Input Parameter**")

        building_parameter_original= st.session_state.building_parameter_original
        building_area=building_parameter_original['Total area'][0]
        Severe_fire_pro_saved = 25.6
        Compartment_num_saved=math.ceil(building_area/1000)
        study_year_saved = 50
        fragility_num_saved = 1
        muq_saved = 780
        sigmaq_saved = 120

        option_analysis_type = st.session_state.option_analysis_type

        if st.checkbox("Reset to default parameter (Direct damage)",value=False):
            option_analysis_type = 'Start a new analysis'
            st.write('**The restored input parameter would not be applied**')



        if 'maintenance_input_original' in st.session_state:
            maintenance_input_original = st.session_state.maintenance_input_original
            study_year_saved = maintenance_input_original.at[0, 'Study year']

        if option_analysis_type == 'Load session variables':
            if 'fragility_parameter_original' in st.session_state:
                fragility_parameter_original = st.session_state.fragility_parameter_original
                Severe_fire_pro_saved = fragility_parameter_original.at[0, 'Probability of severe fire (*10-7)']
                Compartment_num_saved = fragility_parameter_original.at[0, 'Number of compartment']
                fragility_num_saved = fragility_parameter_original.at[0, 'Index of the fragility curves']
                muq_saved = fragility_parameter_original.at[0, 'Location parameter of fire load (mu)']
                sigmaq_saved = fragility_parameter_original.at[0, 'Scale parameter of fire load (sigma)']
                damage_state_cost_value_saved = fragility_parameter_original.at[0, 'Damage cost value']

        Severe_fire_pro = st.number_input("Input probability of severe fire in a compartment (*10-7)", value=Severe_fire_pro_saved)
        Compartment_num = st.number_input("Input number of compartment", value=Compartment_num_saved)
        study_year=study_year_saved
        # study_year = st.number_input("Input study year of the building", value=study_year_saved)

        fragility_curve_method = st.selectbox(
            'How would you like to define the fragility curves',
            ('Use built-in fragility curves', 'Upload file'))
        if fragility_curve_method =='Use built-in fragility curves':

            fragility_curve = pd.read_csv("fragility curve.csv")
            hazard_intensity = np.asarray(fragility_curve.iloc[:,0])
            fragility_num = st.number_input("Input the index of the built-in fragility curves",step=1,value=fragility_num_saved, max_value=10, min_value=1)
            damage_state_num = 4
            upper_bound = (fragility_num) * damage_state_num+1
            lower_bound = (fragility_num - 1) * damage_state_num + 1
            fragility_prob = np.asarray(fragility_curve.iloc[:, lower_bound:upper_bound])


        if fragility_curve_method =='Upload file':
            uploaded_file_fragility = st.file_uploader("Choose a file with fragility functions 1st column: hazard intensity, 2nd to n-th columns: probability")
            fragility_curve = pd.read_csv(uploaded_file_fragility)
            hazard_intensity = np.asarray(fragility_curve.iloc[:,0])
            fragility_num = st.number_input("Input the index of the fragility curves",step=1,value=fragility_num_saved, max_value=10, min_value=1)
            damage_state_num = st.number_input("Input number of damage states", value=4, step=1)
            upper_bound = fragility_num * damage_state_num+1
            lower_bound = (fragility_num - 1) * damage_state_num + 1
            fragility_prob = np.asarray(fragility_curve.iloc[:, lower_bound:upper_bound])

        # Display a text astreamrea for the user to input the array

        construction_cost_df = st.session_state.construction_cost_df
        CI = (construction_cost_df['Floor'][0] + construction_cost_df['Column'][0])/Compartment_num+19.2*1000

        if option_analysis_type == 'Load session variables':
            if 'fragility_parameter_original' in st.session_state:
                damage_state_cost_value=damage_state_cost_value_saved

                st.write("Stored damage state cost value:", damage_state_cost_value)
            else:
                damage_state_cost_value = st.text_area("Enter your damage state value (comma-separated):")
            # Process the input and convert it into a NumPy array
                if damage_state_cost_value:
                    try:
                        input_list = [float(item.strip()) for item in damage_state_cost_value.split(',')]
                        damage_state_cost_value = np.array(input_list)
                        st.write("Input damage state cost value:", damage_state_cost_value)
                    except ValueError:
                        st.write("Invalid input. Please enter a valid comma-separated list of numbers.")
                else:
                    damage_state_cost_value=[0.24*CI, 0.91*CI,1.66*CI,100.00*CI]
                    st.write("Default damage state cost value:", damage_state_cost_value)

        if option_analysis_type == 'Start a new analysis':
            damage_state_cost_value = st.text_area("Enter your damage state value (comma-separated):")
        # Process the input and convert it into a NumPy array
            if damage_state_cost_value:
                try:
                    input_list = [float(item.strip()) for item in damage_state_cost_value.split(',')]
                    damage_state_cost_value = np.array(input_list)
                    st.write("Input damage state cost value:", damage_state_cost_value)
                except ValueError:
                    st.write("Invalid input. Please enter a valid comma-separated list of numbers.")
            else:
                damage_state_cost_value=[0.24*CI, 0.91*CI,1.66*CI,100.00*CI]
                st.write("Default damage state cost value:", damage_state_cost_value)



        fire_load_distribution = st.selectbox(
            'How would you like to define the fire load distribution',
            ('Use given distribution (gumbel distribution)', 'Upload file'))
        if fire_load_distribution=='Use given distribution (gumbel distribution)':
            col1, col2 = st.columns(2)
            with col1:
                muq = st.number_input("Input mean value", value=muq_saved)
            with col2:
                sigmaq = st.number_input("Input standard deviation", value=sigmaq_saved)
            # Generate 1000 random numbers from the gumbel distribution
            qfuel = np.random.gumbel(loc=muq-0.57721*sigmaq*math.sqrt(6)/math.pi, scale=sigmaq*math.sqrt(6)/math.pi,size=10000)

        if fire_load_distribution=='Upload file':
            uploaded_file_fire = st.file_uploader("Choose a file")
            qfuel=np.asarray(uploaded_file_fire.iloc[:,:], float)

        size_fragility = np.shape(hazard_intensity)
        vulnerability_data1 = np.zeros(size_fragility[0])
        vulnerability_data = np.zeros(size_fragility[0])
        for i in range(damage_state_num - 1, 0, -1):
            vulnerability_data1 += np.maximum((-fragility_prob[:, i] + fragility_prob[:, i - 1]),0) * damage_state_cost_value[i-1]

        vulnerability_data = np.maximum(fragility_prob[:, damage_state_num - 1],0) * damage_state_cost_value[damage_state_num - 1] + vulnerability_data1

        damage_value = np.interp(qfuel, hazard_intensity, vulnerability_data)
        damage_value_average=np.average(damage_value)
        environment_impact=st.checkbox("Considering the lifetime environmental impact?",value=False)
        st.session_state.environment_impact = environment_impact

        if environment_impact:
            st.write('**Input the contribution of material at each damage state**')
            input_data = {}

            # Define the number of rows
            rows = 4

            # Column headers
            default_material_proportion = {
                'Content': [0.77, 0.22, 0.22, 0.22],
                'Steel': [0.00, 0.27, 0.50, 0.50],
                'Concrete': [0.00, 0.21, 0.14, 0.14]
            }
            # Create input fields with custom column headers and dynamic default values
            for i in range(rows):
                cols = st.columns(len(default_material_proportion))
                for j, (header, defaults) in enumerate(default_material_proportion.items()):
                    with cols[j]:
                        # Create a unique key for each input based on row and column
                        key = f"{header} {i + 1}"
                        # Ensure the row index does not exceed the list of defaults
                        if i < len(defaults):
                            default_value = defaults[i]
                        else:
                            default_value = ""  # Or any other fallback default value
                        # Collect the input data using text input with a dynamic default value
                        input_data[key] = st.text_input(f"{header} (DS{i + 1})", value=default_value, key=key)

            # Display collected inputs
            st.write("Collected Inputs:")
            st.write(input_data)

            vulnerability_data1_material = np.zeros(size_fragility[0])
            vulnerability_data_material = np.zeros((3,size_fragility[0]))
            damage_value_material = np.zeros((3,qfuel.shape[0]))
            damage_value_material_average=np.zeros(4)
            for j, (header, defaults) in enumerate(default_material_proportion.items()):
                for i in range(damage_state_num -1, 0, -1):
                    vulnerability_data1_material += np.maximum((-fragility_prob[:, i] + fragility_prob[:, i - 1]), 0) * defaults[i-1]*damage_state_cost_value[i-1]
                vulnerability_data_material[j,:] = np.maximum(fragility_prob[:, damage_state_num - 1], 0) * defaults[
                    damage_state_num - 1]*damage_state_cost_value[damage_state_num-1] + vulnerability_data1_material

            for i in range(0,3,1):
                damage_value_material[i,:] = np.interp(qfuel, hazard_intensity, vulnerability_data_material[i,:])
            damage_value_material_average = np.average(damage_value_material,1)



        st.markdown("**parameters for alternative design**")
        #alter_design = st.checkbox('Do you want to get damage cost value for alternative design?')
        if "alter_design" in st.session_state:
            alter_design = st.session_state.alter_design
        else:
            alter_design=[]
        if alter_design:
            fragility_num_alt_saved = 1

            if option_analysis_type == 'Load session variables':
                if 'fragility_parameter_alt' in st.session_state:
                    fragility_parameter_alt=st.session_state.fragility_parameter_alt
                    fragility_num_alt_saved = fragility_parameter_alt.at[0, 'Index of the fragility curves for alt.']
                    damage_state_cost_value_alt_saved = fragility_parameter_alt.at[0, 'Damage cost value for alt.']
                    damage_state_cost_value_alt = damage_state_cost_value_alt_saved
                    print(damage_state_cost_value_alt)
                    st.write("Stored damage state cost value:", np.array(damage_state_cost_value_alt,dtype=int))
                else:
                    damage_state_cost_value_alt = st.text_area("Enter your damage state value (comma-separated) alt.:")
                    # Process the input and convert it into a NumPy array
                    if damage_state_cost_value_alt:
                        try:
                            input_list = [float(item.strip()) for item in damage_state_cost_value_alt.split(',')]
                            damage_state_cost_value_alt = np.array(input_list)
                            st.write("Input damage state cost value for alt.:", math.ceil(damage_state_cost_value_alt))
                        except ValueError:
                            st.write("Invalid input. Please enter a valid comma-separated list of numbers.")
                    else:
                        construction_cost_df_alt = st.session_state.construction_cost_df_alt

                        CI_alt = (construction_cost_df_alt['Floor'][0] + construction_cost_df_alt['Column'][0])/Compartment_num+19.2 * 1000
                        damage_state_cost_value_alt = [0.24 * CI_alt, 0.91 * CI_alt, 1.66 * CI_alt, 100.00 * CI_alt]
                        st.write("Default damage state cost value alt.:", math.ceil(damage_state_cost_value_alt))


            fragility_num_alt = st.number_input("Input the index of the built-in fragility curves (alt.)", step=1,value=fragility_num_alt_saved, max_value=10,min_value=1)
            upper_bound = (fragility_num_alt) * damage_state_num+1
            lower_bound = (fragility_num_alt - 1) * damage_state_num + 1
            fragility_prob_alt = np.asarray(fragility_curve.iloc[:, lower_bound:upper_bound])
            # Display a text astreamrea for the user to input the array
            # damage_state_cost_value_alt = st.text_area("Enter your damage state value (comma-separated) alt.:")
            # Process the input and convert it into a NumPy array
            if option_analysis_type == 'Start a new analysis':
                damage_state_cost_value_alt = st.text_area("Enter your damage state value (comma-separated) alt.:")
                # Process the input and convert it into a NumPy array
                if damage_state_cost_value_alt:
                    try:
                        input_list = [float(item.strip()) for item in damage_state_cost_value_alt.split(',')]
                        damage_state_cost_value_alt = np.array(input_list)
                        st.write("Input damage state cost value for alt.:", damage_state_cost_value_alt)
                    except ValueError:
                        st.write("Invalid input. Please enter a valid comma-separated list of numbers.")
                else:
                    construction_cost_df_alt = st.session_state.construction_cost_df_alt
                    CI_alt = (construction_cost_df_alt['Floor'][0] + construction_cost_df_alt['Column'][
                        0]) / Compartment_num + 19.2 * 1000
                    damage_state_cost_value_alt = [0.24 * CI_alt, 0.91 * CI_alt, 1.66 * CI_alt, 100.00 * CI_alt]
                    st.write("Default damage state cost value alt.:", damage_state_cost_value_alt)


            vulnerability_data1_alt = np.zeros(size_fragility[0])
            vulnerability_data_alt = np.zeros(size_fragility[0])
            for i in range(damage_state_num - 1, 0, -1):
                vulnerability_data1_alt += np.maximum((-fragility_prob_alt[:, i] + fragility_prob_alt[:, i - 1]), 0) * \
                                       damage_state_cost_value_alt[i - 1]

            vulnerability_data_alt = np.maximum(fragility_prob_alt[:, damage_state_num - 1], 0) * damage_state_cost_value_alt[
                damage_state_num - 1] + vulnerability_data1_alt

            damage_value_alt = np.interp(qfuel, hazard_intensity, vulnerability_data_alt)
            damage_value_average_alt = np.average(damage_value_alt)
            if environment_impact:
                vulnerability_data1_material_alt = np.zeros(size_fragility[0])
                vulnerability_data_material_alt = np.zeros((3, size_fragility[0]))
                damage_value_material_alt = np.zeros((3, qfuel.shape[0]))
                damage_value_material_average_alt = np.zeros(4)
                for j, (header, defaults) in enumerate(default_material_proportion.items()):
                    for i in range(damage_state_num - 1, 0, -1):
                        vulnerability_data1_material_alt += np.maximum((-fragility_prob_alt[:, i] + fragility_prob_alt[:, i - 1]), 0) * \
                                                        defaults[i - 1] * damage_state_cost_value[i - 1]
                    vulnerability_data_material_alt[j, :] = np.maximum(fragility_prob_alt[:, damage_state_num - 1], 0) * defaults[
                        damage_state_num - 1] * damage_state_cost_value[damage_state_num - 1] + vulnerability_data1_material_alt

                for i in range(0, 3, 1):
                    damage_value_material_alt[i, :] = np.interp(qfuel, hazard_intensity, vulnerability_data_material_alt[i, :])
                damage_value_material_average_alt = np.average(damage_value_material_alt, 1)

    with st.container():
        st.subheader('Results')
        st.write("---")


        Annual_loss=Severe_fire_pro*damage_value_average*10e-7*Compartment_num

        data = {
            'Average loss per severe fire': [int(damage_value_average)],
            'Annual loss': [int(Annual_loss)],
            'Study year': [int(study_year)],
            'Study year loss': [int(Annual_loss*study_year)],
            'Severe fire frequency per compartment (*10-7)': [Severe_fire_pro],
        }
        direct_damage_loss = pd.DataFrame(data)

        if environment_impact:
            ei_cost = {
                'Average content loss per sever fire': [int(damage_value_material_average[0])],
                'Average steel loss per sever fire': [int(damage_value_material_average[1])],
                'Average concrete loss per sever fire': [int(damage_value_material_average[2])],
            }
            st.session_state.ei_cost = ei_cost

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
            if environment_impact:
                st.dataframe(ei_cost)
            st.session_state.direct_damage_loss = direct_damage_loss  # Attribute API
            st.pyplot(f1)

        if alter_design:

            #st.write("## results for alternative design")

            Annual_loss_alt = Severe_fire_pro * damage_value_average_alt * 10e-7 * Compartment_num
            data_alt = {

                'Average loss per severe fire': [int(damage_value_average_alt)],
                'Annual loss': [int(Annual_loss_alt)],
                'Study year': [int(study_year)],
                'Study year loss': [int(Annual_loss_alt * study_year)],
                'Severe fire frequency per compartment (*10-7)': [Severe_fire_pro],

            }
            direct_damage_loss_alt = pd.DataFrame(data_alt)
            #st.write(" Summary for alternative design")

            if environment_impact:
                ei_cost_alt = {
                    'Average content loss per sever fire':[int(damage_value_material_average_alt[0])],
                    'Average steel loss per sever fire':[int(damage_value_material_average_alt[1])],
                    'Average concrete loss per sever fire':[int(damage_value_material_average_alt[2])],
                }
                st.session_state.ei_cost_alt = ei_cost_alt

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

                if environment_impact:
                    st.dataframe(ei_cost_alt)
                st.session_state.direct_damage_loss_alt = direct_damage_loss_alt  # Attribute API
                st.pyplot(f2)

            data = {
                'Index of the fragility curves for alt.': [fragility_num_alt],
                'Damage cost value for alt.': [damage_state_cost_value_alt],
            }
            fragility_parameter_alt = pd.DataFrame(data)
            st.session_state.fragility_parameter_alt = fragility_parameter_alt  # Attribute API

        data = {
            'Probability of severe fire (*10-7)': [Severe_fire_pro],
            'Number of compartment': [Compartment_num],
            'Study year': [study_year],
            'Method of defining the fragility curves': [fragility_curve_method],
            'Index of the fragility curves': [fragility_num],
            'Damage state number': [damage_state_num],
            'Damage cost value': [damage_state_cost_value],
            'Location parameter of fire load (mu)': [muq],
            'Scale parameter of fire load (sigma)': [sigmaq],
        }
        fragility_parameter_original = pd.DataFrame(data)
        st.session_state.fragility_parameter_original = fragility_parameter_original  # Attribute API



        st.write("---")


