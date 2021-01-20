import numpy as np


def optimal_solution(results, sets):
    for i in range(len(results)):
        for j in range(len(results)):
            if i == j:
                continue
            else:
                if results[i] | results[j] in sets:
                    results.append(results[i] | results[j])
                    if i > j:
                        del results[i]
                        del results[j]
                    else:
                        del results[j]
                        del results[i]
                    # print(results)
                    return optimal_solution(results, sets)
    return results


def problem(parent, sets):
    kara = []
    results = []
    days_working = len(sets[-1]) - len(parent)
    Nparent = parent.copy()
    a, b, c = 1., 1., 1.
    for i in range(len(sets)):
        wart = 0 * len(parent - sets[i]) ** 2 + 0 * (len(parent) - len(sets[i])) ** 2 + 1 * len(sets[i] - parent) ** 2
        kara.append(wart)
    unionres = set([])
    k = 1
    poprzedni = {}
    while not parent.issubset(unionres):
        # print(k)
        k += 1
        idxs = np.where(np.array(kara) == min(kara))[0].tolist()
        setlen = [len(sets[index]) for index in idxs]
        idx = idxs[setlen.index(max(setlen))]
        if len(unionres) > 0 and len(unionres - parent) < len((unionres | sets[idx]) - parent):
            for index in idxs:
                if len(unionres) > 0 and len(unionres - parent) < len((unionres | sets[index]) - parent):
                    continue
                idx = index
        if poprzedni != parent - sets[idx]:
            # if len(unionres) > 0 and len(unionres - parent) < len((unionres | sets[idx]) - parent):
            if len((unionres | sets[idx]) - Nparent) > days_working or len(unionres - Nparent) < len(
                    (unionres | sets[idx]) - Nparent):
                if len((unionres | sets[idx]) - Nparent) > days_working:
                    zmiana_nadmiaru_po_dodaniu = np.abs(len(unionres - Nparent) - len((unionres | sets[idx]) - Nparent))
                    zmiana_niedoboru_po_dodaniu = np.abs(
                        len(Nparent - (unionres | sets[idx])) - len(Nparent - unionres))
                    if zmiana_niedoboru_po_dodaniu < zmiana_nadmiaru_po_dodaniu:
                        break
                elif len(unionres - Nparent) < len((unionres | sets[idx]) - Nparent):
                    zmiana_nadmiaru_po_dodaniu = np.abs(len(unionres - Nparent) - len((unionres | sets[idx]) - Nparent))
                    zmiana_niedoboru_po_dodaniu = np.abs(
                        len(Nparent - (unionres | sets[idx])) - len(Nparent - unionres))
                    if len(
                            Nparent - unionres) <= days_working and zmiana_niedoboru_po_dodaniu < zmiana_nadmiaru_po_dodaniu:
                        break
            results.append(sets[idx])
            unionres |= sets[idx]
            # print(f"BEF: {parent}")
            parent -= sets[idx]
            # print(f"AFTER: {parent}")
        poprzedni = parent
        kara = []
        del sets[idx]
        for i in range(len(sets)):
            wart = a * len(parent - sets[i]) ** 2 + 0 * (len(parent) - len(sets[i])) ** 2 + c * len(
                sets[i] - parent) ** 2
            kara.append(wart)
    print(f"NON OPTIMAL RESULTS: {results}")
    optimal_res = optimal_solution(results.copy(), sets.copy())
    print(f"OPTIMAL RESULTS: {optimal_res}")
    return optimal_res


if __name__ == "__main__":
    parent = {2, 3, 9, 10}
    sets = [{11, 4}, {12, 5}, {13, 6}, {14, 7}, {8, 1, 15}, {9, 2}, {10, 3}, {12, 11, 4, 5}, {13, 12, 5, 6},
            {14, 13, 6, 7}, {1, 7, 8, 14, 15}, {1, 2, 8, 9, 15}, {10, 9, 2, 3}, {11, 10, 3, 4}, {4, 5, 6, 11, 12, 13},
            {5, 6, 7, 12, 13, 14}, {1, 6, 7, 8, 13, 14, 15}, {1, 2, 7, 8, 9, 14, 15}, {1, 2, 3, 8, 9, 10, 15},
            {2, 3, 4, 9, 10, 11}, {3, 4, 5, 10, 11, 12}, {4, 5, 6, 7, 11, 12, 13, 14}, {1, 5, 6, 7, 8, 12, 13, 14, 15},
            {1, 2, 6, 7, 8, 9, 13, 14, 15}, {1, 2, 3, 7, 8, 9, 10, 14, 15}, {1, 2, 3, 4, 8, 9, 10, 11, 15},
            {2, 3, 4, 5, 9, 10, 11, 12}, {3, 4, 5, 6, 10, 11, 12, 13}, {1, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15},
            {1, 2, 5, 6, 7, 8, 9, 12, 13, 14, 15}, {1, 2, 3, 6, 7, 8, 9, 10, 13, 14, 15},
            {1, 2, 3, 4, 7, 8, 9, 10, 11, 14, 15}, {1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 15},
            {2, 3, 4, 5, 6, 9, 10, 11, 12, 13}, {3, 4, 5, 6, 7, 10, 11, 12, 13, 14},
            {1, 2, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15}, {1, 2, 3, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15},
            {1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 13, 14, 15}, {1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 14, 15},
            {1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 15}, {2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14},
            {1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15}, {9, 2, 5}, {1, 10, 3, 6}, {4, 5, 7, 8, 11, 12, 13, 14, 15},
            {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}]
    print(problem(parent, sets))
