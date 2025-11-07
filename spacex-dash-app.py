# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Ensure 'class' column exists (1 for success, 0 for failure)
# if 'class' not in spacex_df.columns:
#     spacex_df['class'] = spacex_df['Outcome'].apply(lambda x: 1 if x.startswith('True') else 0)

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
# Note: Retaining all unique LaunchSite names for the dropdown
launch_sites = spacex_df['Launch Site'].unique().tolist() 

# Prepare dropdown options, explicitly including all site names from the unique list
# dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
# dropdown_options.extend([{'label': site, 'value': site} for site in launch_sites])


# Create a dash application
app = dash.Dash(__name__)

# Create the consolidated app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Dropdown

    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
            ],
            value='ALL',
            placeholder="Select a Launch Site here",
            searchable=True
),

    html.Br(),

    # TASK 2: Pie Chart
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):", style={'padding': '0px 20px'}),

    # TASK 3: Range Slider
    html.Div(dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
        ),
),
    # TASK 4: Scatter Chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# --------------------------------------------------------------------------------
# CALLBACK FUNCTIONS
# --------------------------------------------------------------------------------

# TASK 2: Pie Chart Callback
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Correctly aggregate the full DataFrame to get the sum of 'class' (Total Successes) per site.
        success_counts_by_site = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        success_counts_by_site.columns = ['Launch Site', 'Success_Count']

        fig = px.pie(
            success_counts_by_site,
            values='Success_Count',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # Specific Site: Show Success (1) vs. Failed (0) counts
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_fail_counts = filtered_df['class'].value_counts().reset_index()
        success_fail_counts.columns = ['Class', 'Count']
        success_fail_counts['Class'] = success_fail_counts['Class'].map({1: 'Success', 0: 'Failed'})

        fig = px.pie(
            success_fail_counts,
            names='Class',
            values='Count',
            title=f'Success vs. Failed Launches for site {selected_site}'
        )
        return fig

# TASK 4: Scatter Chart Callback
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range

    # 1. Filter dataframe based on payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]

    # 2. Further filter by launch site if a specific site is selected
    if selected_site != 'ALL':
        # Note: 'LaunchSite' is used here to match the DataFrame column
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Booster Version'],
        title=f'Payload vs. Launch Outcome for {selected_site}',
        labels={'class': 'Launch Outcome (0 = Failure, 1 = Success)'}
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run()