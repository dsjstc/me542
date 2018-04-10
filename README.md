# Mech 542 Term Project

This project is an analysis of heating load and some potential energy conservation measures in a house with hydronic heating.  It's basically a bunch of Jupyter notebooks, and a handful of python files, making heavy use of Pandas and Matplotlib.

### Top level notebooks:

  - [Overview.ipynb](Overview.ipynb) - Description of the project
  - [AHeatingModel.ipynb](AHeatingModel.ipynb) - Heating load model
  - [all.ipynb](all.ipynb) - Runs all of the device models in sequence
  
### Utility notebooks:
  - [Loader.ipynb](Loader.ipynb) - Loads weather and consumption data
  - [ParseIrr.ipynb](ParseIrr.ipynb) - Loads CWEEDs irrigation data
  
### Individual model notebooks:
  - [hp.ipynb](hp.ipynb)
  - [BAU.ipynb](BAU.ipynb)
  - [LowSolar.ipynb](LowSolar.ipynb)
  - [Untitled.ipynb](Untitled.ipynb)
  - [nsb.ipynb](nsb.ipynb)
  - [HighSolar.ipynb](HighSolar.ipynb)
  - [tank.ipynb](tank.ipynb)

### Python model files
These files define the device / energy conservation models.
  - [bau.py](bau.py) - Sets the house state to "business as usual"
  - [boiler.py](boiler.py) - Uses electricity at 100% efficiency to serve remaining residual load.
  - [hp.py](hp.py) - Hydronic heat pump with a linear efficiency curve
  - [hsolar.py](hsolar.py) - Evacuated tube solar collector
  - [loadem.py](loadem.py) - Coiled poly hose solar collector
  - [nsb.py](nsb.py) - Night setback model
  - [tank.py](tank.py) - 1000 Gallon Heat storage tank
  - [loadirr.py](loadirr.py) - Utility loader for irrigation data
