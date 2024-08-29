import numpy as np
from io import StringIO
import pandas as pd
import streamlit as st
import json
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.stats import truncnorm
import scipy.stats as stats

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
def column_cost_calculation( total_A, total_story, baysize1, baysize2, bay_total_load, story_height,
                column_tabular, column_fire_cost_tabular,fire_protection_percentage_column_inp,
                             unit_material_fireprotection,unit_labor_beam):

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
        ## setting the minimum columns size to weight 45
        if floor_load[i2][0][i1]<=190:
            floor_load[i2][0][i1]=190
        # get the number of columns at each story
        floor_load[i2][1][i1] = (floorarea / (baysize1 * baysize2) + x1 / baysize1 + x2 / baysize2 + 1) * story_height

    if max(floor_load[:, 0, i1]) > 1000:
        print(f"Warning: the maximum floor load exceed the column capacity, building index={building_index}")

    column_load = [None] * total_story
    for i4 in range(total_story - 1, -1, -1):

        closest_index = find_closest_larger_index(column_tabular[:, 0],floor_load[i4][0][i1])
        floor_load[i4][2][i1] = column_tabular[closest_index][0]  # 3 column load
        floor_load[i4][3][i1] = column_tabular[closest_index][4]  # 4 price V.L.F
        floor_load[i4][4][i1] = column_tabular[closest_index][6] - 1 # 5 fire protection index

        column_load[i4]=column_tabular[closest_index][2]

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
    column_protection_labor=column_protection_cost/unit_material_fireprotection*unit_labor_beam

    return column_cost, column_protection_cost, floor_load_max, column_protection_labor,column_load

def floor_system_cost(total_A, floor_composite, beam_fire_cost, fireprotectionbeam_ori,fire_protection_percentage_beam_inp,unit_material_fireprotection,unit_labor_beam):
    # fire protection cost on floor system per sq.ft for different building type
    # fireprotectionbeam_default = [0.86, 0.86, 0.79, 0.79, 0.79, 0.79, 0.79, 0.79]
    # floor_defalut_rsmeans = [27.63, 20.56, 13.99, 13.99, 15.39, 13.99, 15.39, 15.39]
    floor_cost = (floor_composite-fireprotectionbeam_ori)*total_A
    floor_protection_cost = beam_fire_cost*total_A*fire_protection_percentage_beam_inp

    floor_labor_hour = floor_protection_cost/unit_material_fireprotection*unit_labor_beam

    return floor_cost, floor_protection_cost, floor_labor_hour


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

# def convert_state_for_json(state):
#     serializable_state = {}
#     for key, value in state.items():
#         if isinstance(value, pd.DataFrame):
#             # Convert DataFrame to a JSON string
#             serializable_state[key] = value.to_json(orient='split')
#         elif isinstance(value, np.bool_):
#             # Convert NumPy boolean to Python boolean
#             serializable_state[key] = bool(value)
#         else:
#             serializable_state[key] = value
#     return serializable_state

def convert_state_for_json(state):
    serializable_state = {}
    for key, value in state.items():
        if isinstance(value, pd.DataFrame):
            # Convert DataFrame to a JSON string
            serializable_state[key] = value.to_json(orient='split')
        elif isinstance(value, np.bool_):
            # Convert NumPy boolean to Python boolean
            serializable_state[key] = bool(value)
        elif isinstance(value, np.ndarray):
            # Convert NumPy array to a list
            serializable_state[key] = value.tolist()
        elif isinstance(value, (np.integer, np.floating)):
            # Convert NumPy integers and floats to Python native types
            serializable_state[key] = value.item()
        else:
            serializable_state[key] = value
    return serializable_state

# def convert_state_from_json(serialized_state):
#     original_state = {}
#     for key, value in serialized_state.items():
#         if isinstance(value, str):
#             try:
#                 # Use StringIO to wrap the JSON string
#                 str_io = StringIO(value)
#                 original_state[key] = pd.read_json(str_io, orient='split')
#             except ValueError:
#                 # If the conversion fails, keep the value as a string
#                 original_state[key] = value
#         else:
#             original_state[key] = value
#     return original_state

def convert_state_from_json(serialized_state):
    original_state = {}
    for key, value in serialized_state.items():
        if isinstance(value, str):
            try:
                # Try to load the string as a DataFrame
                str_io = StringIO(value)
                original_state[key] = pd.read_json(str_io, orient='split')
            except ValueError:
                # If the conversion fails, keep the value as a string
                original_state[key] = value
        elif isinstance(value, list):
            # If the value is a list, convert it to a NumPy array
            original_state[key] = np.array(value)
        else:
            original_state[key] = value
    return original_state

def update_session_state(key):
    """Generic callback to update session state based on the widget's key."""
    st.session_state[key] = st.session_state[f"temp_{key}"]


## indirect loss estimation
def sum_by_label(values, labels):
    """
    Sums elements of the 'values' array based on matching labels in the 'labels' array.

    Parameters:
    values (np.array): Array of numerical values to be summed.
    labels (list of str): Array of labels corresponding to the values.

    Returns:
    dict: Dictionary with labels as keys and the summed values as values.
    """
    label_sums = {}

    for label, value in zip(labels, values):
        if label in label_sums:
            label_sums[label] += value
        else:
            label_sums[label] = value

    return label_sums

def convert_and_replace_nan(value):
    if isinstance(value, np.ndarray):
        value = value.item()
    if pd.isna(value):
        return 0
    return value
def prepare_labels(data):
    labels = []
    for name, info in data.items():
        start, end = info['start_day'], info['complete_day']
        if end < start:
            raise ValueError(f"End time {end} must be greater than start time {start} for {name}")
        labels.append(name.replace('_', ' ').title())
    return labels


def inspection_impedance(num_reals, impeding_factor_medians, impedance_options, repair_classification,
                         inspection_trigger, trunc_pd):
    beta = impedance_options['impedance_beta']
    # Example of accessing a specific option
    # Assuming impeding_factor_medians is a pandas DataFrame
    inspection_medians = impeding_factor_medians[impeding_factor_medians['factor'] == 'inspection']

    # Conditional checks based on the facility type
    is_borp_equivalent = impedance_options['mitigation']['is_borp_equivalent']
    is_essential_facility = impedance_options['mitigation']['is_essential_facility']


    if is_borp_equivalent:
        filt = inspection_medians['category'] == 'borp'
        # BORP equivalent is not affected by surge
        median = inspection_medians.loc[filt, 'time_days'].values[0]
    elif is_essential_facility:
        filt = inspection_medians['category'] == 'essential'
        median = inspection_medians.loc[filt, 'time_days'].values[0]
    else:
        filt = inspection_medians['category'] == 'default'
        median = inspection_medians.loc[filt, 'time_days'].values[0]

    prob_sim = np.random.rand(num_reals)
    x_vals_std_n = trunc_pd.ppf(prob_sim)  # percent point function (inverse of cdf)
    inspection_time = np.exp(x_vals_std_n * beta + np.log(median))
    inspection_imped = np.ceil(inspection_time[:, None] * repair_classification['any'])
    # Only use realizations that require inspection
    if inspection_trigger == 0:
        inspection_time = 0
        inspection_imped = 0 * repair_classification['any']

    # Affects all systems that need repair
    # Assume impedance always takes a full day

    return inspection_imped
def finance_impedance(num_reals,impeding_factor_medians,impedance_options,repair_classification,repair_cost_ratio,trunc_pd):
    beta = impedance_options['impedance_beta']

    # Simulate financing time using a truncated lognormal distribution
    finance_medians = impeding_factor_medians[impeding_factor_medians['factor'] == 'financing']
    capital_available_ratio = impedance_options['mitigation']['capital_available_ratio']
    # Determine the trigger for required financing
    financing_trigger = repair_cost_ratio > capital_available_ratio
    # Determining the median financing time based on the funding source
    funding_source = impedance_options['mitigation']['funding_source']
    if funding_source == 'sba':
        filt = finance_medians['category'] == 'sba'
        median = finance_medians['time_days'][filt].values[0]
    elif funding_source == 'private':
        filt = finance_medians['category'] == 'private'
        median = finance_medians['time_days'][filt].values[0]
    elif funding_source == 'insurance':
        filt = finance_medians['category'] == 'insurance'
        median = finance_medians['time_days'][filt].values[0]
    else:
        raise ValueError(f"Invalid financing type, '{funding_source}', for impedance factor simulation")

    prob_sim = np.random.rand(num_reals)
    x_vals_std_n = trunc_pd.ppf(prob_sim)  # Inverse CDF to transform uniform to truncated normal
    financing_time = np.exp(x_vals_std_n * beta + np.log(median))
    # Apply the financing trigger
    if financing_trigger:
        1
    else:
        financing_time = np.zeros(len(financing_time))
    # Assuming sys_repair_trigger is defined and formatted correctly as a numpy array
    financing_imped = np.ceil(financing_time[:, np.newaxis] * repair_classification['any'])
    # Assuming impeding_factor_medians is a pandas DataFrame and trunc_pd is already defined
    return financing_imped


def permit_impedance(num_reals, impeding_factor_medians,impedance_options, repair_classification, trunc_pd):
    beta = impedance_options['impedance_beta']

    # Filter permit medians based on factor
    permit_medians = impeding_factor_medians[impeding_factor_medians['factor'] == 'permitting']
    # Adjusting the surge factor for permitting
    # Full Permits
    filt = permit_medians['category'] == 'full'
    full_permit_median = permit_medians['time_days'][filt].values[0]
    # Rapid Permits
    filt = permit_medians['category'] == 'rapid'
    rapid_permit_median = permit_medians['time_days'][filt].values[0]
    # Simulate permit times for each type
    # Rapid Permits
    prob_sim = np.random.rand(num_reals)  # Uniform random variables
    x_vals_std_n = trunc_pd.ppf(prob_sim)  # Inverse CDF to transform uniform to truncated normal
    rapid_permit_time = np.exp(x_vals_std_n * beta + np.log(rapid_permit_median))
    rapid_permit_time_per_system = rapid_permit_time[:, np.newaxis] * repair_classification['rapid_permit']

    # Full Permits
    prob_sim = np.random.rand(num_reals)  # Independent simulations
    x_vals_std_n = trunc_pd.ppf(prob_sim)
    full_permit_time = np.exp(x_vals_std_n * beta + np.log(full_permit_median))
    full_permit_time_per_system = full_permit_time[:, np.newaxis] * repair_classification['full_permit']
    # Take the max of full and rapid permit times per system
    permitting_imped = np.ceil(np.maximum(rapid_permit_time_per_system, full_permit_time_per_system))
    return permitting_imped


def contractor_impedance(num_reals, systems, impedance_options, repair_classification):
    if impedance_options['mitigation']['is_contractor_on_retainer']:
        contr_min = systems['imped_contractor_min_days'].values
        contr_max = systems['imped_contractor_max_days'].values
    else:
        contr_min = systems['imped_contractor_min_days_retainer'].values
        contr_max = systems['imped_contractor_max_days_retainer'].values

    # Simulate contractor mobilization impedance
    # This assumes systems are independent
    contractor_mob_imped = np.random.uniform(contr_min, contr_max, (num_reals, len(contr_min)))

    arr = np.array(repair_classification['any'])
    contractor_mob_imped = contractor_mob_imped * arr
    contractor_mob_imped = np.ceil(contractor_mob_imped)
    return contractor_mob_imped


def redesign_impedance(num_reals,building_model, repair_classification, impedance_options, systems, impeding_factor_medians, trunc_pd,
                       is_engineer_on_retainer):
    beta = impedance_options['impedance_beta']

    redesign_trigger = np.array(
        repair_classification['redesign'])  # This should be a boolean array indicating where redesign is required
    # redesign_trigger = redesign_trigger.reshape(10, 1)
    user_options = impedance_options['system_design_time']
    design_min = systems['imped_design_min_days'].values
    design_max = systems['imped_design_max_days'].values
    # Calculate System Design Time
    repair_cost_ratio= building_model['repair_cost_ratio']
    building_value = building_model['building_value']
    RC_total = repair_cost_ratio * building_value
    SDT = RC_total * user_options['f'] / (user_options['r'] * user_options['t'] * user_options['w'])
    # Engineering Mobilization Time
    # Filtering engineering mobilization medians
    eng_mob_medians = impeding_factor_medians[impeding_factor_medians['factor'] == 'engineering mobilization']
    filt = eng_mob_medians['category'] == ('retainer' if is_engineer_on_retainer else 'default')
    median_eng_mob = eng_mob_medians['time_days'][filt].values[0]  # Assume surge_factor is defined

    # Simulation of engineering mobilization time
    prob_sim = np.random.rand(num_reals)
    x_vals_std_n = trunc_pd.ppf(prob_sim)  # trunc_pd should be defined as in previous examples
    eng_mob_time = np.exp(x_vals_std_n * beta + np.log(median_eng_mob))
    eng_mob_imped = np.zeros((len(x_vals_std_n), len(redesign_trigger)))
    for i in range(len(eng_mob_time)):
        eng_mob_imped[i, :] = eng_mob_time[i] * redesign_trigger

    # Engineering Design Time
    design_med = np.minimum(np.maximum(SDT, design_min), design_max)
    design_med = np.array(design_med)
    # Simulation of engineering design time
    prob_sim = np.random.rand(num_reals)
    x_vals_std_n = trunc_pd.ppf(prob_sim)
    eng_design_time = np.zeros((len(x_vals_std_n), len(design_med)))
    eng_design_imped = np.zeros((len(x_vals_std_n), len(design_med)))
    for i in range(len(design_med)):
        eng_design_time[:, i] = np.exp(x_vals_std_n * beta + np.log(design_med[i]))

    for i in range(len(x_vals_std_n)):
        eng_design_imped[i, :] = eng_design_time[i, :] * redesign_trigger

    return eng_mob_imped, eng_design_imped


def reoccupancy_curve(story_complete_day,story_start_day, sub_system,red_tag,num_sys,heavy_smoke_area,burned_area,closed_area,total_area):
    # Initialize arrays for re-occupancy and functionality
    reoccupancy = np.zeros([num_sys,2])
    functionality = np.zeros([num_sys,2])
    fully_repaired = np.zeros([2,2])

    # Check if structural repair is complete
    reoccupancy[0, 0] = 0
    reoccupancy[0, 1] = 1 - closed_area / total_area
    functionality[0, 0] = 0
    functionality[0, 1] = 1 - closed_area / total_area
    if red_tag == 1:
        reoccupancy[1,0] = story_complete_day[0] #structural repair finish
        reoccupancy[1, 1] = 1-heavy_smoke_area/total_area
        reoccupancy[3, 0] = story_complete_day[2] #interior repair finish
        reoccupancy[3, 1] = 1-burned_area/total_area
        reoccupancy[4, 0] = story_complete_day[4] #interior fire repair finish
        reoccupancy[4, 1] = 1
        functionality[1, 0] = story_complete_day[0]  # structural repair finish
        functionality[1, 1] = 1 - heavy_smoke_area/total_area
        functionality[2, 0] = (story_complete_day[1]-(story_complete_day[1]-story_start_day[1])*
                               (sub_system['labor_hour'][2]/(sub_system['labor_hour'][2]+sub_system['labor_hour'][1])))  # exterior window finish
        functionality[2, 1] = 1 - (heavy_smoke_area/total_area*(1-0.25))

        functionality[3, 0] = (story_complete_day[2]--(story_complete_day[1]-story_start_day[1])*
                               (sub_system['labor_hour'][2]/(sub_system['labor_hour'][2]+sub_system['labor_hour'][1])))  # exterior  finish
        functionality[3, 1] = 1 - (heavy_smoke_area/total_area*(1-0.5))

        functionality[4, 0] = story_complete_day[2]  # exterior  finish
        functionality[4, 1] = 1 - (heavy_smoke_area/total_area*(1-0.75))

        functionality[5, 0] = max(story_complete_day)  # exterior  finish
        functionality[5, 1] = 1 - (heavy_smoke_area/total_area*(1-0.75))

    else:
        reoccupancy[3, 0] = story_complete_day[2] #interior repair finish
        reoccupancy[3, 1] = 1-burned_area/total_area
        reoccupancy[4, 0] = story_complete_day[4] #interior fire repair finish
        reoccupancy[4, 1] = 1

        functionality[2, 0] = (story_complete_day[1]-(story_complete_day[1]-story_start_day[1])*
                               (sub_system['labor_hour'][2]/(sub_system['labor_hour'][2]+sub_system['labor_hour'][1])))  # exterior window finish
        functionality[2, 1] = 1 - (heavy_smoke_area/total_area*(1-0.25))

        functionality[3, 0] = (story_complete_day[2]--(story_complete_day[1]-story_start_day[1])*
                               (sub_system['labor_hour'][2]/(sub_system['labor_hour'][2]+sub_system['labor_hour'][1])))  # exterior  finish
        functionality[3, 1] = 1 - (heavy_smoke_area/total_area*(1-0.5))

        functionality[4, 0] = story_complete_day[2]  # exterior  finish
        functionality[4, 1] = 1 - (heavy_smoke_area/total_area*(1-0.75))

        functionality[5, 0] = max(story_complete_day)  # exterior  finish
        functionality[5, 1] = 1 - (heavy_smoke_area/total_area*(1-0.75))

    fully_repaired[1,0] = max(story_complete_day)
    fully_repaired[1,1] = 1
    # Plot the re-occupancy and functionality curves
    plt.figure(figsize=(10, 6))
    plt.plot(reoccupancy, label='Re-occupancy')
    plt.plot(functionality, label='Functionality')
    plt.xlabel('Days')
    plt.ylabel('Value')
    plt.legend()
    plt.show()



def reoccupancy_curve2(story_complete_day, story_start_day, array_component_labor, red_tag, heavy_smoke_area, burned_area, closed_area, total_area):
    # Initialize arrays for re-occupancy, functionality and fully repaired
    reoccupancy = np.zeros([4,2])
    functionality = np.zeros([11,2])
    fully_repaired = np.zeros([3,2])
    sub_system = {
        'labor_hour': array_component_labor
    }
    # Check if structural repair is complete
    reoccupancy[0, 0] = 0
    reoccupancy[0, 1] = 1 - closed_area / total_area
    functionality[0, 0] = 0
    functionality[0, 1] = 1 - closed_area / total_area
    fully_repaired[0, 0] = 0
    fully_repaired[0, 1] = 1 - closed_area / total_area

    # Check if exterior and interior repairs are complete
    if red_tag == 1:
        reoccupancy[1, 0] = story_complete_day[0] #structural repair finish
        reoccupancy[1, 1] = 1 - closed_area / total_area
        reoccupancy[2, 0] = story_complete_day[0] #structural repair finish
        reoccupancy[2, 1] = 1
        reoccupancy[3, 0] = max(story_complete_day) #interior fire repair finish
        reoccupancy[3, 1] = 1
        #
        # reoccupancy[3, 0] = story_complete_day[2] #interior repair finish
        # reoccupancy[3, 1] = 1-heavy_smoke_area/total_area
        # reoccupancy[4, 0] = story_complete_day[2] #interior repair finish
        # reoccupancy[4, 1] = 1-burned_area/total_area
        #
        # reoccupancy[4, 0] = story_complete_day[4] #interior fire repair finish
        # reoccupancy[4, 1] = 1-burned_area/total_area
        # reoccupancy[5, 0] = story_complete_day[4] #interior fire repair finish
        # reoccupancy[5, 1] = 1

        # reoccupancy[6, 0] = max(story_complete_day) #interior fire repair finish
        # reoccupancy[6, 1] = 1


        functionality[1, 0] = story_complete_day[0]  # structural repair finish
        functionality[1, 1] = 1 - closed_area / total_area
        functionality[2, 0] = story_complete_day[0]  # structural repair finish
        functionality[2, 1] = 1 - heavy_smoke_area/total_area

        functionality[3, 0] = story_complete_day[1]
        functionality[3, 1] = 1 - heavy_smoke_area/total_area
        functionality[4, 0] = story_complete_day[1]
        functionality[4, 1] = 1 - (heavy_smoke_area/total_area*(1-0.25))

        functionality[5, 0] = story_complete_day[2]
        functionality[5, 1] = 1 - (heavy_smoke_area/total_area*(1-0.25))
        functionality[6, 0] = story_complete_day[2]
        functionality[6, 1] = 1 - (heavy_smoke_area/total_area*(1-0.5))

        functionality[7, 0] = story_complete_day[2]  # exterior  finish
        functionality[7, 1] = 1 - (heavy_smoke_area/total_area*(1-0.5))
        functionality[8, 0] = story_complete_day[2]  # exterior  finish
        functionality[8, 1] = 1 - (heavy_smoke_area/total_area*(1-0.75))

        functionality[9, 0] = max(story_complete_day)  # exterior  finish
        functionality[9, 1] =1 - (heavy_smoke_area/total_area*(1-0.75))
        functionality[10, 0] = max(story_complete_day)  # exterior  finish
        functionality[10, 1] = 1

        fully_repaired[1,0] = max(story_complete_day)
        fully_repaired[1,1] = 1 - closed_area / total_area
        fully_repaired[2,0] = max(story_complete_day)
        fully_repaired[2,1] = 1
    else:
        reoccupancy[1, 0] = story_complete_day[0] #structural repair finish
        reoccupancy[1, 1] = 1 - closed_area / total_area
        reoccupancy[2, 0] = story_complete_day[0] #structural repair finish
        reoccupancy[2, 1] = 1
        reoccupancy[3, 0] = max(story_complete_day) #interior fire repair finish
        reoccupancy[3, 1] = 1
        # reoccupancy[1, 0] = story_complete_day[2] #interior repair finish
        # reoccupancy[1, 1] = 1-closed_area/total_area
        # reoccupancy[2, 0] = story_complete_day[2] #interior repair finish
        # reoccupancy[2, 1] = 1-burned_area/total_area
        #
        # reoccupancy[3, 0] = story_complete_day[4] #interior fire repair finish
        # reoccupancy[3, 1] = 1-burned_area/total_area
        # reoccupancy[4, 0] = story_complete_day[4] #interior fire repair finish
        # reoccupancy[4, 1] = 1
        # reoccupancy[6, 0] = max(story_complete_day) #interior fire repair finish
        # reoccupancy[6, 1] = 1
        #
        # functionality[3, 0] = (story_complete_day[1] - (story_complete_day[1] - story_start_day[1]) *
        #                        (sub_system['labor_hour'][2] / (
        #                                sub_system['labor_hour'][2] + sub_system['labor_hour'][1])))
        # functionality[3, 1] = 1 - heavy_smoke_area / total_area
        # functionality[4, 0] = (story_complete_day[1] - (story_complete_day[1] - story_start_day[1]) *
        #                        (sub_system['labor_hour'][2] / (
        #                                sub_system['labor_hour'][2] + sub_system['labor_hour'][1])))
        # functionality[4, 1] = 1 - (heavy_smoke_area / total_area * (1 - 0.25))
        #
        # functionality[5, 0] = (story_complete_day[2] - -(story_complete_day[1] - story_start_day[1]) *
        #                        (sub_system['labor_hour'][2] / (
        #                                sub_system['labor_hour'][2] + sub_system['labor_hour'][1])))
        # functionality[5, 1] = 1 - (heavy_smoke_area / total_area * (1 - 0.25))
        # functionality[6, 0] = (story_complete_day[2] - -(story_complete_day[1] - story_start_day[1]) *
        #                        (sub_system['labor_hour'][2] / (
        #                                sub_system['labor_hour'][2] + sub_system['labor_hour'][1])))
        # functionality[6, 1] = 1 - (heavy_smoke_area / total_area * (1 - 0.5))
        #
        # functionality[7, 0] = story_complete_day[2]  # exterior  finish
        # functionality[7, 1] = 1 - (heavy_smoke_area / total_area * (1 - 0.5))
        # functionality[8, 0] = story_complete_day[2]  # exterior  finish
        # functionality[8, 1] = 1 - (heavy_smoke_area / total_area * (1 - 0.75))
        #
        # functionality[9, 0] = max(story_complete_day)  # exterior  finish
        # functionality[9, 1] = 1 - (heavy_smoke_area / total_area * (1 - 0.75))
        # functionality[10, 0] = max(story_complete_day)  # exterior  finish
        # functionality[10, 1] = 1

        functionality[1, 0] = story_complete_day[1]
        functionality[1, 1] = 1 - closed_area/total_area
        functionality[2, 0] = story_complete_day[1]
        functionality[2, 1] = 1 - closed_area/total_area

        functionality[3, 0] = story_complete_day[1]
        functionality[3, 1] = 1 - heavy_smoke_area/total_area
        functionality[4, 0] = story_complete_day[1]
        functionality[4, 1] = 1 - (heavy_smoke_area/total_area*(1-0.25))

        functionality[5, 0] = story_complete_day[2]
        functionality[5, 1] = 1 - (heavy_smoke_area/total_area*(1-0.25))
        functionality[6, 0] = story_complete_day[2]
        functionality[6, 1] = 1 - (heavy_smoke_area/total_area*(1-0.5))

        functionality[7, 0] = story_complete_day[2]  # exterior  finish
        functionality[7, 1] = 1 - (heavy_smoke_area/total_area*(1-0.5))
        functionality[8, 0] = story_complete_day[2]  # exterior  finish
        functionality[8, 1] = 1 - (heavy_smoke_area/total_area*(1-0.75))

        functionality[9, 0] = max(story_complete_day)  # exterior  finish
        functionality[9, 1] =1 - (heavy_smoke_area/total_area*(1-0.75))
        functionality[10, 0] = max(story_complete_day)  # exterior  finish
        functionality[10, 1] = 1

        fully_repaired[1,0] = max(story_complete_day)
        fully_repaired[1,1] = 1 - closed_area / total_area
        fully_repaired[2,0] = max(story_complete_day)
        fully_repaired[2,1] = 1

    for i in range(1, len(reoccupancy)):
        if reoccupancy[i, 0] < reoccupancy[i - 1, 0]:
            reoccupancy[i, 0] = reoccupancy[i - 1, 0]

    # Ensure x-values only increase for functionality
    for i in range(1, len(functionality)):
        if functionality[i, 0] < functionality[i - 1, 0]:
            functionality[i, 0] = functionality[i - 1, 0]

    # Ensure x-values only increase for fully_repaired
    for i in range(1, len(fully_repaired)):
        if fully_repaired[i, 0] < fully_repaired[i - 1, 0]:
            fully_repaired[i, 0] = fully_repaired[i - 1, 0]

    return reoccupancy, functionality, fully_repaired


def impedance_days_ordered(num_sys, inspection_imped, financing_imped, permitting_imped, contractor_mob_imped,
                           eng_mob_imped, eng_design_imped,percentile):
    start_day = {}
    complete_day = {}


    start_day['inspection'] = np.zeros((num_sys))
    complete_day['inspection'] = np.percentile([inspection_imped], percentile, axis=1)

    start_day['financing'] = complete_day['inspection']
    complete_day['financing'] = start_day['financing'] + np.percentile([financing_imped], percentile, axis=1)

    start_day['eng_mob'] = np.maximum(complete_day['inspection'], start_day['financing'])
    complete_day['eng_mob'] = start_day['eng_mob'] + np.percentile([eng_mob_imped], percentile, axis=1)

    start_day['design'] = complete_day['eng_mob']
    complete_day['design'] = start_day['design'] + np.percentile([eng_design_imped], percentile, axis=1)

    start_day['permitting'] = complete_day['design']
    complete_day['permitting'] = start_day['permitting'] + np.percentile([permitting_imped], percentile, axis=1)

    start_day['contractor_mob'] = np.maximum(complete_day['inspection'], start_day['financing'])
    complete_day['contractor_mob'] = start_day['contractor_mob'] + np.percentile([contractor_mob_imped], percentile, axis=1)

    # Combine all impedance factors by system
    time_sys = np.zeros([1, num_sys])
    for key in complete_day:
        time_sys = np.maximum(time_sys, complete_day[key])

    # Assuming 'systems' is a DataFrame and has been initialized

    systems = pd.DataFrame({'name': ['Structure', 'Exterior', 'Interior', 'Exterior (fire)','Interior (fire)','Fire','Content']})

    # Prepare data structures for Gantt chart breakdowns

    breakdowns = {}
    breakdowns['inspection'] = {
        'start_day': np.max(start_day['inspection']),
        'complete_day': np.max(complete_day['inspection'])
    }
    breakdowns['financing'] = {
        'start_day': np.max(start_day['financing']),
        'complete_day': np.max(complete_day['financing'])
    }

    select_sys = [0, 1, 2]  # Indexes corresponding to 'Structure', 'Exterior', 'HVAC'
    for ss in select_sys:
        sys_name = systems.loc[ss, 'name']
        if complete_day['eng_mob'][0, ss]!=0:
            breakdowns[f'eng_mob_{sys_name}'] = {
                'start_day': start_day['eng_mob'][0, ss],
                'complete_day': complete_day['eng_mob'][0, ss]
            }
        if complete_day['design'][0, ss]!=0:
            breakdowns[f'design_{sys_name}'] = {
                'start_day': start_day['design'][0, ss],
                'complete_day': complete_day['design'][0, ss]
            }

    for s in range(len(systems)):
        sys_name = systems.loc[s, 'name']
        if complete_day['permitting'][0, s]!=0:
            breakdowns[f'permitting_{sys_name}'] = {
                'start_day': start_day['permitting'][0, s],
                'complete_day': complete_day['permitting'][0, s]
            }
        if complete_day['contractor_mob'][0, s]!=0:
            breakdowns[f'contractor_mob_{sys_name}'] = {
                'start_day': start_day['contractor_mob'][0, s],
                'complete_day': complete_day['contractor_mob'][0, s]
            }
    return time_sys, breakdowns

def allocate_workers_systems(sys_repair_days, sys_crew_size, max_workers_per_building,
                             sys_idx_priority_matrix, sys_constraint_matrix, condition_tag, sys_impeding_factors):
    """
    Stager repair to each system and allocate workers based on the repair constraints,
    priorities, and repair times of each system.

    Parameters
    ----------
    sys_repair_days : ndarray
        Number of days from the start of repair of each to the completion of the system.
    sys_crew_size : ndarray
        Required crew size for each system.
    max_workers_per_building : int
        Maximum number of workers that can work in the building at the same time.
    sys_idx_priority_matrix : ndarray
        Worker allocation order of system id's prioritized for each realization.
    sys_constraint_matrix : ndarray
        Array of system ids which define which systems are delayed by the system ids.
    condition_tag : ndarray
        True/false if the building is red tagged.
    sys_impeding_factors : ndarray
        Maximum impedance time (days) for each system.

    Returns
    -------
    repair_complete_day_per_system : ndarray
        Number of days from the start of each sequence to the completion of the sequence
        considering the allocation of workers to each sequence.
    worker_data : dict
        Contains the total number of workers in the building at each time step and the
        day of each time step of the worker allocation algorithm.
    """

    # Initial Setup
    num_sys = sys_repair_days.shape[0]
    priority_system_complete_day = np.zeros(num_sys)
    day_vector = np.zeros(0, dtype=int)
    total_workers = np.zeros(0, dtype=int)

    # Re-order system variables based on priority
    priority_sys_workers_matrix = filter_matrix_by_rows(sys_crew_size, sys_idx_priority_matrix)
    priority_sys_constraint_matrix = filter_matrix_by_rows(sys_constraint_matrix, sys_idx_priority_matrix)
    priority_sys_repair_days = filter_matrix_by_rows(sys_repair_days, sys_idx_priority_matrix)


    if sys_impeding_factors.size == 0:
        priority_sys_impeding_factors = np.zeros(num_sys, dtype=int)
    else:
        priority_sys_impeding_factors = filter_matrix_by_rows(sys_impeding_factors, sys_idx_priority_matrix)

    # Round up days to the nearest day
    priority_sys_repair_days = np.ceil(priority_sys_repair_days).astype(int)
    priority_sys_impeding_factors = np.ceil(priority_sys_impeding_factors).astype(int)

    # Assign workers to each system based on repair constraints
    iter = 0
    current_day = 0
    priority_sys_waiting_days = priority_sys_impeding_factors

    while np.sum(priority_sys_repair_days) > 0.01:
        iter += 1
        if iter > 1000:
            raise Exception('PBEE_Recovery:RepairSchedule: Could not converge worker allocations for among systems')

        # Zero out assigned workers matrix
        assigned_workers = np.zeros(num_sys, dtype=int)

        # Limit available workers to the max that can be on any one given story
        available_workers = max_workers_per_building

        # Define what systems are waiting to begin repairs
        sys_blocked = np.zeros(num_sys, dtype=bool)
        sys_incomplete = priority_sys_repair_days > 0

        for s in range(num_sys):
            constrained_systems = priority_sys_constraint_matrix == s + 1  # MATLAB is 1-based, Python is 0-based
            constraining_sys_filt = sys_idx_priority_matrix == s + 1
            is_constraining_sys_incomplete = np.max(sys_incomplete * constraining_sys_filt)

            # Perform the logical operation with proper broadcasting
            # is_constraining_sys_incomplete_broadcasted = np.full_like(constrained_systems,
            #                                                           is_constraining_sys_incomplete, dtype=bool)
            sys_blocked |= constrained_systems & is_constraining_sys_incomplete

        # print(sys_blocked)

        # Need to wait for impeding factors or other repairs to finish
        is_waiting = (current_day < priority_sys_impeding_factors) | sys_blocked

        # Define where needs repair
        needs_repair = (priority_sys_repair_days > 0) & ~is_waiting
        # Define required workers
        required_workers = needs_repair * priority_sys_workers_matrix

        # Assign workers to each system
        for s in range(num_sys):
            enough_workers = required_workers[s] <= available_workers

            assigned_workers[s] = min(required_workers[s], available_workers) if enough_workers else 0

            # Define available workers
            in_series = condition_tag & (s == 0)
            available_workers = 0 if in_series and assigned_workers[s] > 0 else available_workers - assigned_workers[s]

        # Calculate the time associated with this increment of the while loop
        in_progress = assigned_workers > 0
        total_repair_days = np.full_like(in_progress, np.inf, dtype=float)
        total_repair_days[in_progress] = priority_sys_repair_days[in_progress]
        total_waiting_days = priority_sys_waiting_days.astype(float)
        total_waiting_days[total_waiting_days == 0] = np.inf
        total_time = np.minimum(total_repair_days, total_waiting_days)
        delta_days = np.min(total_time)
        delta_days = 0 if np.isinf(delta_days) else delta_days

        # Reduce waiting time
        priority_sys_waiting_days = np.maximum(priority_sys_waiting_days - delta_days, 0)

        # Reduce time needed for repairs
        delta_days_in_progress = delta_days * in_progress
        priority_sys_repair_days = np.maximum(priority_sys_repair_days - delta_days_in_progress, 0)

        # Define start and stop of repair for each sequence
        priority_system_complete_day += delta_days * (needs_repair | is_waiting)

        # Define cumulative day of repair
        day_vector = np.append(day_vector, current_day)
        current_day += delta_days

        # Save worker data over time
        total_workers = np.append(total_workers, np.sum(assigned_workers))
        day_vector = np.append(day_vector, current_day)

    # Untangle system_complete_day back into system table order
    sys_idx_untangle_matrix = np.argsort(sys_idx_priority_matrix)
    repair_complete_day_per_system = filter_matrix_by_rows(priority_system_complete_day, sys_idx_untangle_matrix)

    # Save worker data matrices
    worker_data = {
        'total_workers': total_workers,
        'day_vector': day_vector
    }

    return repair_complete_day_per_system, worker_data


def filter_matrix_by_rows(values, filter):
    """
    Use an identity matrix to filter values from another matrix by rows.

    Parameters
    ----------
    values : ndarray
        Values to filter by row.
    filter : ndarray
        Array indexes to grab from each row of values.

    Returns
    -------
    filtered_values : ndarray
        Values filtered by rows.
    """
    filtered_values = np.zeros_like(values)
    filtered_values[:] = values[filter - 1]  # Subtract 1 for 0-based indexing in Python
    return values


def simulate_tmp_repair_times(is_shoring_damage,shoring_time_med,tmp_fix_time, inspection_complete_day, beta_temp, surge_factor):
    """
    Simulate temporary repair times for each component (where applicable) per realization.

    Parameters
    ----------
    damage : dict
        Contains per damage state damage and loss data for each component in the building.
    inspection_complete_day : ndarray
        Simulated day after the earthquake that inspection is completed.
    beta_temp : float
        Lognormal standard deviation defining the uncertainty in all temporary repair times.
    surge_factor : float
        Amplification factor for temporary repair time based on a post-disaster surge
        in demand for skilled trades and construction supplies.

    Returns
    -------
    tmp_repair_complete_day : ndarray
        Contains the day (after the earthquake) the temporary repair time is resolved per
        damage state damage and realization. Inf represents that there is no temporary
        repair time available for a given component's damage.
    """

    # Initialize Parameters

    # Create basic truncated standard normal distribution for later simulation
    trunc_pd = stats.truncnorm(-2, 2, loc=0, scale=1)


    # Go through damage and determine which realizations have shoring repairs


    # Simulate temporary repair times
    # Simulate shoring time (assumes correlated throughout whole building)
    prob_sim = np.random.rand(100)
    x_vals_std_n = trunc_pd.ppf(prob_sim)
    sim_shoring_time = np.ceil(np.exp(x_vals_std_n * beta_temp + np.log(shoring_time_med)))

    # Find the time to perform all shoring in the building
    building_shoring_time = np.average(sim_shoring_time) * is_shoring_damage

    # Simulate temp repair and clean up time
    tmp_repair_time = surge_factor * tmp_fix_time

    prob_sim = np.random.rand(100)
    x_vals_std_n = trunc_pd.ppf(prob_sim)
    sim_tmp_repair_time = np.average(np.exp(x_vals_std_n * beta_temp + np.log(tmp_repair_time)))
    # Combine to find total temp repair complete date for each component damage state (all stories and tenant units)
    tmp_repair_complete_day = inspection_complete_day + building_shoring_time + sim_tmp_repair_time
    return tmp_repair_complete_day



def allocate_workers_stories(total_worker_days, required_workers_per_story, average_crew_size, max_crews_building,
                             max_workers_per_building):
    """
    Allocate crews to each story to determine the system-level repair time on each story.

    Parameters
    ----------
    total_worker_days : ndarray
        The total worker days needed to repair damage each story for this sequence.
    required_workers_per_story : ndarray
        Number of workers required to repair damage in each story.
    average_crew_size : ndarray
        Average crew size required to repair damage in each story.
    max_crews_building : ndarray
        Maximum number of crews allowed in the building for this system.
    max_workers_per_building : int
        Maximum number of workers allowed in the buildings at a given time.

    Returns
    -------
    repair_start_day : ndarray
        The number of days from the start of repair of this system until the repair of this system starts on each story.
    repair_complete_day : ndarray
        The number of days from the start of repair of this system until each story is repaired for damage in this system.
    max_workers_per_story : ndarray
        Number of workers required for the repair of this story and system.
    """

    # Initial Setup
    [num_real,num_stories] = total_worker_days.shape
    repair_complete_day = np.zeros((1, num_stories))
    repair_start_day = np.full((1,num_stories), np.nan)
    max_workers_per_story = np.zeros((1, num_stories))

    # Allocate workers to each story
    iter = 0
    while np.sum(total_worker_days) > 1:
        iter += 1
        if iter > 1000:
            raise Exception('Could not converge worker allocations for among stories in sequence')

        # Determine the available workers in the building
        available_workers_in_building = max_workers_per_building
        assigned_workers_per_story = np.zeros((1,num_stories))
        assigned_crews_per_story = np.zeros((1,num_stories))

        # Define where needs repair
        needs_repair = total_worker_days > 0

        # Defined Required Workers
        required_workers_per_story = needs_repair * required_workers_per_story

        # Assign Workers to each story
        for s in range(num_stories):
            # Are there enough workers to assign a crew
            sufficient_workers = required_workers_per_story[:,s] <= available_workers_in_building

            # Assign Workers to this story
            assigned_workers_per_story[sufficient_workers, s] = required_workers_per_story[sufficient_workers, s]
            assigned_crews_per_story[:, s] = assigned_workers_per_story[:, s] / average_crew_size[:, s]
            assigned_crews_per_story = np.nan_to_num(assigned_crews_per_story)
            num_crews_in_building = np.sum(assigned_crews_per_story, axis=1)
            exceeded_max_crews = num_crews_in_building > max_crews_building
            assigned_workers_per_story[exceeded_max_crews, s] = 0

            # Define Available Workers
            available_workers_in_building -= assigned_workers_per_story[:, s]

        # Define the start of repairs for each story
        start_repair_filt = np.isnan(repair_start_day) & (assigned_workers_per_story > 0)
        max_day_completed_so_far = np.max(repair_complete_day, axis=1).reshape(-1, 1) * np.ones((1, num_stories))
        repair_start_day[start_repair_filt] = max_day_completed_so_far[start_repair_filt]

        # Calculate the time associated with this increment of the while loop
        in_progress = assigned_workers_per_story > 0
        total_repair_days = np.full_like(in_progress, np.inf, dtype=np.float64)
        total_repair_days[in_progress] = total_worker_days[in_progress] / assigned_workers_per_story[in_progress]
        delta_days = np.min(total_repair_days, axis=1)
        delta_days[np.isinf(delta_days)] = 0
        delta_worker_days = assigned_workers_per_story * delta_days[:, np.newaxis]
        total_worker_days[in_progress] = np.maximum(total_worker_days[in_progress] - delta_worker_days[in_progress], 0)
        total_worker_days[total_worker_days < 1] = 0

        # Define Start and Stop of Repair for each story in each sequence
        repair_complete_day += delta_days[:, np.newaxis] * needs_repair

        # Max Crew Size for use in later function
        max_workers_per_story = np.maximum(max_workers_per_story, assigned_workers_per_story)

    return repair_start_day, repair_complete_day, max_workers_per_story


def calculate_affectedarea_and_days(systems, impeding_factor_medians, repair_cost, building_model, damage_state, ds_prob):
    # Read CSV files using pandas
    # Read CSV files using pandas


    # damage_state = 4
    if damage_state == 4:
        red_tag = 1
    else:
        red_tag = 0

    # building_value = 12000000
    num_sys = systems.shape[0]
    compartments_area = building_model['compartment_area']
    total_area = building_model['total_area_sf']
    Fire_loss = building_model['Fire_loss']
    percentile = building_model['percentile']
    inspection_trigger = 1
    if damage_state == 1:
        inspection_trigger = 1

    pds1 = ds_prob[0]
    pds2 = ds_prob[1]
    pds3 = ds_prob[2]
    pds4 = ds_prob[3]

    repair_cost_ratio = building_model['Fire_loss'] / building_model['building_value']


    component_labels = repair_cost['functionality']
    # protion_labels = ['structural', 'exterior', 'exterior', 'interior', 'interior', 'interior', 'interior']

    # protion_labels = systems['name']

    quantity_components = repair_cost['quantity in every compartment']

    unit_component = repair_cost['unit'].copy()
    unit_component[unit_component == 'sqft'] = compartments_area
    unit_component[unit_component == 'each'] = 1

    quantity_components = repair_cost['quantity in every compartment'] * unit_component

    repair_cost_ds1 = (repair_cost['installation cost DS1'] + repair_cost['demolish cost DS1']) * quantity_components
    repair_cost_ds2 = (repair_cost['installation cost DS2'] + repair_cost['demolish cost DS2']) * quantity_components
    repair_cost_ds3 = (repair_cost['installation cost DS3'] + repair_cost['demolish cost DS3']) * quantity_components

    repair_cost_ds1_percentage = repair_cost_ds1 / np.sum(repair_cost_ds1)
    repair_cost_ds2_percentage = repair_cost_ds2 / np.sum(repair_cost_ds2)
    repair_cost_ds3_percentage = repair_cost_ds3 / np.sum(repair_cost_ds3)


    if damage_state==4:
        loss_DS1 = pds1 * Fire_loss
        loss_DS2 = pds2 * Fire_loss
        loss_DS34 = (pds3 + pds4) * Fire_loss

    if damage_state==3:
        loss_DS1=0
        loss_DS2=0
        loss_DS34 = Fire_loss

    if damage_state==2:
        loss_DS1 = 0
        loss_DS2 = Fire_loss
        loss_DS34 = 0

    if damage_state==1:
        loss_DS1 = Fire_loss
        loss_DS2 = 0
        loss_DS34 = 0

    num_ds1 = int(np.maximum(np.ceil(loss_DS1 / np.sum(repair_cost_ds1)),1))
    num_ds2 = int(np.maximum(np.ceil(loss_DS2 / np.sum(repair_cost_ds2)),1))
    num_ds3 = int(np.maximum(np.ceil(loss_DS34 / np.sum(repair_cost_ds3)), 1))



    # num_ds2 = int(np.ceil(loss_DS2 / np.sum(repair_cost_ds2)))
    # num_ds3 = int(np.ceil(loss_DS34 / np.sum(repair_cost_ds3)))

    mean = repair_cost['labor mean'][0]
    sigma = (repair_cost['labor mean'][0] - repair_cost['labor lower limit'][0]) / 2  # since 3sigma = 20

    x = np.linspace(mean - 4 * sigma, mean + 4 * sigma, 1000)
    y = stats.norm.pdf(x, mean, sigma)
    labor_hour_unit_cost = np.percentile([x], 100 - percentile, axis=1)

    labor_days_DS1 = loss_DS1 / labor_hour_unit_cost / 8
    labor_days_DS2 = loss_DS2 / labor_hour_unit_cost / 8
    labor_days_DS3 = loss_DS34 / labor_hour_unit_cost / 8

    cost_portion_DS1 = repair_cost_ds1_percentage
    cost_portion_DS2 = repair_cost_ds2_percentage
    cost_portion_DS3 = repair_cost_ds3_percentage

    portion_labor_days_DS1 = np.array(np.ceil(cost_portion_DS1 * labor_days_DS1)).reshape(7, 1)
    portion_labor_days_DS2 = np.array(np.ceil(cost_portion_DS2 * labor_days_DS2)).reshape(7, 1)
    portion_labor_days_DS3 = np.array(np.ceil(cost_portion_DS3 * labor_days_DS3)).reshape(7, 1)

    sys_labor_days_DS1 = sum_by_label(portion_labor_days_DS1/num_ds1, component_labels)
    sys_labor_days_DS2 = sum_by_label(portion_labor_days_DS2/num_ds2, component_labels)
    sys_labor_days_DS3 = sum_by_label(portion_labor_days_DS3/num_ds3, component_labels)

    redesign_DS1 = sum_by_label(repair_cost['redesign DS1'], component_labels)
    redesign_DS2 = sum_by_label(repair_cost['redesign DS2'], component_labels)
    redesign_DS3 = sum_by_label(repair_cost['redesign DS3'], component_labels)

    rapid_permit_DS1 = sum_by_label(repair_cost['rapid_permit DS1'], component_labels)
    rapid_permit_DS2 = sum_by_label(repair_cost['rapid_permit DS2'], component_labels)
    rapid_permit_DS3 = sum_by_label(repair_cost['rapid_permit DS3'], component_labels)

    full_permit_DS1 = sum_by_label(repair_cost['full_permit DS1'], component_labels)
    full_permit_DS2 = sum_by_label(repair_cost['full_permit DS2'], component_labels)
    full_permit_DS3 = sum_by_label(repair_cost['full_permit DS3'], component_labels)

    df_DS1 = pd.DataFrame(index=systems['name'], columns=['Single Labor Days'])
    df_DS2 = pd.DataFrame(index=systems['name'], columns=['Single Labor Days'])
    df_DS3 = pd.DataFrame(index=systems['name'], columns=['Single Labor Days'])

    # Assign the values from the result to the DataFrame
    for component_labels, value in sys_labor_days_DS1.items():
        df_DS1.at[component_labels, 'Single Labor Days'] = value

    for component_labels, value in sys_labor_days_DS2.items():
        df_DS2.at[component_labels, 'Single Labor Days'] = value

    for component_labels, value in sys_labor_days_DS3.items():
        df_DS3.at[component_labels, 'Single Labor Days'] = value

    for component_labels, value in redesign_DS1.items():
        df_DS1.at[component_labels, 'redesign'] = value
    for component_labels, value in redesign_DS2.items():
        df_DS2.at[component_labels, 'redesign'] = value

    for component_labels, value in redesign_DS3.items():
        df_DS3.at[component_labels, 'redesign'] = value

    for component_labels, value in rapid_permit_DS1.items():
        df_DS1.at[component_labels, 'rapid_permit'] = value

    for component_labels, value in rapid_permit_DS2.items():
        df_DS2.at[component_labels, 'rapid_permit'] = value

    for component_labels, value in rapid_permit_DS3.items():
        df_DS3.at[component_labels, 'rapid_permit'] = value

    for component_labels, value in full_permit_DS1.items():
        df_DS1.at[component_labels, 'full_permit'] = value

    for component_labels, value in full_permit_DS2.items():
        df_DS2.at[component_labels, 'full_permit'] = value

    for component_labels, value in full_permit_DS3.items():
        df_DS3.at[component_labels, 'full_permit'] = value

    df_DS1['Single Labor Days'] = df_DS1['Single Labor Days'].apply(convert_and_replace_nan)
    df_DS2['Single Labor Days'] = df_DS2['Single Labor Days'].apply(convert_and_replace_nan)
    df_DS3['Single Labor Days'] = df_DS3['Single Labor Days'].apply(convert_and_replace_nan)



    df_DS1.replace('', np.nan, inplace=True)
    df_DS1.fillna(0, inplace=True)

    df_DS2.replace('', np.nan, inplace=True)
    df_DS2.fillna(0, inplace=True)

    df_DS3.replace('', np.nan, inplace=True)
    df_DS3.fillna(0, inplace=True)

    df_DS1.iloc[:, 1:4] = df_DS1.iloc[:, 1:4].map(lambda x: 1 if x >= 1 else x)
    df_DS2.iloc[:, 1:4] = df_DS2.iloc[:, 1:4].map(lambda x: 1 if x >= 1 else x)
    df_DS3.iloc[:, 1:4] = df_DS3.iloc[:, 1:4].map(lambda x: 1 if x >= 1 else x)
    df_DS1['any'] = (df_DS1.iloc[:, 1:4] >= 1).any(axis=1).astype(int)
    df_DS2['any'] = (df_DS2.iloc[:, 1:4] >= 1).any(axis=1).astype(int)
    df_DS3['any'] = (df_DS3.iloc[:, 1:4] >= 1).any(axis=1).astype(int)

    df_DS1 = df_DS1.astype(int)
    df_DS2 = df_DS2.astype(int)
    df_DS3 = df_DS3.astype(int)

    # Combine the arrays

    # Concatenate the repeated arrays along the second axis
    if damage_state == 4:
        total_worker_day_DS1_repeated = np.tile(df_DS1['Single Labor Days'], (num_ds1, 1)).T
        total_worker_day_DS2_repeated = np.tile(df_DS2['Single Labor Days'], (num_ds2, 1)).T
        total_worker_day_DS3_repeated = np.tile(df_DS3['Single Labor Days'], (num_ds3, 1)).T

        total_worker_days = np.concatenate(
            (total_worker_day_DS1_repeated, total_worker_day_DS2_repeated, total_worker_day_DS3_repeated), axis=1)
        closed_area = (num_ds1 + num_ds2 + num_ds3) * compartments_area
    if damage_state == 1:
        num_ds1 = 1
        num_ds2 = 0
        num_ds3 = 0
        total_worker_day_DS1_repeated = np.tile(df_DS1['Single Labor Days'], (num_ds1, 1)).T
        total_worker_days = total_worker_day_DS1_repeated
        closed_area = (num_ds1 + num_ds2 + num_ds3) * compartments_area

    if damage_state == 2:
        num_ds1 = 0
        num_ds2 = 1
        num_ds3 = 0

        total_worker_day_DS2_repeated = np.tile(df_DS2['Single Labor Days'], (num_ds2, 1)).T
        total_worker_days = total_worker_day_DS2_repeated
        closed_area = (num_ds1 + num_ds2 + num_ds3) * compartments_area


    if damage_state == 3:
        num_ds1 = 0
        num_ds2 = 0
        num_ds3 = 1
        total_worker_day_DS3_repeated = np.tile(df_DS3['Single Labor Days'], (num_ds3, 1)).T
        total_worker_days = total_worker_day_DS3_repeated
        closed_area = (num_ds1 + num_ds2 + num_ds3) * compartments_area
    total_worker_days = total_worker_days.T

    total_worker_days_orig = total_worker_days.copy()
    sys_priority_matrix = np.array(systems['priority'])
    # sys_constraint_matrix=np.array([0,1,1,1,1,1,1])
    sys_constraint_matrix = np.ones([len(systems)], dtype=int)
    sys_constraint_matrix[0] = 0

    if damage_state == 1:
        sys_constraint_matrix = np.zeros([len(systems)], dtype=int)
    # input values:
    if damage_state == 4:
        df_repair_classification = df_DS3
    if damage_state == 1:
        df_repair_classification = df_DS1
    if damage_state == 2:
        df_repair_classification = df_DS2
    if damage_state == 3:
        df_repair_classification = df_DS3

    # four systems  structural interior exterior content
    repair_classification = {
        'any': df_repair_classification['any'].values,
        'rapid_permit': df_repair_classification['rapid_permit'].values,
        'full_permit': df_repair_classification['full_permit'].values,
        'redesign': df_repair_classification['redesign'].values
    }

    impedance_options = {
        'include_impedance': {
            'inspection': True,
            'financing': True,
            'permitting': True,
            'engineering': True,
            'contractor': True
        },
        'system_design_time': {
            'f': 0.04,
            'r': 175,
            't': 1.3,
            'w': 8
        },
        'mitigation': {
            'is_essential_facility': False,
            'is_borp_equivalent': False,
            'is_engineer_on_retainer': False,
            'is_contractor_on_retainer': False,
            'funding_source': 'private',
            'capital_available_ratio': 0.1
        },
        'impedance_beta': 0.6,
        'impedance_truncation': 2
    }

    mu = 0
    sigma = 1

    # Loop through the loaded damage data and update the structure
    sys_repair_trigger = repair_classification

    # Example dictionary setups

    # Initialize or update the dictionary
    repair_time_options = {}
    # Setting attributes in the dictionary
    repair_time_options['temp_repair_beta'] = 0.6
    repair_time_options['max_workers_per_sqft_story'] = 0.001
    repair_time_options['max_workers_per_sqft_building'] = 0.00025
    repair_time_options['max_workers_building_min'] = 20
    repair_time_options['max_workers_building_max'] = 260

    # Retrieve truncation limits from the impedance_options dictionary
    th_low = -impedance_options['impedance_truncation']
    th_high = impedance_options['impedance_truncation']
    is_engineer_on_retainer = impedance_options['mitigation']['is_engineer_on_retainer']
    is_contractor_on_retainer = impedance_options['mitigation']['is_contractor_on_retainer']
    # Create the truncated normal distribution
    # The arguments for truncnorm are (a, b, loc, scale) where:
    # a, b are the lower and upper bounds of the truncation, standardized to the standard normal distribution
    # loc is the mean, and scale is the standard deviation of the original distribution
    trunc_pd = truncnorm((th_low - mu) / sigma, (th_high - mu) / sigma, loc=mu, scale=sigma)
    # Retrieve the beta coefficient from the impedance_options

    # Simulate using a truncated lognormal distribution
    num_reals = 1000
    inspection_imped = inspection_impedance(num_reals, impeding_factor_medians, impedance_options,
                                            repair_classification, inspection_trigger, trunc_pd)

    # Filter finance medians based on factor
    financing_imped = finance_impedance(num_reals, impeding_factor_medians, impedance_options, repair_classification,
                                        repair_cost_ratio, trunc_pd)

    permitting_imped = permit_impedance(num_reals, impeding_factor_medians, impedance_options, repair_classification,
                                        trunc_pd)

    contractor_mob_imped = contractor_impedance(num_reals, systems, impedance_options, repair_classification)

    [eng_mob_imped, eng_design_imped] = redesign_impedance(num_reals, building_model, repair_classification,
                                                           impedance_options, systems, impeding_factor_medians,
                                                           trunc_pd, is_engineer_on_retainer)
    [time_sys, breakdowns] = impedance_days_ordered(num_sys, inspection_imped, financing_imped, permitting_imped,
                                                    contractor_mob_imped, eng_mob_imped, eng_design_imped, percentile)
    # Assuming num_reals and num_sys are defined, for example:
    num_sys = len(systems)  # number of systems
    # Initialize the dictionaries to store start and complete days

    # Assuming breakdowns is already properly populated
    impede = breakdowns
    #
    # # Error checking and label preparation
    # labels = prepare_labels(impede)  # This function could be enhanced as described
    #
    # # Plotting as before
    # fig, ax = plt.subplots(figsize=(10, 5))
    # positions = range(len(labels))
    # durations = [data['complete_day'] - data['start_day'] for data in impede.values()]
    # starts = [data['start_day'] for data in impede.values()]
    #
    #
    # ax.barh(positions, durations, left=starts, color='gray', alpha=0.5)
    # ax.set_yticks(positions)
    # ax.set_yticklabels(labels)
    # ax.set_xlabel('Days')
    # ax.set_title('Impedance Times by System and Factor')

    plt.show()

    # Calculate maximum number of workers for the entire building
    max_workers_per_building = min(
        max(
            math.floor(building_model['total_area_sf'] * repair_time_options['max_workers_per_sqft_building'] + 10),
            repair_time_options['max_workers_building_min']
        ),
        repair_time_options['max_workers_building_max']
    )

    # Calculate maximum number of workers that can be on any given story
    max_workers_per_story = math.ceil(
        building_model['area_per_story_sf'] * repair_time_options['max_workers_per_sqft_story']
    )


    num_stories = total_worker_days.shape[0]

    # num_stories = 2
    repair_start_days = np.zeros((num_sys, num_stories))
    repair_complete_days = np.zeros((num_sys, num_stories))
    max_workers_per_storys = np.zeros((num_sys, num_stories))
    priority_system_complete_day = np.zeros((num_sys, num_stories))
    system_complete_day = np.zeros((num_sys, num_stories))
    sys_start_day = np.zeros((num_sys, num_stories))

    num_du_per_crew = 4
    max_crews_per_comp_type = 1
    max_crews_building = max_crews_per_comp_type * 5;

    # average_crew_size = np.array([4.0,4.0])
    average_crew_size = np.tile(4, num_stories)
    worker_upper_limit = np.minimum(max_workers_per_story, max_workers_per_building)
    max_num_crews_per_story = np.maximum(np.floor(worker_upper_limit / average_crew_size), 1)
    num_crews = max_num_crews_per_story

    num_workers = average_crew_size * num_crews

    repair_complete_day = np.zeros((num_stories))
    repair_start_day = np.full((num_stories), np.nan)
    # max_workers_per_story = np.array([max_workers_per_story,max_workers_per_story])
    max_workers_per_story = np.tile(max_workers_per_story, num_stories)

    required_workers_per_story = np.array(num_workers)

    for sys in range(1, num_sys + 1):
        [repair_start_day, repair_complete_day, max_workers_per_story] = allocate_workers_stories(
            total_worker_days[:, sys - 1].reshape(1, num_stories), required_workers_per_story.reshape(1, num_stories),
            average_crew_size.reshape(1, num_stories), max_crews_building, max_workers_per_building)

        # repair_start_days[sys-1,0:2] = np.ceil(np.max(repair_start_day))
        # repair_complete_days[sys-1,0:2] = np.ceil(np.max(repair_complete_day))
        # max_workers_per_storys[sys-1,0:2] = np.ceil(np.max(max_workers_per_story))

        repair_start_days[sys - 1, 0:num_stories + 1] = np.ceil(repair_start_day)
        repair_complete_days[sys - 1, 0:num_stories + 1] = np.ceil(repair_complete_day)
        max_workers_per_storys[sys - 1, 0:num_stories + 1] = np.ceil(max_workers_per_story)

    tmp_repair = simulate_tmp_repair_times(1, 20, 15, 140, 0.6, 1)

    sys_repair_start_days = np.max(repair_start_days, 1)
    sys_repair_complete_days = np.max(repair_complete_days, 1)
    sys_crew_size = np.max(max_workers_per_storys, 1)
    sys_idx_priority_matrix = sys_priority_matrix
    condition_tag = red_tag
    sys_impeding_factors = time_sys[0]
    # Call the function
    repair_complete_day_per_system, worker_data = allocate_workers_systems(
        sys_repair_complete_days, sys_crew_size, max_workers_per_building,
        sys_idx_priority_matrix, sys_constraint_matrix, condition_tag, sys_impeding_factors
    )


    num_sys = len(systems['id'])
    num_units = num_stories
    story_start_day = np.zeros((num_stories))
    story_complete_day = np.zeros((num_stories))
    unit_start_day = np.zeros((num_sys, num_units))
    unit_complete_day = np.zeros((num_sys, num_units))

    # Redistribute repair schedule data
    sys_idx = 0
    for sys_idx in range(num_sys):
        # Calculate system repair times on each story
        system_duration = sys_repair_complete_days[sys_idx]  # total repair time spent in this system over all stories
        start_day = repair_complete_day_per_system[sys_idx] - system_duration
        story_start_day = start_day[np.newaxis] + repair_start_days[sys_idx]
        story_complete_day = start_day[np.newaxis] + repair_complete_days[sys_idx]

        for unit in range(num_units):
            sys_filt = np.asarray(total_worker_days_orig[unit, sys_idx] != 0)
            unit_start_day[sys_idx, unit] = sys_filt * story_start_day[unit]
            unit_complete_day[sys_idx, unit] = sys_filt * story_complete_day[unit]

    # Initialize variables
    sys_repair_times = []
    labs = []
    labels = systems['name']  # This function could be enhanced as described

    print(num_units)
    # Retrieve the field names of the 'impede' dictionary

    # Loop through each system
    for sys in range(1,
                     num_sys + 1):  # WARNING: This assumes the system order in the output of repair schedule is the same order has the impedance breakdowns
        duration = sys_repair_complete_days[sys - 1]

        if duration > 0:
            sys_repair_times.append([repair_complete_day_per_system[sys - 1] - duration, duration])
            labs.append(f"{labels[sys - 1][0].upper()}{labels[sys - 1][1:]} Repairs")

    recovery_day = {
        'building_safety': {
            'red_tag': repair_complete_day_per_system[0],  # structure complete
        },
        'tenant_safety': {
            'interior': unit_complete_day[2, :],  # Replace with actual data
            'exterior': unit_complete_day[1, :],  # Replace with actual data
        }
    }

    # Calculate the day the building is safe
    day_building_safe = recovery_day['building_safety']['red_tag']

    # Check the day each tenant unit is safe
    day_tenant_unit_safe = np.maximum(recovery_day['tenant_safety']['interior'],
                                      recovery_day['tenant_safety']['exterior'])

    # Combine checks to determine when each tenant unit is re-occupiable
    # day_tentant_unit_reoccupiable = np.maximum(day_building_safe, day_tenant_unit_safe)
    day_tentant_unit_reoccupiable = unit_complete_day[0, :]
    if red_tag == 1:
        day_tentant_unit_reoccupiable = np.maximum(day_tentant_unit_reoccupiable,
                                                   np.ceil(impede['permitting_Structure']['complete_day']))
        percent_recovered = np.sort(np.hstack((np.arange(num_units), np.arange(1, num_units + 1)))) / num_units
        percent_recovered = 1 - closed_area / total_area + closed_area / total_area * percent_recovered
        percent_recovered[0] = 0
        percent_recovered[1] = 0
        percent_recovered[2] = 0
        percent_recovered[3] = 1 - closed_area / total_area
        percent_recovered[4] = 1 - closed_area / total_area
        # percent_recovered[3] = 1 - closed_area / total_area
    else:
        day_tentant_unit_reoccupiable = unit_complete_day[0, :]
        percent_recovered = np.sort(np.hstack((np.arange(num_units), np.arange(1, num_units + 1)))) / num_units
        percent_recovered = 1 - closed_area / total_area + closed_area / total_area * percent_recovered

    recovery_days_occupancy = np.sort(np.hstack((day_tentant_unit_reoccupiable, day_tentant_unit_reoccupiable)), axis=0)

    day_tentant_unit_functional = day_tentant_unit_reoccupiable
    for i in range(num_sys):
        day_tentant_unit_functional = np.maximum(day_tentant_unit_functional, unit_complete_day[i, :])

    recovery_days_functionality = np.sort(np.hstack((day_tentant_unit_functional, day_tentant_unit_functional)), axis=0)

    fully_repaired = np.zeros([3, 2])
    if red_tag == 1:
        fully_repaired[0, 0] = 0
        fully_repaired[0, 1] = 0
        fully_repaired[1, 0] = max(recovery_days_functionality)
        fully_repaired[1, 1] = 0
        fully_repaired[2, 0] = max(recovery_days_functionality)
        fully_repaired[2, 1] = 1
    else:
        fully_repaired[0, 0] = 0
        # fully_repaired[0, 1] = 1 - closed_area / total_area
        fully_repaired[0, 1] = 1 - closed_area / total_area
        fully_repaired[1, 0] = max(recovery_days_functionality)
        fully_repaired[1, 1] = 1 - closed_area / total_area
        fully_repaired[2, 0] = max(recovery_days_functionality)
        fully_repaired[2, 1] = 1

    # Flip the labels and repair times for plotting
    labs_rep = labs[::-1]
    y_rep = np.array(sys_repair_times[::-1])

    fig, axs = plt.subplots(3, figsize=(10, 18))  # Create 3 subplots
    labels = prepare_labels(impede)  # This function could be enhanced as described

    positions = range(len(labels))
    durations = [data['complete_day'] - data['start_day'] for data in impede.values()]
    starts = [data['start_day'] for data in impede.values()]

    x = labs_rep
    y_start = y_rep[:, 0]
    y_duration = y_rep[:, 1]
    # Plot the horizontal bar chart

    return impede, recovery_days_occupancy, percent_recovered, recovery_days_functionality, fully_repaired,labs,sys_repair_times



