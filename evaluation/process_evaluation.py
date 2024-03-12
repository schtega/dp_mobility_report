import pandas as pd
import config
import os


dataset= "geolife"
dataset_name = dataset+"_all_reps_smape"
df_output_path = os.path.join(config.OUTPUT_PATH, "tables", dataset)
#berlin_overview = pd.Series.from_csv("tables/berlin/" + dataset_name + ".csv")

rows_to_skip_labels = ['visits_per_tile_ranking', 'od_flows_ranking']  #  skip rows with these labels

# Define a function to skip rows based on their labels
def should_skip_row(row):
    return row.name in rows_to_skip_labels

berlin_overview = pd.read_csv(os.path.join(df_output_path, dataset_name + ".csv"), index_col=0, skiprows=[])

data_to_process = berlin_overview

def key(gauss, count, rep=None):
    if rep is None:
        return "gauss_" + str(gauss) + "_count_" + str(count)
    else:
        return "gauss_" + str(gauss) + "_count_" + str(count) + "_rep_" + str(rep)


# Settings
gauss_array = [True, False]
# gauss_array = [True]
analysis_counts = [1, 2, 4, 8, 12, 16]
# analysis_counts = [16]
reps = 8

similarity_measures_avg = pd.DataFrame()
similarity_measures_std = pd.DataFrame()

for gauss in gauss_array:
    print(gauss)
    for count in analysis_counts:
        similarity_measures_avg[key(gauss, count)] = (
            data_to_process.loc[
            :, data_to_process.columns.str.startswith(key(gauss, count))
            ]
            .T.mean()
            .round(3)
        )
        similarity_measures_std[key(gauss, count)] = (
            data_to_process.loc[
            :, data_to_process.columns.str.startswith(key(gauss, count))
            ]
            .T.std()
            .round(3)
        )
df_output_path = os.path.join(config.OUTPUT_PATH, "tables", dataset)
if not os.path.exists(df_output_path):
    os.makedirs(df_output_path)

similarity_measures_avg.to_csv(
    os.path.join(df_output_path, dataset_name + "_mean.csv"),
    index_label="stat",
)
similarity_measures_std.to_csv(
    os.path.join(df_output_path, dataset_name + "_std.csv"), index_label="stat",
)
