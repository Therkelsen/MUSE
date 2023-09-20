#ifndef DATA_INTERFACE_H
#define DATA_INTERFACE_H

#include <iostream>
#include <utility>
#include <vector>

class DataInterface {
public:
    DataInterface(int num_frequencies, int num_data_points) {
        std::cout << "Data Interface: Initializing." << std::endl;
        raw_sensor_data_.resize(num_frequencies);
        for (int i = 0; i < num_frequencies; i++) {
            raw_sensor_data_.at(i).resize(num_data_points);
        }
    };
    ~DataInterface(){
        std::cout << "Data Interface: Shutting down." << std::endl;
    };

    std::vector<std::vector<double>> get_raw_sensor_data();
    double get_raw_sensor_data_point(int freq_idx, int data_idx);

    void set_raw_sensor_data(std::vector<std::vector<double>> data);
    void set_raw_sensor_data_point(double real, int freq_idx, int data_idx);

    void print_data(std::vector<std::vector<double>> data);

private:
    // private member variables and methods here
    std::vector<std::vector<double>> raw_sensor_data_;
};

#endif // DATA_INTERFACE_H