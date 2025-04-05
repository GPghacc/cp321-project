# %%
import pandas as pd
import numpy as np
import pandas as pd
import dash
from dash import dcc, html, callback, Output, Input, dash_table
import plotly.express as px
import plotly.graph_objects as go



# %%
tot_gender_df = pd.read_csv('TotalGenderByGeo.csv')                                     #get data for q1,3,4

def parse_int_strings(val):                                                             #change all int valued strings to proper int value for easier processing
    if isinstance(val, str) and val.replace(',', '').isdigit():
        return int(val.replace(',', ''))
    return val

tot_gender_df = tot_gender_df.apply(lambda col: col.map(parse_int_strings) if col.dtype == "object" else col)
geolist = tot_gender_df.columns.tolist()

geolist=geolist[1:]


# %%
#data for q1
#313 Nursing and allied health professionals, 
#40040 Commissioned police officers and related occupations in public protection services, 
#40041 Fire chiefs and senior firefighting officers	

essential_service_df = tot_gender_df[tot_gender_df['occupations(NOC)'].isin(['313 Nursing and allied health professionals', '40040 Commissioned police officers and related occupations in public protection services', '40041 Fire chiefs and senior firefighting officers' ])]
essential_service_df



# %%
#data for q2
#gender comparison on highest lv NOC

by_gender_df = pd.read_csv('MajorOccByGender.csv')
by_gender_df = by_gender_df.apply(lambda col: col.map(parse_int_strings) if col.dtype == "object" else col)
OCCLIST = by_gender_df['Occupations(NOC)'].unique()
occupation_dropdown_options =[]

by_gender_df['Men/Women Ratio'] = (by_gender_df['Men']/by_gender_df['Women']).round(2)                          #add ratio between gender


for occ in OCCLIST:
    occupation_dropdown_options.append({'label': occ, 'value': occ})

by_gender_df

# %%
#q3 manpower available - Computer, Mechanical and Electrical engineers

manpower_df = tot_gender_df[tot_gender_df['occupations(NOC)'].isin(['21301 Mechanical engineers', '21310 Electrical and electronics engineers', '21311 Computer engineers (except software engineers and designers)'])]
new_col = manpower_df.iloc[:, 0]
sum_row = manpower_df.sum(numeric_only=True)  # Sum only numeric columns
sum_row['occupations(NOC)'] = 'Total Manpower'
manpower_df = pd.concat([manpower_df, pd.DataFrame([sum_row])], ignore_index=True)

new_col = new_col.values.tolist()
new_col = new_col + ['Total Manpower']
manpower_df = manpower_df.T
manpower_df = manpower_df[1:]
manpower_df = manpower_df.astype('int')
manpower_df.columns = new_col

manpower_df['Geography'] = manpower_df.index
manpower_df = manpower_df[[manpower_df.columns[-1]] + list(manpower_df.columns[:-1])]
manpower_df 


# %%
#q4 Distribution of Computer System Developers in Administrative units
comp_dev_df = tot_gender_df[tot_gender_df['occupations(NOC)'].str.startswith("2123")]

compocc = list(comp_dev_df['occupations(NOC)'])
compsci_occupation_dropdown_options =[]

for occ in compocc:
    compsci_occupation_dropdown_options.append({'label': occ, 'value': occ})
compsci_occupation_dropdown_options

# %%
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1("CP 321 – Data Visualization Project", style={'textAlign': 'center'}),
    html.H2("Geon Woo Park - 169031088", style={'textAlign': 'center'}),    
    html.Div([
        html.H3("Q1 Essential Human Resource Distribution on Administrative Units"),
        html.H4("Press button for each Essential Services"),
        html.Div(children=[
            html.Button('Nursing', id='nurse', n_clicks=0),
            html.Button('Police', id='police', n_clicks=0),
            html.Button('Fire Fighting', id='firefighter', n_clicks=0)
        ],
        style={
            'display': 'flex',          
            'justify-content': 'center', 
            'gap': '20px',              
            'padding': '20px'           
        }),
        dcc.Graph(
            id='q1 bar-graph'
        )
    ]),
    html.Div([
        html.H3("Q2 Gender Difference in Employment Comparison Between Administrative Units"),
        html.H4("Choose Highest Level Occupation:"),
        dcc.Dropdown(
            id='occ-dropdown',
            options=occupation_dropdown_options,
            value=OCCLIST[0],
            style={'width':'40%'}
            ),
        dcc.Graph(
            id='q2 bar-graph'
        ),
        html.H5(id="avg-ratio")
    ]),
    html.Div([
        html.H3("Q3 Enough Manpower to Setup a Factory for Electronic Vehicles"),
        html.H4("Set Manpower Requirements:"),
        html.Div([
            html.Label("Mechanical engineers:"),
            dcc.Input(id='input-mech', type='number', value=0, min=0, max=58690, step=10, style={'margin': '40px'}),        #max = corresponding population for canada
            html.Label("Electrical and electronics engineers:"),
            dcc.Input(id='input-elec', type='number', value=0, min=0, max=47890, step=10, style={'margin': '40px'}),        #step = 10: lowest number after 0 was 10
            html.Label("Computer engineers:"),
            dcc.Input(id='input-comp', type='number', value=0, min=0, max=26730, step=10, style={'margin': '40px'})
        ]),
        html.Div([
            html.Label("Total Manpower:"),
            dcc.Input(id='input-tot', type='number', value=0, min=0, max=133310, step=10, style={'margin': '40px'})
        ]),
        dash_table.DataTable(
            id='q3-table',
            columns=[{"name": col, "id": col} for col in manpower_df.columns]
        )
    ]),
    html.Div([
        html.H3("Q4 Table"),
        html.H4("Choose Computer, software and Web designers and developers Occupation:"),
        dcc.Dropdown(
            id='comp-occ-dropdown',
            options=compsci_occupation_dropdown_options,
            value=compocc[0],
            style={'width':'40%'}
            ),
        dcc.Graph(
            id='q4 bar-graph'
        )
    ])
])



@app.callback(
    [Output('q1 bar-graph', 'figure')],
    [Input('nurse', 'n_clicks'),
    Input('police', 'n_clicks'),
    Input('firefighter', 'n_clicks')]
)

def update_q1_graph(click_nurse, click_police, click_ff):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        button_id = 'nurse'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
    if button_id == 'nurse':
        fig = go.Figure(data=[go.Bar(name='nurse', x=geolist[1:], y=essential_service_df.iloc[0, 2:])])
    elif button_id == 'police':
        fig = go.Figure(data=[go.Bar(name='police', x=geolist[1:], y=essential_service_df.iloc[1, 2:])])
    elif button_id == 'firefighter':
        fig = go.Figure(data=[go.Bar(name='firefighting', x=geolist[1:], y=essential_service_df.iloc[2, 2:])])

    fig.update_layout(
        title=f"Population Distribution for {button_id} Profession",         
        xaxis_title="Geography",             
        yaxis_title="Population",            
        plot_bgcolor="lightgray",             
        paper_bgcolor="white",              
    )
    
    return [fig]




@app.callback(
    [Output('q2 bar-graph', 'figure'),
    Output('avg-ratio', 'children')],
    [Input('occ-dropdown', 'value')]
)

def update_q2_graph(occ):
    
    graph_data = by_gender_df[by_gender_df['Occupations(NOC)'] == occ]
    
    fig = go.Figure(data=[
        go.Bar(name="Male Population", x=graph_data['Geography'], y=graph_data['Men']),
        go.Bar(name="Female Population", x=graph_data['Geography'], y=graph_data['Women']),
        ])
    
    fig.update_layout(
        barmode='group',  
        title=f"Gender Distribution for Occupation: {occ}",
        xaxis_title="Geography",
        yaxis_title="Population",
        plot_bgcolor="lightgray",
        paper_bgcolor="white",
    )
    
    mean_ratio = by_gender_df['Men/Women Ratio'].mean().round(2)
    str = f"The Average M:F ratio of {occ} is {mean_ratio} : 1"
    return [fig, str]

@app.callback([
    Output('q3-table', 'data')],
    [Input('input-mech', 'value'),
    Input('input-elec', 'value'),
    Input('input-comp', 'value'),
    Input('input-tot', 'value'),])

#21301 Mechanical engineers	21310 Electrical and electronics engineers	21311 Computer engineers (except software engineers and designers)	Total Manpower
def update_q3_table(mech, elec, comp, tot):
    data = manpower_df
    cols = manpower_df.columns
    cols = cols[1:]
    for col, input in zip(cols, [mech, elec, comp, tot]):
        data = data[data[col] >= input]
    
    return [data.to_dict('records')]


@app.callback(
    [Output('q4 bar-graph', 'figure')],
    [Input('comp-occ-dropdown', 'value')]
)

def update_q4_graph(occ):
    
    graph_data = comp_dev_df[comp_dev_df['occupations(NOC)'] == occ]
    
    fig = go.Figure(data=[
        go.Bar(name="Female Population", x=geolist[1:], y=graph_data.iloc[0, 2:]),
        ])
    
    fig.update_layout(
        title=f"Geographical Distribution for Occupation: {occ}",
        xaxis_title="Geography",
        yaxis_title="Population",
        plot_bgcolor="lightgray",
        paper_bgcolor="white",
    )
    
    return [fig]

# %%
if __name__ == '__main__':
    app.run(debug=True)



