import multiprocessing as mp

__all__ = ['parallel_mc_run']

def worker_compute(w_id):
    "Worker function executed on the spawned slave process"
    # global _local_rs
    return _worker_mc_compute(_local_rs)


def assign_worker_rs(w_rs):
    """Assign process local random state variable `rs` the given value"""
    assert not '_local_rs' in globals(), "Here comes trouble. Process is not expected to have global variable `_local_rs`"

    global _local_rs
    _local_rs = w_rs
    # wait to ensure that the assignment takes place for each worker
    b.wait()

def parallel_mc_run(random_states, n_workers, n_batches, mc_func):
    """
    Given iterable `random_states` of length `n_workers`, the number of batches `n_batches`,
    and the function `worker_compute` to execute, return iterator with results returned by 
    the supplied function. The function is expected to conform to signature f(worker_id), 
    and has access to worker-local global variable `rs`, containing worker's random states.
    """
    # use of Barrier ensures that every worker gets one
    global b, _worker_mc_compute
    b = mp.Barrier(n_workers)
    
    _worker_mc_compute = mc_func
    with mp.Pool(processes=n_workers) as pool:
        # 1. map over every worker once to distribute RandomState instances
        pool.map(assign_worker_rs, random_states, chunksize=1)
        # 2. Perform computations on workers
        r = pool.map(worker_compute, range(n_batches), chunksize=1)

    return r


def sequential_mc_run(random_states, n_workers, n_batches, mc_func):
    for rs in random_states:
        for _ in range(n_batches):
            yield mc_func(rs)
