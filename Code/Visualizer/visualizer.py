import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.animation import FuncAnimation

def load_data(file_path, slice):
    """
    Load data from the given file path.

    Parameters:
        file_path (str): Path to the data file.
        slice (int): Index from which to slice the data.

    Returns:
        pandas.DataFrame: Loaded data as a DataFrame.
    """
    try:
        if (slice > 0):
            return pd.read_csv(file_path).iloc[slice:]
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except pd.errors.EmptyDataError:
        print(f"Error: File '{file_path}' is empty.")
        return None

def update_data(i):
    """
    Update the plots with new data in each iteration.

    Parameters:
        i (int): Current iteration number.

    Returns:
        None
    """
    raw_sensor_data = load_data("../Data/raw_sensor_data2.csv", 0)
    filtered_sensor_data = load_data("../Data/filtered_data2.csv", 3)
    processed_data = load_data("../Data/processed_data2.csv", 0)

    plt.clf()

    # Create the 2D plot for raw_sensor_data
    num_rows, num_cols = raw_sensor_data.shape

    x = np.arange(1, num_cols + 1)
    y = np.arange(1, num_rows + 1)
    X, Y = np.meshgrid(x, y)

    ax1 = plt.subplot(gs[0, 0])
    raw_data_column = raw_sensor_data.iloc[:, 9]
    min_value = raw_data_column.min()
    mask = raw_data_column >= min_value
    l = ax1.fill_between(y[mask], min_value, raw_data_column[mask], color=[.84, .15, .29], alpha=.3, label='Raw Data')
    ax1.plot(y, raw_data_column, marker='', linestyle='-', color=[.84, .15, .29], linewidth=0.5)
    ax1.set_xlabel('Sample')
    ax1.set_ylabel('Impedance Modulus')
    ax1.set_title('Raw Sensor Data')
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlim(1, num_rows)
    l.set_linewidths([0.1])
    ax1.spines['right'].set_color((.8, .8, .8))
    ax1.spines['top'].set_color((.8, .8, .8))

    # Create the 2D plot for filtered_sensor_data
    
    # Get the dimensions of your data
    num_rows, num_cols = filtered_sensor_data.shape

    x = np.arange(1, num_cols + 1)
    y = np.arange(1, num_rows + 1)
    X, Y = np.meshgrid(x, y)
    
    ax2 = plt.subplot(gs[1, 0])
    filtered_data_column = filtered_sensor_data.iloc[:, 9]
    min_value = filtered_data_column.min()
    mask = filtered_data_column >= min_value
    l = ax2.fill_between(y[mask], min_value, filtered_data_column[mask], color=[.15, .28, .73], alpha=.3)
    ax2.plot(y, filtered_data_column, marker='', linestyle='-', color=[.15, .28, .73], label='Low-Pass Filtered Data', linewidth=0.5)
    ax2.set_xlabel('Sample')
    ax2.set_ylabel('Impedance Modulus')
    ax2.set_title('Filtered Sensor Data')
    ax2.grid(True)
    ax2.legend()
    ax2.set_xlim(1, num_rows)
    l.set_linewidths([0.1])
    ax2.spines['right'].set_color((.8, .8, .8))
    ax2.spines['top'].set_color((.8, .8, .8))
    
    # Create the 2D plot for processed_sensor_data
    num_rows, num_cols = processed_data.shape

    x = np.arange(1, num_cols + 1)
    y = np.arange(1, num_rows + 1)
    X, Y = np.meshgrid(x, y)
    
    ax3 = plt.subplot(gs[2, 0])
    processed_data_column = processed_data.iloc[:, 9]
    min_value = processed_data_column.min()
    mask = processed_data_column >= min_value
    l = ax3.fill_between(y[mask], min_value, processed_data_column[mask], color=[.15, .73, .28], alpha=.3)
    ax3.plot(y, processed_data_column, marker='', linestyle='-', color=[.15, .73, .28], label='Processed Data', linewidth=0.5)
    ax3.set_xlabel('Sample')
    ax3.set_ylabel('Impedance Modulus')
    ax3.set_title('Processed Sensor Data')
    ax3.grid(True)
    ax3.legend()
    ax3.set_xlim(1, num_rows)
    l.set_linewidths([0.1])
    ax3.spines['right'].set_color((.8, .8, .8))
    ax3.spines['top'].set_color((.8, .8, .8))
    
    # FFT of raw data
    # Compute the FFT of the selected frequency column
    fft_result = np.fft.fft(selected_frequency)
    # Compute the magnitude of the FFT result (absolute values)
    magnitude = np.abs(fft_result)[5:]

    nyquist_frequency = 500
    raw_frequency_values = np.linspace(0, nyquist_frequency, len(raw_magnitude) // 2)

    ax4 = plt.subplot(gs[0, 1])
    ax4 = plt.plot(raw_frequency_values, raw_magnitude[:len(raw_magnitude) // 2])
    ax4 = plt.xlabel('Frequency (Hz)')
    ax4 = plt.ylabel('Amplitude')
    ax4 = plt.title('Magnitude Spectrum of FFT (Raw data)')
    ax4 = plt.grid(True)
    
    # FFT of filtered data
    # Compute the FFT of the selected frequency column
    fft_result = np.fft.fft(filtered_data_column)
    # Compute the magnitude of the FFT result (absolute values)
    magnitude = np.abs(fft_result)[5:]

    filtered_frequency_values = np.linspace(0, nyquist_frequency, len(filtered_magnitude) // 2)

    ax5 = plt.subplot(gs[1, 1])
    ax5 = plt.plot(filtered_frequency_values, filtered_magnitude[:len(filtered_magnitude) // 2])
    ax5 = plt.xlabel('Frequency (Hz)')
    ax5 = plt.ylabel('Amplitude')
    ax5 = plt.title('Magnitude Spectrum of FFT (Filtered data)')
    ax5 = plt.grid(True)

    # FFT of processed data
    # Compute the FFT of the selected frequency column
    fft_result = np.fft.fft(processed_data_column)
    # Compute the magnitude of the FFT result (absolute values)
    magnitude = np.abs(fft_result)[5:]

    # Compute the corresponding frequencies for the FFT result
    # Frequency values range from 0 to the Nyquist frequency (half of the sampling rate)
    # Assuming your data was sampled at 1 Hz, the Nyquist frequency would be 0.5 Hz
    nyquist_frequency = 500
    frequency_values = np.linspace(0, nyquist_frequency, len(magnitude) // 2)

    ax6 = plt.subplot(gs[2, 1])
    ax6 = plt.plot(processed_frequency_values, processed_magnitude[:len(processed_magnitude) // 2])
    ax6 = plt.xlabel('Frequency (Hz)')
    ax6 = plt.ylabel('Amplitude')
    ax6 = plt.title('Magnitude Spectrum of FFT (Processed data)')
    ax6 = plt.grid(True)

    # Adjust layout and show the plots
    plt.tight_layout()


if __name__ == "__main__":
    """
    Main entry point of the script.

    Creates subplots for raw, filtered, and processed sensor data. 
    Uses FuncAnimation to update the plots every second.
    """
    fig = plt.figure(figsize=(18, 15))
    gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1, 1])  # 3 rows, 2 columns

    ani = FuncAnimation(fig, update_data, interval=1000, cache_frame_data=False)

    plt.show()
