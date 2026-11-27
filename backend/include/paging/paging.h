#ifndef OS_MEM_SIM_PAGING_PAGING_H
#define OS_MEM_SIM_PAGING_PAGING_H

#include <cstddef>
#include <string>
#include <vector>
#include <nlohmann/json.hpp>
using namespace std;

namespace memsim::paging {

struct PageTableEntry {
    size_t page_number{0};
    bool present{false};
    int frame_number{-1};
    bool dirty{false};
    bool referenced{false};
};

struct TranslationResult {
    size_t logical_address{0};
    size_t page_number{0};
    size_t offset{0};
    bool present{false};
    int frame_number{-1};
    bool valid{false};
    size_t physical_address{0};
    string error{};
};

struct PagingSimulationResult {
    size_t logical_address_space_size{0};
    size_t physical_memory_size{0};
    size_t page_size{0};
    size_t num_pages{0};
    size_t num_frames{0};
    size_t used_frames{0};
    size_t free_frames{0};
    double frame_utilization{0.0};
    vector<PageTableEntry> page_table;
    vector<TranslationResult> translations;
};

PagingSimulationResult run_paging_translation(
    size_t logical_address_space_size,
    size_t physical_memory_size,
    size_t page_size,
    const vector<PageTableEntry>& initial_page_table,
    const vector<size_t>& logical_addresses
);

nlohmann::json paging_result_to_json(const PagingSimulationResult& result);

} // namespace memsim::paging

#endif // OS_MEM_SIM_PAGING_PAGING_H
