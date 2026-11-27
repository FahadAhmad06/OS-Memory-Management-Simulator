#include "paging/paging.h"

#include <stdexcept>
#include <string>
#include <unordered_set>
using namespace std;

namespace memsim::paging {

PagingSimulationResult run_paging_translation(
    size_t logical_address_space_size,
    size_t physical_memory_size,
    size_t page_size,
    const vector<PageTableEntry>& initial_page_table,
    const vector<size_t>& logical_addresses
) {
    if (page_size == 0) {
        throw invalid_argument("page_size must be greater than 0.");
    }
    if (logical_address_space_size == 0) {
        throw invalid_argument("logical_address_space_size must be greater than 0.");
    }
    if (physical_memory_size == 0) {
        throw invalid_argument("physical_memory_size must be greater than 0.");
    }
    if (logical_address_space_size % page_size != 0) {
        throw invalid_argument("logical_address_space_size must be a multiple of page_size.");
    }
    if (physical_memory_size % page_size != 0) {
        throw invalid_argument("physical_memory_size must be a multiple of page_size.");
    }

    if (logical_address_space_size / page_size > 1000000) {
        throw invalid_argument("Logical address space may contain at most 1000000 pages.");
    }

    PagingSimulationResult result;
    result.logical_address_space_size = logical_address_space_size;
    result.physical_memory_size = physical_memory_size;
    result.page_size = page_size;
    result.num_pages = logical_address_space_size / page_size;
    result.num_frames = physical_memory_size / page_size;

    result.page_table.resize(result.num_pages);
    for (size_t p = 0; p < result.num_pages; ++p) {
        result.page_table[p].page_number = p;
        result.page_table[p].present = false;
        result.page_table[p].frame_number = -1;
        result.page_table[p].dirty = false;
        result.page_table[p].referenced = false;
    }

    unordered_set<int> mapped_frames;
    unordered_set<size_t> seen_pages;
    for (const auto& entry : initial_page_table) {
        if (!seen_pages.insert(entry.page_number).second) {
            throw invalid_argument("Page " + to_string(entry.page_number) + " appears more than once in the page table.");
        }
        if (entry.present && !mapped_frames.insert(entry.frame_number).second) {
            throw invalid_argument("Frame " + to_string(entry.frame_number) + " is mapped by more than one page.");
        }
        if (entry.page_number >= result.num_pages) {
            throw invalid_argument("Page table entry page_number out of range.");
        }
        if (entry.present) {
            if (entry.frame_number < 0 || static_cast<size_t>(entry.frame_number) >= result.num_frames) {
                throw invalid_argument("Page table entry frame_number out of physical frame range.");
            }
        }
        auto& target = result.page_table[entry.page_number];
        target.present = entry.present;
        target.frame_number = entry.present ? entry.frame_number : -1;
        target.dirty = entry.dirty;
        target.referenced = entry.referenced;
    }

    for (size_t addr : logical_addresses) {
        TranslationResult tr;
        tr.logical_address = addr;

        if (addr >= logical_address_space_size) {
            tr.valid = false;
            tr.present = false;
            tr.frame_number = -1;
            tr.error = "Logical address exceeds logical address space size.";
            result.translations.push_back(tr);
            continue;
        }

        const size_t page_num = addr / page_size;
        const size_t offset = addr % page_size;
        tr.page_number = page_num;
        tr.offset = offset;

        auto& pte = result.page_table[page_num];
        tr.present = pte.present;
        tr.frame_number = pte.frame_number;

        if (!pte.present || pte.frame_number < 0) {
            tr.valid = false;
            tr.error = "Page not present in physical memory (page fault).";
            result.translations.push_back(tr);
            continue;
        }

        pte.referenced = true;
        tr.valid = true;
        tr.physical_address = static_cast<size_t>(pte.frame_number) * page_size + offset;
        result.translations.push_back(tr);
    }

    unordered_set<int> distinct_used_frames;
    for (const auto& pte : result.page_table) {
        if (pte.present && pte.frame_number >= 0) {
            distinct_used_frames.insert(pte.frame_number);
        }
    }

    result.used_frames = distinct_used_frames.size();
    result.free_frames = result.num_frames >= result.used_frames
        ? result.num_frames - result.used_frames
        : 0;
    result.frame_utilization = result.num_frames > 0
        ? (static_cast<double>(result.used_frames) / static_cast<double>(result.num_frames)) * 100.0
        : 0.0;

    return result;
}

nlohmann::json paging_result_to_json(const PagingSimulationResult& result) {
    nlohmann::json pt_json = nlohmann::json::array();
    for (const auto& pte : result.page_table) {
        pt_json.push_back({
            {"page_number", pte.page_number},
            {"present", pte.present},
            {"frame_number", pte.frame_number},
            {"dirty", pte.dirty},
            {"referenced", pte.referenced}
        });
    }

    nlohmann::json tr_json = nlohmann::json::array();
    for (const auto& tr : result.translations) {
        tr_json.push_back({
            {"logical_address", tr.logical_address},
            {"page_number", tr.page_number},
            {"offset", tr.offset},
            {"present", tr.present},
            {"frame_number", tr.frame_number},
            {"valid", tr.valid},
            {"physical_address", tr.physical_address},
            {"error", tr.error}
        });
    }

    return {
        {"logical_address_space_size", result.logical_address_space_size},
        {"physical_memory_size", result.physical_memory_size},
        {"page_size", result.page_size},
        {"num_pages", result.num_pages},
        {"num_frames", result.num_frames},
        {"used_frames", result.used_frames},
        {"free_frames", result.free_frames},
        {"frame_utilization", result.frame_utilization},
        {"page_table", pt_json},
        {"translations", tr_json}
    };
}

} // namespace memsim::paging
