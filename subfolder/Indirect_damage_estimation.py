
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
def show():
    st.title('Indirect damage estimation')
    indirect_loss_file = 'indirect loss parameters.csv'
    indirect_loss_parameter = pd.read_csv(indirect_loss_file)

    cleanup_repair_table = indirect_loss_parameter.iloc[0:5, 0:6]
    cleanup_repair_time = np.asarray(cleanup_repair_table.iloc[:, 2:], float)

    RecoveryTime_table = indirect_loss_parameter.iloc[7:12, 0:6]
    RecoveryTime_time = np.asarray(RecoveryTime_table.iloc[:, 2:], float)

    Modifier_table = indirect_loss_parameter.iloc[13:19, 0:6]
    Modifier = np.asarray(Modifier_table.iloc[1:, 2:], float)

    RelocationExpense_table = indirect_loss_parameter.iloc[22:27, 0:3]
    RelocationExpense = np.asarray(RelocationExpense_table.iloc[:, 1:], float)

    PercentOwnerOccupied_table = indirect_loss_parameter.iloc[29:34, 0:3]
    PercentOwnerOccupied = np.asarray(PercentOwnerOccupied_table.iloc[:, 2:], float)

    RecaptureFactors_table = indirect_loss_parameter.iloc[29:34, 0:3]
    RecaptureFactors = np.asarray(RecaptureFactors_table.iloc[:, 2:], float)

    proprietorIncome_table = indirect_loss_parameter.iloc[45:50, 0:6]
    proprietorIncome = np.asarray(proprietorIncome_table.iloc[:, 1:], float)
    fragility_curve = st.session_state.fragility_curve

    fragility_parameter_alt=st.session_state.fragility_parameter_alt
    fragility_parameter_original = st.session_state.fragility_parameter_original

    building_parameter_original = st.session_state.building_parameter_original
    Affect_area = building_parameter_original['Total area'][0]
    Compartment_num=fragility_parameter_original.at[0, 'Number of compartment']
    Severe_fire_pro=fragility_parameter_original.at[0,'Probability of severe fire']
    study_year = fragility_parameter_original.at[0,'Study year']

    fragility_num_ref=fragility_parameter_original.at[0, 'Index of the fragility curves']
    hazard_intensity = np.asarray(fragility_curve.iloc[:, 0])
    damage_state_num=4
    upper_bound_ref = fragility_num_ref * damage_state_num + 1
    lower_bound_ref = (fragility_num_ref - 1) * damage_state_num + 1
    fragility_prob_ref = np.asarray(fragility_curve.iloc[:, lower_bound_ref:upper_bound_ref])





    st.header("Economic impact of performance-based structural fire design")

    with st.sidebar:
        # Set up the part for user input file
        st.markdown("## **User Input Parameter**")
        option_analysis_type = st.session_state.option_analysis_type

        if st.checkbox("Reset to default parameter (Indirect damage)",value=False):
            option_analysis_type = 'Start a new analysis'
            st.write('**The restored input parameter would not be applied**')

        indirect_damage_method = st.selectbox(
            'Method to calculate indirect damage',
            ('Default method','Input own value'))

        if option_analysis_type == 'Start a new analysis':
            indirect_damage_loss_saved=0
            indirect_damage_loss_alt_saved = 0

            if option_analysis_type == 'Load session variables':
                if 'indirect_damage_original' in st.session_state:
                    indirect_damage_original = st.session_state.indirect_damage_original
                    indirect_damage_loss_saved = indirect_damage_original.at[
                        0, 'Indirect damage loss']
                else:
                    indirect_damage_loss_saved=0

                if 'indirect_damage_alt' in st.session_state:
                    indirect_damage_alt = st.session_state.indirect_damage_alt
                    indirect_damage_loss_alt_saved = indirect_damage_alt.at[
                        0, 'Indirect damage loss alt.']
                else:
                    indirect_damage_loss_alt_saved=0


        if indirect_damage_method == 'Input own value':
           indirect_damage_loss=st.number_input("Input indirect damage loss",value=indirect_damage_loss_saved)

        if indirect_damage_method == 'Default method':
            building_topology = st.number_input("Input building type", value=1)
            DS4_multiplier = st.number_input("Input multiplier when the fire compartment is in DS4 (to imply the severity of fire spread,"
                                          " 1 means fire confined in 1 compartment, 2 means fire spreadS and 2 compartments are in DS4,"
                                          " 10 means fire spreadS and 2 compartments are in DS4)", value=100)
            size_fragility = np.shape(hazard_intensity)
            disruption_expense1 = np.zeros([size_fragility[0],4])
            rentloss_expense1 = np.zeros([size_fragility[0],4])
            YLOSi1 = np.zeros([size_fragility[0],4])
            RYi1 = np.zeros([size_fragility[0],4])

            RTds=RecoveryTime_time[building_topology-1,:]
            DCi=RelocationExpense[building_topology-1, 1]
            RENTi=RelocationExpense[building_topology-1, 0]
            FAi=Affect_area/Compartment_num #1 single compartment
            RFi=RecaptureFactors[building_topology-1, 0]
            INCi = proprietorIncome[building_topology - 1, 1]
            BCTds=cleanup_repair_time[building_topology-1,:]
            MODds=Modifier[building_topology-1,:]
            LOFds=BCTds*MODds
            # Relocation expense
            for i in range(damage_state_num - 1, 0, -1):
                disruption_expense1[:, i - 1] = np.maximum((-fragility_prob_ref[:, i] + fragility_prob_ref[:, i - 1]), 0)*\
                                       DCi*FAi*(1.0-PercentOwnerOccupied[building_topology-1]/100)
                rentloss_expense1[:, i - 1] = np.maximum((-fragility_prob_ref[:, i] + fragility_prob_ref[:, i - 1]), 0) * \
                                     (DCi+RENTi*RTds[i - 1])*FAi*PercentOwnerOccupied[building_topology-1]/100
                YLOSi1[:, i - 1] =(1-RFi)*FAi*INCi*np.maximum((-fragility_prob_ref[:, i] + fragility_prob_ref[:, i - 1]), 0)*LOFds[i-1]
                RYi1[:, i - 1] = (1.0-PercentOwnerOccupied[building_topology-1]/100)*FAi*RENTi*np.maximum((-fragility_prob_ref[:, i] + fragility_prob_ref[:, i - 1]), 0)*RTds[i - 1]

            disruption_expense = np.maximum(fragility_prob_ref[:, damage_state_num - 1], 0) \
                                 * DCi*FAi*DS4_multiplier*(1.0-PercentOwnerOccupied[building_topology-1]/100) + disruption_expense1.sum(axis=1)
            rentloss_expense = np.maximum(fragility_prob_ref[:, damage_state_num - 1], 0) * \
                               (DCi+RENTi*RTds[damage_state_num - 1])*FAi*DS4_multiplier*PercentOwnerOccupied[building_topology-1]/100 + rentloss_expense1.sum(axis=1)


            YLOSi=(1-RFi)*FAi*DS4_multiplier*INCi*np.maximum(fragility_prob_ref[:, damage_state_num - 1], 0)*LOFds[damage_state_num-1]+YLOSi1.sum(axis=1)
            RYi=(1.0-PercentOwnerOccupied[building_topology-1]/100)*FAi*DS4_multiplier*RENTi*\
                np.maximum(fragility_prob_ref[:, damage_state_num - 1], 0) * RTds[damage_state_num - 1]+RYi1.sum(axis=1)
            qfuel = st.session_state.qfuel

            relocation_loss = np.interp(qfuel, hazard_intensity, disruption_expense+rentloss_expense)
            income_loss = np.interp(qfuel, hazard_intensity, YLOSi)
            rent_loss = np.interp(qfuel, hazard_intensity, RYi)

            relocation_loss_average = np.average(relocation_loss)
            income_loss_average = np.average(income_loss)
            rent_loss_average = np.average(rent_loss)

            # alter_design = st.checkbox('Do you want to get indirect damage cost value for alternative design?')
        st.markdown("**Parameters for alternative design**")
        #alter_design = st.checkbox('Do you want to get damage cost value for alternative design?')

        if "alter_design" in st.session_state:
            alter_design = st.session_state.alter_design
        else:
            alter_design=[]

        if alter_design:
            fragility_num_alt = fragility_parameter_alt.at[0, 'Index of the fragility curves for alt.']
            upper_bound_alt = fragility_num_alt * damage_state_num + 1
            lower_bound_alt = (fragility_num_alt - 1) * damage_state_num + 1
            fragility_prob_alt = np.asarray(fragility_curve.iloc[:, lower_bound_alt:upper_bound_alt])
            if indirect_damage_method == 'Input own value':
                indirect_damage_loss_alt = st.number_input("Input indirection damage loss (alt.)",value=indirect_damage_loss_alt_saved)
            if indirect_damage_method == 'Default method':

                size_fragility = np.shape(hazard_intensity)
                disruption_expense1_alt = np.zeros([size_fragility[0],4])
                rentloss_expense1_alt = np.zeros([size_fragility[0],4])
                YLOSi1_alt = np.zeros([size_fragility[0],4])
                RYi1_alt = np.zeros([size_fragility[0],4])
                RTds = RecoveryTime_time[building_topology - 1, :]
                DCi = RelocationExpense[building_topology - 1, 1]
                RENTi = RelocationExpense[building_topology - 1, 0]
                FAi = Affect_area / Compartment_num  # 1 single compartment
                RFi = RecaptureFactors[building_topology - 1, 0]
                INCi = proprietorIncome[building_topology - 1, 1]
                BCTds = cleanup_repair_time[building_topology - 1, :]
                MODds = Modifier[building_topology - 1, :]
                LOFds = BCTds * MODds

                # Relocation expense
                for i in range(damage_state_num - 1, 0, -1):
                    disruption_expense1_alt[:, i - 1] = np.maximum((-fragility_prob_alt[:, i] + fragility_prob_alt[:, i - 1]), 0) * \
                                           DCi * FAi * (1.0 - PercentOwnerOccupied[building_topology - 1] / 100)
                    rentloss_expense1_alt[:, i - 1]= np.maximum((-fragility_prob_alt[:, i] + fragility_prob_alt[:, i - 1]), 0) * \
                                         (DCi + RENTi * RTds[i - 1]) * FAi * PercentOwnerOccupied[
                                             building_topology - 1] / 100
                    YLOSi1_alt[:, i - 1] = (1 - RFi) * FAi * INCi * np.maximum(
                        (-fragility_prob_alt[:, i] + fragility_prob_alt[:, i - 1]), 0) * LOFds[i - 1]
                    RYi1_alt[:, i - 1] = (1.0 - PercentOwnerOccupied[building_topology - 1] / 100) * FAi * RENTi * np.maximum(
                        (-fragility_prob_alt[:, i] + fragility_prob_alt[:, i - 1]), 0) * RTds[i - 1]


                disruption_expense_alt = np.maximum(fragility_prob_alt[:, damage_state_num - 1], 0) \
                                     * DCi * FAi*DS4_multiplier * (1.0 - PercentOwnerOccupied[building_topology - 1] / 100) + disruption_expense1_alt.sum(axis=1)

                rentloss_expense_alt = np.maximum(fragility_prob_alt[:, damage_state_num - 1], 0) * \
                                   (DCi + RENTi * RTds[damage_state_num - 1]) * FAi*DS4_multiplier * PercentOwnerOccupied[building_topology - 1] / 100 + rentloss_expense1_alt.sum(axis=1)
                YLOSi_alt = (1 - RFi) * FAi*DS4_multiplier * INCi * np.maximum(fragility_prob_alt[:, damage_state_num - 1], 0) * LOFds[
                    damage_state_num - 1] + YLOSi1_alt.sum(axis=1)
                RYi_alt = (1.0 - PercentOwnerOccupied[building_topology - 1] / 100) * FAi*DS4_multiplier * RENTi * \
                      np.maximum(fragility_prob_alt[:, damage_state_num - 1], 0) * RTds[damage_state_num - 1] + RYi1_alt.sum(axis=1)

                qfuel = st.session_state.qfuel

                relocation_loss_alt = np.interp(qfuel, hazard_intensity, disruption_expense_alt + rentloss_expense_alt)
                income_loss_alt = np.interp(qfuel, hazard_intensity, YLOSi_alt)
                rent_loss_alt = np.interp(qfuel, hazard_intensity, RYi_alt)

                relocation_loss_average_alt = np.average(relocation_loss_alt)
                income_loss_average_alt = np.average(income_loss_alt)
                rent_loss_average_alt = np.average(rent_loss_alt)



    with st.container():

        st.subheader('Results')
        st.write("---")
        if indirect_damage_method == 'Default method':
            data = {
                'Relocation loss': [int(relocation_loss_average)],
                'Income loss': [int(income_loss_average)],
                'Rent loss': [int(rent_loss_average)],
                'Total indirect damage loss per severe fire': [int(relocation_loss_average+income_loss_average+rent_loss_average)],
                'Total expected annual indirect damage loss': [int((relocation_loss_average+income_loss_average+rent_loss_average) * Severe_fire_pro * 1e-9*Affect_area)],
                'Study year loss': [int((relocation_loss_average+income_loss_average+rent_loss_average) * Severe_fire_pro * 1e-9* Affect_area* study_year)]
            }

        if indirect_damage_method == 'Input own value':
            data = {
                'Indirect damage loss': [int(indirect_damage_loss)],
            }

        indirect_damage_ref = pd.DataFrame(data)
        st.session_state.indirect_damage_ref = indirect_damage_ref  # Attribute API

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Results for reference design**")
            st.dataframe(indirect_damage_ref, use_container_width=True, hide_index=True)

        if alter_design:
            with col2:
                st.write("**Results for alternative design**")
                if indirect_damage_method == 'Default method':
                    data = {
                        'Relocation loss for alt.': [int(relocation_loss_average_alt)],
                        'Income loss alt.': [int(income_loss_average_alt)],
                        'Rent loss alt.': [int(rent_loss_average_alt)],
                        'Total indirect damage loss alt. per severe fire': [int(relocation_loss_average_alt+income_loss_average_alt+rent_loss_average_alt)],
                        'Total expected annual indirect damage loss alt.': [int((relocation_loss_average_alt+income_loss_average_alt+rent_loss_average_alt)*Severe_fire_pro*1e-9*Affect_area)],
                        'Study year loss': [int((relocation_loss_average_alt+income_loss_average_alt+rent_loss_average_alt)*Severe_fire_pro*1e-9*Affect_area*study_year)]

                    }

                if indirect_damage_method == 'Input own value':
                    data = {
                        'Indirect damage loss alt.': [int(indirect_damage_loss)],
                    }
                indirect_damage_alt = pd.DataFrame(data)

                st.dataframe(indirect_damage_alt, use_container_width=True, hide_index=True)
                st.session_state.indirect_damage_alt = indirect_damage_alt  # Attribute API

