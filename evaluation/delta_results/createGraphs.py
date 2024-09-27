import pandas as pd
import matplotlib.pyplot as plt
import os

# Define paths
prefix = 'tables/'
datasets = ['berlin/berlin', 'geolife/geolife', 'madrid/madrid']
dataset_names = ['berlin', 'geolife', 'madrid']
topics = ['overview', 'place']
store_folder = 'updated_graphs_22'
fontsize = 22

# Define a consistent figure size
figsize = (10, 6)  # Fixed size in inches

# Set a left margin large enough for 5 digits
left_margin = 0.8  # Adjust this value as needed (0.2 is a good start)

# Function to plot data with standard deviation
def plot_with_std(stat, dataset_index, topic):
    x = range(1, 17, 2)

    # Load the mean and standard deviation values for the given dataset and topic
    mean_df = pd.read_csv(prefix + datasets[dataset_index] + f'_all_reps_{topic}_smape_mean.csv')
    std_dev_df = pd.read_csv(prefix + datasets[dataset_index] + f'_all_reps_{topic}_smape_std.csv')

    output_dir = os.path.join(store_folder, topic, dataset_names[dataset_index])

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Plot each stat
    plt.figure(figsize=figsize)  # Use consistent figure size
    if stat in mean_df['stat'].values:
        mean_true = mean_df[mean_df['stat'] == stat].iloc[0, 1:9].values.flatten()
        mean_false = mean_df[mean_df['stat'] == stat].iloc[0, 9:].values.flatten()
        std_dev_true = std_dev_df[std_dev_df['stat'] == stat].iloc[0, 1:9].values.flatten()
        std_dev_false = std_dev_df[std_dev_df['stat'] == stat].iloc[0, 9:].values.flatten()

        # Plot Gauss True
        plt.errorbar(x, mean_true, yerr=std_dev_true, label='Gaussian Mechanism', fmt='-o', capsize=5, capthick=2)

        # Plot Gauss False
        plt.errorbar(x, mean_false, yerr=std_dev_false, label='Laplace Mechanism', fmt='-o', capsize=5, capthick=2)

        # Remove the y-axis label but keep the ticks
        plt.ylabel('')  # No y-axis label
        plt.xlabel('Number of included Analyses', fontsize=fontsize)  # x-axis label
        plt.xticks(fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        plt.legend(fontsize=fontsize)

        # Adjust the left margin to ensure space for 5 digits
        plt.subplots_adjust(left=left_margin)

        # Save the plot as PNG and SVG with the dataset name appended to the file name
        file_name = f'{stat}_comparison_{dataset_names[dataset_index]}'
        plt.savefig(os.path.join(output_dir, f'{file_name}.png'), format='png', bbox_inches='tight', dpi=300)
        plt.savefig(os.path.join(output_dir, f'{file_name}.svg'), format='svg', bbox_inches='tight')
        plt.close()

# Process all topics and datasets
for topic in topics:
    # Create the topic directories if they don't exist
    topic_dir = os.path.join(store_folder, topic)
    if not os.path.exists(topic_dir):
        os.makedirs(topic_dir)

    # Collect all statistics from all datasets for this topic
    all_stats = set()
    for dataset_index in range(len(datasets)):
        mean_df = pd.read_csv(prefix + datasets[dataset_index] + f'_all_reps_{topic}_smape_mean.csv')
        all_stats.update(mean_df['stat'].values)

    # Plot for all datasets and all statistics
    for stat in all_stats:
        for dataset_index in range(len(datasets)):
            plot_with_std(stat, dataset_index, topic)

print("All plots saved successfully.")
