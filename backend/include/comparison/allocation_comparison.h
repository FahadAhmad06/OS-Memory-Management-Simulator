#ifndef OS_MEM_SIM_COMPARISON_ALLOCATION_COMPARISON_H
#define OS_MEM_SIM_COMPARISON_ALLOCATION_COMPARISON_H

#include <cstddef>
#include <vector>
#include <nlohmann/json.hpp>
#include "allocation/first_fit.h"
using namespace std;

namespace memsim::comparison {

struct AllocationComparisonResult {
    memsim::allocation::AllocationSummary first_fit;
    memsim::allocation::AllocationSummary best_fit;
    memsim::allocation::AllocationSummary worst_fit;
};

AllocationComparisonResult run_allocation_comparison(
    size_t total_memory,
    const vector<memsim::allocation::MemoryBlock>& initial_blocks,
    const vector<memsim::allocation::AllocationRequest>& requests
);

nlohmann::json allocation_comparison_to_json(const AllocationComparisonResult& comparison);

} // namespace memsim::comparison

#endif // OS_MEM_SIM_COMPARISON_ALLOCATION_COMPARISON_H
