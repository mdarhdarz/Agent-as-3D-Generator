from .core import OcMesher

# In this local setup we only need OcMesher to satisfy import-time checks while
# running non-terrain smoke tests such as individual asset generation.
__version__ = "2.0"
