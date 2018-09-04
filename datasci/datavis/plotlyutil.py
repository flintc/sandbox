
from types import SimpleNamespace
from ..binder import keyed,assign,assign_multiple,omit

Layouts = SimpleNamespace()
GraphObjects = SimpleNamespace()
Layouts.Jupyter = SimpleNamespace()

Layouts.Jupyter.THEME3D = dict(
    barmode = 'overlay',
    paper_bgcolor = "rgba(50,50,50,0)",
    plot_bgcolor = "rgba(50,50,50,0)",
    **assign_multiple('xaxis','yaxis','zaxis')(dict(
        color="rgb(.5,.5,.5)",
        tickcolor="rgb(.5,.5,.5)",
        gridcolor="rgb(.5,.5,.5)",
    ))
)

Layouts.Jupyter.THEME2D = omit('zaxis')(Layouts.Jupyter.THEME3D)
Layouts.make_xlabel = lambda x: dict(xaxis=dict(title=x))
Layouts.make_ylabel = lambda x: dict(yaxis=dict(title=x))
Layouts.make_zlabel = lambda x: dict(zaxis=dict(title=x))

GraphObjects.MarkerMode = SimpleNamespace()
GraphObjects.MarkerMode.VIRIDIS = dict(
    mode='markers',
    marker=dict(
        colorscale='Viridis',
        showscale=True,
        opacity=0.75,
    ),
)

GraphObjects.MarkerMode.SIZE2D = dict(
    marker = dict(
        size=25,
    )    
)

GraphObjects.MarkerMode.SIZE3D = dict(
    marker = dict(
        size=10,
    )    
)


Layouts.FONT = dict(
    font=dict(family='Courier New',size=20, color='#7f7f7f'),
)


Layouts.Figure3D = SimpleNamespace()

Layouts.Figure3D.ZEROMARGINS = dict(
    margin = assign_multiple('l','r','b','t')(0)
)

Layouts.Figure3D.AXES = dict(
    scene = assign_multiple('xaxis','yaxis','zaxis')(
        dict(
            color="rgb(.5,.5,.5)",
            backgroundcolor="rgba(50,50,50,.95)",
            showbackground= False,
            gridcolor="rgb(.5,.5,.5)",
            zerolinecolor= "rgb(.75,.75,.75)",           
        )
    )
)

Layouts.Figure3D.RGBSPIKES = dict(
    scene= dict(zip(
        ('xaxis','yaxis','zaxis'), 
        map(keyed('spikecolor'),('red','blue','green'))
    ))
)