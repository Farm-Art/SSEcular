import typing as t


class LazySplitlines[T: (str, bytes)]:
    """Lazily splits a string coming in chunks into lines, stripping line ends.

    Works with sync and async iterables.

    By default, discards the last line if it's incomplete (can be
    changed by passing ``discard_incomplete=False``).
    Otherwise, output should be identical to ``''.join(iterable).splitlines()``.
    """

    _iter: t.Iterable[T] | t.AsyncIterable[T]
    _hanging_cr: bool
    _left_over: T | None
    _discard_incomplete: bool

    def __init__(
            self,
            iterable: t.Iterable[T] | t.AsyncIterable[T],
            discard_incomplete: bool = True
    ):
        self._iter = iterable
        self._hanging_cr = False
        self._left_over = None
        self._discard_incomplete = discard_incomplete

    def _feed(self, chunk: T) -> t.Sequence[T]:
        match chunk:
            case bytes():
                cr, lf, empty = b'\r', b'\n', b''
            case str():
                cr, lf, empty = '\r', '\n', ''
            case _:
                raise TypeError(f"chunk must be bytes or str, not {type(chunk).__name__!r}")

        if self._hanging_cr:
            chunk.removeprefix('\n')

        self._hanging_cr = chunk.endswith(cr)

        data = (self._left_over or empty) + chunk

        *lines, rest = data.splitlines() or [empty]
        if chunk.endswith(lf):
            self._left_over = None
            lines.append(rest)
        else:
            self._left_over = rest

        return lines

    def __iter__(self) -> t.Iterator[T]:
        for chunk in self._iter:
            yield from self._feed(chunk)
        if not self._discard_incomplete and self._left_over is not None:
            yield self._left_over

    async def __aiter__(self) -> t.AsyncIterator[T]:
        async for chunk in self._iter:
            for line in self._feed(chunk):
                yield line
        if not self._discard_incomplete and self._left_over is not None:
            yield self._left_over
