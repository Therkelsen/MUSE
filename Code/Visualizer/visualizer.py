import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.animation import FuncAnimation


def update_data(i):
    # Load your data in each iteration (update)
    raw_sensor_data = pd.read_csv("Code/Data/raw_sensor_data.csv")
    filtered_sensor_data = pd.read_csv("Code/Data/filtered_data.csv").iloc[3:]

    # Clear the current plots
    plt.clf()

    # Get the dimensions of your data
    num_rows, num_cols = raw_sensor_data.shape

    # Create a meshgrid for the x and y values
    x = np.arange(1, num_cols + 1)  # x-axis values (freq_1 to freq_15)
    y = np.arange(1, num_rows + 1)  # y-axis values (four sets of data)
    X, Y = np.meshgrid(x, y)

    # Create the 2D plot for selected_frequency (Frequency 5 in this case)
    ax1 = plt.subplot(gs[0, 0])  # 2D plot in the top row
    selected_frequency = raw_sensor_data.iloc[:, 9]  # Change the column index as needed
    min_value = selected_frequency.min()
    mask = selected_frequency >= min_value
    l = ax1.fill_between(y[mask], min_value, selected_frequency[mask], color=[.84, .15, .29], alpha=.3, label='Frequency 10')
    ax1.plot(y, selected_frequency, marker='', linestyle='-', color=[.84, .15, .29], linewidth=0.5)
    ax1.set_xlabel('Data Set')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('2D Plot for Frequency 10')
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlim(1, num_rows)
    # l.set_facecolors([[.5, .5, 1, .3]])
    # l.set_edgecolors([[.22, .48, 1, .3]])
    l.set_linewidths([0.1])
    ax1.spines['right'].set_color((.8, .8, .8))
    ax1.spines['top'].set_color((.8, .8, .8))

    # Create the 2D plot for filtered_sensor_data
    
    # Get the dimensions of your data
    num_rows, num_cols = filtered_sensor_data.shape

    # Create a meshgrid for the x and y values
    x = np.arange(1, num_cols + 1)  # x-axis values (freq_1 to freq_15)
    y = np.arange(1, num_rows + 1)  # y-axis values (four sets of data)
    X, Y = np.meshgrid(x, y)
    
    ax2 = plt.subplot(gs[1, 0])  # 2D plot in the bottom row
    filtered_data_column = filtered_sensor_data.iloc[:, 9]  # Replace with the appropriate column name
    min_value = filtered_data_column.min()
    mask = filtered_data_column >= min_value
    l = ax2.fill_between(y[mask], min_value, filtered_data_column[mask], color=[.15, .73, .28], alpha=.3, label='Frequency 10')
    ax2.plot(y, filtered_data_column, marker='', linestyle='-', color=[.15, .73, .28], label='Filtered Data', linewidth=0.5)
    ax2.set_xlabel('Data Set')
    ax2.set_ylabel('Amplitude')
    ax2.set_title('2D Plot of Filtered Sensor Data from Frequency 10')
    ax2.grid(True)
    ax2.legend()
    ax2.set_xlim(1, num_rows)
    # l.set_facecolors([[.5, .5, 1, .3]])
    # l.set_edgecolors([[.22, .48, 1, .3]])
    l.set_linewidths([0.1])
    ax2.spines['right'].set_color((.8, .8, .8))
    ax2.spines['top'].set_color((.8, .8, .8))

    # Adjust layout and show the plots
    plt.tight_layout()


if __name__ == "__main__":
    # Create a figure and subplots with a grid layout
    fig = plt.figure(figsize=(18, 10))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1])  # 2 rows, 1 column

    # Use FuncAnimation to update the plots every second without caching frame data
    ani = FuncAnimation(fig, update_data, interval=1000, cache_frame_data=False)

    plt.show()
