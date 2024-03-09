import os
import shelve

import config
import geopandas as gpd
import pandas as pd

from dp_mobility_report.benchmark.alternative_benchmark_reports.benchmark_of_reports import BenchmarkReport

path_data = config.PROCESSED_DATA_PATH
path_html_output = config.path_html_output
for dataset_name in config.DATASET_NAMES:
    ds_report_path = os.path.join(config.REPORT_PATH, dataset_name)

if not os.path.exists(path_html_output):
    os.makedirs(path_html_output)

df = pd.read_csv(
    os.path.join(path_data, "berlin_w_tile_id.csv"), dtype={"tile_id": str}
)
tessellation = gpd.read_file(os.path.join(path_data, "berlin_tessellation.gpkg"))

b = shelve.open(
                    os.path.join(
                        ds_report_path,
                        "gauss_None" +"_count_" + "1",
                    ))
a = shelve.open(
                    os.path.join(
                        ds_report_path,
                        "gauss_" + str(True) + "_count_" + str(16),
                    ))
# benchmark
benchmarkreport = BenchmarkReport(
    df_base=df,
    tessellation=tessellation,
    privacy_budget_base=None,
    alternative_report=a[str(0)],

    #analysis_exclusion=const.TRAVEL_TIME,

    # exclude analyses that you are not interested in, so save privacy budget
    # analysis_inclusion # can be used instead of anaylsis_exclusion
    # custom split of the privacy budget: to allocate more budget for certain analyses
    # subtitle="Geolife Benchmark report Gauss",  # provide a meaningful subtitle for your report readers
)


measures = pd.Series(benchmarkreport.similarity_measures)
measures.to_csv(
            os.path.join(path_html_output, "neuerTest.csv"),
            index_label="stat",
        )

benchmarkreport.to_file(
    os.path.join(path_html_output, "neuerTest.html"), top_n_flows=100
)



