import os
from tqdm.auto import tqdm

import shelve
import pandas as pd
import numpy as np
import geopandas as gpd
import time

import config
from dp_mobility_report.benchmark.benchmark_of_reports import BenchmarkReport as br


def key(gauss, count, rep=None):
    if rep is None:
        return "gauss_" + str(gauss) + "_count_" + str(count)
    else:
        return "gauss_" + str(gauss) + "_count_" + str(count) + "_rep_" + str(rep)


for dataset_name in config.DATASET_NAMES:
    ds_report_path = os.path.join(config.REPORT_PATH, dataset_name)
    df_output_path = os.path.join(config.OUTPUT_PATH, "tables", dataset_name)
    tessellation = gpd.read_file(
        os.path.join(config.PROCESSED_DATA_PATH, dataset_name + "_tessellation.gpkg"),
        dtype={"tile_id": str},
    )

    # get config info
    d = shelve.open(os.path.join(ds_report_path, "config"))
    gauss_array = d["gauss"]
    analysis_counts = d["counts"]
    reps = d["reps"]
    d.close()
    total_combinations = len(gauss_array) * len(analysis_counts)
    with tqdm(
        total=total_combinations, desc="Compute error measures for: " + dataset_name
    ) as pbar:  # progress bar
        # if export folder does not exist, create the folder
        if not os.path.exists(df_output_path):
            os.makedirs(df_output_path)

        similarity_measures = pd.DataFrame()
        similarity_measures_avg = pd.DataFrame()
        similarity_measures_std = pd.DataFrame()

        # get baseline report
        d = shelve.open(
            os.path.join(
                ds_report_path, "gauss_None" + "_count_" +str(max(analysis_counts)),
            )
        )
        report_true = d[str(0)]
        d.close()

        # speed up compuation by only computing cost_matrix once
        tile_centroids = (
            tessellation.set_index("tile_id").to_crs(3395).centroid.to_crs(4326)
        )
        sorted_tile_centroids = tile_centroids.loc[
            report_true["visits_per_tile"].data.tile_id
        ]
        tile_coords = list(zip(sorted_tile_centroids.y, sorted_tile_centroids.x))
        cost_matrix = em._get_cost_matrix(tile_coords)

        # compute error measures
        for gauss in gauss_array:
            for count in analysis_counts:
                d = shelve.open(
                    os.path.join(
                        ds_report_path,
                        "gauss_" + str(gauss) + "_count_" + str(count),
                    )
                )
                for i in range(0, reps):
                    if str(i) in list(d.keys()):
                        similarity_measures[key(gauss, count, i)] = pd.Series(
                            br.similarity_measures(
                                report_true, d[str(i)], tessellation, cost_matrix
                            )
                        ).round(3)
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
                d.close()
                pbar.update()

        similarity_measures.to_csv(
            os.path.join(df_output_path, dataset_name + "_all_reps.csv"),
            index_label="stat",
        )
        similarity_measures_avg.to_csv(
            os.path.join(df_output_path, dataset_name + "_mean.csv"),
            index_label="stat",
        )
        similarity_measures_std.to_csv(
            os.path.join(df_output_path, dataset_name + "_std.csv"), index_label="stat",
        )
