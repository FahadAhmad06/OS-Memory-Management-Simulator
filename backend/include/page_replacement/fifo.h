#ifndef OS_MEM_SIM_PAGE_REPLACEMENT_FIFO_H
#define OS_MEM_SIM_PAGE_REPLACEMENT_FIFO_H

#include <cstddef>
#include <string>
#include <vector>
#include <nlohmann/json.hpp>
using namespace std;

namespace memsim::page_replacement {

struct FrameStep {
    size_t step{0};
    int page{0};
    bool hit{false};
    int replaced_page{-1};
    vector<int> frames; // -1 indicates an empty frame slot
};

struct PageReplacementResult {
    string algorithm;
    size_t frame_count{0};
    vector<int> reference_string;
    vector<FrameStep> steps;
    size_t hits{0};
    size_t faults{0};
    double hit_ratio{0.0};
    double fault_ratio{0.0};
};

PageReplacementResult run_fifo(
    size_t frame_count,
    const vector<int>& reference_string
);

nlohmann::json page_replacement_result_to_json(const PageReplacementResult& result);

} // namespace memsim::page_replacement

#endif // OS_MEM_SIM_PAGE_REPLACEMENT_FIFO_H
