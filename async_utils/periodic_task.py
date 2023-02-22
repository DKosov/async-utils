import asyncio
import logging
from functools import partial, wraps
from traceback import format_exception
from typing import Any, Callable, Coroutine, Optional
from async_utils.types import P, T, AsyncOrSyncFunction


def repeat_every(
    *,
    seconds: float,
    wait_first: bool = False,
    execute: bool = True,
    logger: Optional[logging.Logger] = None,
    raise_exceptions: bool = True,
    max_repetitions: Optional[int] = None,
) -> Callable[[AsyncOrSyncFunction[P, T]], Callable[P, Coroutine[Any, Any, None]]]:
    def decorator(func: AsyncOrSyncFunction[P, T]) -> Callable[P, Coroutine[Any, Any, None]]:
        is_coroutine = asyncio.iscoroutinefunction(func)

        @wraps(func)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> Coroutine[Any, Any, None]:
            repetitions = 0
            async_loop = asyncio.get_event_loop()

            async def run() -> None:
                nonlocal repetitions
                try:
                    if is_coroutine:
                        await func(*args, **kwargs)
                    else:
                        pfunc = partial(func, *args, **kwargs)
                        await async_loop.run_in_executor(None, pfunc)
                    repetitions += 1
                except Exception as exc:
                    if logger is not None:
                        formatted_exception = "".join(format_exception(type(exc), exc, exc.__traceback__))
                        logger.error(formatted_exception)
                    if raise_exceptions:
                        raise exc

            async def loop() -> None:
                nonlocal repetitions
                if wait_first:
                    await asyncio.sleep(seconds)
                if execute:
                    await run()
                while max_repetitions is None or repetitions < max_repetitions:
                    await run()
                    await asyncio.sleep(seconds)

            return loop()

        return wrapped

    return decorator
