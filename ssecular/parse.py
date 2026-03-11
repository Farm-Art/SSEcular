import typing as t

from ssecular.event import Event
from ssecular.util import LazySplitlines


class EventStream[T: (str, bytes)]:
    """Parses a text/event-stream into ``Event`` objects.

    Follows
    https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation.
    """

    _source: LazySplitlines
    _event: Event

    def __init__(
            self,
            source: t.Iterable[T] | t.AsyncIterable[T],
            initial_id: str | None = None
    ):
        self._source = LazySplitlines(source)
        self._event = Event(id=initial_id)

    def _parse_line(self, line: T) -> Event | None:
        match line:
            case '' | b'':
                event, self._event = self._event, Event(id=self._event.id)
                return event
            case bytes():
                line = line.decode('utf8')

        field, has_value, value = line.partition(':')
        if has_value:
            value = value.removeprefix(' ')

        match field:
            case 'event':
                self._event = self._event._replace(event=value)
            case 'data':
                self._event = self._event._replace(data=self._event.data + value + '\n')
            case 'id' if '\0' not in value:
                self._event = self._event._replace(id=value)
            case 'retry':
                try:
                    self._event = self._event._replace(retry=int(value) / 1000)
                except ValueError:
                    pass

        return None

    def __iter__(self) -> t.Iterator[Event]:
        for line in self._source:
            if event := self._parse_line(line):
                yield event

    async def __aiter__(self) -> t.AsyncIterator[Event]:
        async for line in self._source:
            if event := self._parse_line(line):
                yield event
