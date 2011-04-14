from locust.stats import RequestStats
import unittest
import time

class TestRequestStats(unittest.TestCase):
	def setUp(self):
		self.s = RequestStats("test_entry")
		self.s.log(45)
		self.s.log(135)
		self.s.log(44)
		self.s.log_error(Exception("dummy fail"))
		self.s.log_error(Exception("dummy fail"))
		self.s.log(375)
		self.s.log(601)
		self.s.log(35)
		self.s.log(79)
		self.s.log_error(Exception("dummy fail"))
	
	def test_median(self):
		self.assertEqual(self.s.median_response_time, 79)
	
	def test_total_rps(self):
		self.assertEqual(self.s.total_rps, 7)
	
	def test_current_tps(self):
		self.s.last_request_timestamp = int(time.time()) + 2
		self.assertEqual(self.s.current_rps, 3.5)
		
		self.s.last_request_timestamp = int(time.time()) + 25
		self.assertEqual(self.s.current_rps, 0)
	
	def test_num_reqs_fails(self):
		self.assertEqual(self.s.num_reqs, 7)
		self.assertEqual(self.s.num_failures, 3)
	
	def test_avg(self):
		self.assertEqual(self.s.avg_response_time, 187.71428571428571428571428571429)
	
	def test_reset(self):
		self.s.reset()
		self.s.log(756)
		self.s.log_error(Exception("dummy fail after reset"))
		self.s.log(85)
		
		self.assertEqual(self.s.total_rps, 2)
		self.assertEqual(self.s.num_reqs, 2)
		self.assertEqual(self.s.num_failures, 1)
		self.assertEqual(self.s.avg_response_time, 420.5)
		self.assertEqual(self.s.median_response_time, 85)
	
	def test_aggregation(self):
		s1 = RequestStats("aggregate me!")
		s1.log(12)
		s1.log(12)
		s1.log(38)
		s1.log_error("Dummy exzeption")
		
		s2 = RequestStats("aggregate me!")
		s2.log_error("Dummy exzeption")
		s2.log_error("Dummy exzeption")
		s2.log(12)
		s2.log(99)
		s2.log(14)
		s2.log(55)
		s2.log(38)
		s2.log(55)
		s2.log(97)
		
		s = s1 + s2
		
		self.assertEqual(s.num_reqs, 10)
		self.assertEqual(s.num_failures, 3)
		self.assertEqual(s.median_response_time, 38)
		self.assertEqual(s.avg_response_time, 43.2)
	
##	def test_size(self):
##		from copy import copy
##		import cPickle as pickle
##		from random import randint
##		for i in xrange(0, 5000000):
##			self.s.log(randint(0, 30000))
##		new = copy(self.s)
##		new.response_times = {self.s.median_response_time:self.s.num_reqs}
##		print "length:", len(pickle.dumps(new))