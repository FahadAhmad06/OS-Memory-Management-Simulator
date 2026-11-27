#include "page_replacement/optimal.h"

#include <algorithm>
#include <limits>
#include <stdexcept>
#include <vector>
using namespace std;

namespace memsim::page_replacement {

PageReplacementResult run_optimal(
    size_t frame_count,
    const vector<int>& reference_string
) {
    if (frame_count == 0) {
        throw invalid_argument("frame_count must be greater than 0.");
    }

    PageReplacementResult result;
    result.algorithm = "optimal";
    result.frame_count = frame_count;
    result.reference_string = reference_string;

    vector<int> frames(frame_count, -1);

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
                step_info.replaced_page = -1;
            } else {
                size_t victim_idx = 0;
                size_t farthest_next_use = 0;
                bool found_never_used = false;

                for (size_t f = 0; f < frame_count; ++f) {
                    const int candidate_page = frames[f];
                    size_t next_pos = numeric_limits<size_t>::max();
                    for (size_t k = i + 1; k < reference_string.size(); ++k) {
                        if (reference_string[k] == candidate_page) {
                            next_pos = k;
                            break;
                        }
                    }

                    if (next_pos == numeric_limits<size_t>::max()) {
                        if (!found_never_used) {
                            found_never_used = true;
                            victim_idx = f;
                        }
                    } else if (!found_never_used && next_pos > farthest_next_use) {
                        farthest_next_use = next_pos;
                        victim_idx = f;
                    }
                }

                step_info.replaced_page = frames[victim_idx];
                frames[victim_idx] = page;
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
