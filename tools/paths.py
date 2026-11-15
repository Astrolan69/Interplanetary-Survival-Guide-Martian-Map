"""Shared paths for the data-processing scripts in tools/.

ROOT  = the repository root (the site: index.html, data/, img/ ...).
TOOLS = this folder.
RAW   = the raw NASA/USGS downloads (DEMs, mosaics, MMGIS waypoints...). They are not
        stored in the repository; set MAREK_RAW to the folder that holds them
        (default: <repo>/raw). See docs/DATA_PIPELINE.md for what goes in it.
"""
import os
TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
RAW = os.environ.get('MAREK_RAW', os.path.join(ROOT, 'raw'))
