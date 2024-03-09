import os

import config
import geopandas as gpd
import pandas as pd

from dp_mobility_report.benchmark.alternative_benchmark_reports.evaluation_benchmarkreport import BenchmarkReport
from dp_mobility_report import DpMobilityReport

path_data = config.PROCESSED_DATA_PATH
path_html_output = config.OUTPUT_PATH

if not os.path.exists(path_html_output):
    os.makedirs(path_html_output)

df = pd.read_csv(
    os.path.join(path_data, "berlin.csv"), dtype={"tile_id": str}
)
tessellation = gpd.read_file(os.path.join(path_data, "berlin_tessellation.gpkg"))
base = DpMobilityReport(
    df,
    tessellation,
    privacy_budget=None,
    max_trips_per_user=5,
    disable_progress_bar=True,
    seed_sampling=1,
)
base.report

alternative = DpMobilityReport(
                        df,
                        tessellation,
                        privacy_budget=1,
                        max_trips_per_user=5,
                        user_privacy=True,
                        disable_progress_bar=True,
                        delta=0.00001,
                        gaussian=True,
                        evalu_analysis_selection_count=12,
                        seed_sampling=1,
                    )


benchmarkreport = BenchmarkReport(base=base, alternative=alternative)
# benchmark

measures = pd.Series(benchmarkreport.similarity_measures)
measures.to_csv(
            os.path.join(path_html_output, "mittelding.csv"),
            index_label="stat",
        )

benchmarkreport.to_file(
    os.path.join(path_html_output, "mittelding.html"), top_n_flows=100
)



