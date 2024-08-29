
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost, calculate_affectedarea_and_days,prepare_labels
import matplotlib.pyplot as plt
def show():
    st.title('Indirect damage estimation')
    indirect_loss_file = 'indirect loss parameters.csv'
    indirect_loss_parameter = pd.read_csv(indirect_loss_file)

    # cleanup_repair_table = indirect_loss_parameter.iloc[0:5, 0:6]
    # cleanup_repair_time = np.asarray(cleanup_repair_table.iloc[:, 2:], float)

    # RecoveryTime_table = indirect_loss_parameter.iloc[7:12, 0:6]
    # RecoveryTime_time = np.asarray(RecoveryTime_table.iloc[:, 2:], float)

    Modifier_table = indirect_loss_parameter.iloc[13:19, 0:6]
    Modifier = np.asarray(Modifier_table.iloc[1:, 2:], float)
    # Modifier=1.00

    RelocationExpense_table = indirect_loss_parameter.iloc[22:27, 0:3]
    RelocationExpense = np.asarray(RelocationExpense_table.iloc[:, 1:], float)

    PercentOwnerOccupied_table = indirect_loss_parameter.iloc[29:34, 0:3]
    PercentOwnerOccupied = np.asarray(PercentOwnerOccupied_table.iloc[:, 2:], float)

    RecaptureFactors_table = indirect_loss_parameter.iloc[37:42, 0:5]

    RecaptureFactors = np.asarray(RecaptureFactors_table.iloc[:, 2:], float)



    proprietorIncome_table = indirect_loss_parameter.iloc[45:50, 0:6]
    proprietorIncome = np.asarray(proprietorIncome_table.iloc[:, 1:], float)
    fragility_curve = st.session_state.fragility_curve

    if "alter_design" in st.session_state:
        alter_design = st.session_state.alter_design
    else:
        alter_design = []
    if alter_design:
        fragility_parameter_alt=st.session_state.fragility_parameter_alt

    fragility_parameter_original = st.session_state.fragility_parameter_original

    df_cost_df=st.session_state.df_cost_cci
    Affect_area = df_cost_df['Total floor area (thousand sq.ft)'][0]*1000
    total_cost = df_cost_df.at[0,'Total Construction Cost (thousand $)']*1000


    building_parameter_original = st.session_state.building_parameter_original
    Compartment_area_saved = fragility_parameter_original.at[0, 'Estimated area of the fire compartment']
    Compartment_num=round(Affect_area/Compartment_area_saved)




    Severe_fire_pro=fragility_parameter_original.at[0,'Probability of severe fire']
    study_year = fragility_parameter_original.at[0,'Study year']
    damage_state_cost_value= fragility_parameter_original.at[0, 'Damage cost value']


    fragility_num_ref=fragility_parameter_original.at[0, 'Index of the fragility curves']
    hazard_intensity = np.asarray(fragility_curve.iloc[:, 0])
    damage_state_num=4
    upper_bound_ref = fragility_num_ref * damage_state_num + 1
    lower_bound_ref = (fragility_num_ref - 1) * damage_state_num + 1
    fragility_prob_ref = np.asarray(fragility_curve.iloc[:, lower_bound_ref:upper_bound_ref])





    st.header("Economic impact of performance-based structural fire design")

    with (((st.sidebar))):
        # Set up the part for user input file
        st.markdown("## **User Input Parameter**")
        option_analysis_type = st.session_state.option_analysis_type
        indirect_damage_loss_saved=0
        indirect_damage_loss_alt_saved = 0
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
            building_type_map = {
                'SingleFamilyDwelling': 1,
                'MultiFamilyDwelling': 2,
                'TemporaryLodging': 3,
                'Professional/Technical/BusinessServices': 4,
                'Hospital': 5
            }

            # Select box for building type input
            option = st.selectbox(
                "Input building type",
                list(building_type_map.keys())
            )

            # Get the corresponding value for the selected option
            building_topology = building_type_map[option]
            percentile = st.number_input("Input percentile", value=90)
            closest_index = st.number_input("Breakdown charts for damage state:", value=4)

            closest_index = closest_index-1
            systems = pd.read_csv('systems.csv')
            impeding_factor_medians = pd.read_csv('impeding_factors.csv')
            repair_cost = pd.read_csv('repair_cost.csv')


            qfuel = st.session_state.qfuel
            # selected_qfuel = np.random.choice(qfuel, size=1, replace=False,quantile=percentile/100)
            selected_qfuel = np.percentile(qfuel, percentile)

            affected_days_list = []
            average_closed_area_list = []
            damage_state_list = []
            impede_list = []
            recovery_days_occupancy_list = []
            percent_recovered_list = []
            recovery_days_functionality_list = []
            fully_repaired_list = []
            labs_list, sys_repair_times_list = [], []

            qfuel1 = selected_qfuel
            ds_exceedance_prob = np.zeros(4)
            ds_prob = np.zeros(5)
            for i in range(4):
                ds_exceedance_prob[i] = np.interp(qfuel1, hazard_intensity, fragility_prob_ref[:, i])

            ds_prob[0] = np.maximum(ds_exceedance_prob[0] - ds_exceedance_prob[1], 0)
            ds_prob[1] = np.maximum(ds_exceedance_prob[1] - ds_exceedance_prob[2], 0)
            ds_prob[2] = np.maximum(ds_exceedance_prob[2] - ds_exceedance_prob[3], 0)
            ds_prob[3] = np.maximum(ds_exceedance_prob[3], 0)
            ds_prob[4] = np.maximum(1 - ds_exceedance_prob[0], 0)
            ds_prob = ds_prob / ds_prob.sum()
            # damage_state = np.random.choice([1,2,3,4,0], size=1, p=ds_prob)

            # Fire_loss = damage_state_cost_value[damage_state]
            # damage_state[0]=4

            for damage_state in range(1, 5):
                building_model = {
                    'total_area_sf': building_parameter_original['Total area'][0],  # total square feet of the building
                    'area_per_story_sf': 1000,
                    'compartment_area': 1000,
                    'building_value': building_parameter_original['Total area'][0]*110,
                    'Fire_loss': damage_state_cost_value[damage_state - 1],
                    'percentile': percentile,
                    'repair_cost_ratio': damage_state_cost_value[damage_state - 1] / total_cost
                }

                [impede, recovery_days_occupancy, percent_recovered, recovery_days_functionality, fully_repaired, labs,
                 sys_repair_times] = \
                    calculate_affectedarea_and_days(systems, impeding_factor_medians, repair_cost, building_model,
                                                    damage_state, ds_prob)
                percentage_closed = 1 - percent_recovered
                # Calculate the durations for each percentage closed
                durations = np.diff(recovery_days_functionality, prepend=0)
                # Calculate the total closed area weighted by duration
                total_closed_area = np.sum(percentage_closed * durations)
                # Calculate the total duration
                total_duration = np.sum(durations)
                # Calculate the average closed area
                average_closed_area = total_closed_area / total_duration * building_parameter_original['Total area'][0]
                affected_days = max(recovery_days_functionality)
                affected_days_list.append(affected_days)
                average_closed_area_list.append(average_closed_area)
                damage_state_list.append(damage_state)

                impede_list.append(impede)
                recovery_days_occupancy_list.append(recovery_days_occupancy)
                percent_recovered_list.append(percent_recovered)
                recovery_days_functionality_list.append(recovery_days_functionality)
                fully_repaired_list.append(fully_repaired)
                labs_list.append(labs)
                sys_repair_times_list.append(sys_repair_times)

            average_closed_area_list = np.array(average_closed_area_list)
            affected_days_list = np.array(affected_days_list)
            # day_area_close = average_closed_area_list*affected_days_list

            # # Get the index of the closest value


            # quantile_data_index = np.where(average_closed_area_list * affected_days_list<=quantile_data)[0][0]
            labs_rep = labs_list[closest_index][::-1]
            y_rep = np.array(sys_repair_times_list[closest_index][::-1])

            fig, axs = plt.subplots(3, figsize=(10, 18))  # Create 3 subplots
            labels = prepare_labels(impede_list[closest_index])  # This function could be enhanced as described

            positions = range(len(labels))
            durations = [data['complete_day'] - data['start_day'] for data in impede_list[closest_index].values()]
            starts = [data['start_day'] for data in impede_list[closest_index].values()]

            axs[0].barh(positions, durations, left=starts, color='gray', alpha=0.5)
            axs[0].set_yticks(positions)
            axs[0].set_yticklabels(labels)
            axs[0].set_xlabel('Days')
            axs[0].set_title('Impedance Times by System and Factor')

            x = labs_rep
            y_start = y_rep[:, 0]
            y_duration = y_rep[:, 1]
            # Plot the horizontal bar chart
            bars = axs[1].barh(x, y_duration, left=y_start, color=[0.1, 0.1, 0.1], alpha=0.5, edgecolor='none')
            # Hide the first part of the stacked bars
            for bar in bars:
                bar.set_visible(True)  # Ensure the repair time bars are visible

            axs[1].set_ylabel('Repair Time')
            axs[1].set_xlabel('Days')
            axs[1].legend(['Repair Time'], loc='upper right')

            # Plot the re-occupancy, functionality and fully repaired curves
            axs[2].plot(recovery_days_occupancy_list[closest_index][:], percent_recovered_list[closest_index][:],
                        label='Re-occupancy')

            axs[2].plot(recovery_days_functionality_list[closest_index][:], percent_recovered_list[closest_index][:],
                        label='Functionality')
            axs[2].plot(fully_repaired_list[closest_index][:, 0], fully_repaired_list[closest_index][:, 1],
                        label='Fully Repaired')
            axs[2].set_xlabel('Days')
            axs[2].set_ylabel('Value')
            axs[2].legend()
            axs[2].set_ylim([fully_repaired_list[closest_index][0, 1], fully_repaired_list[closest_index][2, 1]])
            for ax in axs:
                ax.set_xlim([0, 1.1 * max(np.max(recovery_days_occupancy_list[closest_index][:]),
                                          np.max(recovery_days_functionality_list[closest_index][:]),
                                          np.max(fully_repaired_list[closest_index][:, 0]))])

            size_fragility = np.shape(hazard_intensity)
            disruption_expense1 = np.zeros([size_fragility[0],4])
            rentloss_expense1 = np.zeros([size_fragility[0],4])
            YLOSi1 = np.zeros([size_fragility[0],4])
            RYi1 = np.zeros([size_fragility[0],4])
            RTds=affected_days_list
            DCi=RelocationExpense[building_topology-1, 1]
            RENTi=RelocationExpense[building_topology-1, 0]
            FAi = average_closed_area_list

            RFi=RecaptureFactors[building_topology-1, 0]
            INCi = proprietorIncome[building_topology - 1, 1]

            BCTds = affected_days_list
            # MODds=Modifier[building_topology-1,:]
            # LOFds=BCTds*MODds
            LOFds = BCTds

            # Relocation expense
            for i in range(damage_state_num - 1, 0, -1):
                disruption_expense1[:, i - 1] = np.maximum((-fragility_prob_ref[:, i] + fragility_prob_ref[:, i - 1]), 0)*\
                                       DCi*FAi[i-1]*(1.0-PercentOwnerOccupied[building_topology-1]/100)
                rentloss_expense1[:, i - 1] = np.maximum((-fragility_prob_ref[:, i] + fragility_prob_ref[:, i - 1]), 0) * \
                                     (DCi+RENTi*RTds[i - 1])*FAi[i-1]*PercentOwnerOccupied[building_topology-1]/100
                YLOSi1[:, i - 1] =(1-RFi)*FAi[i-1]*INCi*np.maximum((-fragility_prob_ref[:, i] + fragility_prob_ref[:, i - 1]), 0)*LOFds[i-1]
                RYi1[:, i - 1] = (1.0-PercentOwnerOccupied[building_topology-1]/100)*FAi[i-1]*RENTi*np.maximum((-fragility_prob_ref[:, i] + fragility_prob_ref[:, i - 1]), 0)*RTds[i - 1]

            disruption_expense = np.maximum(fragility_prob_ref[:, damage_state_num - 1], 0) \
                                 * DCi*FAi[i-1]*(1.0-PercentOwnerOccupied[building_topology-1]/100) + disruption_expense1.sum(axis=1)
            rentloss_expense = np.maximum(fragility_prob_ref[:, damage_state_num - 1], 0) * \
                               (DCi+RENTi*RTds[damage_state_num - 1])*FAi[i-1]*PercentOwnerOccupied[building_topology-1]/100 + rentloss_expense1.sum(axis=1)


            YLOSi=(1-RFi)*FAi[i-1]*INCi*np.maximum(fragility_prob_ref[:, damage_state_num - 1], 0)*LOFds[damage_state_num-1]+YLOSi1.sum(axis=1)
            RYi=(1.0-PercentOwnerOccupied[building_topology-1]/100)*FAi[i-1]*RENTi*\
                np.maximum(fragility_prob_ref[:, damage_state_num - 1], 0) * RTds[damage_state_num - 1]+RYi1.sum(axis=1)

            relocation_loss = np.interp(qfuel, hazard_intensity, disruption_expense+rentloss_expense)
            income_loss = np.interp(qfuel, hazard_intensity, YLOSi)
            rent_loss = np.interp(qfuel, hazard_intensity, RYi)

            relocation_loss_average = np.average(relocation_loss)
            income_loss_average = np.average(income_loss)
            rent_loss_average = np.average(rent_loss)


            # alter_design = st.checkbox('Do you want to get indirect damage cost value for alternative design?')
        st.markdown("**Parameters for alternative design**")
        #alter_design = st.checkbox('Do you want to get damage cost value for alternative design?')


        if alter_design:
            fragility_num_alt = fragility_parameter_alt.at[0, 'Index of the fragility curves for alt.']
            damage_state_cost_value_alt = fragility_parameter_alt.at[0, 'Damage cost value for alt.']
            upper_bound_alt = fragility_num_alt * damage_state_num + 1
            lower_bound_alt = (fragility_num_alt - 1) * damage_state_num + 1
            fragility_prob_alt = np.asarray(fragility_curve.iloc[:, lower_bound_alt:upper_bound_alt])

            df_cost_df_alt = st.session_state.df_cost_cci_alt
            Affect_area = df_cost_df_alt['Total floor area (thousand sq.ft)'][0] * 1000
            total_cost_alt = df_cost_df_alt.at[0, 'Total Construction Cost (thousand $)'] * 1000


            if indirect_damage_method == 'Input own value':
                indirect_damage_loss_alt = st.number_input("Input indirection damage loss (alt.)",value=indirect_damage_loss_alt_saved)
            if indirect_damage_method == 'Default method':

                affected_days_list_alt = []
                average_closed_area_list_alt = []
                damage_state_list_alt = []
                impede_list_alt = []
                recovery_days_occupancy_list_alt = []
                percent_recovered_list_alt = []
                recovery_days_functionality_list_alt = []
                fully_repaired_list_alt = []
                labs_list_alt, sys_repair_times_list_alt = [], []

                ds_exceedance_prob_alt = np.zeros(4)
                ds_prob_alt = np.zeros(5)
                for i in range(4):
                    ds_exceedance_prob_alt[i] = np.interp(qfuel1, hazard_intensity, fragility_prob_alt[:, i])

                ds_prob_alt[0] = np.maximum(ds_exceedance_prob_alt[0] - ds_exceedance_prob_alt[1], 0)
                ds_prob_alt[1] = np.maximum(ds_exceedance_prob_alt[1] - ds_exceedance_prob_alt[2], 0)
                ds_prob_alt[2] = np.maximum(ds_exceedance_prob_alt[2] - ds_exceedance_prob_alt[3], 0)
                ds_prob_alt[3] = np.maximum(ds_exceedance_prob_alt[3], 0)
                ds_prob_alt[4] = np.maximum(1 - ds_exceedance_prob_alt[0], 0)
                ds_prob_alt = ds_prob_alt / ds_prob_alt.sum()
                # damage_state = np.random.choice([1,2,3,4,0], size=1, p=ds_prob)

                # Fire_loss = damage_state_cost_value[damage_state]
                # damage_state[0]=4

                for damage_state_alt in range(1, 5):
                    building_model_alt = {
                        'total_area_sf': building_parameter_original['Total area'][0],
                        # total square feet of the building
                        'area_per_story_sf': 1000,
                        'compartment_area': 1000,
                        'building_value': building_parameter_original['Total area'][0]*110,
                        'Fire_loss': damage_state_cost_value_alt[damage_state_alt - 1],
                        'percentile': percentile,
                        'repair_cost_ratio': damage_state_cost_value_alt[damage_state_alt - 1] / total_cost_alt
                    }

                    [impede_alt, recovery_days_occupancy_alt, percent_recovered_alt, recovery_days_functionality_alt, fully_repaired_alt,
                     labs_alt, sys_repair_times_alt] = \
                        calculate_affectedarea_and_days(systems, impeding_factor_medians, repair_cost, building_model_alt,
                                                        damage_state_alt, ds_prob_alt)
                    percentage_closed_alt = 1 - percent_recovered_alt
                    # Calculate the durations for each percentage closed
                    durations_alt = np.diff(recovery_days_functionality_alt, prepend=0)
                    # Calculate the total closed area weighted by duration
                    total_closed_area_alt = np.sum(percentage_closed_alt * durations_alt)
                    # Calculate the total duration
                    total_duration_alt = np.sum(durations_alt)
                    # Calculate the average closed area
                    average_closed_area_alt = total_closed_area_alt / total_duration_alt * \
                                          building_parameter_original['Total area'][0]
                    affected_days_alt = max(recovery_days_functionality_alt)
                    affected_days_list_alt.append(affected_days_alt)
                    average_closed_area_list_alt.append(average_closed_area_alt)
                    damage_state_list_alt.append(damage_state_alt)

                    impede_list_alt.append(impede_alt)
                    recovery_days_occupancy_list_alt.append(recovery_days_occupancy_alt)
                    percent_recovered_list_alt.append(percent_recovered_alt)
                    recovery_days_functionality_list_alt.append(recovery_days_functionality_alt)
                    fully_repaired_list_alt.append(fully_repaired_alt)
                    labs_list_alt.append(labs_alt)
                    sys_repair_times_list_alt.append(sys_repair_times_alt)

                average_closed_area_list_alt = np.array(average_closed_area_list_alt)
                affected_days_list_alt = np.array(affected_days_list_alt)
                # day_area_close = average_closed_area_list*affected_days_list

                # # Get the index of the closest value

                # quantile_data_index = np.where(average_closed_area_list * affected_days_list<=quantile_data)[0][0]
                labs_rep_alt = labs_list_alt[closest_index][::-1]
                y_rep_alt = np.array(sys_repair_times_list_alt[closest_index][::-1])

                fig_alt, axs = plt.subplots(3, figsize=(10, 18))  # Create 3 subplots
                labels = prepare_labels(impede_list_alt[closest_index])  # This function could be enhanced as described

                positions = range(len(labels))
                durations = [data['complete_day'] - data['start_day'] for data in impede_list_alt[closest_index].values()]
                starts = [data['start_day'] for data in impede_list_alt[closest_index].values()]

                axs[0].barh(positions, durations, left=starts, color='gray', alpha=0.5)
                axs[0].set_yticks(positions)
                axs[0].set_yticklabels(labels)
                axs[0].set_xlabel('Days')
                axs[0].set_title('Impedance Times by System and Factor')

                x = labs_rep
                y_start = y_rep_alt[:, 0]
                y_duration = y_rep_alt[:, 1]
                # Plot the horizontal bar chart
                bars = axs[1].barh(x, y_duration, left=y_start, color=[0.1, 0.1, 0.1], alpha=0.5, edgecolor='none')
                # Hide the first part of the stacked bars
                for bar in bars:
                    bar.set_visible(True)  # Ensure the repair time bars are visible

                axs[1].set_ylabel('Repair Time')
                axs[1].set_xlabel('Days')
                axs[1].legend(['Repair Time'], loc='upper right')

                # Plot the re-occupancy, functionality and fully repaired curves
                axs[2].plot(recovery_days_occupancy_list_alt[closest_index][:], percent_recovered_list_alt[closest_index][:],
                            label='Re-occupancy')
                axs[2].plot(recovery_days_functionality_list_alt[closest_index][:],
                            percent_recovered_list_alt[closest_index][:],
                            label='Functionality')
                axs[2].plot(fully_repaired_list_alt[closest_index][:, 0], fully_repaired_list_alt[closest_index][:, 1],
                            label='Fully Repaired')
                axs[2].set_xlabel('Days')
                axs[2].set_ylabel('Value')
                axs[2].legend()
                axs[2].set_ylim([fully_repaired_list_alt[closest_index][0, 1], fully_repaired_list_alt[closest_index][2, 1]])
                for ax in axs:
                    ax.set_xlim([0, 1.1 * max(np.max(recovery_days_occupancy_list_alt[closest_index][:]),
                                              np.max(recovery_days_functionality_list_alt[closest_index][:]),
                                              np.max(fully_repaired_list_alt[closest_index][:, 0]))])

                size_fragility = np.shape(hazard_intensity)
                disruption_expense1_alt = np.zeros([size_fragility[0],4])
                rentloss_expense1_alt = np.zeros([size_fragility[0],4])
                YLOSi1_alt = np.zeros([size_fragility[0],4])
                RYi1_alt = np.zeros([size_fragility[0],4])
                RTds =affected_days_list_alt
                DCi = RelocationExpense[building_topology - 1, 1]
                RENTi = RelocationExpense[building_topology - 1, 0]
                FAi = average_closed_area_list_alt
                RFi = RecaptureFactors[building_topology - 1, 0]

                INCi = proprietorIncome[building_topology - 1, 1]
                BCTds = affected_days_list_alt
                # MODds = Modifier[building_topology - 1, :]
                # LOFds = BCTds * MODds
                LOFds = BCTds


                # Relocation expense
                for i in range(damage_state_num - 1, 0, -1):
                    disruption_expense1_alt[:, i - 1] = np.maximum((-fragility_prob_alt[:, i] + fragility_prob_alt[:, i - 1]), 0) * \
                                           DCi * FAi[i-1] * (1.0 - PercentOwnerOccupied[building_topology - 1] / 100)
                    rentloss_expense1_alt[:, i - 1]= np.maximum((-fragility_prob_alt[:, i] + fragility_prob_alt[:, i - 1]), 0) * \
                                         (DCi + RENTi * RTds[i - 1]) * FAi[i-1] * PercentOwnerOccupied[
                                             building_topology - 1] / 100
                    YLOSi1_alt[:, i - 1] = (1 - RFi) * FAi[i-1] * INCi * np.maximum(
                        (-fragility_prob_alt[:, i] + fragility_prob_alt[:, i - 1]), 0) * LOFds[i - 1]
                    RYi1_alt[:, i - 1] = (1.0 - PercentOwnerOccupied[building_topology - 1] / 100) * FAi[i-1] * RENTi * np.maximum(
                        (-fragility_prob_alt[:, i] + fragility_prob_alt[:, i - 1]), 0) * RTds[i - 1]


                disruption_expense_alt = np.maximum(fragility_prob_alt[:, damage_state_num - 1], 0) \
                                     * DCi * FAi[i-1]* (1.0 - PercentOwnerOccupied[building_topology - 1] / 100) + disruption_expense1_alt.sum(axis=1)

                rentloss_expense_alt = np.maximum(fragility_prob_alt[:, damage_state_num - 1], 0) * \
                                   (DCi + RENTi * RTds[damage_state_num - 1]) * FAi[i-1] * PercentOwnerOccupied[building_topology - 1] / 100 + rentloss_expense1_alt.sum(axis=1)
                YLOSi_alt = (1 - RFi) * FAi[i-1] * INCi * np.maximum(fragility_prob_alt[:, damage_state_num - 1], 0) * LOFds[
                    damage_state_num - 1] + YLOSi1_alt.sum(axis=1)



                RYi_alt = (1.0 - PercentOwnerOccupied[building_topology - 1] / 100) * FAi[i-1] * RENTi * \
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
            if indirect_damage_method == 'Default method':
                st.pyplot(fig)

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
                if indirect_damage_method == 'Default method':
                    st.pyplot(fig_alt)
                st.session_state.indirect_damage_alt = indirect_damage_alt  # Attribute API

