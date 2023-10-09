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
    modulus_raw_data = load_data("Code/Data/modulus_raw_output_data.csv", 0)
    modulus_filtered_data = load_data("Code/Data/modulus_filtered_output_data.csv", 3)
    modulus_processed_data = load_data("Code/Data/modulus_processed_output_data.csv", 0)
    
    phase_raw_data = load_data("Code/Data/phase_raw_output_data.csv", 0)
    phase_filtered_data = load_data("Code/Data/phase_filtered_output_data.csv", 3)
    phase_processed_data = load_data("Code/Data/phase_processed_output_data.csv", 0)

    plt.clf()
    
    # Create the 2D plot for modulus_raw_data
    num_rows, num_cols = modulus_raw_data.shape

    x = np.arange(1, num_cols + 1)
    y = np.arange(1, num_rows + 1)
    X, Y = np.meshgrid(x, y)
    
    ax1 = plt.subplot(gs[0, 0])
    modulus_raw_data_column = modulus_raw_data.iloc[:, 0]
    min_value = modulus_raw_data_column.min()
    mask = modulus_raw_data_column >= min_value
    l = ax1.fill_between(y[mask], min_value, modulus_raw_data_column[mask], color=[.84, .15, .29], alpha=.3, label='Raw Data')
    ax1.plot(y, modulus_raw_data_column, marker='', linestyle='-', color=[.84, .15, .29], linewidth=0.5)
    ax1.set_xlabel('Sample')
    ax1.set_ylabel('Impedance Modulus')
    ax1.set_title('Raw Sensor Data')
    ax1.grid(True)
    ax1.legend()
    ax1.set_xlim(1, num_rows)
    l.set_linewidths([0.1])
    ax1.spines['right'].set_color((.8, .8, .8))
    ax1.spines['top'].set_color((.8, .8, .8))

    # Create the 2D plot for modulus_filtered_data
    num_rows, num_cols = modulus_filtered_data.shape

    x = np.arange(1, num_cols + 1)
    y = np.arange(1, num_rows + 1)
    X, Y = np.meshgrid(x, y)
    
    ax2 = plt.subplot(gs[1, 0])
    modulus_filtered_data_column = modulus_filtered_data.iloc[:, 0]
    min_value = modulus_filtered_data_column.min()
    mask = modulus_filtered_data_column >= min_value
    l = ax2.fill_between(y[mask], min_value, modulus_filtered_data_column[mask], color=[.15, .28, .73], alpha=.3)
    ax2.plot(y, modulus_filtered_data_column, marker='', linestyle='-', color=[.15, .28, .73], label='Low-Pass Filtered Data', linewidth=0.5)
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
    num_rows, num_cols = modulus_processed_data.shape

    x = np.arange(1, num_cols + 1)
    y = np.arange(1, num_rows + 1)
    X, Y = np.meshgrid(x, y)
    
    ax3 = plt.subplot(gs[2, 0])
    modulus_processed_data_column = modulus_processed_data.iloc[:, 0]
    min_value = modulus_processed_data_column.min()
    mask = modulus_processed_data_column >= min_value
    l = ax3.fill_between(y[mask], min_value, modulus_processed_data_column[mask], color=[.15, .73, .28], alpha=.3)
    ax3.plot(y, modulus_processed_data_column, marker='', linestyle='-', color=[.15, .73, .28], label='Processed Data', linewidth=0.5)
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
    modulus_raw_fft_result = np.fft.fft(modulus_raw_data_column)
    modulus_raw_magnitude = np.abs(modulus_raw_fft_result)[5:]

    nyquist_frequency = 500
    modulus_raw_frequency_values = np.linspace(0, nyquist_frequency, len(modulus_raw_magnitude) // 2)

    ax4 = plt.subplot(gs[0, 1])
    ax4 = plt.plot(modulus_raw_frequency_values, modulus_raw_magnitude[:len(modulus_raw_magnitude) // 2])
    ax4 = plt.xlabel('Frequency (Hz)')
    ax4 = plt.ylabel('Amplitude')
    ax4 = plt.title('Magnitude Spectrum of FFT (Raw data)')
    ax4 = plt.grid(True)
    
    # FFT of filtered data
    modulus_filtered_fft_result = np.fft.fft(modulus_filtered_data_column)
    modulus_filtered_magnitude = np.abs(modulus_filtered_fft_result)[5:]

    modulus_filtered_frequency_values = np.linspace(0, nyquist_frequency, len(modulus_filtered_magnitude) // 2)

    ax5 = plt.subplot(gs[1, 1])
    ax5 = plt.plot(modulus_filtered_frequency_values, modulus_filtered_magnitude[:len(modulus_filtered_magnitude) // 2])
    ax5 = plt.xlabel('Frequency (Hz)')
    ax5 = plt.ylabel('Amplitude')
    ax5 = plt.title('Magnitude Spectrum of FFT (Filtered data)')
    ax5 = plt.grid(True)

    # FFT of processed data
    modulus_processed_fft_result = np.fft.fft(modulus_processed_data_column)
    modulus_processed_magnitude = np.abs(modulus_processed_fft_result)[5:]
    
    modulus_processed_frequency_values = np.linspace(0, nyquist_frequency, len(modulus_processed_magnitude) // 2)

    ax6 = plt.subplot(gs[2, 1])
    ax6 = plt.plot(modulus_processed_frequency_values, modulus_processed_magnitude[:len(modulus_processed_magnitude) // 2])
    ax6 = plt.xlabel('Frequency (Hz)')
    ax6 = plt.ylabel('Amplitude')
    ax6 = plt.title('Magnitude Spectrum of FFT (Processed data)')
    ax6 = plt.grid(True)
    
    # Create the 2D plot for phase_raw_data
    num_rows, num_cols = phase_raw_data.shape

    x = np.arange(1, num_cols + 1)
    y = np.arange(1, num_rows + 1)
    X, Y = np.meshgrid(x, y)
    
    ax7 = plt.subplot(gs[0, 2])
    phase_raw_data_column = phase_raw_data.iloc[:, 0]
    min_value = phase_raw_data_column.min()
    mask = phase_raw_data_column >= min_value
    l = ax7.fill_between(y[mask], min_value, phase_raw_data_column[mask], color=[.84, .15, .29], alpha=.3, label='Raw Data')
    ax7.plot(y, phase_raw_data_column, marker='', linestyle='-', color=[.84, .15, .29], linewidth=0.5)
    ax7.set_xlabel('Sample')
    ax7.set_ylabel('Impedance Modulus')
    ax7.set_title('Raw Sensor Data')
    ax7.grid(True)
    ax7.legend()
    ax7.set_xlim(1, num_rows)
    l.set_linewidths([0.1])
    ax7.spines['right'].set_color((.8, .8, .8))
    ax7.spines['top'].set_color((.8, .8, .8))

    # Create the 2D plot for phase_filtered_data
    num_rows, num_cols = phase_filtered_data.shape

    x = np.arange(1, num_cols + 1)
    y = np.arange(1, num_rows + 1)
    X, Y = np.meshgrid(x, y)
    
    ax8 = plt.subplot(gs[1, 2])
    phase_filtered_data_column = phase_filtered_data.iloc[:, 0]
    min_value = phase_filtered_data_column.min()
    mask = phase_filtered_data_column >= min_value
    l = ax8.fill_between(y[mask], min_value, phase_filtered_data_column[mask], color=[.15, .28, .73], alpha=.3)
    ax8.plot(y, phase_filtered_data_column, marker='', linestyle='-', color=[.15, .28, .73], label='Low-Pass Filtered Data', linewidth=0.5)
    ax8.set_xlabel('Sample')
    ax8.set_ylabel('Impedance Modulus')
    ax8.set_title('Filtered Sensor Data')
    ax8.grid(True)
    ax8.legend()
    ax8.set_xlim(1, num_rows)
    l.set_linewidths([0.1])
    ax8.spines['right'].set_color((.8, .8, .8))
    ax8.spines['top'].set_color((.8, .8, .8))
    
    # Create the 2D plot for processed_sensor_data
    num_rows, num_cols = phase_processed_data.shape

    x = np.arange(1, num_cols + 1)
    y = np.arange(1, num_rows + 1)
    X, Y = np.meshgrid(x, y)
    
    ax9 = plt.subplot(gs[2, 2])
    phase_processed_data_column = phase_processed_data.iloc[:, 0]
    min_value = phase_processed_data_column.min()
    mask = phase_processed_data_column >= min_value
    l = ax9.fill_between(y[mask], min_value, phase_processed_data_column[mask], color=[.15, .73, .28], alpha=.3)
    ax9.plot(y, phase_processed_data_column, marker='', linestyle='-', color=[.15, .73, .28], label='Processed Data', linewidth=0.5)
    ax9.set_xlabel('Sample')
    ax9.set_ylabel('Impedance Modulus')
    ax9.set_title('Processed Sensor Data')
    ax9.grid(True)
    ax9.legend()
    ax9.set_xlim(1, num_rows)
    l.set_linewidths([0.1])
    ax9.spines['right'].set_color((.8, .8, .8))
    ax9.spines['top'].set_color((.8, .8, .8))
    
    # FFT of raw data
    phase_raw_fft_result = np.fft.fft(phase_raw_data_column)
    phase_raw_magnitude = np.abs(phase_raw_fft_result)[5:]

    nyquist_frequency = 500
    phase_raw_frequency_values = np.linspace(0, nyquist_frequency, len(phase_raw_magnitude) // 2)

    ax10 = plt.subplot(gs[0, 3])
    ax10 = plt.plot(phase_raw_frequency_values, phase_raw_magnitude[:len(phase_raw_magnitude) // 2])
    ax10 = plt.xlabel('Frequency (Hz)')
    ax10 = plt.ylabel('Amplitude')
    ax10 = plt.title('Magnitude Spectrum of FFT (Raw data)')
    ax10 = plt.grid(True)
    
    # FFT of filtered data
    phase_filtered_fft_result = np.fft.fft(phase_filtered_data_column)
    phase_filtered_magnitude = np.abs(phase_filtered_fft_result)[5:]

    phase_filtered_frequency_values = np.linspace(0, nyquist_frequency, len(phase_filtered_magnitude) // 2)

    ax11 = plt.subplot(gs[1, 3])
    ax11 = plt.plot(phase_filtered_frequency_values, phase_filtered_magnitude[:len(phase_filtered_magnitude) // 2])
    ax11 = plt.xlabel('Frequency (Hz)')
    ax11 = plt.ylabel('Amplitude')
    ax11 = plt.title('Magnitude Spectrum of FFT (Filtered data)')
    ax11 = plt.grid(True)

    # FFT of processed data
    phase_processed_fft_result = np.fft.fft(phase_processed_data_column)
    phase_processed_magnitude = np.abs(phase_processed_fft_result)[5:]
    
    phase_processed_frequency_values = np.linspace(0, nyquist_frequency, len(phase_processed_magnitude) // 2)

    ax12 = plt.subplot(gs[2, 3])
    ax12 = plt.plot(phase_processed_frequency_values, phase_processed_magnitude[:len(phase_processed_magnitude) // 2])
    ax12 = plt.xlabel('Frequency (Hz)')
    ax12 = plt.ylabel('Amplitude')
    ax12 = plt.title('Magnitude Spectrum of FFT (Processed data)')
    ax12 = plt.grid(True)
    
    plt.tight_layout()


if __name__ == "__main__":
    """
    Main entry point of the script.

    Creates subplots for raw, filtered, and processed sensor data. 
    Uses FuncAnimation to update the plots every second.
    """
    fig = plt.figure(figsize=(18, 15))
    gs = gridspec.GridSpec(3, 4, height_ratios=[1, 1, 1])

    ani = FuncAnimation(fig, update_data, interval=1000, cache_frame_data=False)

    plt.show()