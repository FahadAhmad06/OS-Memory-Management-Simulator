#ifndef OS_MEM_SIM_COMPARISON_PAGE_REPLACEMENT_COMPARISON_H
#define OS_MEM_SIM_COMPARISON_PAGE_REPLACEMENT_COMPARISON_H

#include <cstddef>
#include <vector>
#include <nlohmann/json.hpp>
#include "page_replacement/fifo.h"
using namespace std;

namespace memsim::comparison {

struct PageReplacementComparisonResult {
    memsim::page_replacement::PageReplacementResult fifo;
    memsim::page_replacement::PageReplacementResult lru;
    memsim::page_replacement::PageReplacementResult optimal;
};

PageReplacementComparisonResult run_page_replacement_comparison(
    size_t frame_count,
    const vector<int>& reference_string
);

nlohmann::json page_replacement_comparison_to_json(const PageReplacementComparisonResult& comparison);

} // namespace memsim::comparison

#endif // OS_MEM_SIM_COMPARISON_PAGE_REPLACEMENT_COMPARISON_H
