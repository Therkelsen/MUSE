#include "../headers/DataInterface.h"
#include <iterator>

/**
    @brief Returns the entire raw_sensor_data_ private member
    @return Vector of vector of pairs, i.e. a 2D matrix with complex numbers.
*/
std::vector<std::vector<std::pair<double, double>>> DataInterface::get_raw_sensor_data(){
    return raw_sensor_data_;
}

/**
    @brief Returns the pair at (freq_idx, data_idx) from the raw_sensor_data_ private member
    @param freq_idx The frequency index from which to return the pair
    @param data_idx The data index from which to return the pair
    @return Pair of integers, i.e. a complex number.
*/
std::pair<double, double> DataInterface::get_raw_sensor_data_point(int freq_idx, int data_idx){
    return raw_sensor_data_.at(freq_idx).at(data_idx);
}

/**
    @brief Sets the entire raw_sensor_data_ private member
    @param data Vector of vector of pairs, i.e. a 2D matrix with complex numbers.
*/
void DataInterface::set_raw_sensor_data(std::vector<std::vector<std::pair<double, double>>> data) {
        raw_sensor_data_ = data;
}

/**
    @brief Sets a pair in the raw_sensor_data_ private member
    @param real The real value of the complex number
    @param img The imaginary value of the complex number
    @param freq_idx The frequency index at which to update the pair value
    @param data_idx The data index at which to update the pair value
*/
void DataInterface::set_raw_sensor_data_point(double real, double img, int freq_idx, int data_idx) {
        raw_sensor_data_.at(freq_idx).at(data_idx) = {real, img};
}

/**
    @brief Prints the data from the 2D matrix of complex numbers in a human-readable format
    @param data Vector of vector of pairs, i.e. a 2D matrix with complex numbers.
*/
void DataInterface::print_data(std::vector<std::vector<std::pair<double, double>>> data){
    std::cout << "Data point\t";
    for (int i = 0; i < data.size(); i++) {
        std::cout << "Freq " << i + 1 << "\t";
    }
    std::cout << std::endl;
    for (int i = 0; i < data[0].size(); i++) {
        std::cout << i + 1 << "\t\t";
        for (int j = 0; j < data.size(); j++) {
            std::cout << "(" << data[j][i].first << ", " << data[j][i].second << ")\t";
        }
        std::cout << std::endl;
    }
}