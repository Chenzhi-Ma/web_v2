
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
st.set_page_config(page_title="Construction cost estimation")


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

def Modify_database():
    from functions import column_cost, floor_system_cost,fire_service_cost
    import matplotlib.pyplot as plt
    st.header("Economic impact of performance-based structural fire design")


    with st.sidebar:
        st.markdown("## **User Input Parameters**")

        # Set up the input for Column Type selected by users

        BI = st.number_input("Input Building index (start from 1)", value=1, step=1, key=3)
        # Set up the basic non-editable building parameter
        building_index = BI
        Building_type = int(building_information_ori[building_index - 1][8])
        total_story = int(building_information_ori[building_index - 1][2])
        bound = [0, 20, 35, 60, 70, 85, 95, 120, 130]
        #index bound
        low_limit = bound[Building_type - 1]
        up_limit = bound[Building_type]
        #story and area bound
        low_limit_area=min(building_information_ori[low_limit:up_limit,1])
        up_limit_area = max(building_information_ori[low_limit:up_limit, 1])

        low_limit_story = min(building_information_ori[low_limit:up_limit, 2])
        up_limit_story = max(building_information_ori[low_limit:up_limit, 2])


        # default building parameter
        total_floor_area_inp = building_information_ori[building_index - 1][1]  # sq.ft
        story_height_inp = 10  # ft
        bay_total_load_default = [0.115, 0.115, 0.080, 0.08, 0.08, 0.08, 0.08, 0.08]
        bayload_inp = bay_total_load_default[Building_type - 1]  # kips
        baysize1_inp = 20  # ft
        baysize2_inp = 25  # ft


        # Set up the inputs for Material Properties
        Building_para_modi = st.checkbox('Modify default building paramter')
        if Building_para_modi:
            col1,col2 = st.columns(2)
            with col1:
                story_height_inp = st.number_input("story height",value=10, step=1)
            with col2:
                total_floor_area_inp = st.number_input("total floor area (sq.ft)",value=total_floor_area_inp)

            if total_floor_area_inp<low_limit_area or total_floor_area_inp>up_limit_area:
                st.write("Warning: ")
                st.write(f"The total floor area is out of the range in the database, the results on fire service except passive fire protection on steelworks might not be applicable. "
                              f"Min:{low_limit_area} Max:{up_limit_area}")

            col1, col2 = st.columns(2)
            with col1:
                bayload_inp = st.number_input("bay total load (lbf)",value=int(bayload_inp*1000),step=1 )/1000
            with col2:
                total_story = st.number_input("Building storys",value=int(low_limit_story), step=1)

            if total_story<low_limit_story or total_story>up_limit_story:
                st.write("Warning: ")
                st.write(f"The total story is out of the range in the database, the results on fire service except passive fire protection on steelworks might not be applicable. "
                              f"Min:{low_limit_story} Max:{up_limit_story}")

            col1, col2 = st.columns(2)
            with col1:
                baysize1_inp = st.number_input("bay size x direction (ft)",value=25, step=1)
            with col2:
                baysize2_inp = st.number_input("bay size y direction (ft)",value=20, step=1)


        fire_design_para_modi = st.checkbox('Modify default fire design paramter')

        if fire_design_para_modi:

            col1,col2 = st.columns(2)
            with col2:
                column_fire_rating_inp = st.number_input("Column fire rating (hr)",min_value=0,max_value=4,value=2, step=1)
            with col1:
                Beam_fire_rating_inp = st.number_input("Beam fire rating (hr)",min_value=0,max_value=4,value=2, step=1)
            col1, col2 = st.columns(2)
            with col2:
                fire_protection_material_column_inp = st.number_input("Input column fire protection material",min_value=1,value=1, step=1)
            with col1:
                fire_protection_material_beam_inp = st.number_input("Input beam fire protection material",min_value=1,value=1, step=1)
            col1, col2 = st.columns(2)
            with col2:
                fire_protection_percentage_column_inp = st.number_input("Input column fire protection percentage",value=1.00,min_value=0.00, max_value=1.00,step=0.01)
            with col1:
                fire_protection_percentage_beam_inp = st.number_input("Input beam fire protection percentage",value=1.00,min_value=0.00, max_value=1.00,step=0.01)

        else:
            column_fire_rating_inp = int(building_information_ori[building_index - 1][12])
            Beam_fire_rating_inp = int(building_information_ori[building_index - 1][11])
            fire_protection_material_column_inp = 1

            fire_protection_material_beam_inp = 1
            fire_protection_percentage_column_inp=1
            fire_protection_percentage_beam_inp=1

        fire_cost_para_modi = st.checkbox('Modify default fire protection cost value')

        if fire_cost_para_modi:
            uploaded_file_cost = st.file_uploader("Choose a file cost value ")
            st.write("Remark: csv format, base on the sample file, only change the value, can add value for new fire protection material")
        else:
            uploaded_file_cost = default_cost_file

        data_frame = pd.read_csv(uploaded_file_cost)
        # get the column cost arrays
        column_tabular = np.asarray(data_frame.iloc[0:15, 0:8], float)
        # get the indices for different fire protection materials
        row_indices_column = [i + 12 + fire_protection_material_column_inp * 6 for i in range(0, 4)]
        # get the numerical value for given fire protection materials
        column_fire_cost_tabular = np.asarray(data_frame.iloc[row_indices_column, 0:7], float)

        # get the indices for different fire protection materials for beams
        row_indices_beam = [i - 8 + fire_protection_material_beam_inp * 10 for i in range(0, 8)]

        beam_fire_cost_tabular = np.asarray(data_frame.iloc[row_indices_beam, 9:14], float)

        # beam fire cost at different fire rating with given building index
        beam_fire_cost = beam_fire_cost_tabular[Building_type - 1][2:5]

        floor_default_composite = [20.65, 20.65, 19.99, 19.99, 19.99, 19.99, 19.99, 19.99]
        fireprotectionbeam_default = [0.86, 0.86, 0.79, 0.79, 0.79, 0.79, 0.79, 0.79]

        floor_composite = floor_default_composite[Building_type - 1]
        fireprotectionbeam_ori = fireprotectionbeam_default[Building_type - 1]


        column_cost, column_protection_cost, floor_load_max = column_cost(total_floor_area_inp, total_story, baysize1_inp, baysize2_inp,
                                                          bayload_inp,story_height_inp, column_tabular, column_fire_cost_tabular,fire_protection_percentage_column_inp)

        floor_cost, floor_protection_cost = floor_system_cost(total_floor_area_inp, floor_composite, beam_fire_cost,
                                                              fireprotectionbeam_ori,fire_protection_percentage_beam_inp)

        total_cost = totalcost_ori[building_index - 1][2] + floor_cost + column_cost + column_protection_cost[
            column_fire_rating_inp - 1] + floor_protection_cost[Beam_fire_rating_inp - 1]
        total_cost_sqft = total_cost / total_floor_area_inp

        if floor_load_max>1000:
            st.write ("Warning: ")
            st.write ("The floor load is over the max column loading capacity (1000 kips), if want to continue, please use user-defined column cost and capacity data")


        Interpolation_agree = st.checkbox('Enable interpolation when the default building parameter is changed')
        if Interpolation_agree:
            partition_cost, Sprinkler_cost, Fire_pump_cost, Alarm_cost, Ceiling_cost = fire_service_cost(total_floor_area_inp,
                                                                                                         total_story,
                                                                                                         building_information_ori,
                                                                                                         building_index)
        else:
            partition_cost, Sprinkler_cost, Fire_pump_cost, Alarm_cost, Ceiling_cost = [0,0,0,0,0]
        st.write("---")

    with st.container():
        st.subheader('Results')
        st.write("---")

        #define the size of the figure
        f1 = plt.figure(figsize=(8, 8), dpi=200)
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.4, hspace=0.4)

        # two subplots are adopted
        ax1 = f1.add_subplot(2, 1, 1)
        ax1.grid(True)
        column_fire_cost_given_rate=column_protection_cost[column_fire_rating_inp - 1]
        floor_protection_cost_given_rate=floor_protection_cost[Beam_fire_rating_inp - 1]
        p1=ax1.bar([1,2,3,4,5,6,7], [floor_protection_cost_given_rate,column_fire_cost_given_rate,partition_cost,Sprinkler_cost,Fire_pump_cost,Alarm_cost,Ceiling_cost],width=0.4,edgecolor=[1,0,0])
        ax1.set_xticks([1,2,3,4,5,6,7],('Beams','Columns','Partition','Sprinkler', 'Fire pump', 'Alarm', 'Ceiling'))
        ax1.set_ylabel('Cost ($)')
        ax1.set_title('Fire service cost')
        p1[0].set_color([0,0.5,1])
        p1[0].set_edgecolor([0,0,1])
        p1[1].set_color([0,0.5,1])
        p1[1].set_edgecolor([0,0,1])

        # make the y axis can be shown on right side
        ax2 = ax1.twinx()
        p2 = ax2.bar([1, 2, 3, 4, 5, 6, 7],
                     [floor_protection_cost_given_rate, column_fire_cost_given_rate, partition_cost, Sprinkler_cost,
                      Fire_pump_cost, Alarm_cost, Ceiling_cost]/total_cost,width=0.2,edgecolor=[1,0,0])
        ax2.set_ylabel('Cost multiplier', color='red')
        ax2.tick_params(axis='y', labelcolor='red')
        p2[0].set_color([0,0.5,1])
        p2[0].set_edgecolor([0,0,1])
        p2[1].set_color([0,0.5,1])
        p2[1].set_edgecolor([0,0,1])

        #ax1.set_yticks(np.linspace(0, max([floor_protection_cost_given_rate, column_fire_cost_given_rate, partition_cost, Sprinkler_cost,
        #              Fire_pump_cost, Alarm_cost, Ceiling_cost]), 6))
        #ax2.set_yticks(np.linspace(0, max([floor_protection_cost_given_rate, column_fire_cost_given_rate, partition_cost, Sprinkler_cost,
        #              Fire_pump_cost, Alarm_cost, Ceiling_cost]/total_cost), 6))

        # show the table that lists the updated cost data
        data = {
            '': ['Cost ($)',"Cost multiplier"],
            'Floor': [int(floor_protection_cost_given_rate),floor_protection_cost_given_rate/total_cost],
            'Column': [int(column_fire_cost_given_rate),column_fire_cost_given_rate/total_cost],
            'Partition': [int(partition_cost),partition_cost/total_cost],
            'Sprinkler': [int(Sprinkler_cost),Sprinkler_cost/total_cost],
            'Fire pump': [int(Fire_pump_cost),Fire_pump_cost/total_cost],
            'Alarm': [int(Alarm_cost),Alarm_cost/total_cost],
            'Ceiling': [int(Ceiling_cost),Ceiling_cost/total_cost],
        }
        construction_cost_df_updated = pd.DataFrame(data, index=[0,1])
        st.markdown('**Updated cost data with user-defined cost value**')
        st.dataframe(construction_cost_df_updated,use_container_width=True,hide_index=True)


        ax3 = f1.add_subplot(2, 1, 2)

        p3 = ax3.bar([1, 2, 3, 4, 5, 6, 7],
                     building_information_ori[building_index-1, [19, 20, 21, 22, 23, 24, 25]],width=0.4,edgecolor=[1,0,0])

        ax3.set_ylabel('Cost ($))', color='black')
        ax3.tick_params(axis='y', labelcolor='black')
        p3[0].set_color([0,0.5,1])
        p3[0].set_edgecolor([0,0,1])
        p3[1].set_color([0,0.5,1])
        p3[1].set_edgecolor([0,0,1])
        ax3.set_xticks([1,2,3,4,5,6,7],('Beams','Columns','Partition','Sprinkler', 'Fire pump', 'Alarm', 'Ceiling'))
        ax3.set_ylabel('Cost ($)')
        ax3.set_title('Original fire service cost')



        ax4 = ax3.twinx()
        p4 = ax4.bar([1, 2, 3, 4, 5, 6, 7],
                     building_information_ori[building_index-1, [19, 20, 21, 22, 23, 24, 25]]/building_information_ori[building_index-1, 4],width=0.2,edgecolor=[1,0,0])

        ax4.set_ylabel('Cost multiplier', color='red')
        ax4.tick_params(axis='y', labelcolor='red')
        p4[0].set_color([0,0.5,1])
        p4[0].set_edgecolor([0,0,1])
        p4[1].set_color([0,0.5,1])
        p4[1].set_edgecolor([0,0,1])
        ax3.grid(True)


        # show the table that lists the original cost data
        data = {
            '': ['Cost ($)',"Cost multiplier"],
            'Floor': [int(building_information_ori[building_index-1, [19]]),float(building_information_ori[building_index-1, [19]])/total_cost],
            'Column': [int(building_information_ori[building_index-1, [20]]),float(building_information_ori[building_index-1, [20]])/total_cost],
            'Partition': [int(building_information_ori[building_index-1, [21]]),float(building_information_ori[building_index-1, [21]])/total_cost],
            'Sprinkler': [int(building_information_ori[building_index-1, [22]]),float(building_information_ori[building_index-1, [22]])/total_cost],
            'Fire pump': [int(building_information_ori[building_index-1, [23]]),float(building_information_ori[building_index-1, [23]])/total_cost],
            'Alarm': [int(building_information_ori[building_index-1, [24]]),float(building_information_ori[building_index-1, [24]])/total_cost],
            'Ceiling': [int(building_information_ori[building_index-1, [25]]),float(building_information_ori[building_index-1, [25]])/total_cost],
        }
        construction_cost_df_original = pd.DataFrame(data, index=[0,1])
        st.markdown('**Original cost data**')

        st.dataframe(construction_cost_df_original,use_container_width=True,hide_index=True)

        st.pyplot(f1)

        st.session_state.construction_cost_df_original = construction_cost_df_original  # Attribute API
        st.session_state.construction_cost_df = construction_cost_df_updated  # Attribute API

        Download = st.checkbox('Do you want to download the detailed member cost')
        if Download:
            savepath=st.session_state.path_for_save+'user_updated_costdetail.csv'
            construction_cost_df_updated.to_csv(savepath, index=False)

def User_defined_building():
    import pandas as pd
    import numpy as np
    from functions import get_wd_ratio, get_fireprotection_thickness,calculate_fireprotection_cost
    st.header("Economic impact of performance-based structural fire design")
    para_fireprotection=np.zeros([5,2])

    # Set up the second section on the left part
    with (st.sidebar):
        # Set up the part for user input file
        st.markdown("## **User Input File**")
        uploaded_file = st.file_uploader("Choose a csv file")
        if uploaded_file:
            Thickness_method = st.selectbox(
                'How would you like to calculate the protection thickness',
                ('Ignore the thickness, use RSMeans default thickness','Use thickness adjust equation', 'Thickness is given'))

            Cost_method = st.selectbox('What unit cost value you like to use',('RSMeans default value','User defined equation'))

            if Cost_method == 'User defined equation':
                col1, col2= st.columns(2)
                with col1:
                    para_fireprotection[4, 0] = st.number_input("Unit fire protection cost for metal deck, material 1, per sf.")
                with col2:
                    para_fireprotection[4, 1] = st.number_input(
                        "Unit fire protection cost for metal deck, material 2, per sf.")
                No_material = st.selectbox(
                    'How many fire protection material do you have',
                    ('1', '2','3','4'))
                if No_material=='1':
                    col1, col2 = st.columns(2)
                    with col1:
                        para_fireprotection[0,0] = st.number_input("Cost equation parameter a for material 1")
                    with col2:
                        para_fireprotection[0,1] = st.number_input("Cost equation parameter b for material 1")

                elif No_material=='2':
                    col1, col2 = st.columns(2)
                    with col1:
                        para_fireprotection[0,0] = st.number_input("Cost equation parameter a for material 1")
                    with col2:
                        para_fireprotection[0,1] = st.number_input("Cost equation parameter b for material 1")
                    col1, col2 = st.columns(2)
                    with col1:
                        para_fireprotection[1,0] = st.number_input("Cost equation parameter a for material 2")
                    with col2:
                        para_fireprotection[1,1] = st.number_input("Cost equation parameter b for material 2")
                elif No_material=='3':
                    col1, col2 = st.columns(2)
                    with col1:
                        para_fireprotection[0,0] = st.number_input("Cost equation parameter a for material 1")
                    with col2:
                        para_fireprotection[0,1] = st.number_input("Cost equation parameter b for material 1")
                    col1, col2 = st.columns(2)
                    with col1:
                        para_fireprotection[1,0] = st.number_input("Cost equation parameter a for material 2")
                    with col2:
                        para_fireprotection[1,1] = st.number_input("Cost equation parameter b for material 2")
                    col1, col2 = st.columns(2)
                    with col1:
                        para_fireprotection[2,0] = st.number_input("Cost equation parameter a for material 3")
                    with col2:
                        para_fireprotection[2,1] = st.number_input("Cost equation parameter b for material 3")

                elif No_material=='4':
                    col1, col2 = st.columns(2)
                    with col1:
                        para_fireprotection[0,0] = st.number_input("Cost equation parameter a for material 1")
                    with col2:
                        para_fireprotection[0,0] = st.number_input("Cost equation parameter b for material 1")
                    col1, col2 = st.columns(2)
                    with col1:
                        para_fireprotection[1,0] = st.number_input("Cost equation parameter a for material 2")
                    with col2:
                        para_fireprotection[1,1] = st.number_input("Cost equation parameter b for material 2")
                    col1, col2 = st.columns(2)
                    with col1:
                        para_fireprotection[2,0] = st.number_input("Cost equation parameter a for material 3")
                    with col2:
                        para_fireprotection[2,1] = st.number_input("Cost equation parameter b for material 3")
                    col1, col2 = st.columns(2)
                    with col1:
                        para_fireprotection[3,0] = st.number_input("Cost equation parameter a for material 4")
                    with col2:
                        para_fireprotection[3,1] = st.number_input("Cost equation parameter b for material 4")


            else:
                para_fireprotection = [
                    [18.46, 0.4572],  # 1 for sfrm
                    [170.7, 4.654], #2 for intumescent
                    [0,0],
                    [0,0],
                    [2.54]  # price for metal deck, per sf. per inch thickness
                ]

            # input of this function
            material_constant_index = 1

            # import user input file
            user_input = pd.read_csv(uploaded_file)
            # member type
            # 1 is beam, 2 is column, 3 hss member (assume hss cannot be used for beams), 4 metal deck
            member_shape_index_inp = np.asarray(user_input.iloc[:, 0])
            # enclose type
            # case a: 3 sides, case b: 4 sides, case c: box 3 sides, case d: box 4 sides
            enclose_type_inp = np.asarray(user_input.iloc[:, 1])
            # member shape, w16*31 or others
            member_shape_inp = np.asarray(user_input.iloc[:, 2])
            # member number of a specific size
            member_num_inp = np.asarray(user_input.iloc[:, 3])
            # member length of a specific size (inch)
            member_length_inp = np.asarray(user_input.iloc[:, 4])
            # member fire protection thickness, user input value
            member_fire_thick_inp = np.asarray(user_input.iloc[:, 6])
            # member fire rating, user input value
            member_fire_rating_inp = np.asarray(user_input.iloc[:, 7])

            # member fire protection material, user input value
            member_fire_material_inp = np.asarray(user_input.iloc[:, 8])

            # reference member thickness, input
            reference_t = [3 / 8, 13 / 16, 5 / 4];
            # reference member w/d ratio, input
            reference_wd = 0.819
            # material constant, input
            c1_inp = [1.05, 0.86, 1.25, 1.25, 1.01, 0.95]
            c2_inp = [0.61, 0.97, 0.53, 0.25, 0.66, 0.45]

            # total number of members
            num_member = np.shape(member_shape_index_inp)[0]
            # initialize the variables
            member_wholeline = []
            notfound_index = []
            member_parameter_ori = []

            # import the relationship between w/d and thickness of intumescent
            intumescent_thickness = pd.read_csv('intumescent coating.csv')
            intumescent_thick_wd_inp = np.asarray(intumescent_thickness.iloc[:, 3:])
            # member_parameter_wd=[0] * num_member
            member_parameter_wd = np.zeros([num_member])
            member_parameter_peri = np.zeros([num_member])
            member_parameter_surf = np.zeros([num_member])
            # member_parameter output: thickness, cost
            member_parameter_thick = np.zeros([num_member])
            member_unit_price = np.zeros([num_member])
            member_price = np.zeros([num_member])
            member_unit_labor= np.zeros([num_member])
            member_labor = np.zeros([num_member])

            for i in range(0, num_member ):
                text = member_shape_inp[i]
                text = text.replace("*", "×")

                # Find the last occurrence of "×" using rfind()
                last_multiplication_index = max(text.rfind("*"), text.rfind("×"))
                # Extract characters before the last "×"
                input_size1 = text[:last_multiplication_index]
                input_size2 = text[(last_multiplication_index):]
                content, notfound_lable = get_wd_ratio(input_size1, input_size2)
                if notfound_lable != 'found':
                    notfound_index.append(i)

                member_parameter_ori = np.asarray(content[1:])
                # print(3 * (enclose_type_inp[i] - 1) + 1,member_parameter_ori[3 * (enclose_type_inp[i] - 1) + 1])
                member_parameter_wd[i] = member_parameter_ori[3 * (enclose_type_inp[i] - 1) + 1]
                member_parameter_peri[i] = member_parameter_ori[3 * (enclose_type_inp[i] - 1)]
                member_parameter_surf[i] = member_parameter_ori[3 * (enclose_type_inp[i] - 1) + 2]

                # target member w/d ratio
                wd1 = member_parameter_wd[i]
                wd2 = reference_wd
                c1 = c1_inp[material_constant_index - 1];
                c2 = c2_inp[material_constant_index - 1];
                # print(member_fire_rating_inp[i])
                t2 = reference_t[member_fire_rating_inp[i] - 1]
                if Thickness_method == 'Use thickness adjust equation':
                    member_parameter_thick[i] = get_fireprotection_thickness(wd1, member_fire_rating_inp[i],
                                                                         member_fire_material_inp[i],
                                                                         member_shape_index_inp[i], wd2, t2, c1, c2,
                                                                         intumescent_thick_wd_inp)
                    member_unit_price[i]=calculate_fireprotection_cost(member_parameter_thick[i],para_fireprotection,
                                                                       member_parameter_peri[i],member_fire_material_inp[i],member_shape_index_inp[i])
                    member_price[i]=member_unit_price[i]*member_num_inp[i]*member_length_inp[i]/12

                elif Thickness_method == 'Thickness is given':
                    member_unit_price[i] = calculate_fireprotection_cost(member_fire_thick_inp[i], para_fireprotection,
                                                                         member_parameter_peri[i],member_fire_material_inp[i],member_shape_index_inp[i])
                    member_price[i]=member_unit_price[i]*member_num_inp[i]*member_length_inp[i]/12


                elif Thickness_method == 'Ignore the thickness, use RSMeans default thickness':
                    default_cost_input = pd.read_csv(default_cost_file)
                    rsmean_default_beam_cost = np.asarray(default_cost_input.iloc[6:24, 15:24])
                    vector_values = np.arange(1, 7) - 1
                    # Perform element-wise operations
                    result = vector_values * 3 + member_fire_rating_inp[i] - 1
                    fire_protection_cost = [float(rsmean_default_beam_cost[i1, member_fire_material_inp[i]+1]) for i1 in result]
                    exposed_perimeter_inp = [float(rsmean_default_beam_cost[i1, 6]) for i1 in result]
                    labor_inp = [float(rsmean_default_beam_cost[i1, 8]) for i1 in result]
                    m_material, b_material = np.polyfit(exposed_perimeter_inp, fire_protection_cost, 1)
                    m_labor, b_labor = np.polyfit(exposed_perimeter_inp, labor_inp, 1)
                    member_unit_price[i]=m_material*member_parameter_peri[i]+b_material
                    member_unit_labor[i]=m_labor*member_parameter_peri[i]+b_labor

                    member_price[i]=member_unit_price[i]*member_num_inp[i]*member_length_inp[i]/12
                    member_labor[i] = member_unit_labor[i] * member_num_inp[i] * member_length_inp[i]/12


            total_fire_protection_cost = sum(member_price)
            total_fire_protection_cost_material1=0
            total_fire_protection_cost_material2=0
            total_fire_protection_cost_material3=0
            total_fire_protection_cost_material4=0

            total_fire_protection_cost_member1 = 0
            total_fire_protection_cost_member2 = 0
            total_fire_protection_cost_member3 = 0
            total_fire_protection_cost_member4 = 0



            for i in range(0, num_member ):
                if member_fire_material_inp[i]==1:
                    total_fire_protection_cost_material1+=member_price[i]
                elif member_fire_material_inp[i]==2:
                    total_fire_protection_cost_material2 += member_price[i]
                elif member_fire_material_inp[i] == 3:
                    total_fire_protection_cost_material3 += member_price[i]
                elif member_fire_material_inp[i] == 4:
                    total_fire_protection_cost_material4 += member_price[i]

                if member_shape_index_inp[i] == 1:
                    total_fire_protection_cost_member1 += member_price[i]
                elif member_shape_index_inp[i] == 2:
                    total_fire_protection_cost_member2 += member_price[i]
                elif member_shape_index_inp[i] == 3:
                    total_fire_protection_cost_member3 += member_price[i]
                elif member_shape_index_inp[i] == 4:
                    total_fire_protection_cost_member4 += member_price[i]

    with st.container():
        st.subheader('Results')
        st.write("---")
        if uploaded_file==None:
            st.markdown("**Please upload input file**")


            # summary the results we got
        value_material = [total_fire_protection_cost_material1, total_fire_protection_cost_material2,
                  total_fire_protection_cost_material3, total_fire_protection_cost_material4]
        value_member = [total_fire_protection_cost_member1, total_fire_protection_cost_member2,
                  total_fire_protection_cost_member3, total_fire_protection_cost_member4]





        f1 = plt.figure(figsize=(8, 12), dpi=100)
        # two subplots are adopted
        ax1 = f1.add_subplot(3, 2, 1)
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.4, hspace=0.4)

        ax1.grid(True)
        p1 = ax1.bar([i for i in range(1, num_member+1)],np.log10(member_price),width=0.4,edgecolor=[1,0,0])
        ax1.set_xlabel('Member index')
        ax1.set_ylabel('log10(Cost ($))')
        ax1.set_title('Passive fire protection cost')


        ax2 = f1.add_subplot(3, 2, 2)
        ax2.grid(True)
        p2 = ax2.bar([i for i in range(1, num_member+1)],member_price,width=0.4,edgecolor=[1,0,0])
        ax2.set_xlabel('Member index')
        ax2.set_ylabel('Cost ($)')
        ax2.set_title('Passive fire protection cost')



        ax4 = f1.add_subplot(3, 2, 4)
        ax4.grid(True)
        #p4 = ax4.bar([1], total_fire_protection_cost, width=0.4, edgecolor=[1, 0, 0])
        # Categories or labels for the bars (you can customize these)
        categories = ['1', '2', '3', '4']
        # Define colors for each value
        value_colors = ['blue', 'green', 'orange', 'red']
        # Create a figure and axis
        # Create a stacked bar with each value having a different color
        bottom = 0
        bars = ax4.bar(categories, value_material, color=value_colors)
        # for bar, value in zip(bars, values):
        # ax.annotate(str(value), xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
        #          xytext=(5, 0), textcoords='offset points', va='center')

        for value, color, label in zip(value_material, value_colors, categories):
            ax4.bar('Total cost', value, bottom=bottom, color=color, label=label)
            bottom += value
        # Add labels and a title
        ax4.set_ylabel('Cost ($)')
        ax4.set_xlabel('Material')
        ax4.set_title('Total passive fire protection cost')




        # Create a custom legend
        handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in value_colors]
        ax4.legend(handles, categories)
        # Add labels and a legend



        ax5 = f1.add_subplot(3, 2, 5)
        ax5.grid(True)
        bottom = 0
        bars = ax5.bar(categories, value_member, color=value_colors)
        # for bar, value in zip(bars, values):
        # ax.annotate(str(value), xy=(bar.get_width(), bar.get_y() + bar.get_height() / 2),
        #          xytext=(5, 0), textcoords='offset points', va='center')

        for value, color, label in zip(value_member, value_colors, categories):
            ax5.bar('Total cost', value, bottom=bottom, color=color, label=label)
            bottom += value
        # Add labels and a title
        ax5.set_ylabel('Cost ($)')
        ax5.set_xlabel('Member (1 for beam, 2 for column, 4 for metal deck)')
        ax5.set_title('Total passive fire protection cost')




        if Thickness_method == 'Ignore the thickness, use RSMeans default thickness':


            ax3 = f1.add_subplot(3, 2, 3)
            ax3.grid(True)
            p3 = ax3.bar([i for i in range(1, num_member+1)],member_labor,width=0.4,edgecolor=[1,0,0])
            ax3.set_ylabel('Labor hour (hr)')
            ax3.set_title('Labor hour needed for different members')


        st.pyplot(f1)

        data = {
            '': ['Cost ($)'],
            'Floor': [value_member[0]+value_member[3]],
            'Column': [value_member[1]],
            'Partition': [0],
            'Sprinkler': [0],
            'Fire pump': [0],
            'Alarm': [0],
            'Ceiling': [0],
        }
        construction_cost_df = pd.DataFrame(data, index=[0, 1])
        st.session_state.construction_cost_df = construction_cost_df  # Attribute API
        data_array=[member_price,member_labor]


        construction_cost_detail = pd.DataFrame(data_array, index=['Construction cost', 'Labor hour (1 crew)'])
        st.session_state.construction_cost_detail = construction_cost_detail  # Attribute API

        st.session_state.construction_cost_detail

        Download = st.checkbox('Do you want to download the detailed member cost and labor')


        if Download:
            savepath=st.session_state.path_for_save+'userinput_costdetail.csv'
            construction_cost_detail.to_csv(savepath, index=False)


page_names_to_funcs = {
    'Construction cost estimation: Modify database': Modify_database,
    "Construction cost estimation: User defined building": User_defined_building,
}

demo_name = st.sidebar.selectbox("Choose a sub tool", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()