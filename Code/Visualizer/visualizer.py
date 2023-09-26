import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.animation import FuncAnimation


def update_data(i):
    # Load your data in each iteration (update)
    raw_sensor_data = pd.read_csv("Code/Data/raw_sensor_data.csv")
    filtered_sensor_data = pd.read_csv("Code/Data/filtered_data.csv").iloc[3:]
    noise_data = pd.read_csv("Code/Data/noise_data.csv")

    # Clear the current plots
    plt.clf()

    # Get the dimensions of your data
    num_rows, num_cols = raw_sensor_data.shape

    # Create a meshgrid for the x and y values
    x = np.arange(1, num_cols + 1)  # x-axis values (freq_1 to freq_15)
    y = np.arange(1, num_rows + 1)  # y-axis values (four sets of data)
    X, Y = np.meshgrid(x, y)

    # Create the 3D surface plot for raw_sensor_data
    ax1 = plt.subplot(gs[0, 0], projection='3d')  # 3D plot
    surf1 = ax1.plot_surface(X, Y, raw_sensor_data.values, cmap='jet', rstride=1, cstride=1, linewidth=0, antialiased=False)
    ax1.set_xlabel('Frequency')
    ax1.set_ylabel('Data Set')
    ax1.set_zlabel('Amplitude')
    ax1.set_title('Raw Sensor Data')

    # Create the 2D plot for selected_frequency (Frequency 5 in this case)
    ax2 = plt.subplot(gs[0, 1])  # 2D plot
    selected_frequency = raw_sensor_data.iloc[:, 9]  # Change the column index as needed
    min_value = selected_frequency.min()
    mask = selected_frequency >= min_value
    l = ax2.fill_between(y[mask], min_value, selected_frequency[mask], alpha=.3, label='Frequency 10')
    ax2.plot(y, selected_frequency, marker='', linestyle='-', color=[.22, .48, 1])
    ax2.set_xlabel('Data Set')
    ax2.set_ylabel('Amplitude')
    ax2.set_title('2D Plot for Frequency 10')
    ax2.grid(True)
    ax2.legend()
    ax2.set_xlim(1, num_rows)
    l.set_facecolors([[.5, .5, 1, .3]])
    l.set_edgecolors([[.22, .48, 1, .3]])
    l.set_linewidths([1])
    ax2.spines['right'].set_color((.8, .8, .8))
    ax2.spines['top'].set_color((.8, .8, .8))

    # Create the 2D plot for filtered_sensor_data
    
    # Get the dimensions of your data
    num_rows, num_cols = filtered_sensor_data.shape

    # Create a meshgrid for the x and y values
    x = np.arange(1, num_cols + 1)  # x-axis values (freq_1 to freq_15)
    y = np.arange(1, num_rows + 1)  # y-axis values (four sets of data)
    X, Y = np.meshgrid(x, y)
    
    ax3 = plt.subplot(gs[1, 0])  # 2D plot
    filtered_data_column = filtered_sensor_data.iloc[:, 9]  # Replace with the appropriate column name
    min_value = filtered_data_column.min()
    mask = filtered_data_column >= min_value
    l = ax3.fill_between(y[mask], min_value, filtered_data_column[mask], alpha=.3, label='Frequency 10')
    ax3.plot(y, filtered_data_column, marker='', linestyle='-', color=[.22, .48, 1], label='Filtered Data')
    ax3.set_xlabel('Data Set')
    ax3.set_ylabel('Amplitude')
    ax3.set_title('2D Plot of Filtered Sensor Data from Frequency 10')
    ax3.grid(True)
    ax3.legend()
    ax3.set_xlim(1, num_rows)
    l.set_facecolors([[.5, .5, 1, .3]])
    l.set_edgecolors([[.22, .48, 1, .3]])
    l.set_linewidths([1])
    ax3.spines['right'].set_color((.8, .8, .8))
    ax3.spines['top'].set_color((.8, .8, .8))

    # Create the 2D plot for noise_data
    # Get the dimensions of your data
    num_rows, num_cols = noise_data.shape

    # Create a meshgrid for the x and y values
    x = np.arange(1, num_cols + 1)  # x-axis values (freq_1 to freq_15)
    y = np.arange(1, num_rows + 1)  # y-axis values (four sets of data)
    X, Y = np.meshgrid(x, y)
    
    ax4 = plt.subplot(gs[1, 1])  # 2D plot
    noise_data_column = noise_data.iloc[:, 9]  # Replace with the appropriate column name
    min_value = noise_data_column.min()
    mask = noise_data_column >= min_value
    l = ax4.fill_between(y[mask], min_value, noise_data_column[mask], alpha=.3, label='Frequency 10')
    ax4.plot(y, noise_data_column, marker='', linestyle='-', color=[.22, .48, 1], label='Noise Data')
    ax4.set_xlabel('Data Set')
    ax4.set_ylabel('Amplitude')
    ax4.set_title('2D Plot of Noise Data from Frequency 10')
    ax4.grid(True)
    ax4.legend()
    ax4.set_xlim(1, num_rows)
    l.set_facecolors([[.5, .5, 1, .3]])
    l.set_edgecolors([[.22, .48, 1, .3]])
    l.set_linewidths([1])
    ax4.spines['right'].set_color((.8, .8, .8))
    ax4.spines['top'].set_color((.8, .8, .8))

    # Adjust layout and show the plots
    plt.tight_layout()


if __name__ == "__main__":
    # Create a figure and subplots with a grid layout
    fig = plt.figure(figsize=(18, 10))
    gs = gridspec.GridSpec(2, 2, width_ratios=[1, 1])

    # Use FuncAnimation to update the plots every second without caching frame data
    ani = FuncAnimation(fig, update_data, interval=1000, cache_frame_data=False)

    plt.show()
