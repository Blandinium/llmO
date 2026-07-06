#include "benchmarks.h"

#include <iostream>
#include <chrono>
#include <array>
#include <filesystem>
#include <ctime>
#include <sys/resource.h>
#include <vector>
#include <string>
#include <fstream>
#include <unistd.h>

constexpr std::int64_t target_wall_us = 30'000'000;
constexpr std::int64_t min_probe_wall_us = 500'000;
constexpr std::uint64_t min_iterations = 1;
constexpr std::uint64_t default_max_iterations = 10'000'000;

using Clock = std::chrono::steady_clock;
using TimePoint = std::chrono::time_point<Clock>;

constexpr int64_t unavailable_time_us = -1;

struct ResourceSnapshot {
    TimePoint wall_time;
    int64_t process_cpu_us = unavailable_time_us;
    int64_t thread_cpu_us = unavailable_time_us;
    rusage usage{};
};

int64_t to_microseconds(const timespec& value) {
    return static_cast<int64_t>(value.tv_sec) * 1'000'000 +
        static_cast<int64_t>(value.tv_nsec / 1'000);
}

int64_t to_microseconds(const timeval& value) {
    return static_cast<int64_t>(value.tv_sec) * 1'000'000 +
        static_cast<int64_t>(value.tv_usec);
}

int64_t read_clock_us(clockid_t clock_id) {
    timespec value{};
    if (clock_gettime(clock_id, &value) != 0) {
        return unavailable_time_us;
    }

    return to_microseconds(value);
}

ResourceSnapshot take_resource_snapshot() {
    ResourceSnapshot snapshot{};
    snapshot.wall_time = Clock::now();
    snapshot.process_cpu_us = read_clock_us(CLOCK_PROCESS_CPUTIME_ID);
    snapshot.thread_cpu_us = read_clock_us(CLOCK_THREAD_CPUTIME_ID);
    getrusage(RUSAGE_SELF, &snapshot.usage);
    return snapshot;
}

int64_t elapsed_us(int64_t end, int64_t start) {
    if (end == unavailable_time_us || start == unavailable_time_us) {
        return unavailable_time_us;
    }

    return end - start;
}

std::uint64_t estimate_iterations_for_target(
    std::uint64_t probe_iterations,
    std::int64_t probe_wall_us,
    std::int64_t target_wall_us,
    std::uint64_t max_iterations
) {
    if (probe_wall_us <= 0) {
        return probe_iterations;
    }

    double estimated = static_cast<double>(probe_iterations) *
                       static_cast<double>(target_wall_us) /
                       static_cast<double>(probe_wall_us);

    std::uint64_t result = static_cast<std::uint64_t>(estimated);
    if (result < min_iterations) {
        result = min_iterations;
    }
    if (result > max_iterations) {
        result = max_iterations;
    }
    return result;
}

struct CalibrationResult {
    std::uint64_t probe_iterations;
    std::int64_t probe_wall_us;
    std::uint64_t measured_iterations;
    std::uint64_t probe_checksum;
};

template <typename ProbeBody>
CalibrationResult calibrate_iterations(
    ProbeBody&& probe_body,
    std::uint64_t initial_probe_iterations,
    std::uint64_t max_probe_iterations,
    std::uint64_t max_measured_iterations
) {
    std::uint64_t probe_iterations = initial_probe_iterations;
    std::int64_t probe_wall_us = 0;
    std::uint64_t probe_checksum = 0;

    while (true) {
        const ResourceSnapshot start = take_resource_snapshot();
        probe_checksum = probe_body(probe_iterations);
        const ResourceSnapshot end = take_resource_snapshot();

        probe_wall_us = std::chrono::duration_cast<std::chrono::microseconds>(
            end.wall_time - start.wall_time
        ).count();

        if (probe_wall_us >= min_probe_wall_us || probe_iterations >= max_probe_iterations) {
            break;
        }

        std::uint64_t next_iterations = probe_iterations * 2;
        if (probe_wall_us > 0) {
            // If we are very far from min_probe_wall_us, we can jump more aggressively
            // but let's keep it simple and safe. Doubling is fine.
        }

        if (next_iterations > max_probe_iterations) {
            next_iterations = max_probe_iterations;
        }

        if (next_iterations == probe_iterations) {
            break;
        }
        probe_iterations = next_iterations;
    }

    std::uint64_t measured_iterations = estimate_iterations_for_target(
        probe_iterations,
        probe_wall_us,
        target_wall_us,
        max_measured_iterations
    );

    return {probe_iterations, probe_wall_us, measured_iterations, probe_checksum};
}

void print_common_benchmark_metrics(
    const char* benchmark_name,
    std::uint64_t min_input_n,
    std::uint64_t max_input_n,
    std::uint64_t case_count,
    const CalibrationResult& cal,
    std::uint64_t checksum,
    const ResourceSnapshot& start,
    const ResourceSnapshot& end
) {
    const std::uint64_t iterations = cal.measured_iterations;
    const auto wall_us = std::chrono::duration_cast<std::chrono::microseconds>(
        end.wall_time - start.wall_time
    ).count();
    const auto user_cpu_us =
        to_microseconds(end.usage.ru_utime) - to_microseconds(start.usage.ru_utime);
    const auto system_cpu_us =
        to_microseconds(end.usage.ru_stime) - to_microseconds(start.usage.ru_stime);
    const double calls_per_second = wall_us > 0
        ? static_cast<double>(iterations) * 1'000'000.0 / static_cast<double>(wall_us)
        : 0.0;

    std::cout << "benchmark=" << benchmark_name << '\n'
              << "target_wall_us=" << target_wall_us << '\n'
              << "min_probe_wall_us=" << min_probe_wall_us << '\n'
              << "probe_iterations=" << cal.probe_iterations << '\n'
              << "probe_wall_us=" << cal.probe_wall_us << '\n'
              << "probe_checksum=" << cal.probe_checksum << '\n'
              << "input_n=" << max_input_n << '\n'
              << "case_count=" << case_count << '\n'
              << "min_input_n=" << min_input_n << '\n'
              << "max_input_n=" << max_input_n << '\n'
              << "iterations=" << iterations << '\n'
              << "checksum=" << checksum << '\n'
              << "wall_us=" << wall_us << '\n'
              << "process_cpu_us="
              << elapsed_us(end.process_cpu_us, start.process_cpu_us) << '\n'
              << "thread_cpu_us="
              << elapsed_us(end.thread_cpu_us, start.thread_cpu_us) << '\n'
              << "user_cpu_us=" << user_cpu_us << '\n'
              << "system_cpu_us=" << system_cpu_us << '\n'
              << "calls_per_second=" << calls_per_second << '\n'
              << "max_rss_kb=" << end.usage.ru_maxrss << '\n'
              << "minor_faults="
              << end.usage.ru_minflt - start.usage.ru_minflt << '\n'
              << "major_faults="
              << end.usage.ru_majflt - start.usage.ru_majflt << '\n'
              << "voluntary_context_switches="
              << end.usage.ru_nvcsw - start.usage.ru_nvcsw << '\n'
              << "involuntary_context_switches="
              << end.usage.ru_nivcsw - start.usage.ru_nivcsw << '\n';
}

std::uint64_t consume_formatted_list(const SutApi& api, char* value) {
    if (value == nullptr) {
        return 0;
    }

    std::uint64_t checksum = 1469598103934665603ULL;
    for (const unsigned char* cursor = reinterpret_cast<unsigned char*>(value);
         *cursor != '\0';
         ++cursor) {
        checksum ^= *cursor;
        checksum *= 1099511628211ULL;
    }

    api.free_string(value);
    return checksum;
}

std::vector<int> make_format_input(std::size_t size, int salt) {
    std::vector<int> input;
    input.reserve(size);

    for (std::size_t i = 0; i < size; ++i) {
        int value = static_cast<int>(((i * 37 + salt * 101) % 2001) - 1000);
        input.push_back(value);
    }

    return input;
}

struct RepeatedSortCase {
    std::vector<int> input;
    int rounds;
};

std::vector<int> make_values(std::size_t size, int salt, int modulo) {
    std::vector<int> values;
    values.reserve(size);

    for (std::size_t i = 0; i < size; ++i) {
        int value = static_cast<int>(((i * 37 + salt * 101) % modulo) - modulo / 2);
        values.push_back(value);
    }

    return values;
}

struct CountMatchesCase {
    std::vector<int> allowed;
    std::vector<int> queries;
};

struct TopWordsCase {
    std::filesystem::path file_path;
    std::vector<std::string> ignore_words;
    std::size_t max_results;
};

void benchmark_fibonacci(const SutApi& api) {
    std::array<std::uint64_t, 8> inputs = {
        30, 31, 32, 33, 34, 35, 36, 37
    };

    const auto cal = calibrate_iterations(
        [&](std::uint64_t iterations) {
            std::uint64_t c = 0;
            for (std::uint64_t i = 0; i < iterations; ++i) {
                c += api.fibonacci(inputs[i % inputs.size()]);
            }
            return c;
        },
        8,
        default_max_iterations,
        default_max_iterations
    );

    std::uint64_t checksum = 0;
    const ResourceSnapshot start = take_resource_snapshot();
    for (std::uint64_t i = 0; i < cal.measured_iterations; ++i) {
        checksum += api.fibonacci(inputs[i % inputs.size()]);
    }
    const ResourceSnapshot end = take_resource_snapshot();

    print_common_benchmark_metrics(
        "fibonacci",
        30,
        37,
        inputs.size(),
        cal,
        checksum,
        start,
        end
    );
}

void benchmark_format_list(const SutApi& api) {
    std::vector<std::vector<int>> cases;
    std::array<std::size_t, 4> sizes = {768, 1024, 1280, 1536};
    for (int salt = 1; salt <= 8; ++salt) {
        cases.push_back(make_format_input(sizes[(salt - 1) % sizes.size()], salt));
    }

    const auto cal = calibrate_iterations(
        [&](std::uint64_t iterations) {
            std::uint64_t c = 0;
            for (std::uint64_t i = 0; i < iterations; ++i) {
                const auto& input = cases[i % cases.size()];
                c += consume_formatted_list(
                    api,
                    api.format_list(input.data(), input.size())
                );
            }
            return c;
        },
        50,
        default_max_iterations,
        default_max_iterations
    );

    std::uint64_t checksum = 0;
    const ResourceSnapshot start = take_resource_snapshot();
    for (std::uint64_t i = 0; i < cal.measured_iterations; ++i) {
        const auto& input = cases[i % cases.size()];
        checksum += consume_formatted_list(
            api,
            api.format_list(input.data(), input.size())
        );
    }
    const ResourceSnapshot end = take_resource_snapshot();

    print_common_benchmark_metrics(
        "format_list",
        768,
        1536,
        cases.size(),
        cal,
        checksum,
        start,
        end
    );
}

void benchmark_repeated_sort(const SutApi& api) {
    std::vector<RepeatedSortCase> cases;
    std::array<std::size_t, 4> sizes = {1024, 1536, 2048, 2560};
    std::array<int, 4> rounds_list = {1, 2, 3, 5};

    for (int salt = 1; salt <= 8; ++salt) {
        std::size_t size = sizes[(salt - 1) % sizes.size()];
        std::vector<int> input(size);
        for (std::size_t i = 0; i < size; ++i) {
            input[i] = static_cast<int>((i * 48271 + salt * 137) % 100003) - 50'000;
        }
        cases.push_back({std::move(input), rounds_list[(salt - 1) % rounds_list.size()]});
    }

    const auto cal = calibrate_iterations(
        [&](std::uint64_t iterations) {
            std::uint64_t c = 0;
            for (std::uint64_t i = 0; i < iterations; ++i) {
                const auto& case_item = cases[i % cases.size()];
                c += static_cast<std::uint64_t>(
                    api.repeated_sort(case_item.input.data(), case_item.input.size(), case_item.rounds)
                );
            }
            return c;
        },
        8,
        default_max_iterations,
        default_max_iterations
    );

    std::uint64_t checksum = 0;
    const ResourceSnapshot start = take_resource_snapshot();
    for (std::uint64_t i = 0; i < cal.measured_iterations; ++i) {
        const auto& c = cases[i % cases.size()];
        checksum += static_cast<std::uint64_t>(
            api.repeated_sort(c.input.data(), c.input.size(), c.rounds)
        );
    }
    const ResourceSnapshot end = take_resource_snapshot();

    print_common_benchmark_metrics(
        "repeated_sort",
        1024,
        2560,
        cases.size(),
        cal,
        checksum,
        start,
        end
    );
}

void benchmark_count_matches(const SutApi& api) {
    std::vector<CountMatchesCase> cases;
    std::array<std::size_t, 3> allowed_sizes = {2048, 4096, 8192};
    std::array<std::size_t, 2> queries_sizes = {16384, 32768};

    for (int salt = 1; salt <= 6; ++salt) {
        std::size_t a_size = allowed_sizes[(salt - 1) % allowed_sizes.size()];
        std::size_t q_size = queries_sizes[(salt - 1) % queries_sizes.size()];

        auto allowed = make_values(a_size, salt, 10000);
        auto queries = make_values(q_size, salt + 10, 12000);

        for (std::size_t i = 0; i < queries.size(); i += 4) {
            queries[i] = allowed[(i * 13) % allowed.size()];
        }

        cases.push_back({std::move(allowed), std::move(queries)});
    }

    const auto cal = calibrate_iterations(
        [&](std::uint64_t iterations) {
            std::uint64_t c = 0;
            for (std::uint64_t i = 0; i < iterations; ++i) {
                const auto& case_item = cases[i % cases.size()];
                c += api.count_matches(
                    case_item.allowed.data(),
                    case_item.allowed.size(),
                    case_item.queries.data(),
                    case_item.queries.size()
                );
            }
            return c;
        },
        6,
        default_max_iterations,
        default_max_iterations
    );

    std::uint64_t checksum = 0;
    const ResourceSnapshot start = take_resource_snapshot();
    for (std::uint64_t i = 0; i < cal.measured_iterations; ++i) {
        const auto& c = cases[i % cases.size()];
        checksum += api.count_matches(
            c.allowed.data(),
            c.allowed.size(),
            c.queries.data(),
            c.queries.size()
        );
    }
    const ResourceSnapshot end = take_resource_snapshot();

    print_common_benchmark_metrics(
        "count_matches",
        2048,
        8192,
        cases.size(),
        cal,
        checksum,
        start,
        end
    );
}

void benchmark_top_words_from_file(const SutApi& api) {
    const auto temp_dir = std::filesystem::temp_directory_path() /
                          ("librunner_top_words_" + std::to_string(getpid()));
    std::filesystem::create_directories(temp_dir);

    const char* vocabulary[] = {
        "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf",
        "hotel", "india", "juliet", "kilo", "lima", "mike", "november",
        "oscar", "papa", "quebec", "romeo", "sierra", "tango", "uniform",
        "victor", "whiskey", "xray", "yankee", "zulu"
    };

    std::vector<TopWordsCase> cases;
    std::array<std::size_t, 3> input_ns = {2048, 4096, 8192};

    for (int salt = 1; salt <= 4; ++salt) {
        std::size_t n = input_ns[(salt - 1) % input_ns.size()];
        auto path = temp_dir / ("case_" + std::to_string(salt) + ".txt");
        {
            std::ofstream file(path, std::ios::binary);
            for (std::uint64_t i = 0; i < n; ++i) {
                file << vocabulary[(i * 17 + salt * 7) % std::size(vocabulary)];
                if (i % 11 == 0) {
                    file << " THE";
                }
                if (i % 7 == 0) {
                    file << '-';
                } else if (i % 5 == 0) {
                    file << ". ";
                } else {
                    file << ' ';
                }
            }
        }

        std::vector<std::string> ignore;
        if (salt % 2 == 0) {
            ignore = {"the", "and", "of"};
        } else {
            ignore = {"a", "is", "in"};
        }

        cases.push_back({path, std::move(ignore), 16 + static_cast<std::size_t>(salt)});
    }

    struct CaseData {
        std::string path_str;
        std::vector<const char*> ignore_ptrs;
    };
    std::vector<CaseData> prepared_cases;
    for (const auto& c : cases) {
        CaseData pd;
        pd.path_str = c.file_path.string();
        for (const auto& w : c.ignore_words) {
            pd.ignore_ptrs.push_back(w.c_str());
        }
        prepared_cases.push_back(std::move(pd));
    }

    const auto cal = calibrate_iterations(
        [&](std::uint64_t iterations) {
            std::uint64_t c = 0;
            for (std::uint64_t i = 0; i < iterations; ++i) {
                const auto& case_item = cases[i % cases.size()];
                const auto& pd = prepared_cases[i % prepared_cases.size()];
                std::size_t result_length = 0;
                WordCount* result = api.top_words_from_file(
                    pd.path_str.c_str(),
                    pd.ignore_ptrs.data(),
                    pd.ignore_ptrs.size(),
                    case_item.max_results,
                    &result_length
                );
                for (std::size_t result_index = 0; result_index < result_length; ++result_index) {
                    c += result[result_index].count;
                    for (const char* cursor = result[result_index].word;
                         cursor != nullptr && *cursor != '\0';
                         ++cursor) {
                        c = c * 131 + static_cast<unsigned char>(*cursor);
                    }
                }
                api.free_word_counts(result, result_length);
            }
            return c;
        },
        20,
        default_max_iterations,
        default_max_iterations
    );

    std::uint64_t checksum = 0;
    const ResourceSnapshot start = take_resource_snapshot();
    for (std::uint64_t i = 0; i < cal.measured_iterations; ++i) {
        const auto& c = cases[i % cases.size()];
        const auto& pd = prepared_cases[i % prepared_cases.size()];
        std::size_t result_length = 0;
        WordCount* result = api.top_words_from_file(
            pd.path_str.c_str(),
            pd.ignore_ptrs.data(),
            pd.ignore_ptrs.size(),
            c.max_results,
            &result_length
        );

        for (std::size_t result_index = 0; result_index < result_length; ++result_index) {
            checksum += result[result_index].count;
            for (const char* cursor = result[result_index].word;
                 cursor != nullptr && *cursor != '\0';
                 ++cursor) {
                checksum = checksum * 131 + static_cast<unsigned char>(*cursor);
            }
        }

        api.free_word_counts(result, result_length);
    }
    const ResourceSnapshot end = take_resource_snapshot();

    std::filesystem::remove_all(temp_dir);

    print_common_benchmark_metrics(
        "top_words_from_file",
        2048,
        8192,
        cases.size(),
        cal,
        checksum,
        start,
        end
    );
}
