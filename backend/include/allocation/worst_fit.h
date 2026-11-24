#ifndef OS_MEM_SIM_ALLOCATION_WORST_FIT_H
#define OS_MEM_SIM_ALLOCATION_WORST_FIT_H

#include <cstddef>
#include <vector>
#include "allocation/first_fit.h"
using namespace std;

namespace memsim::allocation {

AllocationSummary run_worst_fit(
    size_t total_memory,
    const vector<MemoryBlock>& initial_blocks,
    const vector<AllocationRequest>& requests
);

} // namespace memsim::allocation

#endif // OS_MEM_SIM_ALLOCATION_WORST_FIT_H
