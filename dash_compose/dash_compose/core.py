import inspect
import dash_core_components as dcc   
import dash_html_components as html 
from dash_compose.util.objects import merge_deep, pick, prop, merge_deep_concat
from dash_compose.util.core import spread
from dataclasses import dataclass
from typing import Mapping 

def scatter_graph_base(n_traces):
    return dict(
        figure={
            'data': [{
                'type': 'scatter',
                'mode': 'markers',
            } for i in range(n_traces)]
        }
    )

def scatter_graph_updateable_dependencies(xs,ys): 
    out = dict(
        figure={
            'data': [{
                'x': x,
                'y': y,
            } for x,y in zip(xs,ys)]
        },
    )
    return out



def image_graph_base(n_images):
    return dict(
        figure={
            'data': [],
            'layout': {
                'xaxis': {
                    'scaleanchor': 'y',
                    'scaleratio': 1
                },
                'images': [{
                    'xref': 'x',
                    'yref': 'y',
                    'x': 0,
                    'y': 0,
                    'yanchor': 'bottom',
                    'sizing': 'stretch',
                    'layer': 'below',
                } for i in range(n_images) ],
            }
        },
        config={
            'modeBarButtonsToRemove': [
                'sendDataToCloud',
                'autoScale2d',
                'toggleSpikelines',
                'hoverClosestCartesian',
                'hoverCompareCartesian',
                'zoom2d'
            ]
        },
)
def image_graph_one_shot_dependencies(n_images, src_encoding, margins=dict(l=40, b=40, t=26, r=10) ): 
    out = dict(
        figure={
            'data': [],
            'layout': {
                'margin': margins,
                'images': [{
                    'source': f'data:image/{src_encoding};base64, ',
                } for i in range(n_images) ],
            }
        },
    )
    return out

def image_graph_updateable_dependencies(images): 
    out = dict(
        figure={
            'layout': {
                'xaxis': {
                    'range': (0, images[0].width),
                },
                'yaxis': {
                    'range': (0, images[0].height)
                },
                'images': [{
                    'sizex': image.width,
                    'sizey': image.height,
                } for image in images ],
            }
        },
    )
    return out


def background_images(images,src_encoding,margins):
    return merge_deep(
        image_graph_base(len(images)),
        image_graph_one_shot_dependencies(len(images), src_encoding, margins),
        image_graph_updateable_dependencies( images ),
    )


def upload_div(multiple):
    return html.Div([
        dcc.Upload(
            id='upload-image',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded                                                                                                                                                  
            multiple=multiple,
        ),
        html.Div(id='output-image-upload'),
    ])

def scatter_traces(xs,ys):
    return merge_deep(
        scatter_graph_base(len(xs)),
        scatter_graph_updateable_dependencies(xs,ys),
    )


def props_to_pick(factory_func):
    spec = inspect.getfullargspec(factory_func)
    return spec.args

def graph(**config):
    return config


def factory_eval(factory,config):
    #print('factory_eval',config)
    return eval(factory)(**config)



def make_div(class_name,config):
    out = html.Div([dcc.Graph(**config)],className=class_name) if isinstance(config,Mapping) else \
        html.Div(children=config, className=class_name)
    return out

def make_graph(global_config):
    # if 'row' in global_config.keys():
    #     return [ html.Div(children=[ resolve() for resolve in value ], className='row') for value in global_config.values() ]
    # else:
        return dcc.Graph(**merge_deep_concat( *[factory_eval(factory,config) for factory,config in global_config.items()] ))

def col(config,spec='md'):
    return lambda: html.Div(children=[make_graph(config)],className='col-'+spec)

def row(items):
    return html.Div(children=[ resolve() for resolve in items ], className='row')





