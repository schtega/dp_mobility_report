import pandas as pd
import matplotlib.pyplot as plt
import os

# Define paths
prefix = 'tables/'
datasets = ['berlin/berlin', 'geolife/geolife', 'madrid/madrid']
dataset_names = ['berlin', 'geolife', 'madrid']
topics = ['overview', 'place']


# Function to plot data with standard deviation
def plot_with_std(stat, dataset_index, topic):
    x = range(1, 17, 2)

    # Load the mean and standard deviation values for the given dataset and topic
    mean_df = pd.read_csv(prefix + datasets[dataset_index] + f'_all_reps_{topic}_smape_mean.csv')
    std_dev_df = pd.read_csv(prefix + datasets[dataset_index] + f'_all_reps_{topic}_smape_std.csv')

    output_dir = os.path.join('graphs', topic, dataset_names[dataset_index])

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Plot each stat
    plt.figure(figsize=(10, 6))
    if stat in mean_df['stat'].values:
        mean_true = mean_df[mean_df['stat'] == stat].iloc[0, 1:9].values.flatten()
        mean_false = mean_df[mean_df['stat'] == stat].iloc[0, 9:].values.flatten()
        std_dev_true = std_dev_df[std_dev_df['stat'] == stat].iloc[0, 1:9].values.flatten()
        std_dev_false = std_dev_df[std_dev_df['stat'] == stat].iloc[0, 9:].values.flatten()

        # Plot Gauss True
        plt.errorbar(x, mean_true, yerr=std_dev_true, label='Gaussian Mechanism', fmt='-o', capsize=5, capthick=2)

        # Plot Gauss False
        plt.errorbar(x, mean_false, yerr=std_dev_false, label='Laplace Mechanism', fmt='-o', capsize=5, capthick=2)

        plt.xlabel('Number of included Analyses')
        plt.ylabel(stat)
        plt.title(f'{stat} Comparison with Standard Deviation')
        plt.legend()

        # Save the plot as PNG and SVG in the dataset's directory
        plt.savefig(os.path.join(output_dir, f'{stat}_comparison.png'), format='png')
        plt.savefig(os.path.join(output_dir, f'{stat}_comparison.svg'), format='svg')
        plt.close()


# Process all topics and datasets
for topic in topics:
    # Create the topic directories if they don't exist
    topic_dir = os.path.join('graphs', topic)
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

    # Create and save summary plots for each statistic
    for stat in all_stats:
        fig, axs = plt.subplots(1, len(datasets), figsize=(20, 6))

        for j, name in enumerate(dataset_names):
            img_path = os.path.join('graphs', topic, name, f'{stat}_comparison.png')
            if os.path.exists(img_path):
                img = plt.imread(img_path)
                axs[j].imshow(img)
                axs[j].axis('off')
                axs[j].set_title(name)
            else:
                axs[j].axis('off')

        plt.suptitle(f'{stat} Summary Comparison for {topic}')
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # Save the summary plot as PNG and SVG
        plt.savefig(os.path.join('graphs', topic, f'{stat}_summary.png'), format='png')
        plt.savefig(os.path.join('graphs', topic, f'{stat}_summary.svg'), format='svg')
        plt.close()

print("All plots saved successfully.")
