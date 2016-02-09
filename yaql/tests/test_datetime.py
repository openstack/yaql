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
import time

from dateutil import tz
from testtools import matchers

import yaql.tests

DT = datetime.datetime
TS = datetime.timedelta


class TestDatetime(yaql.tests.TestCase):
    def test_build_datetime_components(self):
        dt = DT(2015, 8, 29, tzinfo=tz.tzutc())
        self.assertEqual(
            dt, self.eval('datetime(2015, 8, 29)'))
        self.assertEqual(
            dt, self.eval('datetime(year => 2015, month => 8, day => 29,'
                          'hour => 0, minute => 0, second => 0, '
                          'microsecond => 0)'))

    def test_build_datetime_iso(self):
        self.assertEqual(
            DT(2015, 8, 29, tzinfo=tz.tzutc()),
            self.eval('datetime("2015-8-29")')
        )
        self.assertEqual(
            DT(2008, 9, 3, 20, 56, 35, 450686, tzinfo=tz.tzutc()),
            self.eval('datetime("2008-09-03T20:56:35.450686")')
        )
        self.assertEqual(
            DT(2008, 9, 3, 20, 56, 35, 450686, tzinfo=tz.tzutc()),
            self.eval('datetime("2008-09-03T20:56:35.450686Z")')
        )
        self.assertEqual(
            DT(2008, 9, 3, 0, 0, tzinfo=tz.tzutc()),
            self.eval('datetime("20080903")')
        )
        dt = self.eval('datetime("2008-09-03T20:56:35.450686+03:00")')
        self.assertEqual(
            DT(2008, 9, 3, 20, 56, 35, 450686),
            dt.replace(tzinfo=None)
        )
        self.assertEqual(TS(hours=3), dt.utcoffset())

    def test_build_datetime_string(self):
        self.assertEqual(
            DT(2006, 11, 21, 16, 30, tzinfo=tz.tzutc()),
            self.eval('datetime("Tuesday, 21. November 2006 04:30PM", '
                      '"%A, %d. %B %Y %I:%M%p")')
        )

    def test_datetime_fields(self):
        dt = DT(2006, 11, 21, 16, 30, tzinfo=tz.tzutc())
        self.assertEqual(2006, self.eval('$.year', dt))
        self.assertEqual(11, self.eval('$.month', dt))
        self.assertEqual(21, self.eval('$.day', dt))
        self.assertEqual(16, self.eval('$.hour', dt))
        self.assertEqual(30, self.eval('$.minute', dt))
        self.assertEqual(0, self.eval('$.second', dt))
        self.assertEqual(0, self.eval('$.microsecond', dt))
        self.assertEqual(1164126600, self.eval('$.timestamp', dt))
        self.assertEqual(1, self.eval('$.weekday', dt))
        self.assertEqual(TS(), self.eval('$.offset', dt))
        self.assertEqual(TS(hours=16, minutes=30), self.eval('$.time', dt))
        self.assertEqual(dt.replace(hour=0, minute=0), self.eval('$.date', dt))
        self.assertEqual(dt, self.eval('$.utc', dt))

    def test_build_timespan(self):
        self.assertEqual(TS(0), self.eval('timespan()'))
        self.assertEqual(
            TS(1, 7384, 5006),
            self.eval('timespan(days => 1, hours => 2, minutes => 3, '
                      'seconds => 4, milliseconds => 5, microseconds => 6)'))
        self.assertEqual(
            TS(1, 7384, 4994),
            self.eval('timespan(days => 1, hours => 2, minutes => 3, '
                      'seconds =>4, milliseconds => 5, microseconds => -6)'))

        self.assertEqual(
            TS(microseconds=-1000), self.eval('timespan(milliseconds => -1)'))

    def test_datetime_from_timestamp(self):
        dt = DT(2006, 11, 21, 16, 30, tzinfo=tz.tzutc())
        self.assertEqual(dt, self.eval('datetime(1164126600)'))

    def test_replace(self):
        dt = DT(2006, 11, 21, 16, 30, tzinfo=tz.tzutc())
        self.assertEqual(
            DT(2009, 11, 21, 16, 40, tzinfo=tz.tzutc()),
            self.eval('$.replace(year => 2009, minute => 40)', dt))

    def test_timespan_fields(self):
        ts = TS(1, 51945, 5000)
        self.assertAlmostEqual(1.6, self.eval('$.days', ts), places=2)
        self.assertAlmostEqual(38.43, self.eval('$.hours', ts), places=2)
        self.assertAlmostEqual(2305.75, self.eval('$.minutes', ts), places=2)
        self.assertAlmostEqual(138345, self.eval('$.seconds', ts), places=1)
        self.assertEqual(138345005, self.eval('$.milliseconds', ts))
        self.assertEqual(138345005000, self.eval('$.microseconds', ts))

    def test_now(self):
        self.assertIsInstance(self.eval('now()'), DT)
        self.assertIsInstance(self.eval('now(utctz())'), DT)
        self.assertIsInstance(self.eval('now(localtz())'), DT)
        self.assertThat(
            self.eval('now(utctz()) - now()'),
            matchers.LessThan(TS(seconds=1))
        )
        self.assertTrue(self.eval('now(localtz()).offset = localtz()'))

    def test_datetime_math(self):
        self.context['dt1'] = self.eval('now()')
        time.sleep(0.1)
        self.context['dt2'] = self.eval('now()')
        delta = TS(milliseconds=120)
        self.assertIsInstance(self.eval('$dt2 - $dt1'), TS)
        self.assertThat(self.eval('$dt2 - $dt1'), matchers.LessThan(delta))
        self.assertTrue(self.eval('($dt2 - $dt1) + $dt1 = $dt2'))
        self.assertTrue(self.eval('$dt1 + ($dt2 - $dt1) = $dt2'))
        self.assertThat(
            self.eval('($dt2 - $dt1) * 2'), matchers.LessThan(2 * delta))
        self.assertThat(
            self.eval('2.1 * ($dt2 - $dt1)'), matchers.LessThan(2 * delta))
        self.assertTrue(self.eval('-($dt1 - $dt2) = +($dt2 - $dt1)'))
        self.assertTrue(self.eval('$dt2 > $dt1'))
        self.assertTrue(self.eval('$dt2 >= $dt1'))
        self.assertTrue(self.eval('$dt2 != $dt1'))
        self.assertTrue(self.eval('$dt1 = $dt1'))
        self.assertTrue(self.eval('$dt1 < $dt2'))
        self.assertTrue(self.eval('$dt1 <= $dt2'))
        self.assertEqual(-1, self.eval('($dt2 - $dt1) / ($dt1 - $dt2)'))
        self.assertTrue(self.eval('$dt2 - ($dt2 - $dt1) = $dt1'))
        self.assertEqual(
            0, self.eval('($dt2 - $dt1) - ($dt2 - $dt1)').total_seconds())

        delta2 = self.eval('($dt2 - $dt1) / 2.1')
        self.assertThat(delta2, matchers.LessThan(delta / 2))
        self.assertTrue(self.eval('$dt1 + $ < $dt2', delta2))
        self.assertTrue(self.eval('$ + $dt1 < $dt2', delta2))
        self.assertTrue(self.eval('$dt2 - $dt1 > $', delta2))
        self.assertTrue(self.eval('$dt2 - $dt1 >= $', delta2))
        self.assertTrue(self.eval('$dt2 - $dt1 != $', delta2))
        self.assertFalse(self.eval('$dt2 - $dt1 < $', delta2))
        self.assertFalse(self.eval('$dt2 - $dt1 <= $', delta2))
        self.assertTrue(self.eval('($dt2 - $dt1) + $ > $', delta2))

    def test_is_datetime(self):
        self.assertTrue(self.eval('isDatetime(datetime("2015-8-29"))'))
        self.assertFalse(self.eval('isDatetime(123)'))
        self.assertFalse(self.eval('isDatetime(abc)'))

    def test_is_timespan(self):
        self.assertTrue(self.eval('isTimespan(timespan(milliseconds => -1))'))
        self.assertFalse(self.eval('isTimespan(123)'))
        self.assertFalse(self.eval('isTimespan(abc)'))
