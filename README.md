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



# Setup Development environment on Windows

1. Install Visual Studio Code [Stable](https://code.visualstudio.com/download) or [Insiders](https://code.visualstudio.com/insiders/) (doesn't matter).
2. Install MinGW

    a. Download the  [latest installer](https://github.com/msys2/msys2-installer/releases/download/2023-05-26/msys2-x86_64-20230526.exe). (link is current, as of September 2023)
    
    b. Run the installer

    c. Use the default settings in the installer, but at the end ensure that the **Run MSYS2 now** box isn't checked and select **Finish**.

    d. After Installation is complete: Open MSYS2 terminal (pink icon).

    * Update the package database and base packages by running: `pacman -Syu && pacman -Su` and typing `Y` at the prompts that require it.

    e. Now switch over to MSYS2 MinGW 64-bit terminal (blue icon).

    * To install gcc/g++ and debugger for C and C++, by running: `pacman -S mingw-w64-x86_64-gcc && pacman -S mingw-w64-x86_64-gdb && pacman -S --needed base-devel mingw-w64-ucrt-x86_64-toolchain`

    f. Enter **Y** when prompted and accept the default number of packages in the toolchain group by pressing **Enter**.

    g. Add the path to your MinGW-w64 `bin` folder to the Windows `PATH` environment variable by using the following steps:
    
    * In the Windows search bar, type **Settings** to open your Windows Settings.
    * Search for **Edit environment variables for your account**.
    * In your **User variables**, select the `Path` variable and then select **Edit**.
    * Select **New** and add the MinGW-w64 destination folder you recorded during the installation process to the list. If you used the default settings above, then this will be the path: `C:\msys64\ucrt64\bin`.
    * Select **OK** to save the updated **PATH**. You will need to reopen any console windows for the new **PATH** location to be available.

    h. Check your MinGW installation

    * To check that your MinGW-w64 tools are correctly installed and available, open a new Command Prompt and type:

            gcc --version
            g++ --version
            gdb --version

3. Install CMake
   
   a. Get the latest precompiled windows binaries from the [downloads page](https://cmake.org/download/)
   
   b. Run the installer and make sure to keep the **Add to PATH** option ticked.

4. Install LLVM for clangd formatting
   
   a. Get the latest version of LLVM for windows on the GitHub [release page](https://github.com/llvm/llvm-project/releases).

   b. Don't get the pre-release. The file will be called something like **LLVM-xx.xx.x-win64.exe** 

   c. Simply run the installer. Make sure the **Add to PATH** option is ticked.


4. Install vscode extensions
   
   a. [clangd](https://marketplace.visualstudio.com/items?itemName=llvm-vs-code-extensions.vscode-clangd)

   b. [CMake Tools](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cmake-tools)

   c. [CMake](https://marketplace.visualstudio.com/items?itemName=twxs.cmake)

   d. [C/C++ extension pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools-extension-pack)

5. Restart your vscode

Now your vscode it setup to build and run the C++ program.

From `./MUSE/` you should be able to run the `CMake: Build Target` and `CMake: Run Without Debugging` commands. On my machine, the keyboard shortcuts for these defaulted to `F7` and `Shift + F5`, respectively.