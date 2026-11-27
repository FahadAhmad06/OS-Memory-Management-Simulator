#include "allocation/best_fit.h"

#include <algorithm>
#include <limits>
#include <stdexcept>
#include <utility>
using namespace std;

namespace memsim::allocation {

namespace {

vector<MemoryBlock> normalize_blocks_best_fit(
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

int next_available_id_best_fit(const vector<MemoryBlock>& blocks) {
    int max_id = 0;
    for (const auto& b : blocks) {
        if (b.id > max_id) {
            max_id = b.id;
        }
    }
    return max_id + 1;
}

} // namespace

AllocationSummary run_best_fit(
    size_t total_memory,
    const vector<MemoryBlock>& initial_blocks,
    const vector<AllocationRequest>& requests
) {
    AllocationSummary summary;
    summary.algorithm = "best_fit";
    summary.total_memory = total_memory;
    summary.memory_blocks = normalize_blocks_best_fit(total_memory, initial_blocks);

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

        int best_index = -1;
        size_t best_waste = numeric_limits<size_t>::max();

        for (size_t i = 0; i < summary.memory_blocks.size(); ++i) {
            const auto& blk = summary.memory_blocks[i];
            if (blk.status == "free" && blk.size >= req.size) {
                const size_t waste = blk.size - req.size;
                if (waste < best_waste) {
                    best_waste = waste;
                    best_index = static_cast<int>(i);
                }
            }
        }

        if (best_index < 0) {
            entry.allocated = false;
            entry.reason = "No free memory block large enough to satisfy request.";
            ++summary.failed_allocations;
            summary.results.push_back(entry);
            continue;
        }

        auto& chosen = summary.memory_blocks[static_cast<size_t>(best_index)];
        const size_t original_size = chosen.size;
        const size_t original_start = chosen.start_address;
        const int new_id = next_available_id_best_fit(summary.memory_blocks);

        chosen.status = "allocated";
        chosen.process_id = req.process_id;
        chosen.requested_size = req.size;
        chosen.size = req.size;
        chosen.internal_fragmentation = 0;

        entry.allocated = true;
        entry.block_id = chosen.id;
        entry.start_address = chosen.start_address;
        entry.block_size = chosen.size;
        entry.internal_fragmentation = chosen.internal_fragmentation;

        if (original_size > req.size) {
            MemoryBlock remainder;
            remainder.id = new_id;
            remainder.status = "free";
            remainder.start_address = original_start + req.size;
            remainder.size = original_size - req.size;
            summary.memory_blocks.insert(
                summary.memory_blocks.begin() + best_index + 1,
                remainder
            );
        }
        entry.reason = "Allocated using Best Fit.";
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

} // namespace memsim::allocation
