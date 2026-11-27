#include "common/json_handler.h"

#include <cstddef>
#include <stdexcept>
#include <string>
#include <vector>
#include "allocation/best_fit.h"
#include "allocation/first_fit.h"
#include "allocation/worst_fit.h"
#include "comparison/allocation_comparison.h"
#include "comparison/page_replacement_comparison.h"
#include "page_replacement/fifo.h"
#include "page_replacement/lru.h"
#include "page_replacement/optimal.h"
#include "paging/paging.h"
using namespace std;

namespace memsim::common {

namespace {

nlohmann::json make_success(const nlohmann::json& result) {
    return {
        {"success", true},
        {"result", result}
    };
}

nlohmann::json make_error(const string& message) {
    return {
        {"success", false},
        {"error", {
            {"message", message}
        }}
    };
}

size_t parse_size_t_field(const nlohmann::json& obj, const string& key, bool required = true) {
    if (!obj.contains(key)) {
        if (required) {
            throw invalid_argument("Missing required field '" + key + "'.");
        }
        return 0;
    }
    const auto& val = obj.at(key);
    if (val.is_number_unsigned()) {
        return val.get<size_t>();
    }
    if (val.is_number_integer()) {
        const long long signed_val = val.get<long long>();
        if (signed_val < 0) {
            throw invalid_argument("Field '" + key + "' cannot be negative.");
        }
        return static_cast<size_t>(signed_val);
    }
    throw invalid_argument("Field '" + key + "' must be a non-negative integer.");
}

vector<memsim::allocation::MemoryBlock> parse_initial_blocks(const nlohmann::json& payload) {
    vector<memsim::allocation::MemoryBlock> blocks;
    if (!payload.contains("initial_blocks") || payload.at("initial_blocks").is_null()) {
        return blocks;
    }
    const auto& arr = payload.at("initial_blocks");
    if (!arr.is_array()) {
        throw invalid_argument("Field 'initial_blocks' must be an array.");
    }
    for (const auto& item : arr) {
        if (!item.is_object()) {
            throw invalid_argument("Each entry in 'initial_blocks' must be an object.");
        }
        memsim::allocation::MemoryBlock blk;
        if (item.contains("id") && !item.at("id").is_null()) {
            if (!item.at("id").is_number_integer()) {
                throw invalid_argument("Block 'id' must be an integer.");
            }
            blk.id = item.at("id").get<int>();
        }
        if (!item.contains("status") || !item.at("status").is_string()) {
            throw invalid_argument("Block 'status' must be a string.");
        }
        blk.status = item.at("status").get<string>();
        blk.start_address = parse_size_t_field(item, "start_address", true);
        blk.size = parse_size_t_field(item, "size", true);
        if (item.contains("process_id") && !item.at("process_id").is_null()) {
            if (!item.at("process_id").is_string()) {
                throw invalid_argument("Block 'process_id' must be a string.");
            }
            blk.process_id = item.at("process_id").get<string>();
        }
        blk.requested_size = parse_size_t_field(item, "requested_size", false);
        blocks.push_back(blk);
    }
    return blocks;
}

vector<memsim::allocation::AllocationRequest> parse_allocation_requests(const nlohmann::json& payload) {
    if (!payload.contains("requests") || !payload.at("requests").is_array()) {
        throw invalid_argument("Field 'requests' must be an array.");
    }
    vector<memsim::allocation::AllocationRequest> requests;
    for (const auto& item : payload.at("requests")) {
        if (!item.is_object()) {
            throw invalid_argument("Each item in 'requests' must be an object.");
        }
        if (!item.contains("process_id") || !item.at("process_id").is_string()) {
            throw invalid_argument("Request 'process_id' must be a string.");
        }
        memsim::allocation::AllocationRequest req;
        req.process_id = item.at("process_id").get<string>();
        req.size = parse_size_t_field(item, "size", true);
        requests.push_back(req);
    }
    return requests;
}

vector<memsim::paging::PageTableEntry> parse_page_table(const nlohmann::json& payload) {
    vector<memsim::paging::PageTableEntry> table;
    if (!payload.contains("page_table") || payload.at("page_table").is_null()) {
        return table;
    }
    const auto& arr = payload.at("page_table");
    if (!arr.is_array()) {
        throw invalid_argument("Field 'page_table' must be an array.");
    }
    for (const auto& item : arr) {
        if (!item.is_object()) {
            throw invalid_argument("Each entry in 'page_table' must be an object.");
        }
        memsim::paging::PageTableEntry pte;
        pte.page_number = parse_size_t_field(item, "page_number", true);
        if (!item.contains("present") || !item.at("present").is_boolean()) {
            throw invalid_argument("Page table entry 'present' must be a boolean.");
        }
        pte.present = item.at("present").get<bool>();
        if (item.contains("frame_number") && !item.at("frame_number").is_null()) {
            if (!item.at("frame_number").is_number_integer()) {
                throw invalid_argument("Page table entry 'frame_number' must be an integer.");
            }
            pte.frame_number = item.at("frame_number").get<int>();
        } else {
            pte.frame_number = -1;
        }
        if (item.contains("dirty") && !item.at("dirty").is_null()) {
            if (!item.at("dirty").is_boolean()) {
                throw invalid_argument("Page table entry 'dirty' must be a boolean.");
            }
            pte.dirty = item.at("dirty").get<bool>();
        }
        if (item.contains("referenced") && !item.at("referenced").is_null()) {
            if (!item.at("referenced").is_boolean()) {
                throw invalid_argument("Page table entry 'referenced' must be a boolean.");
            }
            pte.referenced = item.at("referenced").get<bool>();
        }
        table.push_back(pte);
    }
    return table;
}

vector<size_t> parse_logical_addresses(const nlohmann::json& payload) {
    if (!payload.contains("logical_addresses") || !payload.at("logical_addresses").is_array()) {
        throw invalid_argument("Field 'logical_addresses' must be an array.");
    }
    vector<size_t> addresses;
    for (const auto& item : payload.at("logical_addresses")) {
        if (item.is_number_unsigned()) {
            addresses.push_back(item.get<size_t>());
        } else if (item.is_number_integer() && item.get<long long>() >= 0) {
            addresses.push_back(static_cast<size_t>(item.get<long long>()));
        } else {
            throw invalid_argument("Each entry in 'logical_addresses' must be a non-negative integer.");
        }
    }
    return addresses;
}

size_t parse_frame_count(const nlohmann::json& payload) {
    const size_t frame_count = parse_size_t_field(payload, "frame_count", true);
    if (frame_count == 0) {
        throw invalid_argument("frame_count must be greater than 0.");
    }
    if (frame_count > 10000) {
        throw invalid_argument("frame_count must not exceed 10000.");
    }
    return frame_count;
}

vector<int> parse_reference_string(const nlohmann::json& payload) {
    if (!payload.contains("reference_string") || !payload.at("reference_string").is_array()) {
        throw invalid_argument("Field 'reference_string' must be an array.");
    }
    vector<int> refs;
    for (const auto& item : payload.at("reference_string")) {
        if (!item.is_number_integer()) {
            throw invalid_argument("Each entry in 'reference_string' must be an integer.");
        }
        if (item.is_number_unsigned() && item.get<unsigned long long>() > 2147483647ULL) {
            throw invalid_argument("Page numbers in 'reference_string' must not exceed 2147483647.");
        }
        const long long page_ll = item.get<long long>();
        if (page_ll < 0) {
            throw invalid_argument("Page numbers in 'reference_string' must be non-negative.");
        }
        if (page_ll > 2147483647LL) {
            throw invalid_argument("Page numbers in 'reference_string' must not exceed 2147483647.");
        }
        refs.push_back(static_cast<int>(page_ll));
    }
    return refs;
}

} // namespace

nlohmann::json handle_json_request(const nlohmann::json& request) {
    try {
        if (!request.is_object()) {
            return make_error("Request root must be a JSON object.");
        }
        if (!request.contains("operation") || !request.at("operation").is_string()) {
            return make_error("Missing or invalid 'operation' field.");
        }

        const string operation = request.at("operation").get<string>();
        nlohmann::json payload = request;
        if (request.contains("data") && request.at("data").is_object()) {
            payload = request.at("data");
        }

        if (operation == "first_fit") {
            const size_t total_memory = parse_size_t_field(payload, "total_memory", true);
            const auto initial_blocks = parse_initial_blocks(payload);
            const auto requests = parse_allocation_requests(payload);
            const auto summary = memsim::allocation::run_first_fit(total_memory, initial_blocks, requests);
            return make_success(memsim::allocation::allocation_summary_to_json(summary));
        }

        if (operation == "best_fit") {
            const size_t total_memory = parse_size_t_field(payload, "total_memory", true);
            const auto initial_blocks = parse_initial_blocks(payload);
            const auto requests = parse_allocation_requests(payload);
            const auto summary = memsim::allocation::run_best_fit(total_memory, initial_blocks, requests);
            return make_success(memsim::allocation::allocation_summary_to_json(summary));
        }

        if (operation == "worst_fit") {
            const size_t total_memory = parse_size_t_field(payload, "total_memory", true);
            const auto initial_blocks = parse_initial_blocks(payload);
            const auto requests = parse_allocation_requests(payload);
            const auto summary = memsim::allocation::run_worst_fit(total_memory, initial_blocks, requests);
            return make_success(memsim::allocation::allocation_summary_to_json(summary));
        }

        if (operation == "paging_translate") {
            const size_t logical_size = parse_size_t_field(payload, "logical_address_space_size", true);
            const size_t physical_size = parse_size_t_field(payload, "physical_memory_size", true);
            const size_t page_size = parse_size_t_field(payload, "page_size", true);
            const auto pt = parse_page_table(payload);
            const auto addrs = parse_logical_addresses(payload);
            const auto res = memsim::paging::run_paging_translation(logical_size, physical_size, page_size, pt, addrs);
            return make_success(memsim::paging::paging_result_to_json(res));
        }

        if (operation == "fifo") {
            const size_t frame_count = parse_frame_count(payload);
            const auto refs = parse_reference_string(payload);
            const auto res = memsim::page_replacement::run_fifo(frame_count, refs);
            return make_success(memsim::page_replacement::page_replacement_result_to_json(res));
        }

        if (operation == "lru") {
            const size_t frame_count = parse_frame_count(payload);
            const auto refs = parse_reference_string(payload);
            const auto res = memsim::page_replacement::run_lru(frame_count, refs);
            return make_success(memsim::page_replacement::page_replacement_result_to_json(res));
        }

        if (operation == "optimal") {
            const size_t frame_count = parse_frame_count(payload);
            const auto refs = parse_reference_string(payload);
            const auto res = memsim::page_replacement::run_optimal(frame_count, refs);
            return make_success(memsim::page_replacement::page_replacement_result_to_json(res));
        }

        if (operation == "compare_allocation") {
            const size_t total_memory = parse_size_t_field(payload, "total_memory", true);
            const auto initial_blocks = parse_initial_blocks(payload);
            const auto requests = parse_allocation_requests(payload);
            const auto comp = memsim::comparison::run_allocation_comparison(total_memory, initial_blocks, requests);
            return make_success(memsim::comparison::allocation_comparison_to_json(comp));
        }

        if (operation == "compare_page_replacement") {
            const size_t frame_count = parse_frame_count(payload);
            const auto refs = parse_reference_string(payload);
            const auto comp = memsim::comparison::run_page_replacement_comparison(frame_count, refs);
            return make_success(memsim::comparison::page_replacement_comparison_to_json(comp));
        }

        return make_error("Unsupported operation: '" + operation + "'.");
    } catch (const exception& ex) {
        return make_error(ex.what());
    } catch (...) {
        return make_error("Unknown internal error occurred.");
    }
}

string process_raw_json_input(const string& raw_input) {
    try {
        if (raw_input.find_first_not_of(" \t\r\n") == string::npos) {
            return make_error("Empty JSON input received on stdin.").dump();
        }
        const nlohmann::json parsed = nlohmann::json::parse(raw_input);
        return handle_json_request(parsed).dump();
    } catch (const nlohmann::json::parse_error& ex) {
        return make_error(string("Invalid JSON input: ") + ex.what()).dump();
    } catch (const exception& ex) {
        return make_error(ex.what()).dump();
    } catch (...) {
        return make_error("Unknown error while processing JSON input.").dump();
    }
}

} // namespace memsim::common
