#ifndef OS_MEM_SIM_ALLOCATION_FIRST_FIT_H
#define OS_MEM_SIM_ALLOCATION_FIRST_FIT_H

#include <cstddef>
#include <string>
#include <vector>
#include <nlohmann/json.hpp>

using namespace std;

namespace memsim::allocation {

struct MemoryBlock {
    int id{0};
    string status{"free"}; // "free" or "allocated"
    size_t start_address{0};
    size_t size{0};
    string process_id{};
    size_t requested_size{0};
    size_t internal_fragmentation{0};
};

struct AllocationRequest {
    string process_id;
    size_t size{0};
};

struct AllocationResultEntry {
    string process_id;
    size_t requested_size{0};
    bool allocated{false};
    int block_id{-1};
    size_t start_address{0};
    size_t block_size{0};
    size_t internal_fragmentation{0};
    string reason{};
};

struct AllocationSummary {
    string algorithm;
    size_t total_memory{0};
    size_t allocated_memory{0};
    size_t free_memory{0};
    size_t total_internal_fragmentation{0};
    double memory_utilization{0.0};
    size_t successful_allocations{0};
    size_t failed_allocations{0};
    vector<AllocationResultEntry> results;
    vector<MemoryBlock> memory_blocks;
};

AllocationSummary run_first_fit(
    size_t total_memory,
    const vector<MemoryBlock>& initial_blocks,
    const vector<AllocationRequest>& requests
);

nlohmann::json allocation_summary_to_json(const AllocationSummary& summary);

} // namespace memsim::allocation

#endif // OS_MEM_SIM_ALLOCATION_FIRST_FIT_H
