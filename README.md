# magi_parallel
building code to parallelize magi

1. Write simple multiprocess program - Learning

2. Write simple multithreaded program - Learning

3. Kill thread vs. Kill process

4. Compare performance over extended programs (continuous running for some cycles) - Testing

5. From previous results, start magi.

How to release memory when a process is closed?
"call close() followed by wait() on your Pool object."
https://docs.python.org/3/library/multiprocessing.html#module-multiprocessing.pool
