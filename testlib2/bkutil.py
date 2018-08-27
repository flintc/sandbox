
from .pdutil import ElementWiseDataFrameContainer,DataFrameContainer,S
from .core import pipe,prop,arrows,chunk_list
import testlib2.core as c
import testlib2.pointfree as pf 
import bokeh.io as bio 
import bokeh.plotting as bkp
import bokeh.layouts as bkl
import bokeh.themes as bkthemes
import bokeh.models as bkm
import pyramda as r
import pandas as pd
from dataclasses import dataclass
import bokeh
from typing import Any
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
import yaml

A = arrows() 

@dataclass
class Layout:
    ns: Any
    def __getattr__(self,name):
        def wrapper(*args,**kwargs):
            def wrapped(obj):
                return getattr(self.ns,name)(obj,*args,**kwargs)
            return wrapped
        return wrapper

L = Layout(bokeh.layouts)
I = Layout(bokeh.io)

def circle(**kwargs):
    def wrapper(x):
        return x.circle(**kwargs)
    return wrapper




class BokehLayoutContainer(DataFrameContainer):
    @classmethod
    def empty(cls):
        return cls(pd.DataFrame(dict(figures=[],circles=[]),index=[]) )
    def add_glyph(self,fig_name,glyph_name,**kwargs):
        return self.assign(
            'circles',
            pipe(
                prop('figures'),
                prop(fig_name),
                circle(**kwargs)
            )
        )
    def show(self,model_name):
        return (self
            .get(model_name)
            .map(r.tap(bio.show))
            .write()
        )
    def extend(self,fn):
        return self.concat( type(self)( fn(self) ) )
    def chain(self,fn):
        return self.concat(fn(self.value))


# def add_circle(name,**kwargs):
#     def wrapper(fig):
#         df = pd.DataFrame({'figures': [fig]},index=[fig.name])
#         return BokehLayoutContainer(df).add_glyph(fig.name,name,**kwargs)
#     return wrapper

def to_layout(bklayout,ncols=1):
    return pipe(S.unique(),chunk_list(ncols),bklayout)

def add_circle(fig_name,name,**kwargs):
    def wrapper(x):
        fig = pipe(prop('figures'),prop(fig_name))(x.value)
        glyph = circle(**kwargs)(fig)
        df = pd.DataFrame({'figures': [fig],'circles': [glyph]},index=[fig_name]) 
        return df
    return wrapper

def set_layout(fig_name,pos,**kwargs):
    def wrapper(x):
        fig = pipe(prop('figures'),prop(fig_name))(x.value)
        glyph = circle(**kwargs)(fig)
        df = pd.DataFrame({'figures': [fig],'circles': [glyph]},index=[fig_name]) 
        return df
    return wrapper

def new_figure(**opts):
    def wrapper(x):
        fig = bkp.figure(**opts)
        df = pd.DataFrame({'figures': [fig],'circles': [None]},index=[fig.name]) 
        return df
    return wrapper

def add_linked_figure(fig_name,**opts):
    def wrapper(x):
        base_opts = pipe(
            prop('figures'),
            prop(fig_name),
            A.andop(r.map(prop,('x_range','y_range'))),
            c.zip(('x_range','y_range')),
            dict
        )(x.value)
        fig = bkp.figure(**base_opts,**opts)
        df = pd.DataFrame({'figures': [fig],'circles': [None]},index=[fig.name]) 
        return df
    return wrapper 


def empty():
    return BokehLayoutContainer.empty()

def bokeh_builder(*fns):
    return pipe(*map(pf.extend,fns))

def apply_theme(theme):
    doc = bio.curdoc()
    doc.theme = theme


def doc_modifier(layout,theme,fn):
    def modify_doc(doc):
        roots = fn()
        doc.add_root( layout(*roots) )
        doc.theme = bkthemes.Theme(json=yaml.load(theme))
    return modify_doc

def example_doc_modifier():
    df = sea_surface_temperature.copy()
    source = bkm.ColumnDataSource(data=df)

    plot = bkp.figure(x_axis_type='datetime', y_range=(0, 25),
                  y_axis_label='Temperature (Celsius)',
                  title="Sea Surface Temperature at 43.18, -70.43")
    plot.line('time', 'temperature', source=source)

    def callback(attr, old, new):
        if new == 0:
            data = df
        else:
            data = df.rolling('{0}D'.format(new)).mean()
        source.data = bkm.ColumnDataSource(data=data).data

    slider = bkm.Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
    slider.on_change('value', callback)
    return slider,plot 


dark_theme = '''
attrs:
    Figure:
        background_fill_alpha: 0.2
        border_fill_alpha: 0.0
        outline_line_color: 'white'
        width: 400
        height: 400
        min_border_left: 50
    Axis:
        axis_line_color: "white"
        axis_label_text_color: "white"
        major_label_text_color: "white"
        major_tick_line_color: "white"
        minor_tick_line_color: "white"
        minor_tick_line_color: "white"
    Grid:
        grid_line_dash: [6, 4]
        grid_line_alpha: .3
    Title:
        text_color: "white"
'''

test_app = doc_modifier(bkl.column,dark_theme,example_doc_modifier)

