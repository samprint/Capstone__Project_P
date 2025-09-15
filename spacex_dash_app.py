# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = (
    html.Div(
        children=[
            html.H1(
            'SpaceX Launch Records Dashboard',
                style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
            ),

            # TASK 1: Add a dropdown list to enable Launch Site selection
            # The default select value is for ALL sites
            html.Div([
                html.Label("Select a Launch Site:"),
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
            ]),

            html.Br(),

            # TASK 2: Add a pie chart to show the total successful launches count for all sites
            # If a specific launch site was selected, show the Success vs. Failed counts for the site
            html.Div(
                dcc.Graph(id='success-pie-chart')
            ),

            html.Br(),

            html.P("Payload range (Kg):"),

            # TASK 3: Add a slider to select payload range

            html.Div(
                dcc.RangeSlider(
                    id='payload-slider',
                    min=0,
                    max=10000,
                    step=1000,
                    marks={i: str(i) for i in range(0, 10001, 500)},
                    value=[min_payload, max_payload]
                )
            ),


            # TASK 4: Add a scatter chart to show the correlation between payload and launch success
            html.Div(
                dcc.Graph(id='success-payload-scatter-chart'),
                # style={'height': '80vh'}
            ),
        ]
    )
)

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # filtered_df = spacex_df
    if entered_site == 'ALL':
        exp_data = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = (
            px.pie(
                exp_data,
                values='class',
                names='Launch Site',
                title='Percentage of successful launches of each site out of {} sites launches'.format(entered_site),
            )
        # .update_traces(textinfo='value')
        )
        return fig
    else:
        exp_data1 = spacex_df[spacex_df['Launch Site'] == entered_site]['class'].to_frame().reset_index(drop=True)
        exp_data1['count'] = 1
        exp_data1 = exp_data1.groupby('class')['count'].sum().reset_index()

        fig = px.pie(
            exp_data1,
            values='count',
            names='class',
            title='Percentage of successful launches for {} site'.format(entered_site),
            color='class',
            color_discrete_map =
            {
                1: 'green',
                0: 'red'
            }
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
        [
            Input(component_id='site-dropdown', component_property='value'),
            Input(component_id='payload-slider', component_property='value'),
        ]
)

def get_scatter_chart(entered_site, payload_range):
    min_load, max_load = payload_range

    exp2 = spacex_df[spacex_df['Launch Site'] == entered_site]
    exp2 = exp2[exp2['Payload Mass (kg)'].between(min_load, max_load)]

    if entered_site == 'ALL':
        df = spacex_df[spacex_df['Payload Mass (kg)'].between(min_load, max_load)]
    else:
        df = exp2

    # --- Start of new code to ensure a static legend ---
    # Create a dummy dataframe with all unique booster versions and None for plot values
    all_boosters_df = pd.DataFrame({
        'Booster Version Category': spacex_df['Booster Version Category'].unique(),
        'Payload Mass (kg)': None,
        'class': None
    })
    # Combine the filtered data with the complete list of boosters
    plot_df = pd.concat([df, all_boosters_df])
    # --- End of new code ---

    fig =   px.scatter(
                plot_df,
                x="Payload Mass (kg)",
                y="class",
                color="Booster Version Category",
                # This argument ensures consistent color mapping across filters
                # category_orders={'Booster Version Category': sorted(spacex_df['Booster Version Category'].unique())},
                category_orders={'Booster Version Category': [ 'v1.0', 'v1.1', 'FT', 'B4', 'B5']},
                # Add this line to use a larger color palette with 26 unique colors
                # color_discrete_sequence=px.colors.qualitative.Alphabet,
                range_y=[-0.1, 1.1],
            ).update_layout(
                title_text='Correlation between payload and successfull launch for {} site(s)'.format(entered_site),
                # This legend dictionary is updated to position it at the bottom
                legend=dict(
                    title='Booster Version Category  (from oldest to most recent version)',
                    orientation="h",
                    yanchor="top",      # Anchor the top of the legend
                    y=-0.2,             # Position the legend below the plot
                    xanchor="right",
                    x=1
                )
            )

    return fig

# Run the app
if __name__ == '__main__':
    app.run()
