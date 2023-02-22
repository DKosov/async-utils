import asyncio
import logging
import time
from collections import deque
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, Union

from async_utils.types import P, T

logger = logging.getLogger(__name__)


class Throttler:
    __slots__ = (
        "_rate_limit",
        "_period",
        "_times",
    )

    def __init__(self, rate_limit: int, period: Union[int, float] = 1.0):
        if not (isinstance(rate_limit, int) and rate_limit > 0):
            raise ValueError("`rate_limit` should be positive integer")

        if not (isinstance(period, (int, float)) and period > 0.0):
            raise ValueError("`period` should be positive float")

        self._rate_limit = float(rate_limit)
        self._period = float(period)

        self._times = deque(0.0 for _ in range(rate_limit))

    async def __aenter__(self) -> None:
        while True:
            curr_ts = time.monotonic()
            diff = curr_ts - (self._times[0] + self._period)
            if diff > 0.0:
                self._times.popleft()
                break
            await asyncio.sleep(-diff)

        self._times.append(curr_ts)

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass


# period in seconds
def throttle(rate_limit: int, period: float = 1.0) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        throttler = Throttler(rate_limit, period)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            async with throttler:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


class TooManyTriesException(Exception):
    ...


def retry(
    times: int = 5, delay: float = 3.0, base_error: bool = True, logger: Optional[logging.Logger] = None
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def func_wrapper(f: Callable[P, T]) -> Callable[P, T]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for i in range(times):
                # noinspection PyBroadException
                try:
                    return f(*args, **kwargs)
                except Exception as exc:
                    if logger is not None:
                        logger.error(str(exc), exc_info=True)
                    time.sleep(delay)
                    if i == (times - 1):
                        if base_error:
                            raise exc
                        else:
                            raise TooManyTriesException() from exc
            return f(*args, **kwargs)

        return wrapper

    return func_wrapper
