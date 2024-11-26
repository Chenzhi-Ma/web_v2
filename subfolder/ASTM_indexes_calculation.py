
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
def show():
    st.title('ASTM index calculation')



    st.header("Economic impact of performance-based structural fire design")

    with st.sidebar:
        st.markdown("## **User Input Parameter**")
        astm_index_method = st.selectbox(
            'How would you like to input cost value (present pvalue)',
            ('Based on previous data','type value', 'upload file with given format'))
        #st.markdown("**parameters for alternative design**")
        #alter_design = st.checkbox('Do you want to get damage cost value for alternative design?')

        if "alter_design" in st.session_state:
            alter_design = st.session_state.alter_design
        else:
            alter_design=[]

        if "environment_impact" in st.session_state:
            environment_impact=st.session_state.environment_impact
        else:
            environment_impact=[]


        if astm_index_method == 'Based on previous data':
            construction_cost_df=st.session_state.construction_cost_df
            CI_ref=construction_cost_df['Floor'][0]+construction_cost_df['Column'][0]
            direct_damage_loss=st.session_state.direct_damage_loss
            DD_ref=direct_damage_loss['Study year loss']
            indirect_damage_ref=st.session_state.indirect_damage_ref
            ID_ref=indirect_damage_ref['Study year loss']
            Maintenance_cost_df=st.session_state.Maintenance_cost_df   # Attribute API
            CM_ref=Maintenance_cost_df['Maintenance cost']
            Cobenefits_value_df=st.session_state.Cobenefits_value_df    # Attribute API
            CB_ref=0

            pvlcc_ref = CI_ref + DD_ref + ID_ref+CM_ref - CB_ref

            if alter_design:
                construction_cost_df_alt=st.session_state.construction_cost_df_alt
                CI_alt=construction_cost_df_alt['Floor'][0]+construction_cost_df_alt['Column'][0]
                direct_damage_loss_alt=st.session_state.direct_damage_loss_alt
                DD_alt=direct_damage_loss_alt['Study year loss']
                indirect_damage_alt = st.session_state.indirect_damage_alt    # Attribute API
                ID_alt=indirect_damage_alt['Study year loss']
                maintenance_cost_total_alt=st.session_state.maintenance_cost_total_alt  # Attribute API
                CM_alt=maintenance_cost_total_alt['Maintenance cost']
                Cobenefits_value_df_alt=st.session_state.Cobenefits_value_df_alt    # Attribute API
                CB_alt=Cobenefits_value_df_alt['Reduction in rent loss']
                extra_cost_df=st.session_state.extra_cost_df    # Attribute API

                Extra_ref =extra_cost_df.at[
                        0, 'Extra cost alt.']

                pvlcc_alt = CI_alt + DD_alt + ID_alt + CM_alt - CB_alt+Extra_ref
                net_b = DD_ref + ID_ref-CB_ref - DD_alt - ID_alt + CB_alt+Extra_ref
                net_c = -CI_ref - CM_ref + CI_alt + CM_alt
                pnv = net_b - net_c






        if astm_index_method == 'type value':

            CI_alt = st.number_input("Input initial construction cost for alternative design")
            CI_ref = st.number_input("Input initial construction cost for reference design")
            DD_alt = st.number_input("Input direct damage loss for alternative design")
            DD_ref = st.number_input("Input direct damage loss cost for reference design")
            ID_alt = st.number_input("Input indirect damage loss for alternative design")
            ID_ref = st.number_input("Input indirect damage loss cost for reference design")
            CM_alt = st.number_input("Input maintenance cost for alternative design")
            CM_ref = st.number_input("Input maintenance cost  for reference design")
            CB_alt = st.number_input("Input co-benefit for alternative design")
            CB_ref = st.number_input("Input co-benefit cost for reference design")

            net_b = DD_ref + ID_ref-CB_ref - DD_alt - ID_alt + CB_alt
            net_c = -CI_ref - CM_ref + CI_alt + CM_alt
            pvlcc = [0, 0]  # Initialize the list

            pvlcc[0] = CI_ref + CM_ref + DD_ref + ID_ref - CB_ref
            pvlcc[1] = CI_ref + CM_ref + DD_alt + ID_alt - CB_alt

            bcr = net_b / net_c
            pnv = net_b - net_c


        if astm_index_method == 'upload file with given format':
            astm_index_method_file = st.file_uploader(
                "Choose a file with all the cost data")

    with st.container():
        st.subheader('Results')
        st.write("---")
        #st.write("BCR,LCC,PNV of provided design values")


        #st.session_state.PVLCC = pvlcc  # Attribute API
        st.markdown("### Present value life cycle cost of given fire design")
        f1 = plt.figure(figsize=(8, 8), dpi=300)
        # two subplots are adopted
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.4, hspace=0.4)
        print(CB_ref)
        value_ref=[int(CI_ref),int(CM_ref.iloc[0]),int(DD_ref.iloc[0]),int(ID_ref.iloc[0]),0,int(CB_ref),int(pvlcc_ref.iloc[0])]

        x = np.arange(len(value_ref))

        if alter_design:
            value_alt = [int(CI_alt), int(CM_alt.iloc[0]), int(DD_alt.iloc[0]), int(ID_alt.iloc[0]),int(Extra_ref), int(CB_alt.iloc[0]),
                         int(pvlcc_alt.iloc[0])]
            data = {
                '': ['Reference design', "Alternative design"],
                "Construction cost": [int(CI_ref),int(CI_alt)],
                "Maintenance": [int(CM_ref.iloc[0]), int(CM_alt.iloc[0])],
                "Direct damage": [int(DD_ref.iloc[0]),int(DD_alt.iloc[0])],
                "Indirect damage": [int(ID_ref.iloc[0]),int(ID_alt.iloc[0])],
                "Extra_cost": [0, int(Extra_ref)],
                "Co-benefit": [int(CB_ref),int(CB_alt.iloc[0])],
            }
            Cost_summary = pd.DataFrame(data)
            bar_width=0.35
            ax1 = f1.add_subplot(2, 1, 1)
            ax1.grid(True)
            p1 = ax1.bar(x - bar_width / 2, value_ref,bar_width, label='Ref.', align='center')
            ax1.set_xticks(x,('Construction','Maintenance','Direct','Indirect', 'Extra cost', 'Co-benefit','PVLCC'))
            p2 = ax1.bar(x + bar_width / 2, value_alt, bar_width, label='Alt.', align='center')
            ax1.set_ylabel('Cost ($)')
            ax1.set_title('Lifetime cost breakdown')
            ax1.legend()

            st.pyplot(f1)
            st.dataframe(Cost_summary, use_container_width=True, hide_index=True)
            st.session_state.Cost_summary = Cost_summary
            data = {
                "PVLCC_ref": [int(pvlcc_ref.iloc[0])],
                "PVLCC_alt": [int(pvlcc_alt.iloc[0])],
                "Net benefit": [int(net_b.iloc[0])],
                "Net cost": [int(net_c.iloc[0])],
                "Present net value": [int(pnv.iloc[0])],
            }
            astm_index = pd.DataFrame(data)
            st.dataframe(data, use_container_width=True, hide_index=True)
            st.session_state.astm_index = astm_index
            print(environment_impact)
            if environment_impact:
                environmental_impact_df=st.session_state.environmental_impact_df
                environmental_impact_df_alt=st.session_state.environmental_impact_df_alt
                data_sfrm_co2 = st.session_state.co2_sfrm
                data_sfrm_co2_alt = st.session_state.co2_sfrm_alt

                data_environment = pd.concat([environmental_impact_df['Total(Study year)'], environmental_impact_df_alt['Total(Study year)']], axis=1,
                                             keys=['Total_Reference', 'Total_Alternative'])

                data_environment_sfrm = pd.concat([data_sfrm_co2['Greenhouse gas(CO_2) from SFRM (kg)'], data_sfrm_co2_alt['Greenhouse gas(CO_2) from SFRM alt. (kg)']], axis=1,
                                             keys=['SFRM_Reference', 'SFRM_Alternative'])

                st.markdown("### Environment impact for the two designs")

                st.dataframe(data_environment_sfrm,hide_index=True)
                st.dataframe(data_environment)



        else:
            data = {
                '': ['Reference design'],
                "Construction cost": [int(CI_ref)],
                "Maintenance": [int(CM_ref.iloc[0])],
                "Direct damage": [int(DD_ref.iloc[0])],
                "Indirect damage": [int(ID_ref.iloc[0])],
                "Co-benefit": [int(CB_ref.iloc[0])],
            }
            Cost_summary_ref = pd.DataFrame(data)
            st.dataframe(Cost_summary_ref, use_container_width=True, hide_index=True)
            st.session_state.Cost_summary_ref = Cost_summary_ref


            bar_width=0.35
            ax1 = f1.add_subplot(2, 1, 1)
            ax1.grid(True)
            p1 = ax1.bar(x - bar_width / 2, value_ref,bar_width, label='Ref.', align='center')
            ax1.set_xticks(x,('Construction','Maintenance','Direct','Indirect','Extra cost', 'Co-benefit' ,'PVLCC'))
            ax1.set_ylabel('Cost ($)')
            ax1.set_title('Lifetime cost breakdown')
            ax1.legend()

            st.pyplot(f1)

        Download = st.checkbox('Do you want to download the detailed member cost')
        if alter_design:
            if Download:
                result = pd.concat([Cost_summary, astm_index], axis=1)
                cost_save_tocsv = result.to_csv(index=False)
               # cost_save_tocsv_string_io = StringIO(cost_save_tocsv)
                # Create a download button
                st.download_button(
                    label="Download CSV",
                    data=cost_save_tocsv,
                    file_name='user_updated_lcc.csv',
                    mime='text/csv',
                )

        else:
            if Download:
                # Assuming the session state variables are already set as in your previous code snippet

                result = pd.concat([Cost_summary_ref, astm_index], axis=1)
                cost_save_tocsv = result.to_csv(index=False)
               # cost_save_tocsv_string_io = StringIO(cost_save_tocsv)
                # Create a download button
                st.download_button(
                    label="Download CSV",
                    data=cost_save_tocsv,
                    file_name='user_updated_lcc.csv',
                    mime='text/csv',
                )
        Download_intermediate_data = st.checkbox('Do you want to download all the intermediate data')
        if Download_intermediate_data:
            if alter_design:
                dataframes_to_save = {
                    'construction_cost_df': st.session_state.get('construction_cost_df'),
                    'construction_cost_df_alt': st.session_state.get('construction_cost_df_alt'),
                    'df_cost_cci': st.session_state.get('df_cost_cci'),
                    'df_cost_cci_alt': st.session_state.get('df_cost_cci_alt'),
                    'direct_damage_loss': st.session_state.get('direct_damage_loss'),
                    'direct_damage_loss_alt': st.session_state.get('direct_damage_loss_alt'),
                    'indirect_damage_ref': st.session_state.get('indirect_damage_ref'),
                    'indirect_damage_alt': st.session_state.get('indirect_damage_alt'),
                    'Cobenefits_value_df': st.session_state.get('Cobenefits_value_df'),
                    'Cobenefits_value_df_alt': st.session_state.get('Cobenefits_value_df_alt'),
                }

                # Combine the data into a single DataFrame (optional, depending on your needs)
                combined_df = pd.concat(dataframes_to_save.values(), keys=dataframes_to_save.keys())

                # Convert MultiIndex to flat index
                combined_df.index = combined_df.index.to_flat_index()

                # Concatenate Cost_summary and astm_index DataFrames
                final_combined_df = pd.concat([combined_df, Cost_summary, astm_index], axis=1)

                # Save the final combined DataFrame to CSV
                cost_save_tocsv = final_combined_df.to_csv(index=False)

                # Create a download button
                st.download_button(
                    label="Download CSV",
                    data=cost_save_tocsv,
                    file_name='user_updated_lcc1.csv',
                    mime='text/csv',
                )
                st.write("DataFrame is ready for download."),
            else:
                st.write("Only valid when the alternative design is activated."),

