from ics import Calendar, Event, DisplayAlarm as DA
from ics.utils import get_arrow
from ics.parse import string_to_container, Container


class DisplayAlarm(DA):
    def __hash__(self):
        return hash(repr(self))


def get_uid(text):
    for l in text.splitlines():
        if l.startswith("UID:"):
            return l[4:].strip()
    return text


def _hash(self):
    uid = getattr(self, 'uid', get_uid(str(self)))
    return hash(uid)


def _eq(self, other):
    """Two events are considered equal if they have the same uid."""
    if isinstance(other, Event):
        return self.uid == other.uid
    if isinstance(other, Container):
        return hash(self) == hash(other)
    raise NotImplementedError('Cannot compare Event and {}'.format(type(other)))


Container.__hash__ = _hash
Event.__hash__ = _hash
Event.__eq__ = _eq
