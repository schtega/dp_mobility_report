import os

import config
import geopandas as gpd
import pandas as pd

from dp_mobility_report.benchmark.benchmarkreport import BenchmarkReport
from dp_mobility_report import constants as const

path_data = config.path_data
path_html_output = config.path_html_output

if not os.path.exists(path_html_output):
    os.makedirs(path_html_output)

# GEOLIFE
df = pd.read_csv(os.path.join(path_data, "geolife.csv"))
tessellation = gpd.read_file(os.path.join(path_data, "geolife_tessellation.gpkg"))
tessellation["tile_name"] = tessellation.tile_id

benchmarkreport = BenchmarkReport(
    df_base=df,
    df_alternative=df,
    tessellation=tessellation,
    privacy_budget_base=None,
    privacy_budget_alternative=15.0,
    max_trips_per_user_base=10,
    max_trips_per_user_alternative=10,
    analysis_exclusion=[const.USER_ANALYSIS],
)

measures = benchmarkreport.similarity_measures
print(measures)

print(benchmarkreport.measure_selection)

# measures.to_file(os.path.join(path_html_output, "measures.html"))
benchmarkreport.to_file(os.path.join(path_html_output, "geolife_benchmark.html"), top_n_flows=10)
