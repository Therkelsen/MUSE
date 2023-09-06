#pragma once
#include <iostream>
#include <Windows.h>
#include <stdio.h>
#include <stdlib.h>
#include "pre_defined_params.h"
//#include "PicometerCtrl.h"
using namespace std;
#pragma comment(lib, "PicometerCtrl.lib")
#define BUFFER_SIZE	150

#define	SamplingRateDivider  1		//	Sampling rate divider value, valid values are: 1, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 196, 224, 256, 320, 384, 448, 512, 640, 768, 896, 1024, 1280, 1536, 1792
#define CompensationConf  0			//	Local variable that can have valid values of: 0 - compensation calculations, 1 - compensation calculations enabled and 2 - measure compensation values
											//	All other values are invalid
#define	ExcitationLevel 101		    //	Valid range is 0...255
#define GainVals 0x00// 0 0 0 0		//	Binary access, Bit field of 4-LSB argument bits of the LSB byte are: |    X    |    X    |    X    |    X    | ADCB-G1 | ADCB-G0 | ADCA-G1 | ADCA-G0 |
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

extern "C" char* GetDLLVersion(unsigned long*);
extern "C" char* PicometerControl(unsigned char, unsigned long, unsigned long*, unsigned char*);

typedef struct _stateConnect{
    bool isSuccess;
    unsigned long Id;
    char TxBfr[16]={0};
}_devCon;

typedef struct _elikoData{
    bool state;
    int freq[15];
    float ImpedanceModule[BUFFER_SIZE][15];
    float ImpedancePhase[BUFFER_SIZE][15];
}_elikoRes;

class Eliko
{
public:
	void staticUSE();
    _devCon connect_device();
    bool disconnect_device();
	void get_error();
	void device_start();
    _elikoRes get_data();
	void device_stop();
	void set_samplingrate_divider();
	void set_compensation();
	void set_excitation_level(unsigned long	excitation_level);
	void set_input_gains(unsigned long gianvalues);
	void get_configuration();

private:
	unsigned long	Idx;
	unsigned char	TxtBfr[16];
    //static unsigned long	ErrEvent;
    unsigned long	ErrEvent;
	unsigned long	NrOfDataFrames = BUFFER_SIZE;
	unsigned long	NrOfDataFramesCopied;



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

};

