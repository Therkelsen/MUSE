import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import gridspec


def load_data(file_path, col_idx):
    """
    Load data from the given file path.

    Parameters:
        file_path (str): Path to the data file.
        col_idx (int): Index to extract.

    Returns:
        pandas.DataFrame: Loaded data as a DataFrame.
    """
    try:
        if (col_idx is not None):
            return pd.read_csv(file_path, usecols=[col_idx])
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except pd.errors.EmptyDataError:
        print(f"Error: File '{file_path}' is empty.")
        return None


def remove_character(data, character):
    """
    Remove the given character from the data.

    Parameters:
        data (pandas.DataFrame): Data to remove the character from.
        character (str): Character to remove.

    Returns:
        pandas.DataFrame: Data with the character removed.
    """
    # Apply the replacement to all rows except the first (header) row
    data = data.apply(lambda x: x.str.replace(character, ''), axis=1)

    return data


def update_data(i):
    """
    Update the plots with new data in each iteration.

    Parameters:
        i (int): Current iteration number.

    Returns:
        None
    """
    # modulus_raw_data = load_data("Code/Data/raw_output_data.csv", 1)
    modulus_filtered_data = load_data("Code/GRU_network/MoCap/dynamic/85_FRMJ_6kg_reg/filtered_output_data.csv", 1)
    modulus_processed_data = load_data("Code/GRU_network/MoCap/dynamic/85_FRMJ_6kg_reg/processed_output_data.csv", 1)
    angles_raw_data = remove_character(remove_character(load_data("Code/GRU_network/MoCap/dynamic/85_FRMJ_6kg_reg/elbow_angles.csv", 0), '['), ']')

    # phase_raw_data = load_data("Code/Data/raw_output_data.csv", 2)
    phase_processed_data = load_data("Code/GRU_network/MoCap/dynamic/85_FRMJ_6kg_reg/processed_output_data.csv", 2)
    phase_filtered_data = load_data("Code/GRU_network/MoCap/dynamic/85_FRMJ_6kg_reg/filtered_output_data.csv", 2)

    plt.clf()

    # Create the 2D plot for modulus_filtered_data
    num_rows, num_cols = modulus_filtered_data.shape

    x = np.arange(1, num_cols + 1)
    y = np.arange(1, num_rows + 1)
    X, Y = np.meshgrid(x, y)

    ax1 = plt.subplot(gs[0, 0])
    modulus_filtered_data_column = modulus_filtered_data.iloc[:, 0]
    ax1.plot(y, modulus_filtered_data_column, marker='', linestyle='-', color=[.15, .28, .73], label='Low-Pass Filtered Data', linewidth=0.5)
    ax1.set_xlabel('Time ms')
    ax1.set_ylabel('Modulus of impedance |Ω|')
    ax1.set_title('Filtered bioelectrical impedance modulus')
    ax1.grid(True)
    ax1.set_xlim(1, num_rows)
    ax1.spines['right'].set_color((.8, .8, .8))
    ax1.spines['top'].set_color((.8, .8, .8))

    # Create the 2D plot for processed_sensor_data
    num_rows, num_cols = modulus_processed_data.shape

    x = np.arange(1, num_cols + 1)
    y = np.arange(1, num_rows + 1)
    X, Y = np.meshgrid(x, y)

    ax2 = plt.subplot(gs[1, 0])
    modulus_processed_data_column = modulus_processed_data.iloc[:, 0]
    min_value = modulus_processed_data_column.min()
    mask = modulus_processed_data_column >= min_value
    l = ax2.fill_between(y[mask], min_value, modulus_processed_data_column[mask], color=[.15, .73, .28], alpha=.3)
    ax2.plot(y, modulus_processed_data_column, marker='', linestyle='-', color=[.15, .73, .28], label='Processed Data', linewidth=0.5)
    ax2.set_xlabel('Time ms')
    ax2.set_ylabel('Modulus of impedance |Ω|')
    ax2.set_title('Processed bioelectrical impedance modulus')
    ax2.grid(True)
    ax2.set_xlim(1, num_rows)
    l.set_linewidths([0.1])
    ax2.spines['right'].set_color((.8, .8, .8))
    ax2.spines['top'].set_color((.8, .8, .8))

    # Create the 2D plot for angles_raw_data
    num_rows, num_cols = angles_raw_data.shape
    x = np.arange(1, num_rows + 1)
    y = np.arange(1, num_cols + 1)
    X, Y = np.meshgrid(x, y)

    ax3 = plt.subplot(gs[2, 0])
    angles_raw_data_column = angles_raw_data.iloc[:, 0]
    angles_raw_data_column = pd.to_numeric(angles_raw_data_column, errors='coerce')
    # Transform angles to make 180 degrees become 0 degrees
    angles_raw_data_column = 180 - angles_raw_data_column
    min_value = angles_raw_data_column.min()
    mask = angles_raw_data_column >= min_value
    l = ax3.fill_between(x[mask], min_value, angles_raw_data_column[mask], color=[.84, .15, .29], alpha=.3)
    # Plot against time values on the x-axis
    ax3.plot(x, angles_raw_data_column, marker='', linestyle='-', color=[.84, .15, .29], linewidth=0.5, label='Raw Data')
    ax3.set_xlabel('Sample')
    ax3.set_ylabel('Angle θ')
    ax3.set_title('Raw elbow angles')
    ax3.grid(True)
    ax3.set_xlim(1, num_rows)
    ax3.spines['right'].set_color((.8, .8, .8))
    ax3.spines['top'].set_color((.8, .8, .8))


    # FFT of filtered data
    nyquist_frequency = 500

    modulus_filtered_fft_result = np.fft.fft(modulus_filtered_data_column)
    modulus_filtered_magnitude = np.abs(modulus_filtered_fft_result)[5:]

    modulus_filtered_frequency_values = np.linspace(0, nyquist_frequency, len(modulus_filtered_magnitude) // 2)

    ax4 = plt.subplot(gs[0, 1])
    ax4 = plt.plot(modulus_filtered_frequency_values, modulus_filtered_magnitude[:len(modulus_filtered_magnitude) // 2])
    ax4 = plt.xlabel('Frequency Hz')
    ax4 = plt.ylabel('Magnitude')
    ax4 = plt.title('Magnitude Spectrum for FFT of filtered data')
    ax4 = plt.grid(True)

    # FFT of processed data
    modulus_processed_fft_result = np.fft.fft(modulus_processed_data_column)
    modulus_processed_magnitude = np.abs(modulus_processed_fft_result)[5:]

    modulus_processed_frequency_values = np.linspace(0, nyquist_frequency, len(modulus_processed_magnitude) // 2)

    ax5 = plt.subplot(gs[1, 1])
    ax5 = plt.plot(modulus_processed_frequency_values, modulus_processed_magnitude[:len(modulus_processed_magnitude) // 2])
    ax5 = plt.xlabel('Frequency Hz')
    ax5 = plt.ylabel('Magnitude')
    ax5 = plt.title('Magnitude Spectrum for FFT of processed data')
    ax5 = plt.grid(True)

    # FFT of angle data
    angles_raw_data_column_fft_result = np.fft.fft(angles_raw_data_column)
    angles_raw_data_column_magnitude = np.abs(angles_raw_data_column_fft_result)[5:]

    angles_raw_data_column_frequency_values = np.linspace(0, nyquist_frequency, len(angles_raw_data_column_magnitude) // 2)

    ax6 = plt.subplot(gs[2, 1])
    ax6 = plt.plot(angles_raw_data_column_frequency_values, angles_raw_data_column_magnitude[:len(angles_raw_data_column_magnitude) // 2])
    ax6 = plt.xlabel('Frequency Hz')
    ax6 = plt.ylabel('Magnitude')
    ax6 = plt.title('Magnitude Spectrum for FFT of angle data')
    ax6 = plt.grid(True)

    # Create the 2D plot for phase_filtered_data
    num_rows, num_cols = phase_filtered_data.shape

    x = np.arange(1, num_cols + 1)
    y = np.arange(1, num_rows + 1)
    X, Y = np.meshgrid(x, y)

    ax7 = plt.subplot(gs[0, 2])
    phase_filtered_data_column = phase_filtered_data.iloc[:, 0]
    ax7.plot(y, phase_filtered_data_column, marker='', linestyle='-', color=[.15, .28, .73], label='Low-Pass Filtered Data', linewidth=0.5)
    ax7.set_xlabel('Time ms')
    ax7.set_ylabel('Phase of impedance φ(Ω)')
    ax7.set_title('Filtered bioelectrical impedance phase')
    ax7.grid(True)
    ax7.set_xlim(1, num_rows)
    ax7.spines['right'].set_color((.8, .8, .8))
    ax7.spines['top'].set_color((.8, .8, .8))

    # Create the 2D plot for processed_sensor_data
    num_rows, num_cols = phase_processed_data.shape

    x = np.arange(1, num_cols + 1)
    y = np.arange(1, num_rows + 1)
    X, Y = np.meshgrid(x, y)

    ax8 = plt.subplot(gs[1, 2])
    phase_processed_data_column = phase_processed_data.iloc[:, 0]
    min_value = phase_processed_data_column.min()
    mask = phase_processed_data_column >= min_value
    l = ax8.fill_between(y[mask], min_value, phase_processed_data_column[mask], color=[.15, .73, .28], alpha=.3)
    ax8.plot(y, phase_processed_data_column, marker='', linestyle='-', color=[.15, .73, .28], label='Processed Data', linewidth=0.5)
    ax8.set_xlabel('Time ms')
    ax8.set_ylabel('Phase of impedance φ(Ω)')
    ax8.set_title('Processed bioelectrical impedance phase')
    ax8.grid(True)
    ax8.set_xlim(1, num_rows)
    l.set_linewidths([0.1])
    ax8.spines['right'].set_color((.8, .8, .8))
    ax8.spines['top'].set_color((.8, .8, .8))


    # FFT of filtered data
    nyquist_frequency = 500

    phase_filtered_fft_result = np.fft.fft(phase_filtered_data_column)
    phase_filtered_magnitude = np.abs(phase_filtered_fft_result)[5:]

    phase_filtered_frequency_values = np.linspace(0, nyquist_frequency, len(phase_filtered_magnitude) // 2)

    ax9 = plt.subplot(gs[0, 3])
    ax9 = plt.plot(phase_filtered_frequency_values, phase_filtered_magnitude[:len(phase_filtered_magnitude) // 2])
    ax9 = plt.xlabel('Frequency Hz')
    ax9 = plt.ylabel('Magnitude')
    ax9 = plt.title('Magnitude Spectrum for FFT of filtered data')
    ax9 = plt.grid(True)

    # FFT of processed data
    phase_processed_fft_result = np.fft.fft(phase_processed_data_column)
    phase_processed_magnitude = np.abs(phase_processed_fft_result)[5:]

    phase_processed_frequency_values = np.linspace(0, nyquist_frequency, len(phase_processed_magnitude) // 2)

    ax10 = plt.subplot(gs[1, 3])
    ax10 = plt.plot(phase_processed_frequency_values, phase_processed_magnitude[:len(phase_processed_magnitude) // 2])
    ax10 = plt.xlabel('Frequency Hz')
    ax10 = plt.ylabel('Magnitude')
    ax10 = plt.title('Magnitude Spectrum for FFT of processed data')
    ax10 = plt.grid(True)

    plt.tight_layout()


def on_key_press(event):
    if event.key == 'u':
        update_data(0)  # Call the update_data function when the 'u' key is pressed
        plt.draw()  # Redraw the plot after updating the data


if __name__ == "__main__":
    fig = plt.figure(figsize=(18, 15))
    gs = gridspec.GridSpec(3, 4, height_ratios=[1, 1, 1])

    # Connect the key press event to the on_key_press function
    fig.canvas.mpl_connect('key_press_event', on_key_press)

    update_data(0)  # Call the update_data function initially

    plt.tight_layout()
    plt.show()
