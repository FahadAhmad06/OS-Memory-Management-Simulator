#include "comparison/allocation_comparison.h"

#include "allocation/best_fit.h"
#include "allocation/first_fit.h"
#include "allocation/worst_fit.h"
using namespace std;

namespace memsim::comparison {

AllocationComparisonResult run_allocation_comparison(
    size_t total_memory,
    const vector<memsim::allocation::MemoryBlock>& initial_blocks,
    const vector<memsim::allocation::AllocationRequest>& requests
) {
    AllocationComparisonResult comparison;
    comparison.first_fit = memsim::allocation::run_first_fit(total_memory, initial_blocks, requests);
    comparison.best_fit = memsim::allocation::run_best_fit(total_memory, initial_blocks, requests);
    comparison.worst_fit = memsim::allocation::run_worst_fit(total_memory, initial_blocks, requests);
    return comparison;
}

nlohmann::json allocation_comparison_to_json(const AllocationComparisonResult& comparison) {
    return {
        {"first_fit", memsim::allocation::allocation_summary_to_json(comparison.first_fit)},
        {"best_fit", memsim::allocation::allocation_summary_to_json(comparison.best_fit)},
        {"worst_fit", memsim::allocation::allocation_summary_to_json(comparison.worst_fit)}
    };
}

} // namespace memsim::comparison
