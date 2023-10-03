import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.animation import FuncAnimation


def update_data(i):
    # Load your data in each iteration (update)
    raw_sensor_data = pd.read_csv("Code/Data/raw_sensor_data.csv")
    filtered_sensor_data = pd.read_csv("Code/Data/filtered_data.csv").iloc[3:]
    processed_data = pd.read_csv("Code/Data/processed_data.csv")

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
    l = ax2.fill_between(y[mask], min_value, filtered_data_column[mask], color=[.15, .28, .73], alpha=.3, label='Frequency 10')
    ax2.plot(y, filtered_data_column, marker='', linestyle='-', color=[.15, .28, .73], label='Filtered Data', linewidth=0.5)
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
    
    # Create the 2D plot for processed_sensor_data
    
    # Get the dimensions of your data
    num_rows, num_cols = processed_data.shape

    # Create a meshgrid for the x and y values
    x = np.arange(1, num_cols + 1)  # x-axis values (freq_1 to freq_15)
    y = np.arange(1, num_rows + 1)  # y-axis values (four sets of data)
    X, Y = np.meshgrid(x, y)
    
    ax3 = plt.subplot(gs[2, 0])  # 2D plot in the bottom row
    processed_data_column = processed_data.iloc[:, 9]  # Replace with the appropriate column name
    min_value = processed_data_column.min()
    mask = processed_data_column >= min_value
    l = ax3.fill_between(y[mask], min_value, processed_data_column[mask], color=[.15, .73, .28], alpha=.3, label='Frequency 10')
    ax3.plot(y, processed_data_column, marker='', linestyle='-', color=[.15, .73, .28], label='Filtered Data', linewidth=0.5)
    ax3.set_xlabel('Data Set')
    ax3.set_ylabel('Amplitude')
    ax3.set_title('2D Plot of Processed Sensor Data from Frequency 10')
    ax3.grid(True)
    ax3.legend()
    ax3.set_xlim(1, num_rows)
    # l.set_facecolors([[.5, .5, 1, .3]])
    # l.set_edgecolors([[.22, .48, 1, .3]])
    l.set_linewidths([0.1])
    ax3.spines['right'].set_color((.8, .8, .8))
    ax3.spines['top'].set_color((.8, .8, .8))
    
    # FFT of raw data
    # Compute the FFT of the selected frequency column
    raw_fft_result = np.fft.fft(selected_frequency)
    # Compute the magnitude of the FFT result (absolute values)
    raw_magnitude = np.abs(raw_fft_result)[5:]

    # Compute the corresponding frequencies for the FFT result
    # Frequency values range from 0 to the Nyquist frequency (half of the sampling rate)
    # Assuming your data was sampled at 1 Hz, the Nyquist frequency would be 0.5 Hz
    nyquist_frequency = 500
    raw_frequency_values = np.linspace(0, nyquist_frequency, len(raw_magnitude) // 2)

    # Plot the FFT
    ax4 = plt.subplot(gs[0, 1])
    ax4 = plt.plot(raw_frequency_values, raw_magnitude[:len(raw_magnitude) // 2])
    ax4 = plt.xlabel('Frequency (Hz)')
    ax4 = plt.ylabel('Amplitude')
    ax4 = plt.title('Magnitude Spectrum of FFT (Raw data)')
    ax4 = plt.grid(True)
    
    # FFT of filtered data
    # Compute the FFT of the selected frequency column
    filtered_fft_result = np.fft.fft(filtered_data_column)
    # Compute the magnitude of the FFT result (absolute values)
    filtered_magnitude = np.abs(filtered_fft_result)[5:]

    filtered_frequency_values = np.linspace(0, nyquist_frequency, len(filtered_magnitude) // 2)

    # Plot the FFT
    ax5 = plt.subplot(gs[1, 1])
    ax5 = plt.plot(filtered_frequency_values, filtered_magnitude[:len(filtered_magnitude) // 2])
    ax5 = plt.xlabel('Frequency (Hz)')
    ax5 = plt.ylabel('Amplitude')
    ax5 = plt.title('Magnitude Spectrum of FFT (Filtered data)')
    ax5 = plt.grid(True)

    # FFT of processed data
    # Compute the FFT of the selected frequency column
    processed_fft_result = np.fft.fft(processed_data_column)
    # Compute the magnitude of the FFT result (absolute values)
    processed_magnitude = np.abs(processed_fft_result)[5:]
    
    processed_frequency_values = np.linspace(0, nyquist_frequency, len(processed_magnitude) // 2)

    # Plot the FFT
    ax6 = plt.subplot(gs[2, 1])
    ax6 = plt.plot(processed_frequency_values, processed_magnitude[:len(processed_magnitude) // 2])
    ax6 = plt.xlabel('Frequency (Hz)')
    ax6 = plt.ylabel('Amplitude')
    ax6 = plt.title('Magnitude Spectrum of FFT (Processed data)')
    ax6 = plt.grid(True)
    
    # Lower frequencies of IFFT of raw data
    # Compute the FFT of the selected frequency column
    raw_ifft_result = np.fft.ifft(raw_fft_result[:len(raw_fft_result) // 2])

    frequency_values = np.linspace(0, nyquist_frequency, len(raw_ifft_result) // 2)

    # Plot the FFT
    ax7 = plt.subplot(gs[0, 2])
    ax7 = plt.plot(frequency_values, raw_ifft_result[:len(raw_ifft_result) // 2])
    ax7 = plt.xlabel('Frequency (Hz)')
    ax7 = plt.ylabel('Amplitude')
    ax7 = plt.title('IFFT (Raw data)')
    ax7 = plt.grid(True)

    # Adjust layout and show the plots
    plt.tight_layout()


if __name__ == "__main__":
    # Create a figure and subplots with a grid layout
    fig = plt.figure(figsize=(18, 15))
    gs = gridspec.GridSpec(3, 3, height_ratios=[1, 1, 1])  # 3 rows, 2 columns

    # Use FuncAnimation to update the plots every second without caching frame data
    ani = FuncAnimation(fig, update_data, interval=1000, cache_frame_data=False)

    plt.show()
