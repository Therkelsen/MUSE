# Muscular Signal Processing for Exoskeleton Control (MUSE)
Authored by Simon Chris Vinkel and Thomas Therkelsen

August 2023

## Purpose of the project
The purpose of the project is to solve various problems that affect the quality of life of people with disabilities that affect the muscles and mobility of their arms, namely Parkinson's patients.

This is done by implementing a device for non-invasive, high accuracy recognition of gestures for interactive control using electrical bioimpedance sensing.

An exoskeleton prototype has already been produced for further development. Our main task will be to create a sensor-motor setup connected to a digital signal processing (DSP) unit that can read signals from the arm muscles, extract the relevant signals, and process them. The DSP unit could potentially be made using deep learning technology to process the data in such a way that it can be used to assist arm movement and cancel out shaking in bad cases for affected patients.

## Project goals - project deliverables
The main deliverable of the project will be an AIO package exoskeleton robot arm. The arm uses muscle sensors and motors connected to a microcontroller / minicomputer, which will do the digital signal processing and control the motors. The complete product extends into the monitoring and assistance of finger movement as well, however that is beyond the scope of this project. 

## Success criteria - long-term expectations
The long term goal of the project is to align expectations with patients who suffer from relevant muscle-affecting disabilities and engineer an exoskeleton arm that can improve their quality of life by assisting arm mobility in their everyday lives.

The success of the project will be measured on how well the DSP unit along with a possible deep learning model will perform in terms of accurately detecting the intended gestures of the patient, while reliably disregarding unintended gestures as noise: shaking, locking and over movement.

Moreover, if time permits it, the unit will be implemented directly to the motor control logic as an early prototype and tested for comfort and usability in collaboration with the intended users.

## Specifications:
And accuracy rate of over 90% in terms of correctly distinguishing between desirable and undesirable gestures.
Under 0.5 seconds reaction time from detection to actualization of the motors to adjust and follow the desirable movements of the user.
Proper comfort in use based on direct feedback from users.

## Project organization - project owner, project manager, project participants, etc.
The project owners are professor Xiaofeng Xiong and assistant professor Zhuoqi Chen who will also act as counselors to make the project come into fruition.

Thomas Therkelsen and Simon Vinkel will act as project managers. The gathering of empiri, research, and building and testing the unit will be their responsibility, along with writing the final report.

## Target group
The intended recipients are people with disruptive or weak motor control of their arms, narrowing in on people with Parkinson's disease. It is the intent of the project to go into a collaboration with volunteers with this disease, to gather empiri for the model and to properly understand the challenges at hand. Moreover, to be able to properly test the final product.



# Setup MUSE project on Windows (The sensor doesn't work on Ubuntu)

1. Install [Visual Studio](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=Community&channel=Release&version=VS2022&source=VSLandingPage&cid=2414&workload=dotnetwebcloud&flight=FlipMacCodeCF;35d&installerFlight=FlipMacCodeCF;35d&passive=false#dotnet).
2. Clone the repo by running the following in your shell: `git clone git@github.com:Therkelsen/MUSE.git`
3. Open `../Github/MUSE/Code/PicometerReader.sln`
4. Make sure you're using the x86 compiler
5. Great success!

   ![](https://th.bing.com/th/id/R.96690b2065c29c6e848b69e15c94d0a0?rik=PbCJ86cV%2bS4Gow&riu=http%3a%2f%2fdailyurbanista.com%2fwp-content%2fuploads%2f2016%2f02%2fgreat-success-gif.gif&ehk=QL3L4jXfujCmot5FczjvzdLFwJmBX%2bFG5v2lYJJPkLE%3d&risl=&pid=ImgRaw&r=0)

# Setup Visualizer on Windows
(Assumes you have the repo cloned from the previous step)
1. Install [Python](https://www.python.org/downloads/)
2. Install requirements
   1. From `MUSE` run `$ pip install -r Code/Visualizer/requirements.txt`
3. Run the visualizer
   1. From `MUSE` run `$ py Code/Visualizer/visualizer.py`
   2. It updates the figure once every second, so if you run the MUSE program and gather new data, it will update the figure accordingly.