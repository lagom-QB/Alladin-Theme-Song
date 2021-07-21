from dash.dependencies import Input,Output

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

# %%
song = pd.read_csv('Musicals/WNW/input/song.csv')

song.track_y = song.track_y.fillna(0)
song.length  = song.length.fillna(0)
song.channel_y=song.channel_y.fillna(0)
song.note = song.note.fillna(0)
song.notename= song.notename.fillna('OO')
song.velocity=song.velocity.fillna(0)

print(song.isna().mean().mean())

remove = ['System','Time Signature']
song = song[~song.event.isin(remove)]
list(pio.templates)


# %%
# --> Static Image
instruments = song.parameterMetaSystem.unique()
graph_without_input = dcc.Graph(id='note_length')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.PULSE])
app.title = 'Musical Viz'

# ---> Callbacks and Functions
@app.callback(Output(component_id='notes_produced', component_property='children'),
              Output(component_id='note_length_graph', component_property='figure'),
              Output(component_id='note_velocity', component_property='figure'),
              
              Input(component_id='instruments', component_property='value'),
             )

def select_instrument(instruments):
    notes_by_instrument = notes_produced(instruments)
    
    return (html.Ul([html.Li(note) for note in notes_by_instrument]),
            note_length_graph(instruments), 
            note_velocity_graph(instruments)
           )

def note_length_graph(instrument): 
    notes_by_instrument_and_lengths = pd.DataFrame(data=song[song.parameterMetaSystem == instrument])
    note_length = notes_by_instrument_and_lengths[['notename','length','event']]

    fig = px.scatter(note_length, 
                 x='notename', 
                 y='length',
                 symbol='notename',
                 size='length',
                 color='event',
                 height=600)

    fig.layout.title = 'Notes and Lengths for %s'%instrument
    fig.layout.yaxis.title = 'Notes'
    fig.layout.xaxis.title = 'Lengths'
    fig.layout.template='ggplot2'
    
    return fig

def note_velocity_graph(instrument): 
    notes_by_instrument_and_lengths = pd.DataFrame(data=song[song.parameterMetaSystem == instrument])
    note_length = notes_by_instrument_and_lengths[['notename','velocity', 'event']].reset_index()

    fig = px.scatter(note_length, 
                     x='notename', 
                     y='velocity',
                     symbol='notename', 
                     size='velocity',
                     color='event',
                     animation_group='notename',
                     height=600
                    )

    fig.layout.template='ggplot2'
    fig.layout.title = 'Notes and Velocity for %s'%instrument
    fig.layout.xaxis.title = 'Notes'
    fig.layout.yaxis.title = 'Velocity'
    
    return fig
    

def notes_produced(instrument):
    notes = song[song.parameterMetaSystem == instrument].notename.unique()
    notes = sorted(notes)
    
    return notes

def notes_graph(): #◀️
    notes_counts = pd.DataFrame(data=song[['parameterMetaSystem','time','event']].value_counts(),
                                columns=['counts']).sort_values(by='time').reset_index()

    fig = px.scatter( notes_counts,
                      x = 'counts',
                      y = 'parameterMetaSystem',
                      symbol = 'event',
                      color= 'event',
                      size = 'counts',
                      title = 'Number of Occurences of Notes Per Instrument',
                      labels = {'parameterMetaSystem':'Instruments'},
                      height=1200,
                      #animation_frame='time',
                      animation_group='event'
                    )
    
    fig.layout.template='ggplot2'
    #fig.update_yaxes(tickmode='auto',nticks=23)
    
    #fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 2
    #fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 2
    #display(notes_counts[['parameterMetaSystem','counts','event']])
    
    return fig
    
    
app.layout = html.Div(
                        [
                            dbc.Row([html.H1('A Whole New World ~ Alladin Analysis', style={'text-align':'center'}),], 
                                    align='center',
                                    justify='center'),
                            
                            html.Div([
                                # ---> Instuments
                                html.Br(),
                                html.Div([
                                   html.H3('Instruments'),
                                   html.Hr(),
                                   dcc.RadioItems(
                                      id='instruments', #✅
                                      options=[{'label':instr, 'value':instr} for instr in list(sorted(instruments))],
                                      labelStyle={'display':'block'},
                                      value='HARP',
                                      style={'fontSize':'20px','border-radius':'0.25em', 
                                             'background-color':'grey',
                                             'min-width':'12em !important', 
                                             'max-width':'12em !important',
                                             'padding':'0.5em'}
                                                 ),
                                         ],style={'display':'table-cell','padding':'1em','margin-right':'2em'}),
                                             
                                 # ---> Notes
                                 html.Div([
                                    html.H3('Notes', style={'text-align':'center'}),
                                    html.Hr(),
                                    html.Div(id='notes_produced', #✅
                                             style={'fontSize':'20px','border-radius':'1em','min-width':'30em',
                                                    #'background-color':'violet',
                                                    'padding':'0.5em','max-width':'30em',
                                                    '-webkit-column-count':'4','-moz-column-count':'4','column-count':'4',
                                                    '-webkit-column-gap':'10px','-moz-column-gap':'10px','column-gap':'10px',
                                                    '-webkit-column-rule':'1px single grey','-moz-column-rule':'1px single grey','column-rule':'1px single grey'
                                                    }),
                                     html.Br(),
                                                 
                                            ], style={'display':'table-cell'}),
                                             
                                  # ---> Graphs
                                  html.Div([
                                     html.Br(), 
                                     # ---> Length of Notes
                                     dcc.Graph(
                                         figure=notes_graph(),
                                         id='note_length', #✅ 
                                            ), 
                                     html.Br(),
                                           ], style={'display':'table-cell','margin-top':'-3em'}),#, 'padding':'1em'}),
                                  html.Div([
                                     html.Br(),
                                     # ---> Select Notes Instrument and Note Name 
                                     dcc.Graph(id='note_length_graph', loading_state={'is_loading':True},config={'showAxisDragHandles':True}), #✅
                                     html.Br(),
                                     # ---> Velocity of Notes
                                     dcc.Graph(id='note_velocity') #✅
                                      
                                            ], style={'display':'table-cell', 'padding':'1em'})
                                             
                                          ], style={'display':'table','padding-left':'-1em',
                                                    #'background-color':'yellow', 
                                                    'border-radius':'1em'}
                                )
                                                 
                        ],style={'display':'table','padding':'2em',
                                   #'background-color':'black',
                                   'border-radius':'1em','min-width':'40em','align':'center'
                                }
                     )


if __name__ == '__main__':
    app.run_server(port=1999)
# %%



