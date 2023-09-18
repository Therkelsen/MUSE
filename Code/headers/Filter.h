#ifndef FILTER_H
#define FILTER_H
#include <cstddef>
#include <vector>
#include <utility>
// #include <vcruntime.h>
// #include <xutility>

/** 
    @brief Class for a FIIR filter.
    x_ needs to have n-1 zeroes padded at the end, where n is the filters length, for the convolution to work.
    @param x_ Input signal 
    @param c_ Reversed filter coefficient
    @param y_ Array for output
    @return 
*/

class Filter {
    private:
        std::vector<std::vector<std::pair<double, double>>> x_;
        size_t input_length_;
        std::vector<std::vector<std::pair<double, double>>> c_;
        size_t filter_length_;
        std::vector<std::vector<std::pair<double, double>>> y_;
        size_t output_length_;
 
    public:
        Filter(std::vector<std::vector<std::pair<double, double>>> x, std::vector<std::vector<std::pair<double, double>>> c, std::vector<std::vector<std::pair<double, double>>> y, size_t input_length, size_t filter_length, size_t output_length) {
            x_ = x;
            c_ = c;
            y_ = y;
            input_length_ = input_length;
            filter_length_ = filter_length;
            output_length_ = filter_length;
        };

        Filter() {
            x_.resize(1);
            x_.at(0).resize(1);
            c_.resize(1);
            c_.at(0).resize(1);
            y_.resize(1);
            y_.at(0).resize(1);
            input_length_ = 0;
            filter_length_ = 0;
            output_length_ = 0;
        }

        const std::vector<std::vector<std::pair<double, double>>> get_x();
        const std::vector<std::vector<std::pair<double, double>>> get_c();
        std::vector<std::vector<std::pair<double, double>>> get_y();
        size_t get_input_length();
        size_t get_filter_length();
        size_t get_output_length();

        void set_y(std::vector<std::vector<std::pair<double, double>>> y);
        void set_input_length(size_t input_length);
        void set_filter_length(size_t filter_length);
        void set_output_length(size_t output_length);
        void set_highpass_filter_coefficients(std::vector<std::vector<std::pair<double, double>>> c);

        std::vector<std::vector<std::pair<double, double>>> fir_filter(Filter& input);
 
};

#endif //FILTER_H