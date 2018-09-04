
from ipywidgets import Layout, Button, Box, VBox
from types import SimpleNamespace
from ..core import evert,wrap

box_row_layout = Layout(
    display='flex',
    justify_content='space-between',
    flex_flow='row',
    align_items='stretch',
    width='100%',
    height='85vh'
)

box_col_layout = Layout(
    display='flex',
    justify_content='space-between',
    flex_flow='col',
    align_items='stretch',
    width='100%',
    height='85vh'
)

Layouts = SimpleNamespace()
Layouts.VBox = evert(wrap(VBox))

