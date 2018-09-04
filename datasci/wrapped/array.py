
from .core import wrap_publicmethods, fncaller
import numpy as np
locals().update( wrap_publicmethods(fncaller, np.ndarray ) )