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
    zone = _get_tz(offset)
    return DATETIME_TYPE(year, month, day, hour, minute, second,
                         microsecond, zone)


@specs.name('datetime')
@specs.parameter('timestamp', yaqltypes.Number())
@specs.parameter('offset', TIMESPAN_TYPE)
def datetime_from_timestamp(timestamp, offset=ZERO_TIMESPAN):
    zone = _get_tz(offset)
    return datetime.datetime.fromtimestamp(timestamp, tz=zone)


@specs.name('datetime')
@specs.parameter('string', yaqltypes.String())
@specs.parameter('format__', yaqltypes.String(True))
def datetime_from_string(string, format__=None):
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
    return TIMESPAN_TYPE(
        days=days, hours=hours, minutes=minutes, seconds=seconds,
        milliseconds=milliseconds, microseconds=microseconds)


@specs.yaql_property(TIMESPAN_TYPE)
def microseconds(timespan):
    return (86400000000 * timespan.days +
            1000000 * timespan.seconds +
            timespan.microseconds)


@specs.yaql_property(TIMESPAN_TYPE)
def milliseconds(timespan):
    return microseconds(timespan) / 1000.0


@specs.yaql_property(TIMESPAN_TYPE)
def seconds(timespan):
    return microseconds(timespan) / 1000000.0


@specs.yaql_property(TIMESPAN_TYPE)
def minutes(timespan):
    return microseconds(timespan) / 60000000.0


@specs.yaql_property(TIMESPAN_TYPE)
def hours(timespan):
    return microseconds(timespan) / 3600000000.0


@specs.yaql_property(TIMESPAN_TYPE)
def days(timespan):
    return microseconds(timespan) / 86400000000.0


def now(offset=ZERO_TIMESPAN):
    zone = _get_tz(offset)
    return DATETIME_TYPE.now(tz=zone)


def localtz():
    if python_time.daylight:
        return TIMESPAN_TYPE(seconds=-python_time.altzone)
    else:
        return TIMESPAN_TYPE(seconds=-python_time.timezone)


def utctz():
    return ZERO_TIMESPAN


@specs.name('#operator_+')
@specs.parameter('dt', yaqltypes.DateTime())
@specs.parameter('ts', TIMESPAN_TYPE)
def datetime_plus_timespan(dt, ts):
    return dt + ts


@specs.name('#operator_+')
@specs.parameter('ts', TIMESPAN_TYPE)
@specs.parameter('dt', yaqltypes.DateTime())
def timespan_plus_datetime(ts, dt):
    return ts + dt


@specs.name('#operator_-')
@specs.parameter('dt', yaqltypes.DateTime())
@specs.parameter('ts', TIMESPAN_TYPE)
def datetime_minus_timespan(dt, ts):
    return dt - ts


@specs.name('#operator_-')
@specs.parameter('dt1', yaqltypes.DateTime())
@specs.parameter('dt2', yaqltypes.DateTime())
def datetime_minus_datetime(dt1, dt2):
    return dt1 - dt2


@specs.name('#operator_+')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def timespan_plus_timespan(ts1, ts2):
    return ts1 + ts2


@specs.name('#operator_-')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def timespan_minus_timespan(ts1, ts2):
    return ts1 - ts2


@specs.name('#operator_>')
@specs.parameter('dt1', yaqltypes.DateTime())
@specs.parameter('dt2', yaqltypes.DateTime())
def datetime_gt_datetime(dt1, dt2):
    return dt1 > dt2


@specs.name('#operator_>=')
@specs.parameter('dt1', yaqltypes.DateTime())
@specs.parameter('dt2', yaqltypes.DateTime())
def datetime_gte_datetime(dt1, dt2):
    return dt1 >= dt2


@specs.name('#operator_<')
@specs.parameter('dt1', yaqltypes.DateTime())
@specs.parameter('dt2', yaqltypes.DateTime())
def datetime_lt_datetime(dt1, dt2):
    return dt1 < dt2


@specs.name('#operator_<=')
@specs.parameter('dt1', yaqltypes.DateTime())
@specs.parameter('dt2', yaqltypes.DateTime())
def datetime_lte_datetime(dt1, dt2):
    return dt1 <= dt2


@specs.name('#operator_>')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def timespan_gt_timespan(ts1, ts2):
    return ts1 > ts2


@specs.name('#operator_>=')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def timespan_gte_timespan(ts1, ts2):
    return ts1 >= ts2


@specs.name('#operator_<')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def timespan_lt_timespan(ts1, ts2):
    return ts1 < ts2


@specs.name('#operator_<=')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def timespan_lte_timespan(ts1, ts2):
    return ts1 <= ts2


@specs.name('#operator_*')
@specs.parameter('ts', TIMESPAN_TYPE)
@specs.parameter('n', yaqltypes.Number())
def timespan_by_num(ts, n):
    return TIMESPAN_TYPE(microseconds=(microseconds(ts) * n))


@specs.name('#operator_*')
@specs.parameter('n', yaqltypes.Number())
@specs.parameter('ts', TIMESPAN_TYPE)
def num_by_timespan(n, ts):
    return TIMESPAN_TYPE(microseconds=(microseconds(ts) * n))


@specs.name('#operator_/')
@specs.parameter('ts1', TIMESPAN_TYPE)
@specs.parameter('ts2', TIMESPAN_TYPE)
def div_timespans(ts1, ts2):
    return (0.0 + microseconds(ts1)) / microseconds(ts2)


@specs.name('#operator_/')
@specs.parameter('ts', TIMESPAN_TYPE)
@specs.parameter('n', yaqltypes.Number())
def div_timespan_by_num(ts, n):
    return TIMESPAN_TYPE(microseconds=(microseconds(ts) / n))


@specs.name('#unary_operator_-')
@specs.parameter('ts', TIMESPAN_TYPE)
def negative_timespan(ts):
    return -ts


@specs.name('#unary_operator_+')
@specs.parameter('ts', TIMESPAN_TYPE)
def positive_timespan(ts):
    return ts


@specs.yaql_property(DATETIME_TYPE)
def year(dt):
    return dt.year


@specs.yaql_property(DATETIME_TYPE)
def month(dt):
    return dt.month


@specs.yaql_property(DATETIME_TYPE)
def day(dt):
    return dt.day


@specs.yaql_property(DATETIME_TYPE)
def hour(dt):
    return dt.hour


@specs.yaql_property(DATETIME_TYPE)
def minute(dt):
    return dt.minute


@specs.yaql_property(DATETIME_TYPE)
def second(dt):
    return dt.second


@specs.yaql_property(DATETIME_TYPE)
def microsecond(dt):
    return dt.microsecond


@specs.yaql_property(yaqltypes.DateTime())
def date(dt):
    return DATETIME_TYPE(
        year=dt.year, month=dt.month, day=dt.day, tzinfo=dt.tzinfo)


@specs.yaql_property(yaqltypes.DateTime())
def time(dt):
    return dt - date(dt)


@specs.yaql_property(DATETIME_TYPE)
def weekday(dt):
    return dt.weekday()


@specs.yaql_property(yaqltypes.DateTime())
def utc(dt):
    return dt - dt.utcoffset()


@specs.yaql_property(DATETIME_TYPE)
def offset(dt):
    return dt.utcoffset() or ZERO_TIMESPAN


@specs.yaql_property(DATETIME_TYPE)
def timestamp(dt):
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
    return dt.strftime(format__)


def is_datetime(value):
    return isinstance(value, DATETIME_TYPE)


def is_timespan(value):
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
