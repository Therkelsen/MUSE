#include <iostream>
#include "../headers/DataInterface.h"
#include "../headers/Filter.h"

int main() {
  DataInterface DI(15, 99);
  DI.print_data(DI.get_raw_sensor_data());

  // Example coefficients for a high-pass FIR filter of order 5
  std::vector<std::vector<std::pair<double, double>>> c = {
    {{-0.02, -0.02}, {-0.02, 0.98}, {-0.02, -0.02}},
    {{0.0, 0.0}, {0.0, 0.0}, {0.0, 0.0}},
    {{0.02, -0.02}, {0.02, 0.98}, {0.02, -0.02}}};

  Filter F;

  F.set_highpass_filter_coefficients(c);
} 