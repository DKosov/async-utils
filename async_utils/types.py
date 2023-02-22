from typing import Any, Callable, Coroutine, TypeVar, Union, Awaitable

from typing_extensions import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")

AsyncOrSyncFunction = Callable[P, Awaitable[T]]
NoReturnFuncT = Callable[P, None]
NoReturnAsyncFuncT = Callable[P, Coroutine[Any, Any, None]]
NoReturnDecorator = Callable[[NoReturnAsyncFuncT[P]], NoReturnAsyncFuncT[P]]

NoArgsNoReturnFuncT = Callable[[], None]
NoArgsNoReturnAsyncFuncT = Callable[[], Coroutine[Any, Any, None]]
NoArgsNoReturnDecorator = Callable[[Union[NoArgsNoReturnFuncT, NoArgsNoReturnAsyncFuncT]], NoArgsNoReturnAsyncFuncT]
