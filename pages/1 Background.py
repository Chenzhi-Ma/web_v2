
# Import the necessary packages

import streamlit as st

floor_diagram = "images/floor diagram.jpg"
floor_diagram_rsmeans = "images/concrete slab over metal deck.jpg"

# Display the image based on the file path


st.markdown('# Introduction and Assumptions:')
st.markdown('### Construction cost database')
with st.expander('Description:', expanded=False):
    st.markdown('''<div align='justify'>The construction database selected eight building typologies consisting of four occupancy types and two sizes per occupancy.
     The cost analysis is run on 130 building prototypes selected amongst the eight typologies based on the RSMeans square foot cost estimation.
      To estimate costs, the <b>building type, perimeter, total area, story, and story height</b> are needed. These parameters can be viewed in the page <b>Explore
      construction cost database</b>. Additionally, the width-to-length ratio of the prototypes is set 3/4, and the cost value is based on the US national average 
      for 2022. Considering that the construction cost database mainly focuses on the composite steel frame structures, several parameters 
       in the default RSMeans database are adjusted, such as the floor systems and fire rating on steelwork. <b>The fire rating for the steel 
       and composite structural members is adjusted based on the International Building Code (IBC) requirements.</b>
     ''',unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["**Floor system**", "**Column**", "**Other fire services**"
                                              ])
    with tab1:
        st.markdown(''' 
        The default floor system in RSMeans may not be the commonly used steel-concrete composite systems, for example,
        concrete slab over metal deck with steel joists and joist girder (Left figure) is adopted in default hospital prototypes. 
        This floor system  in the database is replaced with a composite metal deck with shear connector (Right figure) for consistency in the type of 
        steel-concrete composite systems considered.
        ''')

        col1, col2 = st.columns(2)
        with col1:
            st.image(floor_diagram_rsmeans, caption='Default floor system from RSMeans (for certain occupancies)', use_column_width=None)
        with col2:
            st.image(floor_diagram, caption='Updated floor system in the construction database', use_column_width=None)
    with tab2:
        st.markdown(''' 
        The default column number calculation method is not consistent across different building types in the square foot
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
        st.markdown('''
        **Noting that in the RSMeans prototypes, the costs of sprinkler and alarm system are only dependent 
        on the floor area and building type, and the fire pump costs are only dependent on the building type.**
        ''')
st.markdown('### 1. Construction cost estimation')
with st.expander('Description:', expanded=False):
    flow_chart_1 = "images/flowchart construction cost1.jpg"
    flow_chart_2 = "images/flowchart construction cost2.jpg"
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('''
          The construction database established is used to support the development of a generalized method for estimating 
          the cost of passive fire protection on steelwork in buildings. Figure 1 shows the simplified flowchart of the method 
          of assessing the passive fire protection cost on different designs. The obtained initial construction cost can be used 
          for cost-benefit analysis and can help to make the decisions among different designs.  
          ''')
    with col2:
        st.image(flow_chart_1,
                 caption='Figure 1: Overall flowchart of assessing the construction cost of passive fire protection on steelwork. '
                         'Refer to Figure 2 for the detailed flowchart.',
                 use_column_width=None)


    st.markdown('''
                Figure 2 shows the detailed flowchart of three different approaches of assessing the construction cost 
                of passive fire protection.
                ''')
    st.image(flow_chart_2, caption=' Figure 2: Detailed flowchart of assessing the construction cost of passive fire '
                                   'protection with different methods. Refer to Figure 1 for the overall flowchart..',
         use_column_width=None)

    st.markdown('''
    Basic assumptions:  
    * The cost value is based on the **2022 RSMeans national average value**, and an additional correction factor 
    might be necessary in regions where the labor cost deviates significantly from the national average value.
    * The default unit cost values at different fire ratings and fire protection materials are pre-defined in the construction cost database, 
    but they can be replaced by the user defined unit cost in the web interface to achieve a more accurate cost estimation.
    * The construction cost database and the generalized method are based on specific building design parameters, and while the method 
    allows adjusting passive fire protection costs when building design parameters change, potential cost variations in associated 
    nonstructural or structural components are not accounted for in the total construction cost adjustment. In these cases, working 
    with the absolute value of passive fire protection cost could be more convenient than the cost multiplier.
    ''')

with st.expander('Method 1 & 2: Variation in the database:', expanded=False):
       # st.markdown('1')
    #st.markdown('#### Subtool 1: modify database')

    tab1, tab2, tab3,tab4 = st.tabs(["**Building parameter**", "**Fire design parameter**", "**Fire protection cost value**",
                                               "**Enable Alternative design**"])

    with tab1:
        st.markdown('Input building index should be in the range 1 to 130, default fire rating, '
                    'floor area, story, etc, can be found in the _database summary_ of **Explore construction cost database**.'                      )
        st.markdown('''
        For the default building parameter modification, the initial values are the same as the default value in the database.  
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
        per column) of the column. Users can modify this file by uploading their own cost data (A1-G16 provide the correlation between 
        the column cost and capacity).
        It should also affect the unit cost of the floor system (beam size would change due to higher or lower loads) 
        and the corresponding fire protection cost, **but right now is not considered in the codes**.  
        * Modifying the building stories: can have a minor effect on the column fire protection cost since the number of 
        column are changed.  The fire protection cost in floor system would not change since it is only dependent on the floor area.
        * Modifying the bay size x direction and bay size y direction: affect the number of column fire protection 
        cost. Besides, it should also affect the size and number of beams, **but right now we have not developed 
        the relationship between the bay size and floor system fire protection cost**.  
        ''')

    with tab2:
        st.markdown(''' 
        For the default fire design parameter modification, the initial values are the same as the default value in the database.   
        * The unit fire protection costs for beams and columns with different **fire ratings** or **fire protection materials** 
        are pre-defined. Once the fire rating or material is changed, the fire protection cost would be updated. User can also provide their 
        own material cost data under different fire ratings, just by uploading their own unit cost value. However it needs 
        to be noted that the format of the unit cost value should be the same as the sample, only the values in the sample 
        can be modified.  
        * Modifying the **percentage of protected beam or column**: the cost of beam/column fire protection cost, 
        and labor hour would simply be discounted by the inputted percentage. If you want to do a 
        more detailed modification, such as specifying that only central beam is unprotected, it can be 
        done by selecting “user-defined building” function or collecting the percentage of the central beam.
        ''')

    with tab3:
        st.markdown(''' 
        The unit cost data can be modified and uploaded by the user. In A1-G41, the **column construction cost**, **fire protection cost
        and loading capacity** can be modified. In J1-N41, the **floor system fire protection cost** can be modified. In P7-X25
        the **unit beam fire protection cost** with different section size can be modified.
        In Z1-AG6, the cost value related to CREW-G2, SFRM are listed and from which the **labor hour** was calculated, increasing the bare labor 
        cost can increase the labor hour needed.
        * Column construction cost: The default unit construction cost of column is dependent on the column size. The column size 
        is selected automatically based on the floor area and bay load. User can change the table to get higher loading capacity. 
        The following figure shows how to determine the column size when floor area and floor load are given:
        ''')
        fig_column_determine = "images/column size selection.jpg"
        st.image(fig_column_determine,
                 caption=' Flowchart for determine steel column with floor area and load given.',
                 use_column_width=None)
        st.markdown(''' 
        * Column fire protection cost: in the default cost value, the unit of SFRM and intumescent 
        are provided for column size 8, 10, 12 and 14. The **1 h fire rating is obtained by
        extrapolating the RSMeans value for 2h,3h,and 4h fire rating**.
        * Floor system fire protection cost: the floor system fire protection cost at different fire 
        rating is **based on the 20*25 typical bay** with 80 psi
        floor load (19.99 USD/sq.ft) and 115 psi floor load (20.65 USD/sq.ft). If user wants to change 
        the typical bay size, the new floor system cost should be provided to
        get a precise estimation on the cost multiplier and total construction cost. Otherwise, only 
        the total floor system fire protection cost would be updated.
        * Unit beam fire protection cost: this part mainly **affect the user-defined building fire 
        protection cost**, because the fire protection cost for any given section size 
        is calculated by interpolating the exposed perimeter and total cost.
        * Labor hour: The estimation of labor hour is based on the unit cost of crew G-2, which 
        is 1139.28 USD per day (8 HR for working). In RSMeans, each unit cost is composed by bare material cost,
        bare labor cost, and bare equipment cost. The **labor hour is estimated by bare labor cost / 1139.28 *24**. 
        The value of $1139.28 and bare labor cost for unit SFRM can be updated in the unit cost 
        file. **For the intumescent, the labor hour is set as 0 to assume that the intumescent
        coating is applied off-site.**
        
        ''')

    with tab4:
        st.markdown(''' 
        Enable interpolation: for the cost of other the fire services such as partition, sprinkler, 
        fire pump, alarm, and ceiling, these values can be obtained from the construction cost database 
        based on the prototypes in the RSMeans. **The newest value can be interpolated by the 
        floor area based on the known values in the database**.    
        ''')

with st.expander('Method 2: User-defined building:', expanded=False):
    flow_chart_method2 = "images/flow chart method 2.jpg"
    st.image(flow_chart_method2, caption='Figure 1: Flowchart for quantifying the fire protection cost for user-defined buildings.',
         use_column_width=None)
    st.markdown(''' There is a built-in database which can provide the weight, perimeter, and section area of different steel size. Therefore,
    when the steel size (e.g., W16X31, or W18X35) is listed in the input file, **the corresponding perimeter, W/D ratio or A/P ratio would be obtained
    automatically.**
    ''')
    tab1, tab2, tab3 = st.tabs(["**RSMeans default thickness**", "**Thickness adjust equation**", "**Thickness is given**"         ])
    with tab1:
        unit_cost_perimeter = "images/exposed_parameter_unitcost.jpg"
        unit_cost_volume = "images/volume_unit_cost.jpg"
        st.markdown('''
        In RSMeans, the fire protection **thickness on beams or column did not consider the effects of section size**. For a given
        fire rating, the thickness of fire protection would be the same for heavy section and thin section. **The unit fire protection cost
        would linearly increase with the increase of exposed perimeter of the given section**, as shown in Figure 2.
        ''',unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 7, 1])
        with col2:
            st.image(unit_cost_perimeter, caption=' Figure 2: Relationship between unit fire protection cost and exposed perimeter fitted from RSMeans data.',
             use_column_width=True)


        st.markdown(''' The linear fitting of cost – exposed perimeter curves at different fire rating in Figure 2 can be converted to cost
         – volume curves by multiplying with the default fire protection thickness in RSMeans database 
         **(5/8”, 1-1/8”, and 1-1/4” for 1-h, 2-h, and 3-h fire ratings)**, as shown in Figure 3. Then the cost of SFRM for 
         any volume is obtained by:
         </div>
         <div align='center'>$C_{\\text{fire member}} = P(1) \\times V + P(2)$</div>
         </div>  
         where $P(1)$ and $P(2)$ are the slope and y- intercept of the linear fitting curve in Figure 2, 
         with values of $18.59$ and $0.4126$, respectively; $C_{\\text{fire member}}$ is the passive fire protection 
         cost of any steel member with SFRM volume $V$.
         '''
        ,unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 5, 1])
        with col2:
            st.image(unit_cost_volume, caption='Figure 3:  Relationship between SFRM volume and corresponding unit cost in RSMeans.',
             use_column_width=True)
        st.markdown('''
        **It is worthy noting that the SFRM volume-cost curve is converted from the exposed perimeter-cost curve, which means these two options are
        equivalent when the RSMeans default cost value is adopted.**
         ''')

    with tab2:
        st.markdown('''In AISC steel design guide 19 - fire resistance of structural steel framing, the SFRM thickness adjusting equation for beams and columns
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
        </div>
        ''',unsafe_allow_html=True)
        st.markdown('''
        For the intumescent,the thickness varies significantly with the material type and brand. There is no clear equations to adjust the thickness. Here we based on the 
        **UL design X649** to adjust the thickness based on the given table. It worth mentioning that the **table in X649 is for column**.  
        ''',unsafe_allow_html=True)
        st.markdown('''
        For the thickness adjustment of **beams**,no table or equation is found and the table in **X649 is also adopted provisionally**.
        Once the thickness of the fire protection is obtained, the unit volume of fire protection would be calculated by thickness times perimeter of steel
        members. **Assume there is a linear relationship between the unit cost and unit volume: cost=a*volume+b**, where a and b are predefined constant. Users can also
        modify this value based on their own cost data.**(temporarily)**
        ''',unsafe_allow_html=True)

        st.markdown('''
        **Noting that the cost data on intumescent material contains a lot of uncertainty, and very limited data are available
        on the RSMeans.**
        ''',unsafe_allow_html=True)

    with tab3:
        st.markdown(''' 
        User should provide the thickness of each steel member in the uploaded file. **The volume would be calculated based on this given thickness.**
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
    [TG](https://doi.org/10.1016/j.engstruct.2016.01.043): Gernay, Thomas, Negar Elhami Khorasani, 
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

st.markdown('### Fragility Curves')
with st.expander('General Description:', expanded=False):
    st.markdown(''' Fragility curves are used to depict the **probability of exceedance of specific damage states** defined by 
    appropriate engineering demand parameters. These probabilities are conditioned on the intensity measure, 
    such as ground peak acceleration in an earthquake, wind speed in a hurricane, and fire load in a fire event.
    ''')
    st.markdown(''' The probabilistic damage assessment accounts for **uncertainties** in three key areas: **the fire model, 
    the thermal response model, and the structural response model**. To generate the **fragility points** $P(DS=DS_i|q_m)$, 
    fire-thermo-mechanical analyses are conducted by the non-linear analysis of the building.  
    
    The probability of the composite floor reaching a specific 
    damage state $DS_i$ is assessed for a given fire load $q_m$, and is calculated by Eq. (1). Once the fragility points 
    at different fire loads are generated, the **fragility curves** are fitted using a two-parameter lognormal distribution 
    function, as outlined in Eq. (2). The illustration of the fragility curves is shown in Figure 1.  
    ''', unsafe_allow_html=True)

    st.markdown(r'''
    $$
    \begin{align*}
    P\left(DS=DS_i|q_m\right)=\frac{Number\ of\ simulation\ in\ damage\ state\ i\ under\ 
        fire\ load\ q_m}{Total\ number\ of\ simulations\ under\ fire\ load\ q_m}
    \end{align*}
    $$
    <div align='right'><b>Eq.1</b> 
    ''', unsafe_allow_html=True)

    st.markdown(r'''
    $$
    \begin{align*}
    FFs(DS_i|q)=P\left(DS\geq D S_i|q\right)=\emptyset\left[\frac{\ln\
    (MinMaxScaler\left(q\right))-\mu}{\sigma}\right]
    \end{align*}
    $$
    $$
    \begin{align*}
    =\frac{1}{2}\left[1+erf(\frac{\ln{\left
    (\frac{q-q_{min}}{q_{\max{-q_{min}}}}\right)}-\mu}{\sigma\sqrt2})\right]
    \end{align*}
    $$
    <div align='right'><b>Eq.2</b> 
    ''', unsafe_allow_html=True)

    st.markdown('''
    where $\emptyset$ is the standardized normal distribution function, $MinMaxScaler(q)$ 
    normalizes the fire load to range [0, 1], $erf$ is the Gauss error function, $\mu$ and $\sigma$ 
    are two parameters characterizing the fragility functions and are determined by 
    maximizing the best fit with the data from the analysis.
    ''')

    fig_damage_assessment = "images/sample of fragility curve.jpg"
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        st.image(fig_damage_assessment,
                 caption='  Figure 1: Sample of the fragility curves',
                 use_column_width=None)

    st.markdown('''
    From these curves, 
    one can derive the probability of reaching a specific damage state at a given fire load, as well as the cumulative 
    probability of encountering that damage state. This graphical representation is essential for visualizing and 
    understanding the likelihood and severity of damage under varying fire load conditions, thereby providing valuable 
    insights for risk assessment and structural design considerations.
    ''', unsafe_allow_html=True)

with st.expander('Built-in Fragility curves:', expanded=False):
    st.markdown(''' A series of built-in fragility curves is developed based on the recent [NIST full scale fire test on the 
    composite floor system](https://www.nist.gov/el/fire-research-division-73300/national-fire-research-laboratory-73306/steel-concrete-composite). 
    The the composite floor used for developing the fragility curves is the same as the NIST prototypes, with size of $6.14 m X 9.1 m$ and 
    floor gravity load of $5.2kPa$.
    The numerical models were calibrated on recent NIST full-scale fire test prototypes, with the test results validating the model.[Check recent paper
    for details]. The validated models are then used for constructing the fragility curves of various designs.  
    
    Two design methods are considered: **Prescriptive design** and **Performance-based design**. 
    In the prescriptive design, all the **beams are protected**, while the **central beam is unprotected** in the performance-based design.
    ''', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["**Probabilistic parameter**","**Definition of damage state**", "**Index for the built-in fragility curves**"])

    with tab1:
        st.markdown(r'''
        * In **fire model**: opening factor is introduced as a random parameter. [Check ref. for detail] 
        * In **thermal model**: The variability of thermal conductivity $k_i$, 
        specific heat $c_i$, and density $\rho_i$ of SFRM is modeled probabilistically. Detailed equation can check
        paper by [Elhami Khorasani et al.](https://ascelibrary.org/doi/full/10.1061/%28ASCE%29ST.1943-541X.000128) 
        * In **mechanical model**: The randomness of the reduction factor is captured using 
        the random variable $\varepsilon$ that follows the standard normal distribution function. 
        [Elhami Khorasani et al.](https://ascelibrary.org/doi/full/10.1061/%28ASCE%29ST.1943-541X.000128) 
        ''')
        distribution_of_variables = "images/distribution_of_variables.jpg"

        st.image(distribution_of_variables,
                 caption='Figure 1: Distribution of random variable for: (a) Opening factor, (b) '
                         'Thermal conductivity of SFRM, (c) Specific heat of SFRM, (d) Density of SFRM, and (e) Yield strength of steel.',
                 use_column_width=None)

    with tab2:
        damage_state_definition = "images/damage_state_definition.jpg"
        st.markdown(r'''
        * **Damage states one to three** represent mild to moderate damage the composite floor would reach under fire events. Damage 
        state three is the maximum damage the floor system can sustain without experiencing integrity failure. 
        * **Damage state four** is proposed to denote the **integrity failure** of the floor system. Here, once the steel failure is observed in the 
        simulation or the simulation stops due to large deflection, the damage state of that realization is designated as 
        damage state four. 
        
        The assumption of **linking rebar failure with integrity failure** is based on test observation. 
        In NIST test #1, the concrete crack above the central beam developed fast since the ruptured rebar cannot transfer 
        the load across the crack, leading to integrity failure. Flame leakage was observed at the slab top, and similar 
        observation was found in test #3 at 132 mins of exposure, indicating the potential of vertical fire spread. Thus, 
        steel rebar failure is an indicator of crack concentration and may result in flame leakage and integrity failure.
        ''')
        st.image(damage_state_definition,
                 caption='Table 1: Definition of different damage states of the composite floor system.',
                 use_column_width=None)

    with tab3:
        Fragility_curve_t1_t3 = "images/Fragility curve-t1-t3.jpg"
        Fragility_curve_C124 = "images/fragility curve 124.jpg"
        Fragility_curve_C356 = "images/fragility curve 356.jpg"
        aspect_ratio_C378 = "images/aspect ratio illustration.jpg"
        Fragility_curve_C378 = "images/fragility curve 378.jpg"
        BC_C3910 = "images/BC illustration.jpg"
        Fragility_curve_C3910 = "images/fragility curve 3910.jpg"


        st.markdown('''
        The composite floor is designed with 2-hour fire rating. Thickness of SFRM is the same as NIST test for all the following curves.
        (11/16 in for primary beams and girder, 7/16 for protected center beam.)
        * Curve 1: The same design as NIST test #1 prototype, **with protected central beam** and rebar area of 60 mm<sup>2</sup>/m. 
       The rebar area of 60 mm<sup>2</sup>/m is equivalent to **94 mm<sup>2</sup>/m** rebar with yield stress 480 Mpa. 
       **(Hereafter, all the rebar area are defined based on S480)**
       * Curve 2: The same design as NIST test #2 prototype, **with protected central beam** and rebar area of **230 mm<sup>2</sup>/m**. 
       * Curve 3: The same design as NIST test #3 prototype, **with unprotected central beam** and rebar area of **230 mm<sup>2</sup>/m**. 
        ''', unsafe_allow_html=True)

        st.image(Fragility_curve_t1_t3,
                 caption='Figure 2: Fragility curves for three designs of the composite floors tested by the NIST.',
                 use_column_width=None)

        st.markdown('''
        * Curve 4: The same design as NIST test #1 prototype, **with protected central beam** and rebar area of **157 mm<sup>2</sup>/m**. 
        The following figure (figure 3) shows the **Curve 1, Curve 2 and Curve 4** together to show the effects of rebar area on **prescriptive
        design.** The only variable is the rebar area, and all the other design parameters are set the same.
        ''', unsafe_allow_html=True)

        st.image(Fragility_curve_C124,
                 caption='Figure 3: Fragility curves for prescriptive design with different rebar areas.',
                 use_column_width=True)

        st.markdown('''
        * Curve 5: The same design as NIST test #3 prototype, **with unprotected central beam** and rebar area of **142 mm<sup>2</sup>/m**. 
        * Curve 6: The same design as NIST test #3 prototype, **with unprotected central beam** and rebar area of **345 mm<sup>2</sup>/m**. 
        ''', unsafe_allow_html=True)

        st.image(Fragility_curve_C356,
                 caption='Figure 4: Fragility curves for PBD design with different rebar areas.',
                 use_column_width=True)

        st.markdown('''
        Curve 7 and 8 have different **aspect ratios** with respect to curve 3. The **sizes of beam and 
        girder have been adjusted** to ensure the same load ratio as Test #3 when a constant 5.2 kPa load is applied. 
        Furthermore, the thicknesses of the SFRM on the primary beam and girder have been adjusted based on the equation mentioned previously.
        ''', unsafe_allow_html=True)

        st.image(aspect_ratio_C378,
                 caption='Figure 5: Illustration of different aspect ratios considered for the slab panel.',
                 use_column_width=True)

        st.markdown('''
        * Curve 7: The aspect ratio is changed to 1:1, **with unprotected central beam** and rebar area of **230 mm<sup>2</sup>/m**. 
        * Curve 8: The aspect ratio is changed to 1:3, **with unprotected central beam** and rebar area of **230 mm<sup>2</sup>/m**. 
        ''', unsafe_allow_html=True)

        st.image(Fragility_curve_C378,
                 caption='Figure 6: Illustration of different aspect ratios considered for the slab panel.',
                 use_column_width=True)

        st.markdown('''
        Curve 9 and 10 have different **boundary conditions** with respect to curve 3. 
        ''', unsafe_allow_html=True)

        st.image(BC_C3910,
                 caption='Figure 7: Illustration of different boundary conditions considered for the slab panel.',
                 use_column_width=True)
        st.markdown('''
        * Curve 9: simply supported slab (BC1), allowing thermal expansion of structural members, 
        **with unprotected central beam** and rebar area of **230 mm<sup>2</sup>/m**. 
        * Curve 10: restricts thermal expansions in both x and y directions (BC3) , **with unprotected central beam** and rebar area of **230 mm<sup>2</sup>/m**. 
        ''', unsafe_allow_html=True)

        st.image(Fragility_curve_C3910,
                 caption='Figure 8: Illustration of different aspect ratios considered for the slab panel.',
                 use_column_width=True)


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
