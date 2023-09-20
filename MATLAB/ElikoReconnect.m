function ElikoReconnect()
    try
        PicometerControl('Disconnect');
    catch exception

    end

    PicometerControl('Connect');
    PicometerControl('SetSamplingDivider', 1);
    PicometerControl('SetCompensation', 'Off', 'Off');
    PicometerControl('SetExcitationLevel', 90);
    PicometerControl('SetInputGain', '1x', '2x');
end