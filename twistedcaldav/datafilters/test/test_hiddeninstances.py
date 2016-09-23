##
# Copyright (c) 2009-2016 Apple Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

from twistedcaldav.datafilters.hiddeninstance import HiddenInstanceFilter
from twistedcaldav.ical import Component
import twistedcaldav.test.util


class HiddenInstanceFilterTest (twistedcaldav.test.util.TestCase):

    def test_public_default(self):

        data = (
            (
                "Nothing hidden, no recurrence",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VEVENT
UID:12345-67890
DTSTART:20080601T120000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
END:VCALENDAR
""",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VEVENT
UID:12345-67890
DTSTART:20080601T120000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
END:VCALENDAR
""",
            ),
            (
                "Nothing hidden, recurrence",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VEVENT
UID:12345-67890
DTSTART:20080601T120000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080602T120000Z
DTSTART:20080602T123000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080603T120000Z
DTSTART:20080603T123000Z
DTEND:20080601T133000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
END:VCALENDAR
""",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VEVENT
UID:12345-67890
DTSTART:20080601T120000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080602T120000Z
DTSTART:20080602T123000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080603T120000Z
DTSTART:20080603T123000Z
DTEND:20080601T133000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
END:VCALENDAR
""",
            ),
            (
                "One hidden",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VEVENT
UID:12345-67890
DTSTART:20080601T120000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080602T120000Z
DTSTART:20080602T123000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080603T120000Z
DTSTART:20080603T123000Z
DTEND:20080601T133000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
X-CALENDARSERVER-HIDDEN-INSTANCE:T
END:VEVENT
END:VCALENDAR
""",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VEVENT
UID:12345-67890
DTSTART:20080601T120000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
EXDATE:20080603T120000Z
ORGANIZER;CN=User 01:mailto:user1@example.com
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080602T120000Z
DTSTART:20080602T123000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
END:VCALENDAR
""",
            ),
            (
                "Two hidden",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VEVENT
UID:12345-67890
DTSTART:20080601T120000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080602T120000Z
DTSTART:20080602T123000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
X-CALENDARSERVER-HIDDEN-INSTANCE:T
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080603T120000Z
DTSTART:20080603T123000Z
DTEND:20080601T133000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
X-CALENDARSERVER-HIDDEN-INSTANCE:T
END:VEVENT
END:VCALENDAR
""",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VEVENT
UID:12345-67890
DTSTART:20080601T120000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
EXDATE:20080602T120000Z
EXDATE:20080603T120000Z
ORGANIZER;CN=User 01:mailto:user1@example.com
RRULE:FREQ=DAILY
END:VEVENT
END:VCALENDAR
""",
            ),
            (
                "One hidden with timezone",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VTIMEZONE
LAST-MODIFIED:20040110T032845Z
TZID:US/Eastern
BEGIN:DAYLIGHT
DTSTART:20000404T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:20001026T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
UID:12345-67890
DTSTART;TZID=US/Eastern:20080601T120000
DTEND;TZID=US/Eastern:20080601T130000
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID;TZID=US/Eastern:20080602T120000
DTSTART;TZID=US/Eastern:20080602T123000
DTEND;TZID=US/Eastern:20080601T130000
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID;TZID=US/Eastern:20080603T120000
DTSTART;TZID=US/Eastern:20080603T123000
DTEND;TZID=US/Eastern:20080601T133000
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
X-CALENDARSERVER-HIDDEN-INSTANCE:T
END:VEVENT
END:VCALENDAR
""",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VTIMEZONE
TZID:US/Eastern
LAST-MODIFIED:20040110T032845Z
BEGIN:DAYLIGHT
DTSTART:20000404T020000
RRULE:FREQ=YEARLY;BYDAY=1SU;BYMONTH=4
TZNAME:EDT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
END:DAYLIGHT
BEGIN:STANDARD
DTSTART:20001026T020000
RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10
TZNAME:EST
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
UID:12345-67890
DTSTART;TZID=US/Eastern:20080601T120000
DTEND;TZID=US/Eastern:20080601T130000
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
EXDATE;TZID=US/Eastern:20080603T120000
ORGANIZER;CN=User 01:mailto:user1@example.com
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID;TZID=US/Eastern:20080602T120000
DTSTART;TZID=US/Eastern:20080602T123000
DTEND;TZID=US/Eastern:20080601T130000
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
END:VCALENDAR
""",
            ),
            (
                "No master, no hidden",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080602T120000Z
DTSTART:20080602T123000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080603T120000Z
DTSTART:20080603T123000Z
DTEND:20080601T133000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
END:VCALENDAR
""",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080602T120000Z
DTSTART:20080602T123000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080603T120000Z
DTSTART:20080603T123000Z
DTEND:20080601T133000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
END:VCALENDAR
""",
            ),
            (
                "No master, one hidden",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080602T120000Z
DTSTART:20080602T123000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080603T120000Z
DTSTART:20080603T123000Z
DTEND:20080601T133000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
X-CALENDARSERVER-HIDDEN-INSTANCE:T
END:VEVENT
END:VCALENDAR
""",
                """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CALENDARSERVER.ORG//NONSGML Version 1//EN
BEGIN:VEVENT
UID:12345-67890
RECURRENCE-ID:20080602T120000Z
DTSTART:20080602T123000Z
DTEND:20080601T130000Z
ATTENDEE:mailto:user1@example.com
ATTENDEE:mailto:user2@example.com
ORGANIZER;CN=User 01:mailto:user1@example.com
END:VEVENT
END:VCALENDAR
""",
            ),
        )

        for title, test, result in data:
            ics = Component.fromString(test.replace("\n", "\r\n"))
            self.assertEqual(str(HiddenInstanceFilter().filter(ics)), result.replace("\n", "\r\n"), msg="Failed: %s" % (title,))
