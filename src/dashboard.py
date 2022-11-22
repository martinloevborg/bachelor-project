#imports of modules
import plotly.express as px
from dash import Dash, dash_table, html, dcc, Input, Output, State
import pandas as pd
import io
import base64
import dash

#Extra graph buttons
buttons = ["drawopenpath", "drawclosedpath", "drawline", "drawcircle", "drawrect", "eraseshape"]

#Reading the datafile and the 2 images
df = pd.read_csv("Bachelor\src\coordinatesData.csv")
png = 'Bachelor\src\Map.png'
png_base64 = base64.b64encode(open(png, 'rb').read()).decode('ascii')
png2 = 'Bachelor\src\Heatmap2.png'
png_base642 = base64.b64encode(open(png2, 'rb').read()).decode('ascii')

#The visualization that are using images
fig3 = px.density_contour(df, x='x', y='y')
fig3.update_layout(
                images= [dict(
                    source='data:image/png;base64,{}'.format(png_base642),
                    xref="paper", yref="paper",
                    x=0, y=0,  #position from bottom left corner
                    sizex=1, sizey=1,
                    xanchor="left", yanchor="bottom",
                    sizing="stretch",
                    opacity=1,
                    ),])
fig2 = px.density_contour(df, x='x', y='y', template="plotly_white", color='id')
fig2.update_layout(
                images= [dict(
                    source='data:image/png;base64,{}'.format(png_base64),
                    xref="paper", yref="paper",
                    x=0, y=0,  #position from bottom left corner
                    sizex=1, sizey=1,
                    xanchor="left", yanchor="bottom",
                    sizing="stretch",
                    opacity=0.3,
                    layer="below"),])

#Color variable
colorscales = px.colors.named_colorscales()  

#stylesheet variable
stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#Instantiate the file
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=stylesheet) 

#Html elements
app.layout = html.Div([
    html.H1("Dashboard for person coordinates", style={'textAlign': 'center'}),
    dcc.Graph(id="sliderGraph"),
    html.Div(id='outputText'),
    dcc.Slider(
        df['timestamp'].min(),
        df['timestamp'].max(),
        step=None,
        value=df['timestamp'].min(),
        marks={str(time): str(time) for time in df['timestamp'].unique()},
        id='time-slider'
    ),
    html.Div([
            html.Div([dcc.Graph(figure=fig2)], className="six columns"),
            html.Div([dcc.Graph(figure=fig3, config={"modeBarButtonsToAdd": buttons})], className="six columns"),
            ], className="row"),
    html.Div([
            html.Div([
                dcc.Dropdown(
                    id='colorDP', 
                    value='viridis', 
                    options=colorscales,
                ),
                dcc.Graph(id="colorGraph"),], className="six columns"),
            html.Div([
                dcc.Dropdown(
                    id='multiDP', 
                    value=['1','9'], 
                    multi=True, 
                    options=[{'label': x, 'value': x} for x in df.id.unique()]
                ),
                dcc.Graph(id="multiGraph", figure={}),], className="six columns"),
            ], className="row"),
    html.Hr(), #a horizontal line
    dcc.Upload(
        id='data_upload',
        children=html.Div([html.Button('Upload file'), 'or Drag and Drop']), 
        style={'textAlign': 'center'},
        #Uploading multiple files is allowed
        multiple=True
    ),
    html.Div(id='output_table'),
    html.Div(id='output'),
])

#Method for reading the uploaded file and return the options and datatable for that uploaded file
def parse(contents, filename):
    type, string_content = contents.split(',')

    decoder = base64.b64decode(string_content)
    try:
        #For uploading a CSV file
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoder.decode('utf-8')))
        #excel reading
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoder))
        #txt and tsv reading
        elif 'txt' or 'tsv' in filename:
            df = pd.read_csv(io.StringIO(decoder.decode('utf-8')))
    except Exception as error:
        print(error)
        return html.Div(['Something went wrong'])

    return html.Div([
        html.H1(filename),

        html.Div([
                html.Div([
                    html.P("Select graph:"),
                    dcc.RadioItems(
                        id="graph_choice",
                        options=[{'label': 'Recommended', 'value': 'recommended'},
                                {'label': 'Simple', 'value': 'simple'}], 
                        value='recommended'
                    ), 
                    html.Br(),
                    html.Button(id='make_graph', children="Make Graph"),
                ], className="six columns"),
                html.Div([
                    html.P("Pick x-axis:"),
                    dcc.Dropdown(id='x_axis', options=[{'label':x, 'value':x} for x in df.columns], value='x'),
                    html.Br(),
                    html.P("Pick y-axis:"),
                    dcc.Dropdown(id='y_axis', options=[{'label':x, 'value':x} for x in df.columns], value='y'),
                ], className="six columns"),
            ], className="row"),

        html.P("Table of the uploaded data:"),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=10
        ),
        dcc.Store(id='store_id', data=df.to_dict('records')),
    ])

#app.callback() is for output and input and state
@app.callback(Output('output_table', 'children'), Input('data_upload', 'contents'), State('data_upload', 'filename'))
#Method for making the datatable of the uploaded file
def update(contentsList, filenameList):  
    if contentsList is not None:
        children = [parse(c, n) for c, n in zip(contentsList, filenameList)] 
        return children

@app.callback(Output('output', 'children'), Input('make_graph', 'n_clicks'), State('graph_choice', 'value'),
            State('store_id', 'data'), State('x_axis', 'value'), State('y_axis', 'value')) 
#Method for making and returning the graphs that have been choosen
def graph_maker(n, chosen_graph, data, x_val, y_val): 
    if n is None:
        return dash.no_update
    elif chosen_graph == 'recommended':
        fig6 = px.scatter(data, x=x_val, y=y_val, size='id', marginal_x="box", marginal_y="box")
        fig7 = px.density_heatmap(data, x=x_val, y=y_val, marginal_x="violin", marginal_y="violin", text_auto=True)
        fig8 = px.scatter(data, x=x_val, y=y_val, color='id', animation_frame='timestamp')
        return [html.Div([
                html.Div([dcc.Graph(figure=fig6)], className="six columns"),
                html.Div([dcc.Graph(figure=fig7)], className="six columns"),
            ], className="row"),
            dcc.Graph(figure=fig8),
        ]
    elif chosen_graph == 'simple':
        fig9 = px.bar(data, x=x_val, y=y_val, color='id') 
        fig10 = px.histogram(df, x=x_val, y=y_val)
        return dcc.Graph(figure=fig9), dcc.Graph(figure=fig10)

@app.callback(Output('sliderGraph', 'figure'),Input('time-slider', 'value'))
#Method for making the graph with a time slider
def time_graph(time_selection):
    specific_df = df[df.timestamp==time_selection]
    fig1 = px.scatter(specific_df, x='x', y='y', color='id')
    return fig1

@app.callback(Output('multiGraph', 'figure'), Input('multiDP', 'value'))
#Method for making the graph controlled by the multi dropdown
def update_graph(id_chosen):
    dff = df[df.id.isin(id_chosen)]
    fig5 = px.line(data_frame=dff, x='x', y='y', color='id')
    fig5.update_traces(mode='lines+markers')
    return fig5

@app.callback(Output('colorGraph', 'figure'),Input('colorDP', 'value'))
#Method for making the graph which colors changed based on a dropdown
def color_graph(color):
    fig4 = px.scatter(df, x='x', y='y', color='id', color_continuous_scale=color)
    return fig4

@app.callback(Output('outputText', 'children'),Input('time-slider', 'value'))
#Method for changing the text based on the time slider
def dynamic_text(slider_input):
    return f'Timestamp: {slider_input}'

#For running the program
if __name__ == '__main__':
    app.run_server(debug=True) 