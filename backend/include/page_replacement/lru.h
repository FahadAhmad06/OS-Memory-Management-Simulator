#ifndef OS_MEM_SIM_PAGE_REPLACEMENT_LRU_H
#define OS_MEM_SIM_PAGE_REPLACEMENT_LRU_H

#include <cstddef>
#include <vector>
#include "page_replacement/fifo.h"
using namespace std;

namespace memsim::page_replacement {

PageReplacementResult run_lru(
    size_t frame_count,
    const vector<int>& reference_string
);

} // namespace memsim::page_replacement

#endif // OS_MEM_SIM_PAGE_REPLACEMENT_LRU_H
