#include "page_replacement/lru.h"

#include <algorithm>
#include <stdexcept>
#include <vector>
using namespace std;

namespace memsim::page_replacement {

PageReplacementResult run_lru(
    size_t frame_count,
    const vector<int>& reference_string
) {
    if (frame_count == 0) {
        throw invalid_argument("frame_count must be greater than 0.");
    }

    PageReplacementResult result;
    result.algorithm = "lru";
    result.frame_count = frame_count;
    result.reference_string = reference_string;

    vector<int> frames(frame_count, -1);
    vector<size_t> last_used(frame_count, 0);

    for (size_t i = 0; i < reference_string.size(); ++i) {
        const int page = reference_string[i];
        const size_t current_time = i + 1;

        FrameStep step_info;
        step_info.step = current_time;
        step_info.page = page;

        auto found = find(frames.begin(), frames.end(), page);
        if (found != frames.end()) {
            const auto idx = static_cast<size_t>(distance(frames.begin(), found));
            last_used[idx] = current_time;
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
                last_used[idx] = current_time;
                step_info.replaced_page = -1;
            } else {
                size_t lru_idx = 0;
                for (size_t f = 1; f < frame_count; ++f) {
                    if (last_used[f] < last_used[lru_idx]) {
                        lru_idx = f;
                    }
                }
                step_info.replaced_page = frames[lru_idx];
                frames[lru_idx] = page;
                last_used[lru_idx] = current_time;
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

} // namespace memsim::page_replacement
