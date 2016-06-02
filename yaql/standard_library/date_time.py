#    Copyright (c) 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
The module describes which operations can be done with datetime objects.
"""

import datetime
import time as python_time

from yaql.language import specs
from yaql.language import yaqltypes

from dateutil import parser
from dateutil import tz


DATETIME_TYPE = datetime.datetime
TIMESPAN_TYPE = datetime.timedelta
ZERO_TIMESPAN = datetime.timedelta()
UTCTZ = yaqltypes.DateTime.utctz


def _get_tz(offset):
    if offset is None:
        return None
    if offset == ZERO_TIMESPAN:
        return UTCTZ
    return tz.tzoffset(None, seconds(offset))


@specs.name('datetime')
@specs.parameter('year', int)
@specs.parameter('month', int)
@specs.parameter('day', int)
@specs.parameter('hour', int)
@specs.parameter('minute', int)
@specs.parameter('second', int)
@specs.parameter('microsecond', int)
@specs.parameter('offset', TIMESPAN_TYPE)
def build_datetime(year, month, day, hour=0, minute=0, second=0,
                   microsecond=0, offset=ZERO_TIMESPAN):
    """:yaql:datetime

    Returns datetime object built on year, month, day, hour, minute, second,
    microsecond, offset.

    :signature: datetime(year, month, day, hour => 0, minute => 0, second => 0,
                         microsecond => 0, offset => timespan(0))
    :arg year: number of years in datetime
    :argType year: integer between 1 and 9999 inclusive
    :arg month: number of months in datetime
    :argType month: integer between 1 and 12 inclusive
    :arg day: number of days in datetime
    :argType day: integer between 1 and number of days in given month
    :arg hour: number of hours in datetime, 0 by default
    :argType hour: integer between 0 and 23 inclusive
    :arg minute: number of minutes in datetime, 0 by default
    :argType minute: integer between 0 and 59 inclusive
    :arg second: number of seconds in datetime, 0 by default
    :argType second: integer between 0 and 59 inclusive
    :arg microsecond: number of microseconds in datetime, 0 by default
    :argType microsecond: integer between 0 and 1000000-1
    :arg offset: datetime offset in microsecond resolution, needed for tzinfo,
        timespan(0) by default
    :argType offset: timespan type
    :returnType: datetime object

    .. code::

        yaql> let(datetime(2015, 9, 29)) -> [$.year, $.month, $.day]
        [2015, 9, 29]
    """
    zone = _get_tz(offset)
    return DATETIME_TYPE(year, month, day, hour, minute, second,
                         microsecond, zone)


@specs.name('datetime')
@specs.parameter('timestamp', yaqltypes.Number())
@specs.parameter('offset', TIMESPAN_TYPE)
def datetime_from_timestamp(timestamp, offset=ZERO_TIMESPAN):
    """:yaql:datetime

    Returns datetime object built by timestamp.

    :signature: datetime(timestamp, offset => timespan(0))
    :arg timestamp: timespan object to represent datetime
    :argType timestamp: number
    :arg offset: datetime offset in microsecond resolution, needed for tzinfo,
        timespan(0) by default
    :argType offset: timespan type
    :returnType: datetime object

    .. code::

        yaql> let(datetime(1256953732)) -> [$.year, $.month, $.day]
        [2009, 10, 31]
    """
    zone = _get_tz(offset)
    return DATETIME_TYPE.fromtimestamp(timestamp, tz=zone)


@specs.name('datetime')
@specs.parameter('string', yaqltypes.String())
@specs.parameter('format__', yaqltypes.String(True))
def datetime_from_string(string, format__=None):
    """:yaql:datetime

    Returns datetime object built by string parsed with format.

    :signature: datetime(string, format => null)
    :arg string: string representing datetime
    :argType string: string
    :arg format: format for parsing input string which should be supported
        with C99 standard of format codes. null by default, which means
        parsing with Python dateutil.parser usage
    :argType format: string
    :returnType: datetime object

    .. code::

        yaql> let(datetime("29.8?2015")) -> [$.year, $.month, $.day]
        [2015, 8, 29]
        yaql> let(datetime("29.8?2015", "%d.%m?%Y"))->[$.year, $.month, $.day]
        [2015, 8, 29]
    """
    if not format__:
        result = parser.parse(string)
    else:
        result = DATETIME_TYPE.strptime(string, format__)
    if not result.tzinfo:
        return result.replace(tzinfo=UTCTZ)
    return result


@specs.name('timespan')
@specs.parameter('days', int)
@specs.parameter('hours', int)
@specs.parameter('minutes', int)
@specs.parameter('seconds', yaqltypes.Integer())
@specs.parameter('milliseconds', yaqltypes.Integer())
@specs.parameter('microseconds', yaqltypes.Integer())
def build_timespan(days=0, hours=0, minutes=0, seconds=0,
                   milliseconds=0, microseconds=0):
    """:yaql:timespan

    Returns timespan object with specified args.

    :signature: timespan(days => 0, hours => 0, minutes => 0, seconds => 0,
                         milliseconds => 0, microseconds => 0)
    :arg days: number of days in timespan, 0 by default
    :argType days: integer
    :arg hours: number of hours in timespan, 0 by default
    :argType hours: integer
    :arg minutes: number of minutes in timespan, 0 by default
    :argType minutes: integer
    :arg seconds: number of seconds in timespan, 0 by default
    :argType seconds: integer
    :arg milliseconds: number of microseconds in timespan, 0 by default
    :argType milliseconds: integer
    :arg microsecond: number of microseconds in timespan, 0 by default
    :argType microsecond: integer
    :returnType: timespan object

    .. code::

        yaql> timespan(days => 1, hours => 2, minutes => 3).hours
        26.05
    """
    return TIMESPAN_TYPE(
        days=days, hours=hours, minutes=minutes, seconds=seconds,
        milliseconds=milliseconds, microseconds=microseconds)


@specs.yaql_property(TIMESPAN_TYPE)
def microseconds(timespan):
    """:yaql:property microseconds

    Returns total microseconds in timespan.

    :signature: timespan.microseconds
    :returnType: integer

    .. code::

        yaql> timespan(seconds => 1).microseconds
        1000000
    """
    return (86400000000 * timespan.days +
            1000000 * timespan.seconds +
            timespan.microseconds)


@specs.yaql_property(TIMESPAN_TYPE)
def milliseconds(timespan):
    """:yaql:property milliseconds

    Returns total milliseconds in timespan.

    :signature: timespan.milliseconds
    :returnType: float

    .. code::

        yaql> timespan(seconds => 1).milliseconds
        1000.0
    """
    return microseconds(timespan) / 1000.0


@specs.yaql_property(TIMESPAN_TYPE)
def seconds(timespan):
    """:yaql:property seconds

    Returns total seconds in timespan.

    :signature: timespan.seconds
    :returnType: float

    .. code::

        yaql> timespan(minutes => 1).seconds
        60.0
    """
    return microseconds(timespan) / 1000000.0


@specs.yaql_property(TIMESPAN_TYPE)
def minutes(timespan):
    """:yaql:property minutes

    Returns total minutes in timespan.

    :signature: timespan.minutes
    :returnType: float

    .. code::

        yaql> timespan(hours => 2).minutes
        120.0
    """
    return microseconds(timespan) / 60000000.0


@specs.yaql_property(TIMESPAN_TYPE)
def hours(timespan):
    """:yaql:property hours

    Returns total hours in timespan.

    :signature: timespan.hours
    :returnType: float

    .. code::

        yaql> timespan(days => 2).hours
        48.0
    """
    return microseconds(timespan) / 3600000000.0


@specs.yaql_property(TIMESPAN_TYPE)
def days(timespan):
    """:yaql:property days

    Returns total days in timespan.

    :signature: timespan.days
    :returnType: float

    .. code::

        yaql> timespan(days => 2, hours => 48).days
        4.0
    """
    return microseconds(timespan) / 86400000000.0


def now(offset=ZERO_TIMESPAN):
    """:yaql:now

    Returns the current local date and time.

    :signature: now(offset => timespan(0))
    :arg offset: datetime offset in microsecond resolution, needed for tzinfo,
        timespan(0) by default
    :argType offset: timespan type
    :returnType: datetime

    .. code::

        yaql> let(now()) -> [$.year, $.month, $.day]
        [2016, 7, 18]
        yaql> now(offset=>localtz()).hour - now().hour
        3
    """
    zone = _get_tz(offset)
    return DATETIME_TYPE.now(tz=zone)


def localtz():
    """:yaql:localtz

    Returns local time zone in timespan object.

    :signature: localtz()
    :returnType: timespan object

    .. code::

        yaql> localtz().hours
        3.0
    """
    if python_time.daylight:
        return TIMESPAN_TYPE(seconds=-python_time.altzone)
    else:
        return TIMESPAN_TYPE(seconds=-python_time.timezone)


def utctz():
    """:yaql:utctz

    Returns UTC time zone in timespan object.

    :signature: utctz()
    :returnType: timespan object

    .. code::

        yaql> utctz().hours
        0.0
    """
    return ZERO_TIMESPAN


@specs.name('#operator_+')
@specs.parameter('dt', yaqltypes.DateTime())
@specs.parameter('ts', TIMESPAN_TYPE)
def datetime_plus_timespan(dt, ts):
    """:yaql:operator +

    Returns datetime object with added timespan.

    :signature: left + right
    :arg left: input datetime object
    :argType left: datetime object
    :arg right: input timespan object
    :argType right: timespan object
    :returnType: datetime object

    .. code::

        yaql> let(now() + timespan(days => 100)) -> $.month
        10
    """
    return dt + ts


@specs.name('#operator_+')
@specs.parameter('ts', TIMESPAN_TYPE)
@specs.parameter('dt', yaqltypes.DateTime())
def timespan_plus_datetime(ts, dt):
    """:yaql:operator +

    Returns datetime object with added timespan.

    :signature: left + right
    :arg left: input timespan object
    :argType left: timespan object
    :arg right: input datetime object
    :argType right: datetime object
    :returnType: datetime object

    .. code::

        yaql> let(timespan(days => 100) + now()) -> $.month
        10
    """
    return ts + dt


@specs.name('#operator_-')
@specs.parameter('dt', yaqltypes.DateTime())
@specs.parameter('ts', TIMESPAN_TYPE)
def datetime_minus_timespan(dt, ts):
    """:yaql:operator -

    Returns datetime object with subtracted timespan.

    :signature: left - right
    :arg left: input datetime object
    :argType left: datetime object
    :arg right: input timespan object
    :argType right: timespan object
    :returnType: datetime object

    .. code::

        yaql> let(now() - timespan(days => 100)) -> $.month
        4
    """
    return dt - ts


@specs.name('#operator_-')
@specs.parameter('dt1', yaqltypes.DateTime())
@specs.parameter('dt2', yaqltypes.DateTime())
def datetime_minus_datetime(dt1, dt2):
    """:yaql:operator -

    Returns datetime object dt1 with subtracted dt2.

    :signature: left - right
    :arg left: input datetime object
    :argType left: datetime object
    :arg right: datetime object to be subtracted
    :argType right: datetime object
    :returnType: timespan object

    .. code::

        yaql> let(now() - now()) -> $.microseconds
        -325
    """
    return dt1 - dt2


@specs.name('#operator_+')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def timespan_plus_timespan(ts1, ts2):
    """:yaql:operator +

    Returns sum of two timespan objects.

    :signature: left + right
    :arg left: input timespan object
    :argType left: timespan object
    :arg right: input timespan object
    :argType right: timespan object
    :returnType: timespan object

    .. code::

        yaql> let(timespan(days => 1) + timespan(hours => 12)) -> $.hours
        36.0
    """
    return ts1 + ts2


@specs.name('#operator_-')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def timespan_minus_timespan(ts1, ts2):
    """:yaql:operator -

    Returns timespan object with subtracted another timespan object.

    :signature: left - right
    :arg left: input timespan object
    :argType left: timespan object
    :arg right: input timespan object
    :argType right: timespan object
    :returnType: timespan object

    .. code::

        yaql> let(timespan(days => 1) - timespan(hours => 12)) -> $.hours
        12.0
    """
    return ts1 - ts2


@specs.name('#operator_>')
@specs.parameter('dt1', yaqltypes.DateTime())
@specs.parameter('dt2', yaqltypes.DateTime())
def datetime_gt_datetime(dt1, dt2):
    """:yaql:operator >

    Returns true if left datetime is strictly greater than right datetime,
    false otherwise.

    :signature: left > right
    :arg left: left datetime object
    :argType left: datetime object
    :arg right: right datetime object
    :argType right: datetime object
    :returnType: boolean

    .. code::

        yaql> datetime(2011, 11, 11) > datetime(2010, 10, 10)
        true
    """
    return dt1 > dt2


@specs.name('#operator_>=')
@specs.parameter('dt1', yaqltypes.DateTime())
@specs.parameter('dt2', yaqltypes.DateTime())
def datetime_gte_datetime(dt1, dt2):
    """:yaql:operator >=

    Returns true if left datetime is greater or equal to right datetime,
    false otherwise.

    :signature: left >= right
    :arg left: left datetime object
    :argType left: datetime object
    :arg right: right datetime object
    :argType right: datetime object
    :returnType: boolean

    .. code::

        yaql> datetime(2011, 11, 11) >= datetime(2011, 11, 11)
        true
    """
    return dt1 >= dt2


@specs.name('#operator_<')
@specs.parameter('dt1', yaqltypes.DateTime())
@specs.parameter('dt2', yaqltypes.DateTime())
def datetime_lt_datetime(dt1, dt2):
    """:yaql:operator <

    Returns true if left datetime is strictly less than right datetime,
    false otherwise.

    :signature: left < right
    :arg left: left datetime object
    :argType left: datetime object
    :arg right: right datetime object
    :argType right: datetime object
    :returnType: boolean

    .. code::

        yaql> datetime(2011, 11, 11) < datetime(2011, 11, 11)
        false
    """
    return dt1 < dt2


@specs.name('#operator_<=')
@specs.parameter('dt1', yaqltypes.DateTime())
@specs.parameter('dt2', yaqltypes.DateTime())
def datetime_lte_datetime(dt1, dt2):
    """:yaql:operator <=

    Returns true if left datetime is less or equal to right datetime,
    false otherwise.

    :signature: left <= right
    :arg left: left datetime object
    :argType left: datetime object
    :arg right: right datetime object
    :argType right: datetime object
    :returnType: boolean

    .. code::

        yaql> datetime(2011, 11, 11) <= datetime(2011, 11, 11)
        true
    """
    return dt1 <= dt2


@specs.name('#operator_>')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def timespan_gt_timespan(ts1, ts2):
    """:yaql:operator >

    Returns true if left timespan is strictly greater than right timespan,
    false otherwise.

    :signature: left > right
    :arg left: left timespan object
    :argType left: timespan object
    :arg right: right timespan object
    :argType right: timespan object
    :returnType: boolean

    .. code::

        yaql> timespan(hours => 2) > timespan(hours => 1)
        true
    """
    return ts1 > ts2


@specs.name('#operator_>=')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def timespan_gte_timespan(ts1, ts2):
    """:yaql:operator >=

    Returns true if left timespan is greater or equal to right timespan,
    false otherwise.

    :signature: left >= right
    :arg left: left timespan object
    :argType left: timespan object
    :arg right: right timespan object
    :argType right: timespan object
    :returnType: boolean

    .. code::

        yaql> timespan(hours => 24) >= timespan(days => 1)
        true
    """
    return ts1 >= ts2


@specs.name('#operator_<')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def timespan_lt_timespan(ts1, ts2):
    """:yaql:operator <

    Returns true if left timespan is strictly less than right timespan,
    false otherwise.

    :signature: left < right
    :arg left: left timespan object
    :argType left: timespan object
    :arg right: right timespan object
    :argType right: timespan object
    :returnType: boolean

    .. code::

        yaql> timespan(hours => 23) < timespan(days => 1)
        true
    """
    return ts1 < ts2


@specs.name('#operator_<=')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def timespan_lte_timespan(ts1, ts2):
    """:yaql:operator <=

    Returns true if left timespan is less or equal to right timespan,
    false otherwise.

    :signature: left <= right
    :arg left: left timespan object
    :argType left: timespan object
    :arg right: right timespan object
    :argType right: timespan object
    :returnType: boolean

    .. code::

        yaql> timespan(hours => 23) <= timespan(days => 1)
        true
    """
    return ts1 <= ts2


@specs.name('#operator_*')
@specs.parameter('ts', TIMESPAN_TYPE)
@specs.parameter('n', yaqltypes.Number())
def timespan_by_num(ts, n):
    """:yaql:operator *

    Returns timespan object built on timespan multiplied by number.

    :signature: left * right
    :arg left: timespan object
    :argType left: timespan object
    :arg right: number to multiply timespan
    :argType right: number
    :returnType: timespan

    .. code::

        yaql> let(timespan(hours => 24) * 2) -> $.hours
        48.0
    """
    return TIMESPAN_TYPE(microseconds=(microseconds(ts) * n))


@specs.name('#operator_*')
@specs.parameter('n', yaqltypes.Number())
@specs.parameter('ts', TIMESPAN_TYPE)
def num_by_timespan(n, ts):
    """:yaql:operator *

    Returns timespan object built on number multiplied by timespan.

    :signature: left * right
    :arg left: number to multiply timespan
    :argType left: number
    :arg right: timespan object
    :argType right: timespan object
    :returnType: timespan

    .. code::

        yaql> let(2 * timespan(hours => 24)) -> $.hours
        48.0
    """
    return TIMESPAN_TYPE(microseconds=(microseconds(ts) * n))


@specs.name('#operator_/')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def div_timespans(ts1, ts2):
    """:yaql:operator /

    Returns result of division of timespan microseconds by another timespan
    microseconds.

    :signature: left / right
    :arg left: left timespan object
    :argType left: timespan object
    :arg right: right timespan object
    :argType right: timespan object
    :returnType: float

    .. code::

        yaql> timespan(hours => 24) / timespan(hours => 12)
        2.0
    """
    return (0.0 + microseconds(ts1)) / microseconds(ts2)


@specs.name('#operator_/')
@specs.parameter('ts', TIMESPAN_TYPE)
@specs.parameter('n', yaqltypes.Number())
def div_timespan_by_num(ts, n):
    """:yaql:operator /

    Returns timespan object divided by number.

    :signature: left / right
    :arg left: left timespan object
    :argType left: timespan object
    :arg right: number to divide by
    :argType right: number
    :returnType: timespan object

    .. code::

        yaql> let(timespan(hours => 24) / 2) -> $.hours
        12.0
    """
    return TIMESPAN_TYPE(microseconds=(microseconds(ts) / n))


@specs.name('#unary_operator_-')
@specs.parameter('ts', TIMESPAN_TYPE)
def negative_timespan(ts):
    """:yaql:operator unary -

    Returns negative timespan.

    :signature: -arg
    :arg arg: input timespan object
    :argType arg: timespan object
    :returnType: timespan object

    .. code::

        yaql> let(-timespan(hours => 24)) -> $.hours
        -24.0
    """
    return -ts


@specs.name('#unary_operator_+')
@specs.parameter('ts', TIMESPAN_TYPE)
def positive_timespan(ts):
    """:yaql:operator unary +

    Returns timespan.

    :signature: +arg
    :arg arg: input timespan object
    :argType arg: timespan object
    :returnType: timespan object

    .. code::

        yaql> let(+timespan(hours => -24)) -> $.hours
        -24.0
    """
    return ts


@specs.yaql_property(DATETIME_TYPE)
def year(dt):
    """:yaql:property year

    Returns year of given datetime.

    :signature: datetime.year
    :returnType: integer

    .. code::

        yaql> datetime(2006, 11, 21, 16, 30).year
        2006
    """
    return dt.year


@specs.yaql_property(DATETIME_TYPE)
def month(dt):
    """:yaql:property month

    Returns month of given datetime.

    :signature: datetime.month
    :returnType: integer

    .. code::

        yaql> datetime(2006, 11, 21, 16, 30).month
        11
    """
    return dt.month


@specs.yaql_property(DATETIME_TYPE)
def day(dt):
    """:yaql:property day

    Returns day of given datetime.

    :signature: datetime.day
    :returnType: integer

    .. code::

        yaql> datetime(2006, 11, 21, 16, 30).day
        21
    """
    return dt.day


@specs.yaql_property(DATETIME_TYPE)
def hour(dt):
    """:yaql:property hour

    Returns hour of given datetime.

    :signature: datetime.hour
    :returnType: integer

    .. code::

        yaql> datetime(2006, 11, 21, 16, 30).hour
        16
    """
    return dt.hour


@specs.yaql_property(DATETIME_TYPE)
def minute(dt):
    """:yaql:property minute

    Returns minutes of given datetime.

    :signature: datetime.minute
    :returnType: integer

    .. code::

        yaql> datetime(2006, 11, 21, 16, 30).minute
        30
    """
    return dt.minute


@specs.yaql_property(DATETIME_TYPE)
def second(dt):
    """:yaql:property minute

    Returns seconds of given datetime.

    :signature: datetime.second
    :returnType: integer

    .. code::

        yaql> datetime(2006, 11, 21, 16, 30, 2).second
        2
    """
    return dt.second


@specs.yaql_property(DATETIME_TYPE)
def microsecond(dt):
    """:yaql:property microsecond

    Returns microseconds of given datetime.

    :signature: datetime.microsecond
    :returnType: integer

    .. code::

        yaql> datetime(2006, 11, 21, 16, 30, 2, 123).microsecond
        123
    """
    return dt.microsecond


@specs.yaql_property(yaqltypes.DateTime())
def date(dt):
    """:yaql:property date

    Returns datetime object with only year, month, day and tzinfo
    part of given datetime.

    :signature: datetime.date
    :returnType: datetime object

    .. code::

        yaql> let(datetime(2006, 11, 21, 16, 30, 2, 123).date) ->
            [$.year, $.month, $.day, $.hour]
        [2006, 11, 21, 0]
    """
    return DATETIME_TYPE(
        year=dt.year, month=dt.month, day=dt.day, tzinfo=dt.tzinfo)


@specs.yaql_property(yaqltypes.DateTime())
def time(dt):
    """:yaql:property time

    Returns timespan object built on datetime without year, month, day and
    tzinfo part of it.

    :signature: datetime.time
    :returnType: timespan object

    .. code::

        yaql> let(datetime(2006, 11, 21, 16, 30).time) -> [$.hours, $.minutes]
        [16.5, 990.0]
    """
    return dt - date(dt)


@specs.yaql_property(DATETIME_TYPE)
def weekday(dt):
    """:yaql:property weekday

    Returns the day of the week as an integer, Monday is 0 and Sunday is 6.

    :signature: datetime.weekday
    :returnType: integer

    .. code::

        yaql> datetime(2006, 11, 21, 16, 30).weekday
        1
    """
    return dt.weekday()


@specs.yaql_property(yaqltypes.DateTime())
def utc(dt):
    """:yaql:property utc

    Returns datetime converted to UTC.

    :signature: datetime.utc
    :returnType: datetime object

    .. code::

        yaql> datetime(2006, 11, 21, 16, 30, offset =>
            timespan(hours => 3)).utc.hour
        13
    """
    return dt - dt.utcoffset()


@specs.yaql_property(DATETIME_TYPE)
def offset(dt):
    """:yaql:property offset

    Returns offset of local time from UTC.

    :signature: datetime.offset
    :returnType: timespan

    .. code::

        yaql> datetime(2006, 11, 21, 16, 30, offset =>
            timespan(hours => 3)).offset.hours
        3.0
    """
    return dt.utcoffset() or ZERO_TIMESPAN


@specs.yaql_property(DATETIME_TYPE)
def timestamp(dt):
    """:yaql:property timestamp

    Returns total seconds from datetime(1970, 1, 1) to
    datetime UTC.

    :signature: datetime.timestamp
    :returnType: float

    .. code::

        yaql> datetime(2006, 11, 21, 16, 30).timestamp
        1164126600.0
    """
    return (utc(dt) - DATETIME_TYPE(1970, 1, 1, tzinfo=UTCTZ)).total_seconds()


@specs.method
@specs.parameter('dt', yaqltypes.DateTime())
@specs.parameter('year', int)
@specs.parameter('month', int)
@specs.parameter('day', int)
@specs.parameter('hour', int)
@specs.parameter('minute', int)
@specs.parameter('second', int)
@specs.parameter('microsecond', int)
@specs.parameter('offset', TIMESPAN_TYPE)
def replace(dt, year=None, month=None, day=None, hour=None, minute=None,
            second=None, microsecond=None, offset=None):
    """:yaql:replace

    Returns datetime object with applied replacements.

    :signature: dt.replace(year => null, month => null, day => null,
                           hour => null, minute => null, second => null,
                           microsecond => null, offset => null)
    :receiverArg dt: input datetime object
    :argType dt: datetime object
    :arg year: number of years to replace, null by default which means
        no replacement
    :argType year: integer between 1 and 9999 inclusive
    :arg month: number of months to replace, null by default which means
        no replacement
    :argType month: integer between 1 and 12 inclusive
    :arg day: number of days to replace, null by default which means
        no replacement
    :argType day: integer between 1 and number of days in given month
    :arg hour: number of hours to replace, null by default which means
        no replacement
    :argType hour: integer between 0 and 23 inclusive
    :arg minute: number of minutes to replace, null by default which means
        no replacement
    :argType minute: integer between 0 and 59 inclusive
    :arg second: number of seconds to replace, null by default which means
        no replacement
    :argType second: integer between 0 and 59 inclusive
    :arg microsecond: number of microseconds to replace, null by default
        which means no replacement
    :argType microsecond: integer between 0 and 1000000-1
    :arg offset: datetime offset in microsecond resolution to replace, null
        by default which means no replacement
    :argType offset: timespan type
    :returnType: datetime object

    .. code::

        yaql> datetime(2015, 9, 29).replace(year => 2014).year
        2014
    """
    replacements = {}
    if year is not None:
        replacements['year'] = year
    if month is not None:
        replacements['month'] = month
    if day is not None:
        replacements['day'] = day
    if hour is not None:
        replacements['hour'] = hour
    if minute is not None:
        replacements['minute'] = minute
    if second is not None:
        replacements['second'] = second
    if microsecond is not None:
        replacements['microsecond'] = microsecond
    if offset is not None:
        replacements['tzinfo'] = _get_tz(offset)

    return dt.replace(**replacements)


@specs.method
@specs.parameter('dt', yaqltypes.DateTime())
@specs.parameter('format__', yaqltypes.String())
def format_(dt, format__):
    """:yaql:format

    Returns a string representing datetime, controlled by a format string.

    :signature: dt.format(format)
    :receiverArg dt: input datetime object
    :argType dt: datetime object
    :arg format: format string
    :argType format: string
    :returnType: string

    .. code::

        yaql> now().format("%A, %d. %B %Y %I:%M%p")
        "Tuesday, 19. July 2016 08:49AM"
    """
    return dt.strftime(format__)


def is_datetime(value):
    """:yaql:isDatetime

    Returns true if value is datetime object, false otherwise.

    :signature: isDatetime(value)
    :arg value: input value
    :argType value: any
    :returnType: boolean

    .. code::

        yaql> isDatetime(now())
        true
        yaql> isDatetime(datetime(2010, 10, 10))
        true
    """
    return isinstance(value, DATETIME_TYPE)


def is_timespan(value):
    """:yaql:isTimespan
    Returns true if value is timespan object, false otherwise.

    :signature: isTimespan(value)
    :arg value: input value
    :argType value: any
    :returnType: boolean

    .. code::

        yaql> isTimespan(now())
        false
        yaql> isTimespan(timespan())
        true
    """
    return isinstance(value, TIMESPAN_TYPE)


def register(context):
    functions = (
        build_datetime, build_timespan, datetime_from_timestamp,
        datetime_from_string, now, localtz, utctz, utc,
        days, hours, minutes, seconds, milliseconds, microseconds,
        datetime_plus_timespan, timespan_plus_datetime,
        datetime_minus_timespan, datetime_minus_datetime,
        timespan_plus_timespan, timespan_minus_timespan,
        datetime_gt_datetime, datetime_gte_datetime,
        datetime_lt_datetime, datetime_lte_datetime,
        timespan_gt_timespan, timespan_gte_timespan,
        timespan_lt_timespan, timespan_lte_timespan,
        negative_timespan, positive_timespan,
        timespan_by_num, num_by_timespan, div_timespans, div_timespan_by_num,
        year, month, day, hour, minute, second, microsecond, weekday,
        offset, timestamp, date, time, replace, format_, is_datetime,
        is_timespan
    )

    for func in functions:
        context.register_function(func)
