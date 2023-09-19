
# Import the necessary packages
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from functions import column_cost_calculation, floor_system_cost,fire_service_cost,calculate_fireprotection_cost
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to PBSFD project! 👋")
# Streamlit app
st.markdown('### **Enter the path for saving the files**')
# User input for the save path
save_path = st.text_input('Path:')
st.write(save_path)
st.session_state.path_for_save = save_path     # Attribute API
# upload images

floor_diagram = "images/floor diagram.jpg"
floor_diagram_rsmeans = "images/concrete slab over metal deck.jpg"

# Display the image based on the file path


st.markdown('# Introduction and Assumptions:')
st.markdown('### Construction cost database')
with st.expander('Descrition:', expanded=False):
    st.markdown(''' The construction database selected eight building typologies consisting of four occupancy types and two sizes per occupancy.
     The cost analysis is run on 130 building prototypes selected amongst the eight typologies based on the RS.Means square foot cost estimation.
      To estimate costs, the **building type, perimeter, total area, story, and story height** are needed. These parameters can be viewed in the page **Explore
      construction cost database**. Additionally, the width-to-length ratio of the prototypes is set 3/4, and the cost value is based on the US national average 
      for 2022. Considering that the construction cost database mainly focuses on the composite steel frame structures,several parameters 
       in the default RS.Means database are adjusted, such as the floor systems and fire rating on steelwork.**The fire rating for the steel 
       and composite structural members is adjusted based on the International Building Code (IBC) requirements.**
    ''')
    tab1, tab2, tab3 = st.tabs(["**Floor system**", "**Column**", "**Other fire services**"
                                              ])
    with tab1:
        st.markdown(''' 
        The default floor system in RS.Means may not be the commonly used steel-concrete composite systems, for example,
        concrete slab over metal deck with steel joists and joist girder (Left figure) is adopted in default hospital prototypes. 
        This floor system  in the database is replaced with a composite metal deck with shear connector (Right figure) for consistency in the type of 
        steel-concrete composite systems considered.
        ''')

        col1, col2 = st.columns(2)
        with col1:
            st.image(floor_diagram_rsmeans, caption='Default floor system from RS.Means (for certain occupancies)', use_column_width=None)
        with col2:
            st.image(floor_diagram, caption='Updated floor system in the construction database', use_column_width=None)
    with tab2:
        st.markdown(''' 
        The default column number calculation method is not consistant across different building types in the square foot
        cost estimation. For example, in the left figure for apartment building, the number of column in high-rise (with story 8-24) buildings is much
        higher that that for mid-rise (with story 5-7) buildings, even though the area and story is close 
        **(area 74500 story 7 vs area 80750 story 8).**  
        
        Similar difference can be found in the office building. Therefore, **the calculation of column number is adjusted by the following equation**:
        ''')
        st.markdown(        r"$N_{column}^i=A/(b_1\times b_2\ )+x_1/b_1\ +x_2/b_2\ +1$"
    '''
        <div align='right'>**Eq.1.1**</div>
        $N_{column}^i$ is the number of column per story;
        $A$ is the story area; $b_1$ and $b_2$ are the length and width of a typical bay; 
        $x_1$ and $x_2$ are the length and width of the story
        ''',unsafe_allow_html=True)

        fig_apartment_column = "images/apartment_building_column.jpg"
        fig_office_column = "images/office_building_column.jpg"
        col1, col2 = st.columns(2)
        with col1:
            st.image(fig_apartment_column,
                 caption=' Number of column under different floor area and story for apartment building.',
                 use_column_width=None)
        with col2:
                st.image(fig_office_column,
                         caption=' Number of column under different floor area and story for office building.',
                         use_column_width=None)
    with tab3:
        st.markdown('''
        * **Partition fire protection cost:** only consider the costs of fire-resistant related materials on the partitions.  
        * **Sprinkler cost:** includes the cost of wet pipe sprinkler system and the high-rise accessory package of the whole building.  
        * **Fire pump cost:** includes the cost of both the fire pump and corresponding controller of the whole building.  
        * **Fire alarm cost:** fire alarm cost of the whole building.  
        * **Ceiling fire protection cost:** cost of non-structural fire rated materials in the ceiling (at all stories).
        May include “suspended gypsum boards” for example. 
        ''')


st.markdown('### 1. Construction cost estimation')
with st.expander('Method 1: modify database:', expanded=False):
       # st.markdown('1')
    #st.markdown('#### Subtool 1: modify database')
    flow_chart_method1 = "images/flow chart method 1.jpg"
    st.image(flow_chart_method1, caption=' Flowchart for quantifying the fire protection cost for buildings in the database.',
         use_column_width=None)

    tab1, tab2, tab3,tab4 = st.tabs(["**Building parameter**", "**Fire design parameter**", "**Fire protection cost value**",
                                               "**Enable Alternative design**"])

    with tab1:
        st.markdown('Input building index should be in the range 1 to 130, default fire rating, '
                    'floor area, stories, etc, can be found in the database summary of **Explore construction cost database**.'                      )
        st.markdown('''
        For the default building parameter modification,the initial values are the same as the default value in the database.  
        ''')

        st.markdown('''
        * Modification of story height: story height can affect the total length of columns, and therefore affect the amount of column 
        passive fire protection cost. It would not affect the cost of the floor system.  ''')
        st.markdown('''
        * Modifying total floor area: total floor area would affect both the floor system fire protection cost and the column fire 
        protection cost. The number of columns would increase with the increase of floor area. 
        * Modifying bay total load: the bay total load would affect the column section size and then can make a difference in
        the column fire protection cost and column construction cost. If the warning (Floor load is over the max column 
        loading capacity) shows, it means the maximum load is higher than the maximum capacity (right now, it is 1000 kips 
        per column) in the column. Users can modify this file by uploading their own cost data.
        It should also affect the unit cost of the floor system (beam size would change due to higher or lower loads) 
        and the corresponding fire protection cost, **but right now is not considered in the codes**.  
        * Modifying the building stories: can have a minor effect on the column fire protection cost since the number of 
        column are changed.  
        * Modifying the bay size x direction and bay size y direction: affect the number of column fire protection 
        cost. Besides, it should also affect the size and number of beams, **but right now we have not developed 
        the relationship between the bay size and floor system fire protection cost**.  
        ''')

    with tab2:
        st.markdown(''' 
        For the default fire design parameter modification, the initial values are the same as the default value in the database.   
        * The unit fire protection costs for beams and columns with different fire ratings or materials are pre-defined. 
        Once the fire rating or material is changed, the fire protection cost would be updated. User can also provide their 
        own material cost data under different fire ratings, just by uploading their own unit cost value. However it needs 
        to be noted that the format of the unit cost value should be the same as the sample, only the values in the sample 
        can be modified.  
        * Modifying the beam or column fire protection percentage: the cost of beam/column fire protection cost, 
        and labor hour would simply be discounted by the inputted percentage. If you want to do a 
        more detailed modification, such as specifying that only central beam is unprotected, it can be 
        done by selecting “user-defined building” function or collecting the percentage of the central beam.
        ''')

    with tab3:
        st.markdown(''' 
        The unit cost data can be modified and uploaded by the user. In row 1-41, column 1-7, the **column construction cost**, **fire protection cost
        and loading capacity** can be modified. In row 1-41, column 10-14, the **floor system fire protection cost** can be modified. In row 7-25, column 15-24
        the **unit beam fire protection cost** with different section size can be modifed.
        In row 1-6, column 25-33, the value related to **labor hour** can be calculated.
        * Column construction cost: The default unit construction cost of column is obtained from RS.Means, based on the floor area and bay load, the column size
        is selected automatically. User can change the table to get higher loading capacity. The following figure shows how to determine the column size when
        floor area and floor load are given:
        ''')
        fig_column_determine = "images/column size selection.jpg"
        st.image(fig_column_determine,
                 caption=' Flowchart for determine steel column with floor area and load given.',
                 use_column_width=None)
        st.markdown(''' 
        * Column fire protection cost: in the default cost value, the unit of SFRM and intumescent are provided for column size 8, 10, 12 and 14. The **1 h fire rating is obtained by
        interpolating the RS.Means value for 2h,3h,and 4h fire rating**.
        * Floor system fire protection cost: the floor system fire protection cost at different fire rating is **based on the 20*25 typical bay** with 80 psi
        floor load (19.99 USD/sq.ft) and 115 psi floor load (20.65 USD/sq.ft). If user wants to change the typical bay size, the new floor system cost should be provided to
        get a precise estimation on the cost multiplier and total construction cost. Otherwise, only the total floor system fire protection cost would be updated.
        * Unit beam fire protection cost: this part mainly **affect the user-defined building fire protection cost**, because the fire protection cost for any given section size 
        is calculated by interpolating the exposed perimater and total cost.
        * Labor hour: The estimation of labor hour is based on the unit cost of crew G-2, which is 1139.28 USD per day (8 HR for working). In RS.Means, each unit cost is composed by bare material cost,
        bare labor cost, and bare equipment cost. The **labor hour is estimated by bare labor cost / 1139.28 *24**. 
        The value of $1139.28 and bare labor cost for unit SFRM can be updated in the unit cost file. **For the intumescent, the labor hour is set as 0 to assume that the intumescent
        coating is applied off-site.**
        
        ''')

    with tab4:
        st.markdown(''' 
        Enable interpolation: for the cost of other the fire services such as partition, sprinkler, 
        fire pump, alarm, and ceiling, these values can be obtained from the construction cost database 
        based on the prototypes in the RS.Means. **The newest value can be interpolated by the 
        floor area based on the known values in the database**.    
        ''')

with st.expander('Method 2: User-defined building:', expanded=False):
    flow_chart_method2 = "images/flow chart method 2.jpg"
    st.image(flow_chart_method2, caption=' Flowchart for quantifying the fire protection cost for user-defined buildings.',
         use_column_width=None)
    st.markdown(''' There is a built-in database which can provide the weight, perimeter, and section area of different steel size. Therefore,
    when the steel size (e.g., W16X31, or W18X35) is listed in the input file, **the corresponding perimeter, W/D ratio or A/P ratio would be obtained
    aotumatically.**
    ''')
    tab1, tab2, tab3 = st.tabs(["**RS.Means default thickness**", "**Thickness adjust equation**", "**Thickness is given**"         ])
    with tab1:
        st.markdown("""
        In RS.Means, the fire protection **thickness on beams or column did not consider the effects of section size**. For a given
        fire rating, the thickness of fire protection would be the same for heavy section and thin section. **The unit fire protection cost
        would linearly increse with the increase of exposed perimeter of the given section.**
        """,unsafe_allow_html=True)
        fig_unit_cost = "images/unit cost linear interpolation.jpg"
        st.image(fig_unit_cost, caption='  Relationship between unit fire protection cost and exposed perimeter fitted from RS.Means data.',
             use_column_width=None)
    with tab2:
        st.markdown(''' justify align <div align='justify'>
        In AISC steel design guide 19 - fire resistance of structural steel framing, the SFRM thickness adjusting equation for beams and columns
        are provided. For sections with higher W/D ratio, the thickness would be thinner. Several material constants are provided in the design guide and can help to
        adjust the thickness of SFRM for steel columns. **The equations are listed as following**:
        </div>
        Column:
        <div align='center'>$h=R/[c_1\ (W/D)+c_2\ ]$</div> 
        <div align='right'>**Eq.1.2**</div>
        Beam:
        <div align='center'>$h_1=[W_2/D_2\ +0.6] h_2/[W_1/D_1 +0.6]$</div> 
        <div align='right'>**Eq.1.3**</div> 
        <div align='justify'>
        where $h$ is the SFRM thickness (in.); $R$ is the fire resistance rating (hours); $W$ is the weight (lbs. per ft.); $D$ is the perimeter of column at the interface 
        of the SFRM (in.); $c_1$ and $c_2$ are material dependent constants; the subscript 1 in $h$, $W$ and $D$ refers to desired beam size and required material thickness; 
        the subscript 2 in $h$, $W$ and $D$ refers to given beam size and material thickness shown on the individual design.          
        For the intumescent,the thickness varies significantly with the material type and brand. There is no clear equations to adjust the thickness. Here we based on the 
        **UL design X649** to adjust the thickness based on the given table. It worth mentioning that the **table in X649 is for column**. 
        For the thickness adjustment of **beams**,no table or equaiton is found and the table in **X649 is also adopted provisionally**.
        Once the thickness of the fire protection is obtained, the unit volumn of fire protection would be calculated by thickness times perimeter of steel
        members. **Assume there is a linear relationship between the unit cost and unit volumn: cost=a*volumn+b**, where a and b are predefined constant. Users can also
        modify this value based on their own cost data.**(temporarily)**
        </div>
        ''',unsafe_allow_html=True)
    with tab3:
        st.markdown(''' 
        User should provide the thickness of each steel member in the uploaded file. **The volumn would be calculated based on this given thickness.**
        ''')

st.markdown('### 2. Direct damage estimation')
with st.expander('General description on direct and indirect damage estimation:', expanded=False):
    st.markdown('''The following flow chart from [NFPA report](https://biblio.ugent.be/publication/01GVXPJ6YXPCGJ3J3KDD6T6HFM) shows the procedure of
    conducting damage assessment of buildings under fire. The first step is to determine the hazard intensity such as fire load. The second step is to determine
    the direct property loss, such as the demolish and reconstruction cost of the fire compartment. These are also direct losses related to human life and injury.
    The next step is to estimate the indirect loss such as the rent loss due to the fire.
     ''')
    flow_chart_fire_loss = "images/flowchart of estimating fire loss in building.jpg"
    st.image(flow_chart_fire_loss, caption=' Flowchart of estimating fire loss in building [NFPA REPORT].',
         use_column_width=None)
with st.expander('Details on direct damage estimation:', expanded=False):

    st.markdown('''
    **Firstly**, obtained the fragility function for all the possible fire compartment based on the following flow chart:
    ''')
    fig_damage_assessment = "images/damage assessment.jpg"
    st.image(fig_damage_assessment,
             caption='  Procedure for the development of the Local Fragility Functions FFL,i corresponding to a fire located in compartment i.[TG]'                ,
             use_column_width=None)

    st.markdown('''
    [TG](https://doi.org/10.1016/j.engstruct.2016.01.043):'Gernay, Thomas, Negar Elhami Khorasani, 
    and Maria Garlock. "Fire fragility curves for steel buildings in a community context: A methodology." 
    Engineering Structures 113 (2016): 259-276.
    ''')
    st.markdown('''
    **Secondly**, combining all the fragility function to the vulnerability function of the whole building, which can bridge the 
    damage state and damage value for the building.
    ''')
    st.markdown('''
    Right now, only **one compartment fire is considered**, and the possibility of fire spread would considered by defined the cost value at the highest
    damage state.
    ''')


st.markdown('### 3. Indirect damage estimation')
with st.expander('Details:', expanded=False):
    st.markdown('1')
st.markdown('### 4. Maintenance estimation')
with st.expander('Details:', expanded=False):
    st.markdown('1')
st.markdown('### 5. Co-benefit estimation')
with st.expander('Details:', expanded=False):
    st.markdown('1')
st.markdown('### 6. ASTM indexes calculation')
with st.expander('Details:', expanded=False):
    flow_chart_astm = "images/flow chart astm.jpg"
    st.image(flow_chart_astm,
             caption=' Flowchart of the cost-benefit analysis.',
             use_column_width=None)




# Save the DataFrame when the user clicks the button
#if st.button('Save DataFrame'):
#    try:
#        df.to_csv(save_path, index=False)
#        st.success(f'DataFrame saved to {save_path}')
#    except Exception as e:
#        st.error(f'An error occurred: {str(e)}')
