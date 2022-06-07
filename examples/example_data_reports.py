import os

import geopandas as gpd
import pandas as pd

from dp_mobility_report import md_report

path_data = (
    "data/processed"
)
path_html_output = "examples/html"

if not os.path.exists(path_html_output):
    os.makedirs(path_html_output)

# GEOLIFE
df = pd.read_csv(os.path.join(path_data, "geolife.csv"))
tessellation = gpd.read_file(os.path.join(path_data, "geolife_tessellation.gpkg"))
tessellation["tile_name"] = tessellation.tile_id

report = md_report.MobilityDataReport(
    df,
    tessellation,
    privacy_budget=50,
    analysis_selection=["overview", "place_analysis"],
    evalu=True,
    max_trips_per_user=5,
    max_travel_time=90,
    bin_range_travel_time=5,
    max_jump_length=30,
    bin_range_jump_length=3,
    max_radius_of_gyration=18,
    bin_range_radius_of_gyration=1.5,
)
report.to_file(os.path.join(path_html_output, "geolife.html"), top_n_flows=100)

# MADRID
df = pd.read_csv(os.path.join(path_data, "madrid.csv"))
tessellation = gpd.read_file(os.path.join(path_data, "madrid_tessellation.gpkg"))

report = md_report.MobilityDataReport(
    df,
    tessellation,
    privacy_budget=10,
    analysis_selection=["all"],
    max_trips_per_user=5,
    max_travel_time=90,
    bin_range_travel_time=5,
    max_jump_length=30,
    bin_range_jump_length=3,
    max_radius_of_gyration=18,
    bin_range_radius_of_gyration=1.5,
)
report.to_file(os.path.join(path_html_output, "madrid.html"), top_n_flows=300)


# BERLIN
df = pd.read_csv(
    os.path.join(path_data, "berlin_w_tile_id.csv"), dtype={"tile_id": str}
)
tessellation = gpd.read_file(os.path.join(path_data, "berlin_tessellation.gpkg"))

report = md_report.MobilityDataReport(
    df,
    tessellation,
    privacy_budget=1,
    analysis_selection=["all"],
    max_trips_per_user=5,
    max_travel_time=90,
    bin_range_travel_time=5,
    max_jump_length=30,
    bin_range_jump_length=3,
    max_radius_of_gyration=18,
    bin_range_radius_of_gyration=1.5,
)
report.to_file(os.path.join(path_html_output, "berlin.html"), top_n_flows=300)
