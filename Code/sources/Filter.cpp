#include "../headers/Filter.h"

const std::vector<std::vector<std::pair<double, double>>> Filter::get_x(){
    return x_;
}

const std::vector<std::vector<std::pair<double, double>>> Filter::get_c(){
    return c_;
}

std::vector<std::vector<std::pair<double, double>>> Filter::get_y(){
    return y_;
}

size_t Filter::get_input_length(){
    return input_length_;
}

size_t Filter::get_filter_length(){
    return filter_length_;
}

size_t Filter::get_output_length(){
    return output_length_;
}

void Filter::set_y(std::vector<std::vector<std::pair<double, double>>> y){
    y_ = y;
}

void Filter::set_input_length(size_t input_length){
    input_length_ = input_length;
}

void Filter::set_filter_length(size_t filter_length){
    filter_length_ = filter_length;
}

void Filter::set_output_length(size_t output_length){
    output_length_ = output_length;
}

void Filter::set_highpass_filter_coefficients(std::vector<std::vector<std::pair<double, double>>> c) {
    c_ = c;
    filter_length_ = c.size();
}

std::vector<std::vector<std::pair<double, double>>> Filter::fir_filter(Filter& input) {
    const auto x = input.get_x();
    const auto c = input.get_c();
    auto y = input.get_y();

    for (auto i = 0u; i < input.output_length_; ++i) {
        for (auto j = 0u; j < input.filter_length_; ++j) {
            y[i][j].first = 0.0;
            y[i][j].second = 0.0;
            y[i][j].first += x[i][j].first * c[i][j].first;
            y[i][j].second += x[i][j].second * c[i][j].second;
        }
    }

    return y;
}