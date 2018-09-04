
from .core import wrap_publicmethods,fncaller
import pandas as pd 

locals().update(wrap_publicmethods(fncaller,pd.Series))