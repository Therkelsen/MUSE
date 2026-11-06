# Muscular Signal Processing for Exoskeleton Control (MUSE)

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![C++](https://img.shields.io/badge/C%2B%2B-MSVC%20x86-00599C?logo=c%2B%2B&logoColor=white)](https://visualstudio.microsoft.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-009688?logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![Weights & Biases](https://img.shields.io/badge/Weights_%26_Biases-FFBE00?logo=weightsandbiases&logoColor=black)](https://wandb.ai/)

## Overview
This repository contains the software stack for the MUSE project, a Human-Machine Interface (HMI) designed for the POW-EXO exoskeleton. The system processes Electrical Impedance Myography (EIM) signals to predict user intent, enabling dynamic switching between assist- and resist-as-needed exoskeleton control modes. 

The pipeline handles hardware interfacing, real-time digital signal processing, computer vision-based kinematic tracking, and time-series forecasting using Gated Recurrent Unit (GRU) neural networks.

## Research Publication
The bachelor project report can be found here:
* [Vinkel, S. C., & Therkelsen, T. (2023). **MUSE - Muscular Signal Processing for Exoskeleton Control**](https://www.researchgate.net/publication/395586057_MUSE_-_Muscular_Signal_Processing_for_Exoskeleton_Control)

## System Architecture

* **Hardware Interfacing (C++)**: Interfaces with the Eliko Quadra Picometer to capture multi-frequency bioimpedance data. Handles memory management and direct device communication via DLLs.
* **Digital Signal Processing (C++)**: Implements custom FIR (Finite Impulse Response) filters and moving average algorithms to clean raw EIM modulus and phase data in real-time.
* **Kinematic Tracking (Python)**: Utilizes OpenCV and Google MediaPipe (`angle_calculator.py`) to extract positional landmarks from a webcam feed, calculating real-time elbow joint angles to serve as ground-truth labels for model training.
* **Deep Learning Pipeline (Python)**: A TensorFlow/Keras stack built around a Bidirectional GRU architecture. Processes multivariate time-series data to predict joint angles and payload mass. Integrates with Weights & Biases (`wandb`) for automated hyperparameter optimization (Bayesian/Random sweeps).
* **Data Visualization (Python)**: A real-time monitoring suite (`visualizer.py`) using Matplotlib to display raw/filtered impedance signals, kinematic angles, and Fast Fourier Transform (FFT) magnitude spectrums.

## Prerequisites

**Hardware:**
* POW-EXO exoskeleton
* Eliko Quadra device with EIM electrodes
* Webcam (USB or Integrated)
* Windows 10/11 (Required for Eliko Quadra drivers)

**Software:**
* Python 3.11.6
* Visual Studio (with x86 C++ build tools)
* MacroRecorder & PhraseExpress (Optional: for automated experimental protocol scripting)

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Therkelsen/MUSE.git
   cd MUSE
   ```

2. **Install Hardware Drivers:**
   * Execute `Assets/Eliko/Drivers/QuadraUSBDriverInstaller_v1.1.EXE`
   * Execute `Assets/Eliko/Drivers/RunTime Installer v20/install.exe`

3. **Configure Python Environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Compile C++ Data Reader:**
   * Open `Code/PicometerReader.sln` in Visual Studio.
   * **Critical:** Set the build configuration to **x86** (the Eliko DLLs will not link correctly under x64).
   * Build the solution.

## Usage Pipeline

### 1. Data Collection
1. Connect the Eliko Quadra device and attach EIM electrodes to the subject.
2. Run the compiled C++ `PicometerReader` executable. Follow the CLI prompts to initialize a throwaway sample (press `s`, `k`, then `y`) to synchronize hardware timers.
3. Launch the kinematic tracker:
   ```bash
   python Code/angle_tracker/angle_calculator.py
   ```
4. Press `s` in the Python tracker and begin the experimental protocol. Press `k` to save the CSV output and `q` to exit.

### 2. Visualization
To monitor the signal quality, filtering efficiency, and FFT spectrums during or after collection:
```bash
python Code/Visualizer/visualizer.py
```

### 3. Model Training & Tuning
The machine learning pipeline is contained within `Code/GRU_network/network.ipynb` (and `implementation.py`).
* Data preprocessing includes synchronization of EIM timestamps with OpenCV frame timestamps, interpolation, and `MinMaxScaler` normalization.
* Hyperparameter sweeps are configured via the `sweep_config` dictionary for `wandb` integration.
* Execute the notebook cells sequentially to train the Bidirectional GRU model and evaluate prediction accuracy against the test holdout set.

## Documentation & Resources
* [MUSE Bachelor Thesis Document](https://github.com/Therkelsen/MUSE/blob/main/Assets/MUSE___Bachelor_project.pdf)
* [POW-EXO Exoskeleton Reference Paper](https://github.com/Therkelsen/MUSE/blob/main/Assets/Learning-Based_Multifunctional_Elbow_Exoskeleton_Control.pdf)
* [Eliko Quadra Impedance Spectroscopy](https://eliko.tech/quadra-impedance-spectroscopy/)