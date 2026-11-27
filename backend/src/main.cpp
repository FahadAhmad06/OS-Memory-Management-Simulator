#include <iostream>
#include <iterator>
#include <string>
#include "common/json_handler.h"
using namespace std;

int main() {
    cin.tie(nullptr);
    const string raw_input(
        (istreambuf_iterator<char>(cin)),
        istreambuf_iterator<char>()
    );

    const string output = memsim::common::process_raw_json_input(raw_input);
    cout << output << '\n';
    cout.flush();
    return 0;
}
