%
%
%   This is example Matlab GUI that can continuesly receive impedance data
%   and plot it on the GUI. This GUI also includes additional controls to
%   adjust excitation and input levels and to update device shunt values
%   from the analog front end. This example also demonstrates how to adjust
%   'GetData' command buffer size according to selected samplingrate divider
%   value.
%
%
%
%



function varargout = ZReader(varargin)
% ZREADER M-file for ZReader.fig
%      ZREADER, by itself, creates a new ZREADER or raises the existing
%      singleton*.
%
%      H = ZREADER returns the handle to a new ZREADER or the handle to
%      the existing singleton*.
%
%      ZREADER('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in ZREADER.M with the given input arguments.
%
%      ZREADER('Property','Value',...) creates a new ZREADER or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before ZReader_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to ZReader_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help ZReader

% Last Modified by GUIDE v2.5 01-Mar-2016 16:29:19

    % Begin initialization code - DO NOT EDIT
    gui_Singleton = 1;
    gui_State = struct('gui_Name',       mfilename, ...
                       'gui_Singleton',  gui_Singleton, ...
                       'gui_OpeningFcn', @ZReader_OpeningFcn, ...
                       'gui_OutputFcn',  @ZReader_OutputFcn, ...
                       'gui_LayoutFcn',  [] , ...
                       'gui_Callback',   []);
    if nargin && ischar(varargin{1})
        gui_State.gui_Callback = str2func(varargin{1});
    end

    if nargout
        [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
    else
        gui_mainfcn(gui_State, varargin{:});
    end


    % End initialization code - DO NOT EDIT

    global Count;
    Count = 1;

    global PrevCount;
    PrevCount = 0;
    
    global ZData;
    global Frequencies;
    


end

% --- Executes just before ZReader is made visible.
function ZReader_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to ZReader (see VARARGIN)

    global Frequencies;

    global Divider;
    Divider = 1;
    
    PicometerControl('Connect')
    
    % Calculate frequency values from bins array
    DevConf = PicometerControl('GetConfData');
    Frequencies = transpose((double(DevConf.FrequencyBins) .* 1000) ./ 1);
    
    % Choose default command line output for ZReader
    handles.output = hObject;

    % Update handles structure
    guidata(hObject, handles);
end

% UIWAIT makes ZReader wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = ZReader_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

    % Get default command line output from handles structure
    varargout{1} = handles.output;
end

% --- Executes on button press in StartStop.
function StartStop_Callback(hObject, eventdata, handles)
% hObject    handle to StartStop (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

    global PrevCount;


    button_state = get(hObject,'Value');
    if button_state == get(hObject,'Max')
        % toggle button is pressed
        PicometerControl('Start');
        set(handles.StartStop, 'String', 'STOP');

        PrevCount = 0;
        
        set(handles.Divider,'Enable','off');
        
        % start with loop where received data is processed continuesly
        while( get(handles.StartStop, 'value') );

            UpdateData(hObject, eventdata, handles)
            drawnow; %force event queue update
            
        end

    elseif button_state == get(hObject,'Min')
        % toggle button is not pressed
        PicometerControl('Stop');
        %stop(handles.timer);
        set(handles.StartStop, 'String', 'START');
        
        set(handles.Divider,'Enable','on');

    end
end


% --- Executes when user attempts to close figure1.
function figure1_CloseRequestFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

    PicometerControl('Disconnect')

    % Hint: delete(hObject) closes the figure
    delete(hObject);
end



function UpdateData(obj, event, handles)

    %global Count
    
    global PrevCount;
    
    global ZData;
    global Frequencies;
    global Divider;
    
    NrOfSpectras = 50 / Divider;  % 50ms minimum plot refresh rate
    if NrOfSpectras < 1
        
        NrOfSpectras = 1;
     
    end

    ZData = PicometerControl('GetData', NrOfSpectras);

    % Create Module plot
    plot(handles.Module, Frequencies, ZData.ImpedanceModule(1, 1:15));
    set(handles.Module, 'XScale', 'log');
    set(handles.Module, 'YScale', 'log');
    set(handles.Module, 'YMinorTick', 'on');
    set(handles.Module, 'YGrid', 'on');
    set(handles.Module, 'YMinorGrid', 'on');
    set(handles.Module, 'XLim', [min(Frequencies) max(Frequencies)]);
    set(handles.Module, 'XTick', Frequencies);

    % Create Phase plot
    plot(handles.Phase, Frequencies, ZData.ImpedancePhase(1, 1:15));
    set(handles.Phase, 'XScale', 'log');
    set(handles.Phase, 'YMinorTick', 'on');
    set(handles.Phase, 'YGrid', 'on');
    set(handles.Phase, 'XLim', [min(Frequencies) max(Frequencies)]);
    set(handles.Phase, 'XTick', Frequencies);

    set(handles.MeasCount,'String', num2str(ZData.MeasurementCycleCount(1)));
    set(handles.MeasPer,'String', num2str(ZData.MeasurementCyclePeriod(1)));
    
    set(handles.MinMax,'String', sprintf('%d\n%d\n%d\n%d', ZData.MaxChA(1), ZData.MinChA(1),  ZData.MaxChB(1), ZData.MinChB(1) ) );
    
    for n = 1 : NrOfSpectras

        Delat = ZData.MeasurementCycleCount(n) - PrevCount;
        
        if Delat > 1
            
            set(handles.MeasCount,'String', num2str(Delat));
        
        end
        
        PrevCount = ZData.MeasurementCycleCount(n);
        
    end
    


end



function MeasCount_Callback(hObject, eventdata, handles)
% hObject    handle to MeasCount (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of MeasCount as text
%        str2double(get(hObject,'String')) returns contents of MeasCount as a double

end

% --- Executes during object creation, after setting all properties.
function MeasCount_CreateFcn(hObject, eventdata, handles)
% hObject    handle to MeasCount (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

    % Hint: edit controls usually have a white background on Windows.
    %       See ISPC and COMPUTER.
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end
end


function CountDelta_Callback(hObject, eventdata, handles)
% hObject    handle to CountDelta (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of CountDelta as text
%        str2double(get(hObject,'String')) returns contents of CountDelta as a double

end

% --- Executes during object creation, after setting all properties.
function CountDelta_CreateFcn(hObject, eventdata, handles)
% hObject    handle to CountDelta (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

    % Hint: edit controls usually have a white background on Windows.
    %       See ISPC and COMPUTER.
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end
end



function MeasPer_Callback(hObject, eventdata, handles)
% hObject    handle to MeasPer (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

    % Hints: get(hObject,'String') returns contents of MeasPer as text
    %        str2double(get(hObject,'String')) returns contents of MeasPer as a double

end
    
% --- Executes during object creation, after setting all properties.
function MeasPer_CreateFcn(hObject, eventdata, handles)
% hObject    handle to MeasPer (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

    % Hint: edit controls usually have a white background on Windows.
    %       See ISPC and COMPUTER.
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end
end



function MinMax_Callback(hObject, eventdata, handles)
% hObject    handle to MinMax (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of MinMax as text
%        str2double(get(hObject,'String')) returns contents of MinMax as a double
end

% --- Executes during object creation, after setting all properties.
function MinMax_CreateFcn(hObject, eventdata, handles)
% hObject    handle to MinMax (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

    % Hint: edit controls usually have a white background on Windows.
    %       See ISPC and COMPUTER.
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end
end


% --- Executes on slider movement.
function ExcitLevel_Callback(hObject, eventdata, handles)
% hObject    handle to ExcitLevel (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

PicometerControl('SetExcitationLevel', get(hObject,'Value'))

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
end

% --- Executes during object creation, after setting all properties.
function ExcitLevel_CreateFcn(hObject, eventdata, handles)
% hObject    handle to ExcitLevel (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

    % Hint: slider controls usually have a light gray background.
    if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor',[.9 .9 .9]);
    end
end


% --- Executes on selection change in GainA.
function GainA_Callback(hObject, eventdata, handles)
% hObject    handle to GainA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

    % Hints: contents = get(hObject,'String') returns GainA contents as cell array
    %        contents{get(hObject,'Value')} returns selected item from GainA

    GainsA = get(handles.GainA,'String');
    SelectedGainIdxA = get(handles.GainA,'Value');
    SelectedGainA = GainsA{SelectedGainIdxA};

    GainsB = get(handles.GainB,'String');
    SelectedGainIdxB = get(handles.GainB,'Value');
    SelectedGainB = GainsB{SelectedGainIdxB};
    
    PicometerControl('SetInputGain', SelectedGainA, SelectedGainB);

end

% --- Executes during object creation, after setting all properties.
function GainA_CreateFcn(hObject, eventdata, handles)
% hObject    handle to GainA (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

    % Hint: popupmenu controls usually have a white background on Windows.
    %       See ISPC and COMPUTER.
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

end


% --- Executes on selection change in GainB.
function GainB_Callback(hObject, eventdata, handles)
% hObject    handle to GainB (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

    % Hints: contents = get(hObject,'String') returns GainB contents as cell array
    %        contents{get(hObject,'Value')} returns selected item from GainB

    GainsA = get(handles.GainA,'String');
    SelectedGainIdxA = get(handles.GainA,'Value');
    SelectedGainA = GainsA{SelectedGainIdxA};

    GainsB = get(handles.GainB,'String');
    SelectedGainIdxB = get(handles.GainB,'Value');
    SelectedGainB = GainsB{SelectedGainIdxB};
    
    PicometerControl('SetInputGain', SelectedGainA, SelectedGainB);
    
end

% --- Executes during object creation, after setting all properties.
function GainB_CreateFcn(hObject, eventdata, handles)
% hObject    handle to GainB (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

    % Hint: popupmenu controls usually have a white background on Windows.
    %       See ISPC and COMPUTER.
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

end


% --- Executes on button press in SetShunt.
function SetShunt_Callback(hObject, eventdata, handles)
% hObject    handle to SetShunt (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

    global Frequencies;    

    ShuntComplex = PicometerControl('GetShuntData', Frequencies);
    
    PicometerControl('SetShuntVal', ShuntComplex);

end


% --- Executes on selection change in Divider.
function Divider_Callback(hObject, eventdata, handles)
% hObject    handle to Divider (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = get(hObject,'String') returns Divider contents as cell array
%        contents{get(hObject,'Value')} returns selected item from Divider

    global Divider;
    global Frequencies;
   
    Dividers = get(handles.Divider,'String');
    SelectedDividersIdx = get(handles.Divider,'Value');
    Divider = str2num(Dividers{SelectedDividersIdx});
   
    % Calculate frequency values from bins array
    DevConf = PicometerControl('GetConfData');
    Frequencies = transpose((double(DevConf.FrequencyBins) .* 1000) ./ Divider);

    
    PicometerControl('SetSamplingDivider', Divider);

end

% --- Executes during object creation, after setting all properties.
function Divider_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Divider (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
    if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
        set(hObject,'BackgroundColor','white');
    end

end

