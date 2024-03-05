import os

import config
import geopandas as gpd
import pandas as pd

from dp_mobility_report import DpMobilityReport

# set paths to data and output (either with config file or hardcoded)
path_data = config.path_data
path_html_output = config.path_html_output

if not os.path.exists(path_html_output):
    os.makedirs(path_html_output)


# BERLIN
df = pd.read_csv(
    os.path.join(path_data, "berlin_w_tile_id.csv"), dtype={"tile_id": str}
)
tessellation = gpd.read_file(os.path.join(path_data, "berlin_tessellation.gpkg"))

report = DpMobilityReport(
    df,
    tessellation,
    privacy_budget=1,
    max_trips_per_user=5,
    gaussian=True,
    delta=0.00001,
    subtitle="Berlin Dataset - privacy - gauss",
)
report.to_file(os.path.join(path_html_output, "berlin_gauss.html"), top_n_flows=300)

report = DpMobilityReport(
    df,
    tessellation,
    privacy_budget=None,
    max_trips_per_user=5,
    subtitle="Berlin Dataset - no privacy ",
)
report.to_file(os.path.join(path_html_output, "berlin_noPrivacy_gauss.html"), top_n_flows=300)
