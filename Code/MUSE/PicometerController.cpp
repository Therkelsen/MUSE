#include "PicometerController.h"

static unsigned long ErrEvent = 0;

/**
* @brief Method for throwing runtime error
* @param error_msg Error message to be thrown
*/
void throw_runtime_error(const std::string& error_msg) {
	throw std::runtime_error("PicometerController: " + error_msg + "\nExiting...");
}

/**
* @brief Checks that the .dll version isn't NULL
*/
void PicometerController::static_use() {
	char* version = GetDLLVersion(NULL);
	if (version == NULL) {
		throw_runtime_error(".dll version is NULL!!!");
	}
	printf("PicometerController: .dll version is: %s \n", version);
}

/**
* @brief Attempts to connect to the Eliko Picometer device
*/
void PicometerController::connect_device() {
	printf("Connecting...\n");

	char* error_str_ptr = PicometerControl(DEVICE_CONNECT, 0, &Idx, TxtBfr);
	if (error_str_ptr != NULL) {
		throw_runtime_error("Device connection failed!");
		picometer_status = PicometerStatus::ERROR_FOUND;
	}
	std::cout << Idx << "\n" << TxtBfr << "\nPicometerController: Device connection successfully established." << std::endl;
	picometer_status = PicometerStatus::CONNECTED;
}

/**
* @brief Attempts to disconnect from the Eliko Picometer device
*/
void PicometerController::disconnect_device() {
	char* error_str_ptr = PicometerControl(DEVICE_DISCONNECT, 0, NULL, NULL);
	if (error_str_ptr != NULL) {
		throw_runtime_error("Device disconnect failed!");
		picometer_status = PicometerStatus::ERROR_FOUND;
	}
	std::cout << "PicometerController: Device successfully disconnected." << std::endl;
	picometer_status = PicometerStatus::DISCONNECTED;
}

/**
* @brief Attempts to start the Eliko Picometer device
*/
void PicometerController::device_start() {
	char* error_str_ptr = PicometerControl(START, 0, NULL, NULL);
	if (error_str_ptr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		throw_runtime_error("Device startup failed!");
		picometer_status = PicometerStatus::ERROR_FOUND;
	}
	std::cout << "PicometerController: Device startup successful." << std::endl;
}

/**
* @brief Attempts to stop the Eliko Picometer device
*/
void PicometerController::device_stop() {
	char* error_str_ptr = PicometerControl(STOP, 0, NULL, NULL);
	if (error_str_ptr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		throw_runtime_error("Device stop failed!");
		picometer_status = PicometerStatus::ERROR_FOUND;
	}
	std::cout << "PicometerController: Device successfully stopped." << std::endl;
}

/**
* @brief Gets the latest error from the Eliko Picometer device
*/
void PicometerController::get_error() {
	PicometerControl(GET_ERROR, 0, &ErrEvent, NULL);
	if (ErrEvent != NULL) {
		char* error_str_ptr = PicometerControl(GET_ERROR, 0, &ErrEvent, NULL);
		std::cerr << error_str_ptr << std::endl;
	}
	std::cerr << ErrEvent << std::endl;
}

/**
* @brief Attempts to get the device configuration data
*/
void PicometerController::get_configuration() {
	char* error_str_ptr = PicometerControl(GET_CONFIGURATION, 0, NULL, (PBYTE)&ConfData);
	if (error_str_ptr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		throw_runtime_error("Configuration data getter failed!");
		picometer_status = PicometerStatus::ERROR_FOUND;
	}
	std::cout << "PicometerController: Configuration data gotten successfully."
	<< "\nPicometerController: Configuration data -- InputCompenValReal:" << ConfData.InputCompenValReal
	<< "\nPicometerController: Configuration data -- ShuntImpedanceImaginary:" << ConfData.ShuntImpedanceImaginary
	<< "\nPicometerController: Configuration data -- ShuntImpedanceReal:" << ConfData.ShuntImpedanceReal << std::endl;
}

/**
* @brief Attempts to print the passed data
* @param data Data to be printed
*/
void PicometerController::print_data(std::vector<std::vector<float>> data) {
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
		throw_runtime_error("No data to print!");
		return;
	}

	std::cout << std::setprecision(2) << std::scientific << std::setw(16) << std::left << "Time step";

	// Print frequency headers
	for (unsigned int i = 0; i < data[0].size(); i++) {
		std::cout << std::left << "Freq " << (i + 1);
		if (i != data[0].size() - 1) {
			std::cout << "\t\t";
		}
	}
	std::cout << std::endl;

	// Print data
	for (unsigned int i = 0; i < data.size(); i++) {
		std::cout << i + 1 << "\t\t";
		for (unsigned int j = 0; j < data[0].size(); j++) {
			std::cout << "(" << data[i][j] << ")\t";
		}
		std::cout << std::endl;
	}

	std::cout << std::endl;
}

/**
* @brief Attempts to get the data from the Eliko Picometer device
* @return Data gotten from the device
*/
std::pair<std::vector<float>, std::vector<float>> PicometerController::get_data() {
	char* error_str_ptr = PicometerControl(GET_DATA, NrOfDataFrames, &NrOfDataFramesCopied, (unsigned char*)Data);
	if (error_str_ptr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		picometer_status = PicometerStatus::ERROR_FOUND;
		throw std::runtime_error("PicometerController: Failed to get the data! Error: " + std::string(error_str_ptr));
	}

	std::vector<float> impedance_module(Data->ImpedanceModule, Data->ImpedanceModule + 15);
	std::vector<float> impedance_phase(Data->ImpedancePhase, Data->ImpedancePhase + 15);

	return { impedance_module, impedance_phase };
}

/**
* @brief Attempts to set the sampling rate divider
*/
void PicometerController::set_samplingrate_divider() {
	char* error_str_ptr = PicometerControl(SET_SAMPLINGRATE_DIVIDER, SamplingRateDivider, NULL, NULL);

	if (error_str_ptr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		throw std::runtime_error("PicometerController: Sampling rate divider could not be set! Error: " + std::string(error_str_ptr));
	}
	std::cout << "PicometerController: Sampling rate divider successfully set." << std::endl;
}

/**
* @brief Attempts to set the compensation value
*/
void PicometerController::set_compensation() {
	char* error_str_ptr = PicometerControl(SET_COMPENSATION, CompensationConf, NULL, NULL);

	if (error_str_ptr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		throw std::runtime_error("PicometerController: Compensation could not be set! Error: " + std::string(error_str_ptr));
	}
	std::cout << "PicometerController: Compensation successfully set." << std::endl;
}

/**
* @brief Attempts to set the excitation level
*/
void PicometerController::set_excitation_level(unsigned long excitation_level) {
	char* error_str_ptr = PicometerControl(SET_EXCITATION_LEVEL, excitation_level, NULL, NULL);

	if (error_str_ptr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		throw std::runtime_error("PicometerController: Excitation level could not be set! Error: " + std::string(error_str_ptr));
	}
	std::cout << "PicometerController: Excitation level successfully set." << std::endl;
}

/**
* @brief Attempts to set the input gains
*/
void PicometerController::set_input_gains(unsigned long gain_values) {
	char* error_str_ptr = PicometerControl(SET_INPUT_GAINS, gain_values, NULL, NULL);

	if (error_str_ptr != NULL && picometer_status != PicometerStatus::CONNECTED) {
		throw std::runtime_error("PicometerController: Input gains could not be set! Error: " + std::string(error_str_ptr));
	}
	std::cout << "PicometerController: Input gains successfully set." << std::endl;
}