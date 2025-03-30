import pandas as pd
import plotly.express as px
import dash 
from dash import dcc, html, Dash, callback, Output, Input

# load the dataset containing information on the FIFA World Cup 
df = pd.read_csv("List_of_FIFA_World_Cup_finals_2.csv", encoding='latin1')

# clean up the 'Winner' and 'Runner-up' strings
df['Winners'] = df['Winners'].str.strip().str.replace('\xa0', ' ', regex=False)
df['Runners-up'] = df['Runners-up'].str.strip().str.replace('\xa0', ' ', regex=False)

# change it so West Germany and Germany are the same
df['Winners'] = df['Winners'].replace({'West Germany': 'Germany'})
df['Runners-up'] = df['Runners-up'].replace({'West Germany': 'Germany'})

# count the total number of wins for each country
wins = df['Winners'].value_counts().rename_axis('Country').reset_index(name='Wins')
# count the total number of runner-up appearances for each country
runners_up = df['Runners-up'].value_counts().rename_axis('Country').reset_index(name='RunnerUps')
# merge wins and runner-up appearances into one dataframe
summary_df = pd.merge(wins, runners_up, on='Country', how='outer').fillna(0)
summary_df['RunnerUps'] = summary_df['RunnerUps'].astype(int)

# Create choropleth map
fig = px.choropleth(
    summary_df,
    locations="Country",
    locationmode="country names",
    color="Wins",
    hover_name="Country",
    color_continuous_scale="Viridis",
    title="FIFA World Cup Wins by Country"
)

# initialize Dash app
app = Dash(__name__)
server = app.server

# dropdown options that has all the countries
countries = sorted(summary_df['Country'].tolist())

# make the layout of the dashboard
app.layout = html.Div([
    html.H1("FIFA World Cup Dashboard", style={'textAlign': 'center'}),
    dcc.Graph(
        id='world-cup-map',
        figure=fig
    ),

    # dropdown for the country selection 
    html.Label("Select a Country:"),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country} for country in countries],
        value='Argentina' # set as the default country (first alphabetically)
    ),
    html.Div(id='country-stats', style={'marginTop': 20}), # this outputs the country's stats

    # dropdown for the year selection
    html.Label("Select a World Cup Year:"),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': int(y), 'value': y} for y in sorted(df['Year'].dropna().unique())],
        value=2022 # default year (most recent World Cup)
    ), 
    html.Div(id='year-stats', style={'marginTop': 20}) # this outputs the stats for that year
])

# callback for the country selections
@app.callback(
    Output('country-stats', 'children'),
    Input('country-dropdown', 'value')
)
# function to update the stats based on the country that was selected
def update_country_stats(selected_country):
    row = summary_df[summary_df['Country'] == selected_country].iloc[0]
    return html.Div([
        html.H3(f"Stats for {selected_country}:"),
        html.P(f"🏆 Wins: {int(row['Wins'])}"),
        html.P(f"🥈 Runner-up finishes: {int(row['RunnerUps'])}")
    ])

# callback for the years selections 
@app.callback(
    Output('year-stats', 'children'),
    Input('year-dropdown', 'value')
)
# function to update the stats based on the year that was selected
def update_year_stats(selected_year):
    row=df[df['Year'] == selected_year].iloc[0]
    return html.Div([
        html.H3(f"World Cup {int(selected_year)} Results:"),
        html.P(f"🏆 Winner: {row['Winners']}"),
        html.P(f"🥈 Runner-up: {row['Runners-up']}"),
        html.P(f"🏟️ Venue: {row['Venue']}"),
        html.P(f"📍 Location: {row['Location']}"),
        html.P(f"👥 Attendance: {row['Attendance']}")
    ])

if __name__ == "__main__":
    app.run(debug=True, port=8051)
