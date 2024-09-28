import os
from pathlib import Path
import shelve
from tqdm.auto import tqdm

import pandas as pd
import numpy as np
import geopandas as gpd

import config
from dp_mobility_report import DpMobilityReport
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
    df = pd.read_csv(
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

    # Settings
    gauss_array = [True, False]
    analysis_counts = [1, 2, 4, 8, 12, 16]
    reps = 2
    
    # compute reports
    d = shelve.open(os.path.join(ds_report_path, "config"))
    d["gauss"] = gauss_array
    d["counts"] = analysis_counts
    d["reps"] = reps
    d.close()
    total_runs = len(analysis_counts) * reps
    with tqdm(
        total=total_runs, desc="Create reports for " + dataset_name
    ) as pbar:  # progress bar

            for count in analysis_counts:
                shelve_path = os.path.join(
                    ds_report_path, "gauss_" + str(None) + "_count_" + str(count)
                )
                if os.path.exists(shelve_path + ".db"):
                    os.remove(shelve_path + ".db")
                d = shelve.open(shelve_path)
                for i in range(0, reps):
                    d[str(i)] = DpMobilityReport(
                        df,
                        tessellation,
                        privacy_budget=None,
                        analysis_selection=[
                            "overview",
                            "place_analysis",
                            "od_analysis",
                            "user_analysis",
                        ],
                        max_trips_per_user=5,
                        disable_progress_bar=True,
                        evalu_analysis_selection_count=count,
                        seed_sampling=1,
                    ).report
                    pbar.update()
                d.close()
