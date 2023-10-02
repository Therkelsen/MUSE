#ifndef UTILS_H
#define UTILS_H

#include <utility>

namespace utils {
	enum class MainStatus {
		IDLE,
		OFFLINE_MODE,
		COLLECTING,
		SAVING,
		CONTINUOUS,
		STOPPING,
	};

	bool file_exists(const std::string& path) {
		std::ifstream file(path);
		return file.good();
	}

	void write_data_to_csv(const std::vector<std::vector<float>>& data, const std::string& path) {
		// Check if the file exists before attempting to delete it
		if (utils::file_exists(path)) {
			if (std::remove(path.c_str()) != 0) {
				std::perror("Error deleting the existing file");
				return;
			}
		}

		std::ofstream file(path);

		if (!file.is_open()) {
			std::cerr << "Failed to open the file: " << path << std::endl;
			return;
		}

		// Write header row
		file << "\"freq_1\", \"freq_2\", \"freq_3\", \"freq_4\", \"freq_5\", \"freq_6\", \"freq_7\", \"freq_8\", \"freq_9\", \"freq_10\", \"freq_11\", \"freq_12\", \"freq_13\", \"freq_14\", \"freq_15\"\n";

		// Write data rows
		for (const std::vector<float>& row : data) {
			for (size_t i = 0; i < row.size(); ++i) {
				file << row[i];
				if (i < row.size() - 1) {
					file << ",";
				}
			}
			file << "\n";
		}

		file.close();
		std::cout << "Data has been written to " << path << std::endl;
	}

	std::vector<float> get_filter_coefficients(const std::string& coefficients_file) {
		// Check if the file exists
		if (!utils::file_exists(coefficients_file)) {
			throw std::runtime_error("Error loading file: " + coefficients_file + "\nExiting...");
			return {};
		}

		// Open the file for reading
		std::ifstream file(coefficients_file);
		if (!file.is_open()) {
			throw std::runtime_error("Failed to open the file: " + coefficients_file + "\nExiting...");
			return {};
		}

		std::string line;
		std::vector<float> filter_coefficients;  // Changed the type to a single-dimensional vector

		// Read and process each line of the file
		while (std::getline(file, line)) {
			std::istringstream ss(line);
			std::string cell;

			// Split the line by commas and convert to floats
			while (std::getline(ss, cell, ',')) {
				try {
					float value = std::stof(cell);
					// std::cout << "value: " << value << "\n" << std::endl;
					filter_coefficients.push_back(value);  // Push coefficients into the single-dimensional vector
				}
				catch (const std::invalid_argument& e) {
					// Handle conversion error
					std::cerr << "Error converting data: " << e.what() << std::endl;
					continue; // Skip this cell
				}
			}
		}

		file.close();
		return filter_coefficients;  // Return the single-dimensional vector of coefficients
	}

	std::pair<std::vector<std::vector<float>>, std::vector<std::vector<float>>> collect_data(PicometerController& PC, FIRFilter filter, std::vector<std::vector<float>>& input_signal, std::vector<std::vector<float>>& output_signal) {
		if (PC.picometer_status == PicometerController::PicometerStatus::CONNECTED) {
			std::vector<float> input_row;
			std::vector<float> output_row;

			// Collect data from the picometer
			input_row = PC.get_data().first;

			// Apply the filter to the input data
			output_row = apply_filter(&filter, input_row);

			// Append the collected data to input_signal and output_signal
			input_signal.emplace_back(input_row);
			output_signal.emplace_back(output_row);

			return { input_signal, output_signal };
		}
		return { input_signal, output_signal };  // Return the unchanged signals if not connected
	}

	void collect_data_from_file(FIRFilter& filter, const std::string& input_file, std::vector<std::vector<float>>& raw, std::vector<std::vector<float>>& filtered) {
		// Check if the file exists
		if (!utils::file_exists(input_file)) {
			throw std::runtime_error("Error loading file: " + input_file + "\nExiting...");
			return;
		}

		// Open the file for reading
		std::ifstream file(input_file);
		if (!file.is_open()) {
			throw std::runtime_error("Error loading file: " + input_file + "\nExiting...");
			return;
		}

		std::string line;
		raw.clear();

		// Read and process each line of the file
		bool isHeader = true;  // Flag to skip the header row
		while (std::getline(file, line)) {
			if (isHeader) {
				isHeader = false;
				continue;  // Skip the header row
			}

			std::vector<float> row;
			std::istringstream ss(line);
			std::string cell;

			// Split the line by commas and convert to floats
			while (std::getline(ss, cell, ',')) {
				try {
					float value = std::stof(cell);
					//std::cout << "value: " << value << "\n" << std::endl;
					row.push_back(value);
				}
				catch (const std::invalid_argument& e) {
					// Handle conversion error
					std::cerr << "Error converting data: " << e.what() << std::endl;
					continue; // Skip this cell
				}
			}
			raw.emplace_back(row);
			filtered.emplace_back(apply_filter(&filter, row));
		}

		file.close();
	}
}
#endif // UTILS_H

