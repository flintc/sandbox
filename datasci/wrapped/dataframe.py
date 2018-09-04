
from .core import wrap_publicmethods,fncaller
import pandas as pd 
from functools import partial
locals().update(wrap_publicmethods(fncaller,pd.DataFrame))
