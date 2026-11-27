#include "comparison/page_replacement_comparison.h"

#include "page_replacement/fifo.h"
#include "page_replacement/lru.h"
#include "page_replacement/optimal.h"
using namespace std;

namespace memsim::comparison {

PageReplacementComparisonResult run_page_replacement_comparison(
    size_t frame_count,
    const vector<int>& reference_string
) {
    PageReplacementComparisonResult comparison;
    comparison.fifo = memsim::page_replacement::run_fifo(frame_count, reference_string);
    comparison.lru = memsim::page_replacement::run_lru(frame_count, reference_string);
    comparison.optimal = memsim::page_replacement::run_optimal(frame_count, reference_string);
    return comparison;
}

nlohmann::json page_replacement_comparison_to_json(const PageReplacementComparisonResult& comparison) {
    return {
        {"fifo", memsim::page_replacement::page_replacement_result_to_json(comparison.fifo)},
        {"lru", memsim::page_replacement::page_replacement_result_to_json(comparison.lru)},
        {"optimal", memsim::page_replacement::page_replacement_result_to_json(comparison.optimal)}
    };
}

} // namespace memsim::comparison
