import numpy as np

# Define functions for searching data
def FindIndexfromList(List, Target):
    # This function find a target from a list and return the index of the target's position
    # Inputs:
    # List: a list to carry out the search (input a 1-D vector)
    # Target: the target searched for

    # Output:
    # Index of the Target found in this List

    # Covert the list into numpy array form
    NPlist = np.asarray(List)
    # Find the total number of elements in this list
    nele = np.shape(NPlist)[0]
    # Initialize the output list
    IndexList = []
    # Loop over the whole list
    for i in range(0, nele):
        if Target in NPlist[i]:
            IndexList.append(i)

    # Convert the index list to numpy array form
    IndexList = np.asarray(IndexList)
    return IndexList


def find_closest_larger_index(array, target):
    absolute_diff = array - target
    filtered_diff = np.where(absolute_diff > 0, absolute_diff, np.inf)
    closest_index = np.argmin(filtered_diff)
    return closest_index


# calculate column cost
def column_cost( total_A, total_story, baysize1, baysize2, bay_total_load, story_height,
                column_tabular, column_fire_cost_tabular,fire_protection_percentage_column_inp):

    building_index=1
    i1 = building_index - 1
    max_input_index = building_index
    # define the floor area
    A = total_A / total_story
    # get the size of the projection of the building
    x2 = 2 * A**0.5 / (3 ** 0.5)
    x1 = x2 * 3 / 4
    perimeter = x1 + x2

    # initiate the record variable
    record = np.zeros((max_input_index, 8))
    cost_column = np.zeros((max_input_index, 5))
    # record the data of the input building

    record[i1][0] = total_A
    record[i1][1] = total_story
    record[i1][2] = perimeter
    # get the area per story and per bay
    floorarea = total_A / total_story
    bayarea = baysize2 * baysize1

    # initiate the floor load as 0 at different stories
    floor_load = np.zeros((total_story + 1, 9, max_input_index))

    for i2 in range(total_story-1, -1, -1):
        # calculate the floor load at different stories
        floor_load[i2][0][i1] = bayarea * bay_total_load + floor_load[i2 + 1][0][i1]
        # get the number of columns at each story
        floor_load[i2][1][i1] = (floorarea / (baysize1 * baysize2) + x1 / baysize1 + x2 / baysize2 + 1) * story_height

    if max(floor_load[:, 0, i1]) > 1000:
        print(f"Warning: the maximum floor load exceed the column capacity, building index={building_index}")



    for i4 in range(total_story - 1, -1, -1):
        closest_index = find_closest_larger_index(column_tabular[:, 0],floor_load[i4][0][i1])
        floor_load[i4][2][i1] = column_tabular[closest_index][0]  # 3 column load
        floor_load[i4][3][i1] = column_tabular[closest_index][4]  # 4 price V.L.F
        floor_load[i4][4][i1] = column_tabular[closest_index][6] - 1 # 5 fire protection index

        floor_load[i4][5][i1] = column_fire_cost_tabular[int(floor_load[i4][4][i1]), 3]  # 6 fire protection cost 1h
        floor_load[i4][6][i1] = column_fire_cost_tabular[int(floor_load[i4][4][i1]), 4]  # 6 fire protection cost 2h
        floor_load[i4][7][i1] = column_fire_cost_tabular[int(floor_load[i4][4][i1]), 5]  # 6 fire protection cost 3h
        floor_load[i4][8][i1] = column_fire_cost_tabular[int(floor_load[i4][4][i1]), 6]  # 6 fire protection cost 4h
        i4 -= 1

    cost_column[i1, 0] = 0
    cost_column[i1][1] = 0
    cost_column[i1][2] = 0
    cost_column[i1][3] = 0

    for i5 in range(total_story - 1, -1, -1):
        # price*number
        cost_column[i1, 0] += floor_load[i5][3][i1] * floor_load[i5][1][i1]
        cost_column[i1][1] += floor_load[i5][5][i1] * floor_load[i5][1][i1]
        cost_column[i1][2] += floor_load[i5][6][i1] * floor_load[i5][1][i1]
        cost_column[i1][3] += floor_load[i5][7][i1] * floor_load[i5][1][i1]
        cost_column[i1][4] += floor_load[i5][8][i1] * floor_load[i5][1][i1]
        i5 += 1

    record[i1][3] = cost_column[i1, 0]
    record[i1][4] = cost_column[i1][1]
    record[i1][5] = cost_column[i1][2]
    record[i1][6] = cost_column[i1][3]
    record[i1][7] = cost_column[i1][4]
    column_cost = cost_column[i1, 0]
    column_protection_cost = cost_column[i1][1:4]*fire_protection_percentage_column_inp
    floor_load_max=max(floor_load[:, 0, i1])
    i1 += 1

    return column_cost, column_protection_cost, floor_load_max

def floor_system_cost(total_A, floor_composite, beam_fire_cost, fireprotectionbeam_ori,fire_protection_percentage_beam_inp):
    # fire protection cost on floor system per sq.ft for different building type
    # fireprotectionbeam_default = [0.86, 0.86, 0.79, 0.79, 0.79, 0.79, 0.79, 0.79]
    # floor_defalut_rsmeans = [27.63, 20.56, 13.99, 13.99, 15.39, 13.99, 15.39, 15.39]
    floor_cost = (floor_composite-fireprotectionbeam_ori)*total_A
    floor_protection_cost = beam_fire_cost*total_A*fire_protection_percentage_beam_inp
    return floor_cost, floor_protection_cost


def fire_service_cost(total_A, total_story, building_information_ori,building_index):
    import numpy as np
    bound = [0, 20, 35, 60, 70, 85, 95, 120, 130]
    # index bound
    Building_type = int(building_information_ori[building_index - 1][8])
    low_limit = bound[Building_type - 1]
    up_limit = bound[Building_type]

    # change with story:  'Partition',do not change with story: 'Sprinkler','Fire pump','Alarm','Ceiling'
    fire_service_cost_ori = building_information_ori[low_limit:up_limit, [21, 22, 23, 24, 25]]
    partition_cost= np.interp(total_A, building_information_ori[low_limit:up_limit,1], fire_service_cost_ori[:, 0])

    Sprinkler_cost = np.interp(total_A, building_information_ori[low_limit:up_limit, 1],
                               fire_service_cost_ori[:, 1])

    Fire_pump_cost = np.interp(total_A, building_information_ori[low_limit:up_limit, 1],
                               fire_service_cost_ori[:, 2])

    Alarm_cost = np.interp(total_A, building_information_ori[low_limit:up_limit, 1],
                               fire_service_cost_ori[:, 3])

    Ceiling_cost = np.interp(total_A, building_information_ori[low_limit:up_limit, 1],
                               fire_service_cost_ori[:, 4])

    return partition_cost,Sprinkler_cost,Fire_pump_cost,Alarm_cost,Ceiling_cost

def get_wd_ratio(input_size1,input_size2):
    import pandas as pd
    import numpy as np
    import re

    wd_database = pd.read_csv('WD_AP_RATIO.csv')
    member_shape = np.asarray(wd_database.iloc[:, 0])
    member_wholeline = np.asarray(wd_database.iloc[:, 0:13])
    NPlist = np.asarray(member_shape)
    # Find the total number of elements in this list
    nele = np.shape(NPlist)[0]
    # Initialize the output list
    IndexList = []
    Index_target = []
    # Loop over the whole list

    for i in range(0, nele):
        if input_size1 in str(NPlist[i]):
            IndexList.append(i)

    #if IndexList:
        #for i in range(min(IndexList), min(max(IndexList) + 50, nele)):
            #if input_size2 in str(NPlist[i]):
            #   Index_target.append(i)
            #   notfound_label='found'

    if IndexList:
        for i in range(min(IndexList), min(max(IndexList) + 50, nele)):
            pattern_x1 = re.compile(rf'{input_size2}\b')
            match_x1 = re.search(pattern_x1, str(NPlist[i]))
            if match_x1:
               Index_target.append(i)
               notfound_label='found'


    else:
        print(f'member size {input_size1 + input_size2} is not available')
        Index_target=[1]
        notfound_label=input_size1+input_size2

    return member_wholeline[Index_target[0]],  notfound_label





def get_fireprotection_thickness(wd1, firerating, material_type, membertype, reference_wd, reference_t, c1, c2, intumescent):
    import numpy as np
    R = firerating


    if membertype == 1:  # 1 is beam, 2 is column, 3 is not mentioned, 4 is metal deck

        if material_type == 1:  # SFRM
            wd2 = reference_wd  # known, reference w/d
            T2 = reference_t  # GIVEN thickness
            T1 = (wd2 + 0.6) / (wd1 + 0.6) * T2  # calculated thickness

            if wd1 < 0.3:
                raise ValueError('The minimum W/D is less than the required value 0.37')

        elif material_type == 2:  # intumescent
            column_idx = {1: 1, 1.5: 2, 2: 3, 3: 4, 4: 5}
            if firerating in column_idx:
                T1 = np.interp(wd1, intumescent[:, 0], intumescent[:, column_idx[firerating]])
            else:
                raise ValueError("Invalid firerating value")

            if T1 == 0:
                raise ValueError('For the given size, the fire rating is not applicable')

    elif membertype == 2:

        if material_type == 1:  # SFRM
            T1 = R / (c1 * (wd1 + c2))  # calculated SFRM thickness

        elif material_type == 2:  # intumescent
            column_idx = {1: 1, 1.5: 2, 2: 3, 3: 4, 4: 5}
            if firerating in column_idx:
                T1 = np.interp(wd1, intumescent[:, 0], intumescent[:, column_idx[firerating]])
            else:
                raise ValueError("Invalid firerating value")

            if T1 == 0:
                raise ValueError('For the given size, the fire rating is not applicable')

    elif membertype == 3:
        T1 = (R - 0.2) / 4.43 / (wd1)

    elif membertype == 4:
        T1 = 1

    return T1

# You can call this function with the required parameters to get the thickness.

def calculate_fireprotection_cost(thickness,para_fireprotection,perimeter,material_type,membertype):
    T1=thickness
    volume = perimeter * T1 / 12 / 12
    price = para_fireprotection[material_type-1][0] * volume + para_fireprotection[material_type-1][1]  # for sfrm
    print(membertype)
    if membertype == 4:
        price = para_fireprotection[4][0] * T1 * 12
        print(price)

    return price


