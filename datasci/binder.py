from .objects import merge,prop,assign,assign_multiple,keyed,omit
from .core import evert,wrap
from operator import *
from plotly.graph_objs import *

locals().update( 
    dict([
        (k,evert(wrap(fn))) for k,fn in locals().items() if not k.startswith('_')
    ])
 )