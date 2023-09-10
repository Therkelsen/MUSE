#include "../headers/DataInterface.h"
#include <iterator>

/**
    @brief Returns the entire raw_sensor_data_ private member
*/
std::vector<std::vector<std::pair<int, int>>> DataInterface::get_raw_sensor_data(){
    return raw_sensor_data_;
}

/**
    @brief Returns the pair at (freq_idx, data_idx) from the raw_sensor_data_ private member
    @param freq_idx The frequency index from which to return the pair
    @param data_idx The data index from which to return the pair
*/
std::pair<int, int> DataInterface::get_raw_sensor_data_point(int freq_idx, int data_idx){
    return raw_sensor_data_.at(freq_idx).at(data_idx);
}

/**
    @brief Sets the entire raw_sensor_data_ private member
    @param data Vector of vector of pairs, i.e. a 2D matrix with complex numbers.
*/
void DataInterface::set_raw_sensor_data(std::vector<std::vector<std::pair<int, int>>> data) {
        raw_sensor_data_ = data;
}

/**
    @brief Sets a pair in the raw_sensor_data_ private member
    @param real The real value of the complex number
    @param img The imaginary value of the complex number
    @param freq_idx The frequency index at which to update the pair value
    @param data_idx The data index at which to update the pair value
*/
void DataInterface::set_raw_sensor_data_point(int real, int img, int freq_idx, int data_idx) {
        raw_sensor_data_.at(freq_idx).at(data_idx) = {real, img};
}