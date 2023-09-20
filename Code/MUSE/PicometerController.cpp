#include "PicometerController.h"

// do not remove
static unsigned long ErrEvent = 0;

void PicometerController::staticUSE() {
	char* version = GetDLLVersion(NULL);
	if (version == NULL) {
		std::cerr << "PicometerController: .dll version is NULL!!!" << std::endl;
	} else {
		printf("PicometerController: .dll version is: %s \n", version);
	}
}

void PicometerController::connect_device() {
	printf("Connecting...\n");

	char* ErrorStrPtr = PicometerControl(DEVICE_CONNECT, 0, &Idx, TxtBfr);
	if (ErrorStrPtr != NULL) {
		std::cerr << "PicometerController: Device connection failed!" << std::endl;
		picometer_status = PicometerStatus::ERROR_FOUND;
	} else {
		std::cout << Idx << "\n" << TxtBfr << "\nPicometerController: Device connection successfully established." << std::endl;
		picometer_status = PicometerStatus::CONNECTED;
	}
}

void PicometerController::disconnect_device() {
	char* ErrorStrPtr = PicometerControl(DEVICE_DISCONNECT, 0, NULL, NULL);
	if (ErrorStrPtr != NULL) {
		std::cerr << "PicometerController: Device disconnect failed!" << std::endl;
		picometer_status = PicometerStatus::ERROR_FOUND;
	} else {
		std::cout << "PicometerController: Device successfully disconnected." << std::endl;
		picometer_status = PicometerStatus::DISCONNECTED;
	}
}

void PicometerController::device_start() {
	char* ErrorStrPtr = PicometerControl(START, 0, NULL, NULL);
	if (ErrorStrPtr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		std::cerr << "PicometerController: Device startup failed!" << std::endl;
		picometer_status = PicometerStatus::ERROR_FOUND;
	} else {
		std::cout << "PicometerController: Device startup successful." << std::endl;
	}
}

void PicometerController::device_stop() {
	char* ErrorStrPtr = PicometerControl(STOP, 0, NULL, NULL);
	if (ErrorStrPtr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		std::cerr << "PicometerController: Device stop failed!" << std::endl;
		picometer_status = PicometerStatus::ERROR_FOUND;
	} else {
		std::cout << "PicometerController: Device succesfully stopped." << std::endl;
	}
}

void PicometerController::get_error() {
	PicometerControl(GET_ERROR, 0, &ErrEvent, NULL);
	if (ErrEvent != NULL) {
		char* ErrorStrPtr = PicometerControl(GET_ERROR, 0, &ErrEvent, NULL);
		std::cerr << ErrorStrPtr << std::endl;
	} else {
		std::cerr << ErrEvent << std::endl;
	}
}

void PicometerController::get_configuration() {
	char* ErrorStrPtr = PicometerControl(GET_CONFIGURATION, 0, NULL, (PBYTE)&ConfData);
	if (ErrorStrPtr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		std::cerr << "PicometerController: Configuration data getter failed!" << std::endl;
		picometer_status = PicometerStatus::ERROR_FOUND;
	} else {
		std::cout << "PicometerController: Configuration data gotten successfully."
				  << "\nPicometerController: Configuration data -- InputCompenValReal:" << ConfData.InputCompenValReal
		          << "\nPicometerController: Configuration data -- ShuntImpedanceImaginary:" << ConfData.ShuntImpedanceImaginary
				  << "\nPicometerController: Configuration data -- ShuntImpedanceReal:" << ConfData.ShuntImpedanceReal << std::endl;
	}
}

void PicometerController::print_data(std::vector<std::vector<float>> data) {
	bool is_empty = true;
	for (const auto& element : data) {
		for(const auto& value : element) {
			if (value != 0) {
				is_empty = false;
				break;
			}
		}
	}
	
	if(is_empty) {
		std::cerr << "PicometerController: No data to print!" << std::endl;
		return;
	}

	std::cout << std::setprecision(2) << std::scientific << std::setw(16) << std::left << "Time step";

	// Print frequency headers
	for (int i = 0; i < data[0].size(); i++) {
		std::cout << std::left << "Freq " << (i + 1);
		if (i != data[0].size() - 1) {
			std::cout << "\t\t";
		}
	}
	std::cout << std::endl;

	// Print data
	for (int i = 0; i < data.size(); i++) {
		std::cout << i + 1 << "\t\t";
		for (int j = 0; j < data[0].size(); j++) {
			std::cout << "(" << data[i][j] << ")\t";
		}
		std::cout << std::endl;
	}

	std::cout << std::endl;
}

std::pair<std::vector<float>, std::vector<float>> PicometerController::get_data() {
	char* ErrorStrPtr = PicometerControl(GET_DATA, NrOfDataFrames, &NrOfDataFramesCopied, (unsigned char*)Data);
	if (ErrorStrPtr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		std::cerr << "PicometerController: Failed to get the data, aborting! Error: " << ErrorStrPtr << std::endl;
		picometer_status = PicometerStatus::ERROR_FOUND;
		return { {}, {} };
	} else {
		std::vector<float> impedanceModule(Data->ImpedanceModule, Data->ImpedanceModule + 15);
		std::vector<float> impedancePhase(Data->ImpedancePhase, Data->ImpedancePhase + 15);

		return { impedanceModule, impedancePhase };
	}
}

std::vector<std::vector<float>> PicometerController::get_n_data_steps(size_t n) {
	std::vector<std::vector<float>> result;
	result.reserve(n);

	for (size_t i = 0; i < n; ++i) {
		if(picometer_status != PicometerStatus::CONNECTED) {
			break;
		}
		// Call get_data to retrieve impedance data for each time step
		auto impedanceData = get_data().first;

		// Append the impedance data to the result vector
		result.emplace_back(impedanceData);
	}

	return result;
}

std::vector<std::vector<float>> PicometerController::get_raw_sensor_data() {
	if(!raw_data_ready) {
		std::cerr << "PicometerController: Raw sensor data not ready!" << std::endl;
		return {};
	}
	return raw_sensor_data;
}
std::vector<std::vector<float>> PicometerController::get_filtered_sensor_data() {
	if(!filtered_data_ready) {
		std::cerr << "PicometerController: Filtered sensor data not ready!" << std::endl;
		return {};
	}
	return filtered_sensor_data;
}

void PicometerController::set_samplingrate_divider() {
	char* ErrorStrPtr = PicometerControl(SET_SAMPLINGRATE_DIVIDER, SamplingRateDivider, NULL, NULL);

	if (ErrorStrPtr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		std::cerr << "PicometerController: Sampling rate divider could not be set!" << ErrorStrPtr << std::endl;
	} else {
		std::cout << "PicometerController: Sampling rate divider succesfully set." << std::endl;
	}
}

void PicometerController::set_compensation() {
	char* ErrorStrPtr = PicometerControl(SET_COMPENSATION, CompensationConf, NULL, NULL);

	if (ErrorStrPtr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		std::cerr << "PicometerController: Compensation could not be set!" << std::endl;
	} else {
		std::cout << "PicometerController: Compensation successfully set." << std::endl;
	}
}

void PicometerController::set_excitation_level(unsigned long excitation_level) {
	char* ErrorStrPtr = PicometerControl(SET_EXCITATION_LEVEL, excitation_level, NULL, NULL);

	if (ErrorStrPtr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		std::cerr << "PicometerController: Excitation level could not be set!" << std::endl;
	} else {
		std::cout << "PicometerController: Excitation level successfully set." << std::endl;
	}
}

void PicometerController::set_input_gains(unsigned long gianvalues) {
	char* ErrorStrPtr = PicometerControl(SET_INPUT_GAINS, gianvalues, NULL, NULL);

	if (ErrorStrPtr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		std::cerr << "PicometerController: Input gains could not be set!" << std::endl;
	} else {
		std::cout << "PicometerController: Input gains successfully set." << std::endl;
	}
}

void PicometerController::set_raw_sensor_data(std::vector<std::vector<float>> data) {
	bool is_empty = true;
	for (const auto& element : data) {
		for (const auto& value : element) {
			if (value != 0) {
				is_empty = false;
				break;
			}
		}
	}

	if (is_empty) {
		std::cerr << "PicometerController: No data to save!" << std::endl;
		return;
	}
	
	raw_sensor_data = data;
	raw_data_ready = true;
}

void PicometerController::set_filtered_sensor_data(std::vector<std::vector<float>> data) {
	bool is_empty = true;
	for (const auto& element : data) {
		for (const auto& value : element) {
			if (value != 0) {
				is_empty = false;
				break;
			}
		}
	}

	if (is_empty) {
		std::cerr << "PicometerController: No data to save!" << std::endl;
		return;
	}

	filtered_sensor_data = data;
	filtered_data_ready = true;
}