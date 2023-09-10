#include <iostream>
#include "../headers/DataInterface.h"

int main() {
  DataInterface DI(15, 99);
  std::vector<std::vector<std::pair<int, int>>> data = DI.get_raw_sensor_data();
  std::cout << "Data point\t";
    for (int i = 0; i < data.size(); i++) {
        std::cout << "Freq " << i << "\t";
    }
    std::cout << std::endl;
    for (int i = 0; i < data[0].size(); i++) {
        std::cout << i << "\t\t";
        for (int j = 0; j < data.size(); j++) {
            std::cout << "(" << data[j][i].first << ", " << data[j][i].second << ")\t";
        }
        std::cout << std::endl;
    }

  return 0;
}
