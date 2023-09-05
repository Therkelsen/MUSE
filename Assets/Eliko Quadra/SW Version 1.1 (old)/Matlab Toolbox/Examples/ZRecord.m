%
%
%   For QUADRA(TM) Impedance Data Acquisition Toolbox v1.0
%
%   This is Matlab demo script that calls Quadra Picometer device control
%   toolbox to measure and record impedance spectra's to workspace variable.
%
%   IMPORTANT:
%   It is required that this script and PicometerControl.mexwXX files 
%	are located at the same workspace folder.
%
%   For 64-Bit Matlab copy PicometerControl.mexw64 from
%   \x64 folder.
%
%

%   Before sending 'Connect' command check if the device is connected to
%   USB port and the drivers are installed. If connection to the device USB
%   is established then device serial and status data is printed out.
PicometerControl('Connect');

%   Initialize device with default settings by sending the commands:
%   'SetSamplingDivider' - On value '1' device is configured to 
%       measure impedance at these frequencies: 1000.00Hz, 2000.00Hz,
%       3000.00Hz, 7000.00Hz, 11000.00Hz, 17000.00Hz, 23000.00Hz,
%       31000.00Hz, 43000.00Hz, 61000.00Hz, 89000.00Hz, 127000.00Hz, 
%       179000.00Hz, 251000.00Hz, 349000.00Hz.
%   'SetCompensation' - Parameter 2. 'Off' the input impedance compensation
%       calculations are disabled. Parameter 3. 'Off' compensation values
%       are not measured. On impedance spectra calculations the default
%       shunt values are used - default shunt complex values for all 15
%       frequency are: 1000 + 0i; 1000 + 0i; 1000 + 0i; 1000 + 0i; 1000 +
%       0i; 1000 + 0i; 1000 + 0i; 1000 + 0i; 1000 + 0i; 1000 + 0i; 1000 +
%       0i; 1000 + 0i; 1000 + 0i; 1000 + 0i; 1000 + 0i.
%    'SetExcitationLevel' - Step value 90 sets the excitation level to
%       ~2.52Vp-p.
%    'SetInputGain' - Parameters of 2. and 3. '1x' sets the input voltage
%       and current channels gains to one.
%
PicometerControl('SetSamplingDivider', 1);
PicometerControl('SetCompensation', 'Off', 'Off');
PicometerControl('SetExcitationLevel', 90);
PicometerControl('SetInputGain', '1x', '1x');

%   To get current device configuration data the 'GetConfData' command
%   is sent to record frequencies count, bin values, shunt impedance values
%   and compensation impedance values to workspace variable as structure.
%   These shunt impedance values 'ShuntComplexValues' and bin values
%   'FrequencyBins' are used during impedance calculations in the device.
DevConf = PicometerControl('GetConfData');

%   To get impedance spectra frequency values use 'FrequencyBins' values 
%   and current sampling rate divider value of 1.
Frequency = (uint32(DevConf.FrequencyBins) .* 1000) ./ 1;

%   'Start' command sets the device to active measurement mode during which
%   the toolbox thread continuously receives the data to internal buffer. At
%   sampling rate divider of one 100 impedance spectra's can be buffered by
%   toolbox application. To avoid data loss caused by buffer overflow the
%   user script must be able to send command 'GetData' with parameter 2. set
%   to 100 within the period of 100ms.
PicometerControl('Start');

%   Prepare empty workspace variables where the impedance data is recorded
ZSpectraCount = uint32.empty(0);
ZModule = single.empty(0);
ZPhase = single.empty(0);

%   Start data acquisition loop to collect 10s of impedance data.
%   Impedance acquisition period is 1ms, collect 100ms 100 times -> 10s
for n = 1 : 100

    %   In this loop the 'GetData' command is sent with argument 2. set to
    %   100 to collect 100 impedance spectra's before toolbox call returns.
    %   While the number of impedance spectra's are collected this loop is
    %   blocked by 'PicometerControl' call.
	Data = PicometerControl('GetData', 100);
    
    %   Copy and append new data
    ZSpectraCount = vertcat(ZSpectraCount, Data.MeasurementCycleCount);
    ZModule = vertcat(ZModule, Data.ImpedanceModule);
    ZPhase = vertcat(ZPhase, Data.ImpedancePhase);

end

%   'Stop' command is send to switch device to idle mode, because data
%   acqusition loop has finished and no new impedance data is required.
PicometerControl('Stop');

%   To release USB resources and internal buffer resources send
%   'Disconnect' command.
PicometerControl('Disconnect');

