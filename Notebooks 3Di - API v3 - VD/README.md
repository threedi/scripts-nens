3Di api v3 & Lizard scripts
==========================

In this folder you can find 3 different Jupyter notebooks making use of the API v3:
- notebook 1: From starting your simulation to analysing your results
- notebook 2: Using 3Di and Lizard together in one notebook for validation purposes
- notebook 3: Download a maximum waterdepth raster from Lizard from a 3Di simulation

This repository aims to exchange and showcase scripts around [3Di hydrodynamic
modelling software](http://www.3diwatermanagement.com/).

These scripts are Jupyter Notebooks which can be executed best within an
Python 3 environment set up within Anaconda. Most dependencies can be
installed using the Anaconda Navigator. If an dependency is not available
within Anaconda Navigator it can be installed using pip.

How to install a package in an Anaconda environment using pip?

1. Open *Anaconda Prompt*
2. Activate the correct environment: *activate <<environment_name>>*
3. Install the package: *pip install <<package_name>>*


Required packages:
- openapi_client
- threedi_api_client
- datetime
- getpass
- requests
- geopandas
- rasterio
- shapely


If you have any questions, feel free to contact Valerie Demetriades (valerie.demetriades@nelen-schuurmans.nl).
