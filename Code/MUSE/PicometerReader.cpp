// PicometerReader.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <iostream>
#include <Windows.h>
#include <stdio.h>
#include <stdlib.h>
#include "pre_defined_params.h"
using namespace std;
#pragma comment(lib, "PicometerCtrl.lib")

extern "C" char* GetDLLVersion(unsigned long*);
extern "C" char* PicometerControl(unsigned char, unsigned long, unsigned long*, unsigned char*);

#define BUFFER_SIZE	1024
unsigned long	Idx;
unsigned char	TxtBfr[16];
static unsigned long	ErrEvent;
unsigned long	NrOfDataFrames = BUFFER_SIZE;
unsigned long	NrOfDataFramesCopied;
unsigned long	SamplingRateDivider = 1;		//	Sampling rate divider value, valid values are: 1, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 196, 224, 256, 320, 384, 448, 512, 640, 768, 896, 1024, 1280, 1536, 1792
unsigned long 	CompensationConf = 0;			//	Local variable that can have valid values of: 0 - compensation calculations, 1 - compensation calculations enabled and 2 - measure compensation values
												//	All other values are invalid
unsigned long	ExcitationLevel = 90;		    //	Valid range is 0...255
unsigned long 	GainVals = 0x00;// 0 0 0 0		//	Binary access, Bit field of 4-LSB argument bits of the LSB byte are: |    X    |    X    |    X    |    X    | ADCB-G1 | ADCB-G0 | ADCA-G1 | ADCA-G0 | 
												//	| ADCB-G1 | ADCB-G0 | GAIN |
												//	|    0    |    0    |   1  |
												//	|    0    |    1    |   2  |
												//	|    1    |    0    |   5  |
												//	|    1    |    1    |   10 |
												//	
												//	| ADCA-G1 | ADCA-G0 | GAIN |
												//	|    0    |    0    |   1  |
												//	|    0    |    1    |   2  |
												//	|    1    |    0    |   5  |
												//	|    1    |    1    |   10 |

struct IMP_DATA_T
{
	unsigned short int  AddressControl;
	unsigned short int  DataIdentificator;
	unsigned short int  FrameSizeBytes;
	unsigned short int  SysErrors;
	unsigned int        MeasurementCycleCount;
	unsigned int		MeasurementCyclePeriod;
	unsigned short int  MaxChA;
	unsigned short int  MinChA;
	unsigned short int  MaxChB;
	unsigned short int  MinChB;
	float               ImpedanceModule[15];
	float               ImpedancePhase[15];
	unsigned short int  BatteryLevel;
	unsigned short int  ChargerStatus;
	unsigned short int  GPIOState;
	unsigned short int  Reserved[20];
	unsigned short int  CRCChk16;
}Data[BUFFER_SIZE];
struct
{
	unsigned short		BinCnt;
	unsigned short		DFTBins[15];
	float				ShuntImpedanceReal[15];
	float				ShuntImpedanceImaginary[15];
	float				InputCompenValReal[15];
	float				InputCompenValImaginary[15];
}ConfData;						//	Structured data buffer


void staticUSE()
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

void connect_device()
{
	printf("Connecting...\n");

	char* ErrorStrPtr = PicometerControl(DEVICE_CONNECT, 0, &Idx, TxtBfr);
	if (ErrorStrPtr != NULL)
	{
		printf("connect the device faliured!\n");
		return;
	}
	else
	{
		std::cout << Idx << std::endl;
		std::cout << TxtBfr << std::endl;
		printf("connect the device succesfully!\n");
		return;
	}
}

void disconnect_device()
{
	char* ErrorStrPtr = PicometerControl(DEVICE_DISCONNECT, 0, NULL, NULL);
	if (ErrorStrPtr != NULL)
	{
		printf("failed to stop the device connection!\n");
		return;
	}
	else
	{
		printf("stop the device connection succesfully!\n");
		return;

	}
}

void get_error()
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

void device_start()
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
void get_data()
{
	char* ErrorStrPtr = PicometerControl(GET_DATA, NrOfDataFrames, &NrOfDataFramesCopied, (unsigned char*)Data);
	if (ErrorStrPtr != NULL)
	{
		printf("failed to get the data!\n");
		std::cout << ErrorStrPtr << std::endl;
		return;
	}
	else
	{
		printf("get the data successflly!\n");
		std::cout << "ImpedanceModule:";
		for (int i = 0; i < 15; i++)
		{
			std::cout << Data->ImpedanceModule[i] << ", ";
		}
		std::cout << std::endl;
		std::cout << "ImpedancePhase:";
		for (int i = 0; i < 15; i++)
		{
			std::cout << Data->ImpedancePhase[i] << ", ";
		}
		std::cout << std::endl;
		return;

	}
}
void device_stop()
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

void set_samplingrate_divider()
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

void set_compensation()
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

void set_excitation_level(unsigned long	excitation_level)
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

void set_input_gains(unsigned long gianvalues)
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

void get_configuration()
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
//int multip5_3(int a, int* p)
//{
//	*p = 5 * a;
//	return 0;
//}

//int main()
//{
//	staticUSE();
//	connect_device();
//	set_samplingrate_divider(); // this function should be run in idle mode
//	get_configuration(); // this function should be run in idle mode
//	device_start();
//	//set_compensation();
//	//set_excitation_level(ExcitationLevel); // changes the excitation amplitude 
//	//set_input_gains(GainVals); // setting the two gains, local in the initial parameter setting.
//	
//	//get_error();
//
//	for (int i = 0; i < 10; i++)
//	{
//		get_data(); // get the ImpedanceModule[15] and ImpedancePhase[15]
//	}
//	system("pause");
//	device_stop();
//	return 0;
//	//examples
//	//HMODULE	dll_com = LoadLibrary(L"PicometerCtrl.dll");
//	//if (dll_com == NULL)
//	//{
//	//	printf("fail to load the .dll file");
//	//	return 0;
//	//}
//	disconnect_device();
//}
