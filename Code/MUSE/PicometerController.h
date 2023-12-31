#ifndef PICOMETER_CONTROLLER_H
#define PICOMETER_CONTROLLER_H

#define NOMINMAX

#include <algorithm>
#include <cstdio>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <utility>
#include <vector>
#include <Windows.h>

#include "pre_defined_params.h"
#pragma comment(lib, "PicometerCtrl.lib")

extern "C" char* GetDLLVersion(unsigned long*);
extern "C" char* PicometerControl(unsigned char, unsigned long, unsigned long*, unsigned char*);

constexpr auto BUFFER_SIZE = 1;

class PicometerController {
public:
	PicometerController() {
		for (int i = 0; i < BUFFER_SIZE; i++) {
			Data[i].AddressControl = 0;
			Data[i].DataIdentificator = 0;
			Data[i].FrameSizeBytes = 0;
			Data[i].SysErrors = 0;
			Data[i].MeasurementCycleCount = 0;
			Data[i].MeasurementCyclePeriod = 0;
			Data[i].MaxChA = 0;
			Data[i].MinChA = 0;
			Data[i].MaxChB = 0;
			Data[i].MinChB = 0;
			Data[i].BatteryLevel = 0;
			Data[i].ChargerStatus = 0;
			Data[i].GPIOState = 0;
			Data[i].CRCChk16 = 0;
			for (int j = 0; j < (sizeof(Data[i].ImpedanceModule) / sizeof(*Data[i].ImpedanceModule)); ++j) {
				Data[i].ImpedanceModule[j] = 0.0f;
				Data[i].ImpedancePhase[j] = 0.0f;
			}
			for (int k = 0; k < (sizeof(ConfData.DFTBins) / sizeof(*ConfData.DFTBins)); k++) {
				ConfData.DFTBins[k] = 0;
				ConfData.ShuntImpedanceReal[k] = 0.0f;
				ConfData.ShuntImpedanceImaginary[k] = 0.0f;
				ConfData.InputCompenValReal[k] = 0.0f;
				ConfData.InputCompenValImaginary[k] = 0.0f;
			}
			ConfData.BinCnt = 0;
		}
		NrOfDataFrames = BUFFER_SIZE;
		NrOfDataFramesCopied = 0;
		CompensationConf = 0;
		Idx = 0;
		for (int i = 0; i < (sizeof(TxtBfr) / sizeof(*TxtBfr)); i++) {
			TxtBfr[i] = 0;
		}

		static_use();
		connect_device();
		set_samplingrate_divider(); // this function should be run in idle mode
		get_configuration(); // this function should be run in idle mode
		device_start();
		std::cout << "PicometerController: Initialized" << std::endl;
	}

	~PicometerController() {
		device_stop();
		disconnect_device();
	}

	// Function declarations
	void static_use();
	void connect_device();
	void disconnect_device();
	void device_start();
	void device_stop();
	void print_data(std::vector<std::vector<float>> data);

	void get_error();
	std::pair<std::vector<float>, std::vector<float>> get_data();
	void get_configuration();

	void set_samplingrate_divider();
	void set_compensation();
	void set_excitation_level(unsigned long excitation_level);
	void set_input_gains(unsigned long gain_values);

	void write_data_to_csv(const std::vector<std::vector<float>>& data, const std::string& path);

	bool file_exists(const std::string& path);

	unsigned long Idx = 0;
	unsigned char TxtBfr[16];
	unsigned long NrOfDataFrames = BUFFER_SIZE;
	unsigned long NrOfDataFramesCopied = 0;
	unsigned long SamplingRateDivider = 1;// 56;
	unsigned long CompensationConf = 0;
	unsigned long ExcitationLevel = 200;// 146;
	unsigned long GainVals = 0x0011; // 0x0011;

	unsigned long buffer_size = 0;

	bool raw_data_ready = false;
	bool filtered_data_ready = false;

	enum class PicometerStatus {
		DISCONNECTED,
		CONNECTED,
		ERROR_FOUND,
	};

	PicometerStatus picometer_status = PicometerStatus::DISCONNECTED;

	// IMP_DATA_T struct
	struct IMP_DATA_T {
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
	} Data[BUFFER_SIZE];

	// ConfData struct
	struct conf_data {
		unsigned short  BinCnt;
		unsigned short  DFTBins[15];
		float    ShuntImpedanceReal[15];
		float    ShuntImpedanceImaginary[15];
		float    InputCompenValReal[15];
		float    InputCompenValImaginary[15];
	} ConfData;

private:
	std::vector<std::vector<float>> raw_sensor_data;
	std::vector<std::vector<float>> filtered_sensor_data;
};


#endif // PICOMETER_CONTROLLER_H