import heapq
import logging

def greedy_set_cover(subsets, parent_set,res=None):
    if type(parent_set)!=type(set()):
        parent_set = set(parent_set)
    max = len(parent_set)
    # create the initial heap. Note 'subsets' can be unsorted,
    # so this is independent of whether remove_redunant_subsets is used.
    heap = []
    for s in subsets:
        # Python's heapq lets you pop the *smallest* value, so we
        # want to use max-len(s) as a score, not len(s).
        # len(heap) is just proving a unique number to each subset,
        # used to tiebreak equal scores.
        heapq.heappush(heap, [max - len(s), len(heap), s])
    if res== None:
        results = []
    else:
        results = res
    result_set = set()
    while result_set < parent_set:
        logging.debug('len of result_set is {0}'.format(len(result_set)))
        best = []
        unused = []
        while heap:
            score, count, s = heapq.heappop(heap)
            if not best:
                best = [max - len(s - result_set), count, s]
                continue
            if score >= best[0]:
                # because subset scores only get worse as the resultset
                # gets bigger, we know that the rest of the heap cannot beat
                # the best score. So push the subset back on the heap, and
                # stop this iteration.
                heapq.heappush(heap, [score, count, s])
                break
            score = max - len(s - result_set)
            if score >= best[0]:
                unused.append([score, count, s])
            else:
                unused.append(best)
                best = [score, count, s]
        try:
            add_set = best[2]
        except IndexError:
            print(best)
        logging.debug('len of add_set is {0} score was {1}'.format(len(add_set), best[0]))
        results.append(add_set)
        result_set.update(add_set)
        # subsets that were not the best get put back on the heap for next time.
        while unused:
            heapq.heappush(heap, unused.pop())
        flaga = True
        np = []
        for u in parent_set:
            if not any(u in i for i in results):
                flaga = False
                np.append(u)
        if not flaga:
            del subsets[subsets.index(results[-1])]
            if len(results[-1]-parent_set) > 1:
                results.pop()
                return greedy_set_cover(subsets, parent_set, results)
            else:
                subsets = [i for i in subsets if len(i) <= len(np)]
                # print("s",subsets)
                # print("np", np)
                return greedy_set_cover(subsets, np, results)
    print("r", results)
    return results


if __name__ == "__main__":
    subsets = [set([1,2,3]),set([1,2,3,4,5,6,7,8]),set([2,4]),set([4,5])]
    parent = set([1,2,3,4,5])
    print(greedy_set_cover(subsets,parent))