import json
import typing as t


class Event(t.NamedTuple):
    """A single event in an event stream.

    Can be serialized into a transmittable format with ``as_sse``,
    which is useful for testing.
    """
    id: str | None = None
    event: str | None = None
    data: str = ''
    retry: float | None = None
    """reconnection time in *seconds*.
    
    Note: transmitted data is an integer in milliseconds, which
    is customary for JS; Python tends to use floating points in
    seconds instead. ``as_sse`` accounts for this and converts
    before output, but the constructor expects the value to be
    in seconds.
    """

    def json(self) -> t.Any:
        """Get event data as parsed JSON"""
        return json.loads(self.data)

    def as_sse(self, sep: str = '\r\n', dispatch: bool = False) -> str:
        """Format event data as a ready-to-transmit Server-Sent Event.

        Also available as the ``sse`` format specifier.

        If ``dispatch`` is True, includes an empty line at the end that
        triggers an event dispatch.
        """
        lines = [
            f'data: {line}' if line else 'data' for line in self.data.splitlines()
        ]

        if self.event is not None:
            lines.append(f'event: {self.event}' if self.event else 'event')

        if self.id is not None:
            lines.append(f'id: {self.id}' if self.id else 'id')

        if self.retry is not None:
            lines.append(f'retry: {round(self.retry * 1000)}')

        if lines or dispatch:
            lines.append(sep if dispatch else '')

        return sep.join(lines)

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case '':
                return str(self)
            case 'sse':
                return self.as_sse()
            case _:
                raise ValueError(
                    f"Invalid format specifier {format_spec!r} "
                    f"for object of type {type(self).__name__!r}"
                )
