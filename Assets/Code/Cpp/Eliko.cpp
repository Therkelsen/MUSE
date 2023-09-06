#include "Eliko.h"

void Eliko::staticUSE()
{
	char* version = GetDLLVersion(NULL);
	if (version == NULL)
	{
		printf("the version is NULL !!!\n");
	}
	else
	{
		printf("the dll version is: %s \n", version);
	}
}

_devCon Eliko::connect_device()
{
    _devCon device;
	printf("Connecting...\n");

	char* ErrorStrPtr = PicometerControl(DEVICE_CONNECT, 0, &Idx, TxtBfr);
	if (ErrorStrPtr != NULL)
	{
		printf("connect the device faliured!\n");
        device.isSuccess = 0;
        return device;
	}
	else
	{
        device.isSuccess=1;
        device.Id=Idx;
        for(int i=0;i<16;i++)
        {
            device.TxBfr[i] = TxtBfr[i];
        }

        //device.TxBfr;
		std::cout << Idx << std::endl;
		std::cout << TxtBfr << std::endl;
		printf("connect the device succesfully!\n");
        return device;
	}
}

bool Eliko::disconnect_device()
{
	char* ErrorStrPtr = PicometerControl(DEVICE_DISCONNECT, 0, NULL, NULL);
	if (ErrorStrPtr != NULL)
	{
		printf("failed to stop the device connection!\n");
        return 0;
	}
	else
	{
		printf("stop the device connection succesfully!\n");
        return 1;

	}
}

void Eliko::get_error()
{
	PicometerControl(GET_ERROR, 0, &ErrEvent, NULL);
	if (ErrEvent != NULL)
	{
		char* ErrorStrPtr = PicometerControl(GET_ERROR, 0, &ErrEvent, NULL);
		std::cout << ErrorStrPtr << std::endl;
		return;
	}
	else
	{
		cout << ErrEvent << "\n";
	}
}

void Eliko::device_start()
{
	char* ErrorStrPtr = PicometerControl(START, 0, NULL, NULL);
	if (ErrorStrPtr != NULL)
	{
		printf("failed to startup the device!\n");
		return;
	}
	else
	{
		printf("startup the device succesfully!\n");
		return;

	}
}
_elikoRes Eliko::get_data()
{
    _elikoRes res;
    char* ErrorStrPtr = PicometerControl(GET_DATA, NrOfDataFrames, &NrOfDataFramesCopied, (unsigned char*)Data);//&Data[0]
	if (ErrorStrPtr != NULL)
	{
        res.state = 0;
        printf("failed to get the data!\n");
		std::cout << ErrorStrPtr << std::endl;
        return res;
	}
	else
	{
        res.state = 1;
        //printf("get the data successflly!\n");
        //std::cout << "ImpedanceModule:";

        for(int i = 0; i < 150; i++)
        {
            for (int j = 0; j < 15; j++)
            {
                res.ImpedanceModule[i][j] = Data[i].ImpedanceModule[j];
                res.ImpedancePhase[i][j] = Data[i].ImpedancePhase[j];
                //std::cout << Data->ImpedanceModule[i] << ", ";
            }
        //std::cout << std::endl;
        //std::cout << "ImpedancePhase:";

        //std::cout << std::endl;
        }
        return res;

	}
}
void Eliko::device_stop()
{
	char* ErrorStrPtr = PicometerControl(STOP, 0, NULL, NULL);
	if (ErrorStrPtr != NULL)
	{
		printf("failed to stop the device!\n");
		return;
	}
	else
	{
		printf("stop the device succesfully!\n");
		return;

	}
}

void Eliko::set_samplingrate_divider()
{
	char* ErrorStrPtr = PicometerControl(SET_SAMPLINGRATE_DIVIDER, SamplingRateDivider, NULL, NULL);

	if (ErrorStrPtr != NULL)
	{
		printf("set samplingrate divider failed!\n");
		std::cout << ErrorStrPtr << std::endl;
		return;
		//	Error encountered, print ErrorStrPtr
	}
	else
	{
		printf("set samplingrate divider succesfully!\n");
		return;
	}
}

void Eliko::set_compensation()
{
	char* ErrorStrPtr = PicometerControl(SET_COMPENSATION, CompensationConf, NULL, NULL);

	if (ErrorStrPtr != NULL)
	{
		printf("set compensation failed!\n");
		return;
		//	Error encountered, print ErrorStrPtr
	}
	else
	{
		printf("set compensation successflly!\n");
		return;
		//	Error encountered, print ErrorStrPtr
	}
}

void Eliko::set_excitation_level(unsigned long	excitation_level)
{
	char* ErrorStrPtr = PicometerControl(SET_EXCITATION_LEVEL, excitation_level, NULL, NULL);

	if (ErrorStrPtr != NULL)
	{
		printf("set excitation level failed!\n");
		return;
		//	Error encountered, print ErrorStrPtr
	}
	else
	{
		printf("set excitation level successflly!\n");
		return;
	}
}

void Eliko::set_input_gains(unsigned long gianvalues)
{
	char* ErrorStrPtr = PicometerControl(SET_INPUT_GAINS, gianvalues, NULL, NULL);

	if (ErrorStrPtr != NULL)
	{
		printf("set input gains failed!\n");
		return;
		//	Error encountered, print ErrorStrPtr
	}
	else
	{
		printf("set input gains successflly!\n");
		return;
	}
}

void Eliko::get_configuration()
{
	char* ErrorStrPtr = PicometerControl(GET_CONFIGURATION, 0, NULL, (PBYTE)&ConfData);
	if (ErrorStrPtr != NULL)
	{
		printf("get configuration data failed!\n");
		return;
	}
	else
	{
		printf("get configuration data successflly!\n");
		std::cout << "configuration data -- InputCompenValReal:" << ConfData.InputCompenValReal << std::endl;
		std::cout << "configuration data -- ShuntImpedanceImaginary:" << ConfData.ShuntImpedanceImaginary << std::endl;
		std::cout << "configuration data -- ShuntImpedanceReal:" << ConfData.ShuntImpedanceReal << std::endl;

		return;
	}
}
