from pathlib import Path

from android_sync.utils import Month
from android_sync.utils import get_month
from android_sync.utils import get_month_name


def test_next_over_year():
    assert Month(2000, 12).next() == Month(2001, 1)


def test_next():
    assert Month(2000, 1).next() == Month(2000, 2)


def test_month_name():
    assert get_month_name(1) == 'jan'
    assert get_month_name(12) == 'dec'


def test_get_month_basic_file():
    assert get_month(Path('IMG_20190203_040506.jpg')) == Month(year=2019, month=2)
    assert get_month(Path('VID_20190203_040506.mp4')) == Month(year=2019, month=2)


def test_get_month_no_month():
    assert get_month(Path('test_image.txt')) is None


def test_get_month_burst():
    assert get_month(Path('00008IMG_00008_BURST20190203040506_COVER.jpg')) == Month(year=2019, month=2)
    assert get_month(Path('00007XTR_00007_BURST20190203040506.jpg.jpg')) == Month(year=2019, month=2)

