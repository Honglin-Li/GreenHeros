import streamlit as st
#import pandas as pd
#import pandas_profiling
#from pydantic_settings import BaseSettings
#from streamlit_pandas_profiling import st_profile_report
from power_data_handler import read_one_csv, read_csv_in_list, get_overview_power_data, get_selected_overview, WATT_METRICS, get_compare_data
import altair as alt
#import nivo_chart as nc

# settings
st.set_page_config(layout="wide")

# prepare data source
#@st.cache_data # TODO: de-comment
def get_data_source():
     df_list = read_csv_in_list()
     df_overview = get_overview_power_data(df_list)

     return df_list, df_overview


ds_list, ds_overview = get_data_source()


# ---------------------------------------Main Part---------------------------------------
st.title('ING :orange[Power Consumption] Dashboard')


# ---------------------------------------Metrics Card---------------------------------------

with st.container():
     st.subheader('Metrics (Recent Minute)')

     current_data = ds_overview.iloc[-1]

     last_data = ds_overview.iloc[-2]
     delta_data = current_data - last_data

     metric_columns = st.columns(ds_overview.shape[1])

     for column, (index, value), (i_delta, v_delta) in zip(metric_columns, current_data.items(), delta_data.items()):
          with column:
               with st.container(border=True):
                    st.metric(label=index, value=int(value), delta=int(v_delta))

     st.write('Note: The indicator change amount is relative to the indicator data 1 minute ago')


# ---------------------------------------Card: Options---------------------------------------
# layout
#row1 = st.columns(spec=[0.6, 0.4])

#with row1[0]:

          # INPUT 2: chart series
          #st.write('**:orange[Option2]:**   Select the **series** to observe in the chart')
          #check_columns = st.columns(4, gap='small')

          # update the list if changing series
          #series_names = ['CpuWatts', 'DimmWatts', 'Minimum', 'Peak']

          #series_checkboxes = {}

          # create checkboxes dynamically
          #for check_column, series_name in zip(check_columns, series_names):
               #with check_column:
                    #series_checkboxes[series_name] = st.checkbox(series_name, value=True)


          # narrow down the data by slider


# ---------------------------------------Card: Show Data---------------------------------------
#with row1[1]:
     #with st.container(border=True):
          #st.subheader('Power Data Overview')

          # show data
          #st.write(ds_overview_selected)


# ---------------------------------------Card: Overview---------------------------------------
st.markdown("## Board 1")
with st.container(border=True):
     st.header(':clipboard: :orange[Board]: Server Integration Level (by Minute)')

     # accept User Input
     # INPUT 1: time selection
     time_period = st.slider(
          'Drag the slider to adjust the time period (**x-axis, minutes**) in the chart',
          5,
          ds_overview.shape[0],
          int(ds_overview.shape[0] / 3 * 2)
     )

     st.write("---")

     ds_overview_selected = get_selected_overview(ds_overview, time_period)

     # main Power overview chart
     st.subheader(':chart_with_upwards_trend: Chart: Server Power Consumption (KWatts/Minute)')
     #st.line_chart(ds_overview_selected[['Average', 'Minimum', 'Peak']])

     # Reshape the data for Altair
     data_melted_overview = ds_overview_selected[['Average', 'Minimum', 'Peak']].reset_index().melt(
          id_vars='Time', var_name='Series', value_name='KWatts')

     # Create Altair chart
     chart_overview = alt.Chart(data_melted_overview).mark_line().encode(
          x='Time',
          y=alt.Y('KWatts', scale=alt.Scale(domain=[135, 168])),
          color='Series'
     ).interactive()

     st.altair_chart(chart_overview, use_container_width=True)

     st.subheader(':chart_with_upwards_trend: Chart: Cpu & Memory Power Consumption (KWatts/Minute)')
     with st.expander('Click to check the Chart'):
          st.line_chart(ds_overview_selected[['CpuWatts', 'DimmWatts']])

     st.subheader(':chart_with_upwards_trend: Chart: Cpu Utilization (Percent)')
     with st.expander('Click to check the Chart'):
          st.line_chart(ds_overview_selected[['CpuUtil']])

     # data
     with st.expander('Click to check **:orange[Overview Data]**'):
          st.write(ds_overview_selected)

     #st.write(get_nivo_data(df_selected))
     #bump_chart = get_bump_chart(df_selected, 'Bump Chart: Power Consumption Overview')

     #nc.nivo_chart(
          #data=bump_chart['data'],
          #layout=bump_chart['layout'],
          #key='bump_chart'
     #)

#-----------------------------------Card: Compare---------
st.markdown("## Board 2")
with st.container(border=True):
     st.header(':clipboard: :orange[Improvement Results]')

     row_input = st.columns(3)
     with row_input[0]:
          time_start = st.text_input('Start time', value='19:45')
     with row_input[1]:
          time_end = st.text_input('End time', value='20:30')
     with row_input[2]:
          improve_time = st.text_input('Improvement time', value='20:08')

     st.subheader(':chart_with_upwards_trend: Line Chart')

     data, y_min, y_max, co2, trees = get_compare_data(
          ds_overview,
          time_start,
          time_end,
          improve_time
     )

     # Reshape the data for Altair
     data_melted = data[['Average', 'Minimum']].reset_index().melt(
          id_vars='Time', var_name='Series', value_name='KWatts')

     # Create Altair chart
     chart = alt.Chart(data_melted).mark_line().encode(
          x='Time',
          y=alt.Y('KWatts', scale=alt.Scale(domain=[y_min, y_max])),
          color='Series'
     ).interactive()

     st.altair_chart(chart, use_container_width=True)

     # show CO2 Trees
     st.subheader(':green[Sustainability Output in 100 days]')

     row = st.columns(spec=[0.2, 0.3, 0.2, 0.3])

     with st.container(border=True):
          with row[0]:
               st.image('images/co2.png', use_column_width=True)
          with row[1]:
               st.header(':orange[CO2 (kg)]')
               st.subheader(co2)

     with st.container(border=True):
          with row[2]:
               st.image('images/trees.jpeg', use_column_width=True)
          with row[3]:
               st.header(':orange[Trees]')
               st.subheader(trees)

     celebrate_btn = st.button(':tada::tada::tada: Good Job! Celebrate Time! :tada::tada::tada: ', type='primary')

     if celebrate_btn:
          st.balloons()


# ---------------------------------------Card: Server Individual Level---------------------------------------
st.markdown("## Board 3")
with st.container(border=True):
     st.header(':clipboard: :orange[Overview]: Server Individual Level')

     server_number = 8

     tab_name_list = ['Server' + str(i) for i in range(server_number)]

     tab_list = st.tabs(tab_name_list)

     for tab, ds in zip(tab_list, ds_list):
          with tab:
               #st.subheader(':chart_with_upwards_trend: Chart: Cpu Utilization (Percent)')
               #st.line_chart(ds[['CpuUtil']])

               st.subheader(':chart_with_upwards_trend: Chart: Server Power Consumption')
               st.line_chart(ds.set_index('Time')[WATT_METRICS])

               #st.subheader(':chart_with_upwards_trend: Chart: Cpu & Memory Power Consumption')
               #st.line_chart(ds[['CpuWatts', 'DimmWatts']])




# df profile
#pr = df_selected.profile_report()
#st_profile_report(pr)



# ---------------------------------------sidebar---------------------------------------
with st.sidebar:
     st.image('images/ING_Primary_Logo_RGB.png')

     st.markdown("### Quick Navigation")
     st.markdown("- [Server Overview (Integration Level)](#board-1)")
     st.markdown("- [Sustainability Improvement Results](#board-2)")
     st.markdown("- [Server Overview (Individual Level)](#board-3)")

     st.write("---")

     st.header('Metrics Description')
     st.markdown('''
          **:orange[CpuUtil]** CPU utilization in percent.

          **:orange[CpuWatts]** The power consumed by the system CPUs in Watts.

          **:orange[DimmWatts]** The power consumed by the system memory DIMMs in Watts.

          **:orange[Minimum]** Minimum power in Watts over the sample time(10 seconds).

          **:orange[Peak]** Peak power in Watts over the sample time.
          
          **:orange[Average]** Average power in Watts over the sample time.
     ''')


