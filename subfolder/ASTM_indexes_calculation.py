
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

        if astm_index_method == 'Based on previous data':
            construction_cost_df=st.session_state.construction_cost_df
            CI_ref=construction_cost_df['Floor'][0]+construction_cost_df['Column'][0]
            direct_damage_loss=st.session_state.direct_damage_loss
            DD_ref=direct_damage_loss['Study year loss']
            indirect_damage_loss_df=st.session_state.indirect_damage_loss_df
            ID_ref=indirect_damage_loss_df['indirect damage loss']
            Maintenance_cost_df=st.session_state.Maintenance_cost_df   # Attribute API
            CM_ref=Maintenance_cost_df['Maintenance cost']
            Cobenefits_value_df=st.session_state.Cobenefits_value_df    # Attribute API
            CB_ref=Cobenefits_value_df['Cobenefit']-Cobenefits_value_df['rent loss']

            pvlcc_ref = CI_ref + DD_ref + ID_ref+CM_ref - CB_ref

            if alter_design:
                construction_cost_df_alt=st.session_state.construction_cost_df_alt
                CI_alt=construction_cost_df_alt['Floor'][0]+construction_cost_df_alt['Column'][0]
                direct_damage_loss_alt=st.session_state.direct_damage_loss_alt
                DD_alt=direct_damage_loss_alt['Study year loss']
                indirect_damage_loss_df_alt=st.session_state.indirect_damage_loss_df_alt
                ID_alt=indirect_damage_loss_df_alt['indirect damage loss']
                maintenance_cost_total_alt=st.session_state.maintenance_cost_total_alt  # Attribute API
                CM_alt=maintenance_cost_total_alt['Maintenance cost']
                Cobenefits_value_df_alt=st.session_state.Cobenefits_value_df_alt    # Attribute API
                CB_alt=Cobenefits_value_df_alt['Cobenefit']-Cobenefits_value_df_alt['rent loss']
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
        st.markdown("### present value life cycle cost of given fire design")
        f1 = plt.figure(figsize=(8, 8), dpi=300)
        # two subplots are adopted
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.4, hspace=0.4)
        value_ref=[int(CI_ref),int(CM_ref.iloc[0]),int(DD_ref.iloc[0]),int(ID_ref.iloc[0]),0,int(CB_ref.iloc[0]),int(pvlcc_ref.iloc[0])]

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
                "Co-benefit": [int(CB_ref.iloc[0]),int(CB_alt.iloc[0])],
            }
            Cost_summary = pd.DataFrame(data)
            bar_width=0.35
            ax1 = f1.add_subplot(2, 1, 1)
            ax1.grid(True)
            p1 = ax1.bar(x - bar_width / 2, value_ref,bar_width, label='Ref.', align='center')
            ax1.set_xticks(x,('Construction','Maintenance','Direct','Indirect', 'Co-benefit','Extra cost', 'PVLCC'))
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
            ax1.set_xticks(x,('Construction','Maintenance','Direct','Indirect', 'Co-benefit','Extra cost', 'PVLCC'))
            ax1.set_ylabel('Cost ($)')
            ax1.set_title('Lifetime cost breakdown')
            ax1.legend()

            st.pyplot(f1)