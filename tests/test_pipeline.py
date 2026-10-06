"""
tests/test_pipeline.py
Unit and Integration Tests for Distributed Web Log Analytics Pipeline
"""

import unittest
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing.parser import parse_line, parse_request
from mapreduce.session_mapper import parse_epoch
from mapreduce.session_reducer import process_host_sessions
from mapreduce.navigation_reducer import process_host_transitions

class TestLogParser(unittest.TestCase):
    def test_valid_log_line(self):
        line = '199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245'
        valid, record = parse_line(line)
        self.assertTrue(valid)
        self.assertEqual(record[0], "199.72.81.55")
        self.assertEqual(record[2], "GET")
        self.assertEqual(record[3], "/history/apollo/")
        self.assertEqual(record[5], "200")
        self.assertEqual(record[6], "6245")

    def test_missing_bytes_dash(self):
        line = 'uplherc.upl.com - - [01/Aug/1995:00:00:07 -0400] "GET / HTTP/1.0" 304 -'
        valid, record = parse_line(line)
        self.assertTrue(valid)
        self.assertEqual(record[6], "0")

    def test_malformed_empty_line(self):
        valid, _ = parse_line("")
        self.assertFalse(valid)

    def test_malformed_incomplete_line(self):
        valid, _ = parse_line("just a random corrupt string")
        self.assertFalse(valid)

class TestSessionizationLogic(unittest.TestCase):
    def test_epoch_parsing(self):
        epoch1 = parse_epoch("01/Jul/1995:00:00:00 -0400")
        epoch2 = parse_epoch("01/Jul/1995:00:30:00 -0400")
        self.assertEqual(epoch2 - epoch1, 1800)

    def test_session_timeout_threshold(self):
        # Two requests within 10 minutes -> 1 session
        # Third request 40 minutes later -> new session
        requests = [
            (1000, "01/Jul/1995:00:00:00 -0400", "/page1", 100),
            (1600, "01/Jul/1995:00:10:00 -0400", "/page2", 200),
            (4200, "01/Jul/1995:00:50:00 -0400", "/page3", 300),
        ]
        
        import io
        buf = io.StringIO()
        process_host_sessions("host1", requests, out=buf)
        emitted = buf.getvalue().strip().splitlines()
            
        self.assertEqual(len(emitted), 2)
        # Session 1: 2 requests
        self.assertIn("host1_s1", emitted[0])
        self.assertIn("\t2\t", emitted[0])
        # Session 2: 1 request
        self.assertIn("host1_s2", emitted[1])
        self.assertIn("\t1\t", emitted[1])

class TestNavigationLogic(unittest.TestCase):
    def test_intra_session_transition(self):
        # Two requests within 30 minutes -> 1 transition
        # Third request 45 minutes later -> no transition across session boundary
        requests = [
            (1000, "/index.html"),
            (1500, "/about.html"),
            (4500, "/contact.html"),
        ]
        
        import io
        buf = io.StringIO()
        process_host_transitions("host1", requests, out=buf)
        emitted = buf.getvalue().strip().splitlines()
            
        self.assertEqual(len(emitted), 1)
        self.assertEqual(emitted[0], "/index.html\t/about.html\t1")

if __name__ == "__main__":
    unittest.main()
