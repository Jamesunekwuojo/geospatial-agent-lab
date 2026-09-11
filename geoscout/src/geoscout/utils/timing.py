import time
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def timer() -> Iterator[dict[str, float]]:
    """Measure elapsed wall-clock time."""

    result: dict[str, float] = {}

    start = time.perf_counter()

    try:
        yield result
    finally:
        result["elapsed_ms"] = (time.perf_counter() - start) * 1000
