#include "allocation/first_fit.h"

#include <algorithm>
#include <stdexcept>
#include <utility>
using namespace std;

namespace memsim::allocation {

namespace {

vector<MemoryBlock> normalize_blocks(
    size_t total_memory,
    const vector<MemoryBlock>& initial_blocks
) {
    if (total_memory == 0) {
        throw invalid_argument("total_memory must be greater than 0.");
    }

    if (initial_blocks.empty()) {
        MemoryBlock initial;
        initial.id = 1;
        initial.status = "free";
        initial.start_address = 0;
        initial.size = total_memory;
        initial.process_id = "";
        initial.requested_size = 0;
        initial.internal_fragmentation = 0;
        return {initial};
    }

    vector<MemoryBlock> blocks = initial_blocks;
    sort(blocks.begin(), blocks.end(), [](const MemoryBlock& a, const MemoryBlock& b) {
        return a.start_address < b.start_address;
    });

    size_t expected_start = 0;
    int next_id = 1;
    vector<MemoryBlock> normalized;
    normalized.reserve(blocks.size() + 1);

    for (auto blk : blocks) {
        if (blk.size == 0) {
            throw invalid_argument("Memory block size must be greater than 0.");
        }
        if (blk.status != "free" && blk.status != "allocated") {
            throw invalid_argument("Memory block status must be 'free' or 'allocated'.");
        }
        if (blk.start_address < expected_start) {
            throw invalid_argument("Memory blocks overlap or are out of range.");
        }
        if (blk.start_address > expected_start) {
            MemoryBlock gap;
            gap.id = next_id++;
            gap.status = "free";
            gap.start_address = expected_start;
            gap.size = blk.start_address - expected_start;
            normalized.push_back(gap);
        }
        if (blk.start_address + blk.size > total_memory) {
            throw invalid_argument("Memory block exceeds total_memory.");
        }
        if (blk.id <= 0) {
            blk.id = next_id++;
        } else {
            next_id = max(next_id, blk.id + 1);
        }
        if (blk.status == "free") {
            blk.process_id.clear();
            blk.requested_size = 0;
            blk.internal_fragmentation = 0;
        } else {
            if (blk.requested_size == 0) {
                blk.requested_size = blk.size;
            }
            if (blk.requested_size > blk.size) {
                throw invalid_argument("Allocated block requested_size cannot exceed block size.");
            }
            blk.internal_fragmentation = blk.size - blk.requested_size;
        }
        expected_start = blk.start_address + blk.size;
        normalized.push_back(move(blk));
    }

    if (expected_start < total_memory) {
        MemoryBlock tail;
        tail.id = next_id++;
        tail.status = "free";
        tail.start_address = expected_start;
        tail.size = total_memory - expected_start;
        normalized.push_back(tail);
    }

    return normalized;
}

int next_available_id(const vector<MemoryBlock>& blocks) {
    int max_id = 0;
    for (const auto& b : blocks) {
        if (b.id > max_id) {
            max_id = b.id;
        }
    }
    return max_id + 1;
}

} // namespace

AllocationSummary run_first_fit(
    size_t total_memory,
    const vector<MemoryBlock>& initial_blocks,
    const vector<AllocationRequest>& requests
) {
    AllocationSummary summary;
    summary.algorithm = "first_fit";
    summary.total_memory = total_memory;
    summary.memory_blocks = normalize_blocks(total_memory, initial_blocks);

    for (const auto& req : requests) {
        AllocationResultEntry entry;
        entry.process_id = req.process_id;
        entry.requested_size = req.size;

        if (req.process_id.empty()) {
            entry.allocated = false;
            entry.reason = "Process ID must not be empty.";
            ++summary.failed_allocations;
            summary.results.push_back(entry);
            continue;
        }

        if (req.size == 0) {
            entry.allocated = false;
            entry.reason = "Requested allocation size must be greater than 0.";
            ++summary.failed_allocations;
            summary.results.push_back(entry);
            continue;
        }

        int target_index = -1;
        for (size_t i = 0; i < summary.memory_blocks.size(); ++i) {
            const auto& blk = summary.memory_blocks[i];
            if (blk.status == "free" && blk.size >= req.size) {
                target_index = static_cast<int>(i);
                break;
            }
        }

        if (target_index < 0) {
            entry.allocated = false;
            entry.reason = "No free memory block large enough to satisfy request.";
            ++summary.failed_allocations;
            summary.results.push_back(entry);
            continue;
        }

        auto& chosen = summary.memory_blocks[static_cast<size_t>(target_index)];
        const size_t original_size = chosen.size;
        const size_t original_start = chosen.start_address;
        const int new_id = next_available_id(summary.memory_blocks);

        chosen.status = "allocated";
        chosen.process_id = req.process_id;
        chosen.requested_size = req.size;
        chosen.size = req.size;
        chosen.internal_fragmentation = 0;

        if (original_size > req.size) {
            MemoryBlock remainder;
            remainder.id = new_id;
            remainder.status = "free";
            remainder.start_address = original_start + req.size;
            remainder.size = original_size - req.size;
            summary.memory_blocks.insert(
                summary.memory_blocks.begin() + target_index + 1,
                remainder
            );
        }

        entry.allocated = true;
        entry.block_id = chosen.id;
        entry.start_address = chosen.start_address;
        entry.block_size = chosen.size;
        entry.internal_fragmentation = chosen.internal_fragmentation;
        entry.reason = "Allocated using First Fit.";
        ++summary.successful_allocations;
        summary.results.push_back(entry);
    }

    size_t alloc_mem = 0;
    size_t free_mem = 0;
    size_t total_frag = 0;

    for (const auto& blk : summary.memory_blocks) {
        if (blk.status == "allocated") {
            alloc_mem += blk.size;
            total_frag += blk.internal_fragmentation;
        } else {
            free_mem += blk.size;
        }
    }

    summary.allocated_memory = alloc_mem;
    summary.free_memory = free_mem;
    summary.total_internal_fragmentation = total_frag;
    summary.memory_utilization = summary.total_memory > 0
        ? (static_cast<double>(alloc_mem) / static_cast<double>(summary.total_memory)) * 100.0
        : 0.0;

    return summary;
}

nlohmann::json allocation_summary_to_json(const AllocationSummary& summary) {
    nlohmann::json results_json = nlohmann::json::array();
    for (const auto& r : summary.results) {
        results_json.push_back({
            {"process_id", r.process_id},
            {"requested_size", r.requested_size},
            {"allocated", r.allocated},
            {"block_id", r.block_id},
            {"start_address", r.start_address},
            {"block_size", r.block_size},
            {"internal_fragmentation", r.internal_fragmentation},
            {"reason", r.reason}
        });
    }

    nlohmann::json blocks_json = nlohmann::json::array();
    for (const auto& b : summary.memory_blocks) {
        blocks_json.push_back({
            {"id", b.id},
            {"status", b.status},
            {"start_address", b.start_address},
            {"size", b.size},
            {"process_id", b.process_id},
            {"requested_size", b.requested_size},
            {"internal_fragmentation", b.internal_fragmentation}
        });
    }

    return {
        {"algorithm", summary.algorithm},
        {"total_memory", summary.total_memory},
        {"allocated_memory", summary.allocated_memory},
        {"free_memory", summary.free_memory},
        {"total_internal_fragmentation", summary.total_internal_fragmentation},
        {"memory_utilization", summary.memory_utilization},
        {"successful_allocations", summary.successful_allocations},
        {"failed_allocations", summary.failed_allocations},
        {"results", results_json},
        {"memory_blocks", blocks_json}
    };
}

} // namespace memsim::allocation
