# Muscular Signal Processing for Exoskeleton Control (MUSE)

Authored by Simon Chris Vinkel and Thomas Therkelsen

Updated December 2023

# Introduction

This is the code stack for the MUSE bachelor's project written by Simon Chris Vinkel and Thomas Therkelsen. To read the full thesis, follow [this link](https://github.com/Therkelsen/MUSE/blob/main/Assets/MUSE___Bachelor_project.pdf).

The stack is not quite as polished as we would have liked, that may or may not change in the future, if we continue working on it.

# Prerequisites

1. You'll need a POW-EXO exoskeleton, refer to [this paper](https://github.com/Therkelsen/MUSE/blob/main/Assets/Learning-Based_Multifunctional_Elbow_Exoskeleton_Control.pdf) for more info.
2. Windows 10/11 PC, as the sensor device used does not run on Ubuntu.
3. Eliko Quadra device with EIM electrodes, check [this link](https://eliko.tech/quadra-impedance-spectroscopy/) for more info.
4. Integrated or USB webcam for kinematic angle tracker.

# Setup MUSE project

1. Install [Visual Studio](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=Community&channel=Release&version=VS2022&source=VSLandingPage&cid=2414&workload=dotnetwebcloud&flight=FlipMacCodeCF;35d&installerFlight=FlipMacCodeCF;35d&passive=false#dotnet)
2. Clone the repo by running the following in your shell: `git clone https://github.com/Therkelsen/MUSE.git`
3. Install drivers for Eliko device

   1. From `MUSE` run `Assets/Eliko/Drivers/QuadraUSBDriverInstaller_v1.1.EXE`
   2. From `MUSE` run `Assets/Eliko/Drivers/RunTime Installer v20/install.exe`

4. Connect the Eliko device with EIM electrodes
5. From `MUSE` open `Code/PicometerReader.sln`
6. Make sure you're using the x86 compiler when running or debugging, otherwise it won't build!
7. When you've run the program, create a throwaway sample (**S**, **K**, then **Y** and **Enter**) so the startup sequence of the Eliko device doesn't cause a mismatch in time. Now you're ready to record.

# Setup Visualizer and Angle Tracker

1. Install [Python 3.11.6](https://www.python.org/downloads/release/python-3116/)
2. Install requirements

   1. From `MUSE` run `$ pip install -r requirements.txt`

3. Run the visualizer

   1. From `MUSE` run `$ py Code/Visualizer/visualizer.py`
   2. It updates the figure once every second, so if you run the MUSE program and gather new data, it will update the figure accordingly.

4. Run the angle tracker

   1. From `MUSE` run `$ py Code/angle_tracker/angle_calculator.py`
   2. Once the program is running, press **S** to start recording data, **K** while recording to save, and **Q** to exit the program.

# Setup hotkeys to start and stop recording

1. Install [MacroRecorder](https://www.macrorecorder.com/download/)
2. Install [PhraseExpress](https://www.phraseexpress.com/download/)
3. Open **MacroRecorder**
   
   1. Open `start_recording.mrf` located in `Assets/Macros`
   2. Click **Send to PhraseExpress** in the toolbar
   3. Select **Hotkey** as your trigger in the dropdown, then configure a hotkey combination to start the macro. We used **Ctrl + Shift + F8**
   4. Repeat for `stop_recording.mrf`, for that we used **Ctrl + Shift + F9**
   5. Click **File** and **Save**
   6. You may close **PhraseExpress**, just make sure it's running in the background still so it can register the hotkey combinations.

# Record samples

1. Following **Experimental protocol.pdf** located in `Assets`, prepare for sample recording.
2. Once you have everything prepared, use the **start_recording** macro hotkey to start recording a sample, and the **stop_recording** macro hotkey to stop recording.
3. NOW you're fully ready to record! Great success!

   ![](https://th.bing.com/th/id/R.96690b2065c29c6e848b69e15c94d0a0?rik=PbCJ86cV%2bS4Gow&riu=http%3a%2f%2fdailyurbanista.com%2fwp-content%2fuploads%2f2016%2f02%2fgreat-success-gif.gif&ehk=QL3L4jXfujCmot5FczjvzdLFwJmBX%2bFG5v2lYJJPkLE%3d&risl=&pid=ImgRaw&r=0)