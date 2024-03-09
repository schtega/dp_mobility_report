import os

import config
import geopandas as gpd
import pandas as pd

from dp_mobility_report.benchmark.benchmarkreport import BenchmarkReport
from dp_mobility_report import constants as const

path_data = config.PROCESSED_DATA_PATH
path_html_output = config.OUTPUT_PATH

if not os.path.exists(path_html_output):
    os.makedirs(path_html_output)

df = pd.read_csv(
    os.path.join(path_data, "berlin.csv"), dtype={"tile_id": str}
)
tessellation = gpd.read_file(os.path.join(path_data, "berlin_tessellation.gpkg"))

# benchmark
benchmarkreport = BenchmarkReport(
    df_base=df,
    tessellation=tessellation,
    privacy_budget_base=None,
    analysis_selection=[
        "overview",
        "place_analysis",
        "od_analysis",
        "user_analysis",
    ],
    privacy_budget_alternative=1,
    max_trips_per_user_base=5,
    max_trips_per_user_alternative=5,
    gaussian_alternative=True,
    user_privacy_alternative= True,
    delta_alternative=0.00001,
    delta=0.00001,
    evalu_analysis_selection_count=16,
    evalu_analysis_selection_count_alternative=16,
    seed_sampling=1,
    # exclude analyses that you are not interested in, so save privacy budget
    # analysis_inclusion # can be used instead of anaylsis_exclusion
    # custom split of the privacy budget: to allocate more budget for certain analyses
    subtitle="Berlin Benchmark report Gauss",  # provide a meaningful subtitle for your report readers
)


measures = pd.Series(benchmarkreport.similarity_measures)
measures.to_csv(
            os.path.join(path_html_output, "basictest.csv"),
            index_label="stat",
        )

benchmarkreport.to_file(
    os.path.join(path_html_output, "basictest.html"), top_n_flows=100
)



