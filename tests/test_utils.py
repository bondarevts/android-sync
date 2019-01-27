from android_sync.utils import Month
from android_sync.utils import get_month_name


def test_next_over_year():
    assert Month(2000, 12).next() == Month(2001, 1)


def test_next():
    assert Month(2000, 1).next() == Month(2000, 2)


def test_month_name():
    assert get_month_name(1) == 'jan'
    assert get_month_name(12) == 'dec'
