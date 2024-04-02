import os
from pathlib import Path
import shelve
from tqdm.auto import tqdm

import pandas as pd
import numpy as np
import geopandas as gpd

import config
from dp_mobility_report import DpMobilityReport, constants
from dp_mobility_report import constants as const
from dp_mobility_report.benchmark.benchmarkreport import BenchmarkReport
from dp_mobility_report.model import preprocessing


if not os.path.exists(config.REPORT_PATH):
    os.makedirs(config.REPORT_PATH)


for dataset_name in config.DATASET_NAMES:
    if not Path(
        os.path.join(config.PROCESSED_DATA_PATH, dataset_name + ".csv")
    ).exists():
        print("No data for " + dataset_name + " exists. Data set is skipped.")
        continue

    if not Path(
        os.path.join(config.PROCESSED_DATA_PATH, dataset_name + "_tessellation.gpkg")
    ).exists():
        print(
            "Tessellation for " + dataset_name + " does not exist. Data set is skipped."
        )
        continue

    # load data
    if dataset_name == "berlin":
        df = pd.read_csv(
            os.path.join(config.PROCESSED_DATA_PATH, "berlin_w_tile_id" + ".csv"),
            #os.path.join(config.PROCESSED_DATA_PATH, dataset_name + ".csv"),
            dtype={"tile_id": str},
        )
    else:
        df = pd.read_csv(
            #os.path.join(config.PROCESSED_DATA_PATH, "berlin_w_tile_id" + ".csv"),
            os.path.join(config.PROCESSED_DATA_PATH, dataset_name + ".csv"),
            dtype={"tile_id": str},
        )

    tessellation = gpd.read_file(
        os.path.join(config.PROCESSED_DATA_PATH, dataset_name + "_tessellation.gpkg"),
        dtype={"tile_id": str},
    )
    # assign tile ids beforehand so it does not have to be repeated for every run
    if "tile_name" not in tessellation.columns:
        tessellation["tile_name"] = tessellation.tile_id


    #if "tile_id" not in df.columns:
     #   df = preprocessing.assign_points_to_tessellation(df, tessellation)
    ds_report_path = os.path.join(config.REPORT_PATH, dataset_name)
    if not os.path.exists(ds_report_path):
        os.makedirs(ds_report_path)

    df_output_path = os.path.join(config.OUTPUT_PATH, "tables", dataset_name)


    def key(gauss, count, rep=None):
        if rep is None:
            return "gauss_" + str(gauss) + "_count_" + str(count)
        else:
            return "gauss_" + str(gauss) + "_count_" + str(count) + "_rep_" + str(rep)


    # Settings
    gauss_array = [True, False]
    #gauss_array = [True]
    analysis_counts = [1,3,5,7,9,11,13,15]
    #analysis_counts = [16]
    reps = 8

    similarity_measures = pd.DataFrame()
    similarity_measures_avg = pd.DataFrame()
    similarity_measures_std = pd.DataFrame()

    '''
    base = DpMobilityReport(
        df,
        tessellation,
        privacy_budget=None,
        max_trips_per_user=5,
        disable_progress_bar=True,
        seed_sampling=1,
    )
    base.report
    '''

    total_runs = len(analysis_counts) * len(gauss_array) * reps
    with tqdm(
        total=total_runs, desc="Create evaluation for " + dataset_name
    ) as pbar:  # progress bar
        if not os.path.exists(df_output_path):
            os.makedirs(df_output_path)

        for gauss in gauss_array:
            print(gauss)
            for count in analysis_counts:

                for i in range(0, reps):
                    benchmark = BenchmarkReport(
                        df_base=df,
                        tessellation=tessellation,
                        privacy_budget_base=None,
                        analysis_selection=[
                            #const.OVERVIEW,
                            #const.PLACE_ANALYSIS,
                            const.OD_ANALYSIS,
                            #const.USER_ANALYSIS

                        ],
                        privacy_budget_alternative=1,
                        max_trips_per_user_base=5,
                        max_trips_per_user_alternative=5,
                        gaussian_alternative=gauss,
                        user_privacy_alternative=True,
                        delta_alternative=0.00001,
                        evalu_analysis_selection_count_alternative=count,
                        seed_sampling=1,
                        # exclude analyses that you are not interested in, so save privacy budget
                        # analysis_inclusion # can be used instead of anaylsis_exclusion
                        # custom split of the privacy budget: to allocate more budget for certain analyses
                        subtitle="Geolife Benchmark report Gauss",
                        # provide a meaningful subtitle for your report readers
                    )
                    similarity_measures[key(gauss, count, i)] = pd.Series(
                        benchmark.smape
                    ).round(7)
                    pbar.update()
                '''
                similarity_measures_avg[key(gauss, count)] = (
                    similarity_measures.loc[
                        :, similarity_measures.columns.str.startswith(key(gauss, count))
                    ]
                    .T.mean()
                    .round(3)
                )
                similarity_measures_std[key(gauss, count)] = (
                    similarity_measures.loc[
                        :, similarity_measures.columns.str.startswith(key(gauss, count))
                    ]
                    .T.std()
                    .round(3)
                )
                '''

        similarity_measures.to_csv(
            os.path.join(df_output_path, dataset_name + "_all_reps_user_smape.csv"),
            index_label="stat",
        )
        '''
        similarity_measures_avg.to_csv(
            os.path.join(df_output_path, dataset_name + "_mean.csv"),
            index_label="stat",
        )
        similarity_measures_std.to_csv(
            os.path.join(df_output_path, dataset_name + "_std.csv"), index_label="stat",
        )
        '''
