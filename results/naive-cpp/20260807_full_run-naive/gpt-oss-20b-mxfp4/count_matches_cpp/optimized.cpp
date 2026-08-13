extern "C" {

size_t count_matches(
    const int* allowed,
    size_t allowed_length,
    const int* queries,
    size_t queries_length
) {
    if ((allowed == nullptr && allowed_length != 0) ||
        (queries == nullptr && queries_length != 0)) {
        return 0;
    }
    if (allowed_length == 0 || queries_length == 0) {
        return 0;
    }

    size_t matches = 0;
    const int* a_end = allowed + allowed_length;

    // Special case for a single allowed value to avoid loop overhead
    if (allowed_length == 1) {
        const int target = allowed[0];
        for (const int* q = queries; q != queries + queries_length; ++q) {
            if (*q == target) {
                ++matches;
            }
        }
        return matches;
    }

    for (const int* q = queries; q != queries + queries_length; ++q) {
        const int val = *q;
        const int* a = allowed;
        while (a != a_end) {
            if (*a == val) {
                ++matches;
                break;
            }
            ++a;
        }
    }

    return matches;
}

}
