import dash 
import dash_compose.core as dc 
from dataclasses import dataclass 
import numpy as np 


@dataclass
class ImagePlaceholder:
    width: int 
    height: int 

example_config = {
    'graph': {
        'id': 'interactive-image',
    },
    'background_images': {
        'src_encoding': 'png',
        'margins': {'l': 40, 'b': 40, 't': 26, 'r': 10},
        'images': [ImagePlaceholder(1200,800),ImagePlaceholder(666,800)]
    },
    'scatter_traces': {
        'xs': [np.random.randn(10)*1200 for i in range(2)],
        'ys': [np.random.randn(10)*800 for i in range(2)],
    }
}

example_config2 = {
    'graph': {
        'id': 'interactive-image2',
    },
    'background_images': {
        'src_encoding': 'png',
        'margins': {'l': 40, 'b': 40, 't': 26, 'r': 10},
        'images': [ImagePlaceholder(300,800)]
    },
}

app = dash.Dash()

app.layout = dc.row([
    dc.col(dc.upload_div(True),'md-2'),
    dc.col(example_config,'md-4'),
    dc.col(example_config2,'md-3'),
])

external_css = ["https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css"] 

for css in external_css:
    app.css.append_css({"external_url": css})


if __name__ == '__main__':
    app.run_server(debug=True)