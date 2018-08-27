import plotly
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from ipywidgets import widgets
from IPython.display import display, clear_output, Image


dark_theme = {
    "barmode": "overlay",
    "paper_bgcolor":'rgba(0,0,0,0)',
    "plot_bgcolor":'rgba(0,0,0,0)',
     "xaxis": {"color":"white",
              "tickcolor": "white"},
     "yaxis": {"color":"white",
              "tickcolor": "white"},
     "legend": {"font": {"color":"white"}}
}

spike_3d_colors = dict(
    scene= dict(
        xaxis='blue',
        yaxis='green',
        zaxis='blue',
    )
)

three_d_margins = dict(
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=100
))

three_d_scene = dict(
    color="white",
    backgroundcolor="rgb(50,50,50)",
    showbackground= True,
    gridcolor="rgb(.5,.5,.5)",
    zerolinecolor= "rgb(.75,.75,.75)",
)

scatter3d_layout_dark = go.Layout(
    **three_d_margins,
    autosize=False,
    scene={
        "xaxis": dict(spikecolor="blue",**three_d_scene),
        "yaxis": dict(spikecolor="green",**three_d_scene),
        "zaxis": dict(spikecolor="red",**three_d_scene)
    }
    ,**dark_theme
)