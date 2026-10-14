"""Representative sample data for the `sessions` and `navigation_patterns`
collections.

These documents mirror the schema and realistic values produced by the Hadoop
MapReduce jobs against the NASA Kennedy Space Center HTTP logs. They are used as
a fallback so the dashboard is populated even before the (Docker-based) HDFS /
MapReduce pipeline has been run. A real pipeline run overwrites them.
"""

# (host, session_id, start, end, request_count, duration_seconds, total_bytes)
_SESSIONS = [
    ("199.72.81.55", "s1", "1995-07-01 00:00:01", "1995-07-01 00:04:12", 14, 251, 184320),
    ("unicomp6.unicomp.net", "s1", "1995-07-01 00:00:06", "1995-07-01 00:12:48", 42, 762, 892160),
    ("199.120.110.21", "s1", "1995-07-01 00:00:09", "1995-07-01 00:01:34", 6, 85, 73400),
    ("burger.letters.com", "s1", "1995-07-01 00:00:11", "1995-07-01 00:28:51", 71, 1720, 2451456),
    ("ppptky391.asahi-net.or.jp", "s1", "1995-07-01 00:01:22", "1995-07-01 00:03:09", 9, 107, 112640),
    ("alyssa.prodigy.com", "s1", "1995-07-01 00:02:40", "1995-07-01 00:15:21", 33, 761, 714752),
    ("piweba3y.prodigy.com", "s1", "1995-07-01 00:03:01", "1995-07-01 00:41:55", 118, 2334, 4194304),
    ("ix-or6-14.ix.netcom.com", "s1", "1995-07-01 00:04:17", "1995-07-01 00:06:02", 7, 105, 86016),
    ("slip137-5.pt.uk.ibm.net", "s1", "1995-07-01 00:05:33", "1995-07-01 00:09:48", 18, 255, 311296),
    ("www-b2.proxy.aol.com", "s1", "1995-07-01 00:06:19", "1995-07-01 00:33:40", 54, 1641, 1572864),
    ("gateway.cisco.com", "s1", "1995-07-01 00:07:44", "1995-07-01 00:08:59", 4, 75, 40960),
    ("port03.csl.co.uk", "s1", "1995-07-01 00:08:12", "1995-07-01 00:19:37", 27, 685, 583680),
    ("drjo003a096.embratel.net.br", "s1", "1995-07-01 00:09:50", "1995-07-01 00:11:03", 5, 73, 61440),
    ("ppp13.dialin.ucla.edu", "s1", "1995-07-01 00:10:28", "1995-07-01 00:52:14", 96, 2506, 3407872),
    ("dd10-046.compuserve.com", "s1", "1995-07-01 00:11:19", "1995-07-01 00:14:52", 12, 213, 155648),
    ("crl5.crl.com", "s1", "1995-07-01 00:12:03", "1995-07-01 00:25:41", 38, 818, 798720),
    ("204.120.229.4", "s1", "1995-07-01 00:13:47", "1995-07-01 00:15:09", 6, 82, 69632),
    ("ad11-013.compuserve.com", "s1", "1995-07-01 00:14:22", "1995-07-01 00:38:50", 61, 1468, 1884160),
    ("tty10-05.swipnet.se", "s1", "1995-07-01 00:15:58", "1995-07-01 00:17:11", 5, 73, 51200),
    ("rush.internic.net", "s1", "1995-07-01 00:16:40", "1995-07-01 00:49:22", 83, 1962, 2883584),
]

# (source_url, destination_url, count)
_NAVIGATION = [
    ("/ksc.html", "/images/ksclogo-medium.gif", 41623),
    ("/shuttle/missions/missions.html", "/images/NASA-logosmall.gif", 38214),
    ("/", "/ksc.html", 34188),
    ("/shuttle/countdown/", "/htbin/cdt_main.pl", 29845),
    ("/history/apollo/", "/images/NASA-logosmall.gif", 31207),
    ("/shuttle/missions/missions.html", "/images/KSC-logosmall.gif", 24931),
    ("/", "/history/apollo/", 22504),
    ("/ksc.html", "/shuttle/missions/missions.html", 28116),
    ("/shuttle/countdown/", "/shuttle/countdown/liftoff.html", 19842),
    ("/history/apollo/", "/history/apollo/apollo-11/", 18402),
    ("/images/launch-logo.gif", "/shuttle/countdown/", 16733),
    ("/shuttle/missions/sts-69/", "/shuttle/missions/sts-69/mission-sts-69.html", 15988),
    ("/", "/images/NASA-logosmall.gif", 14920),
    ("/ksc.html", "/images/MOSAIC-logosmall.gif", 13874),
    ("/shuttle/missions/sts-70/", "/shuttle/missions/sts-70/mission-sts-70.html", 12640),
    ("/history/apollo/apollo-11/", "/history/apollo/apollo-11/apollo-11.html", 11905),
    ("/shuttle/countdown/liftoff.html", "/images/NASA-logosmall.gif", 10877),
    ("/facilities/", "/facilities/vab.html", 9842),
    ("/history/", "/history/apollo/", 9211),
    ("/shuttle/technology/sts-newsref/", "/shuttle/technology/sts-newsref/stsref-toc.html", 8530),
    ("/images/KSC-logosmall.gif", "/ksc.html", 7914),
    ("/software/winvn/", "/software/winvn/winvn.html", 7203),
    ("/shuttle/missions/sts-71/", "/shuttle/missions/sts-71/mission-sts-71.html", 6688),
    ("/news/", "/news/sci.space.news/", 5942),
    ("/persons/astronauts/", "/persons/astronauts/u-to-z/", 5110),
]


def sample_sessions():
    return [
        {
            "host": host,
            "session_id": f"{host}_{sid}",
            "start_time": start,
            "end_time": end,
            "request_count": count,
            "duration_seconds": duration,
            "total_bytes": total_bytes,
        }
        for host, sid, start, end, count, duration, total_bytes in _SESSIONS
    ]


def sample_navigation():
    return [
        {"source_url": src, "destination_url": dst, "count": count}
        for src, dst, count in _NAVIGATION
    ]
