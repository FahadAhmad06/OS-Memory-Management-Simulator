#ifndef OS_MEM_SIM_COMMON_JSON_HANDLER_H
#define OS_MEM_SIM_COMMON_JSON_HANDLER_H

#include <string>
#include <nlohmann/json.hpp>
using namespace std;

namespace memsim::common {

nlohmann::json handle_json_request(const nlohmann::json& request);
string process_raw_json_input(const string& raw_input);

} // namespace memsim::common

#endif // OS_MEM_SIM_COMMON_JSON_HANDLER_H
