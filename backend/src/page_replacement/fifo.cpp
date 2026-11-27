#include "page_replacement/fifo.h"

#include <algorithm>
#include <queue>
#include <stdexcept>
using namespace std;

namespace memsim::page_replacement {

PageReplacementResult run_fifo(
    size_t frame_count,
    const vector<int>& reference_string
) {
    if (frame_count == 0) {
        throw invalid_argument("frame_count must be greater than 0.");
    }

    PageReplacementResult result;
    result.algorithm = "fifo";
    result.frame_count = frame_count;
    result.reference_string = reference_string;

    vector<int> frames(frame_count, -1);
    queue<size_t> fifo_slots;

    for (size_t i = 0; i < reference_string.size(); ++i) {
        const int page = reference_string[i];
        FrameStep step_info;
        step_info.step = i + 1;
        step_info.page = page;

        auto found = find(frames.begin(), frames.end(), page);
        if (found != frames.end()) {
            step_info.hit = true;
            step_info.replaced_page = -1;
            ++result.hits;
        } else {
            step_info.hit = false;
            ++result.faults;

            auto empty_it = find(frames.begin(), frames.end(), -1);
            if (empty_it != frames.end()) {
                const auto idx = static_cast<size_t>(distance(frames.begin(), empty_it));
                frames[idx] = page;
                fifo_slots.push(idx);
                step_info.replaced_page = -1;
            } else {
                const size_t victim_idx = fifo_slots.front();
                fifo_slots.pop();
                step_info.replaced_page = frames[victim_idx];
                frames[victim_idx] = page;
                fifo_slots.push(victim_idx);
            }
        }

        step_info.frames = frames;
        result.steps.push_back(step_info);
    }

    const size_t total_refs = reference_string.size();
    result.hit_ratio = total_refs > 0
        ? static_cast<double>(result.hits) / static_cast<double>(total_refs)
        : 0.0;
    result.fault_ratio = total_refs > 0
        ? static_cast<double>(result.faults) / static_cast<double>(total_refs)
        : 0.0;

    return result;
}

nlohmann::json page_replacement_result_to_json(const PageReplacementResult& result) {
    nlohmann::json steps_json = nlohmann::json::array();
    for (const auto& s : result.steps) {
        steps_json.push_back({
            {"step", s.step},
            {"page", s.page},
            {"hit", s.hit},
            {"replaced_page", s.replaced_page},
            {"frames", s.frames}
        });
    }

    return {
        {"algorithm", result.algorithm},
        {"frame_count", result.frame_count},
        {"reference_string", result.reference_string},
        {"steps", steps_json},
        {"hits", result.hits},
        {"faults", result.faults},
        {"hit_ratio", result.hit_ratio},
        {"fault_ratio", result.fault_ratio}
    };
}

} // namespace memsim::page_replacement
