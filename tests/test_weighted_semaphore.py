import threading
import time
import pytest

from bigdata_briefs.weighted_semaphore import WeightedSemaphore


def test_acquire_and_release():
    SEMAPHORE_WEIGHT = 1
    sem = WeightedSemaphore(SEMAPHORE_WEIGHT)
    acquired = []
    
    def worker(weight, idx):
        with sem(weight):
            acquired.append(idx)

    t1 = threading.Thread(target=worker, args=(1, 'A'))
    t1.start()
    t1.join()

    assert acquired == ['A']
    assert sem.weight_available() == SEMAPHORE_WEIGHT, "Semaphore should be released after all workers complete"

def test_several_workers_acquire_and_release():
    SEMAPHORE_WEIGHT = 4
    sem = WeightedSemaphore(SEMAPHORE_WEIGHT)
    order = []
    def worker(weight, idx):
        with sem(weight):
            order.append(idx)
    threads = [threading.Thread(target=worker, args=(1, i)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sorted(order) == [0, 1, 2, 3]
    assert sem.weight_available() == SEMAPHORE_WEIGHT, "Semaphore should be released after all workers complete"

def test_several_workers_block_and_acquire():
    SEMAPHORE_WEIGHT = 1
    sem = WeightedSemaphore(SEMAPHORE_WEIGHT)
    results = []
    def worker(idx):
        with sem(1):
            results.append(idx)
            time.sleep(0.05)
    t1 = threading.Thread(target=worker, args=(1,))
    t2 = threading.Thread(target=worker, args=(2,))
    t1.start()
    time.sleep(0.01)
    t2.start()
    t1.join()
    t2.join()
    assert results == [1, 2]

    assert sem.weight_available() == SEMAPHORE_WEIGHT, "Semaphore should be released after all workers complete"

def test_context_manager_releases_after_exception():
    SEMAPHORE_WEIGHT = 2
    sem = WeightedSemaphore(SEMAPHORE_WEIGHT)

    with pytest.raises(RuntimeError):
        with sem(2):
            raise RuntimeError()

    assert sem.weight_available() == SEMAPHORE_WEIGHT, "Semaphore should be released after exception"
