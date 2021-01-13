def problem(parent, sets):
    kara = []
    results = []
    for i in range(len(sets)):
        wart = len(parent - sets[i]) ** 2 + (len(parent) - len(sets[i])) ** 2
        kara.append(wart)
    unionres = set([])
    k =1
    poprzedni = {}
    while not parent.issubset(unionres):
        # print(k)
        k+=1
        idx = kara.index(min(kara))

        if poprzedni != parent - sets[idx]:
            if len(unionres) > 0 and len(unionres - parent) < len((unionres | sets[idx]) - parent):
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
            wart = len(parent - sets[i]) ** 2 + (len(parent) - len(sets[i])) ** 2
            kara.append(wart)
        print(f"RESULTS: {results}")
    return results


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
    print(problem(parent,sets))