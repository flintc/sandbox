import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
#import dash_table_experiments as dt                                                                                                                                                           

import datetime
import json
import pandas as pd
import plotly
import io
import numpy as np
from base64 import decodestring



app = dash.Dash()

app.scripts.config.serve_locally = True

app.layout = html.Div([
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
        multiple=True
    ),
    html.Div(id='output-image-upload'),
])


def parse_contents(contents):
    return html.Div([

        # HTML images accept base64 encoded strings in the same format                                                                                                                         
        # that is supplied by the upload                                                                                                                                                       
        html.Img(src=contents),
        html.Hr(),
        html.Div('Raw Content'),
        html.Pre(contents[:100] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])
@app.callback(Output('output-image-upload', 'children'),
              [Input('upload-image', 'contents')])
def update_output(images):
    if not images:
        return

    for i, image_str in enumerate(images):
        image = image_str.split(',')[1]
        data = decodestring(image.encode('ascii'))
        with open(f"image_{i+1}.jpg", "wb") as f:
            f.write(data)
    print('here!!!')
    children = [parse_contents(i) for i in images]
    return children


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug=True)