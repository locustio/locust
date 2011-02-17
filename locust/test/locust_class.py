from locust.core import Locust, require_once, WebLocust
import unittest
from testcases import WebserverTestCase

class TestLocustClass(unittest.TestCase):
	def test_task_ratio(self):
		t1 = lambda l: None
		t2 = lambda l: None
		class MyLocust(Locust):
			tasks = {t1:5, t2:2}
			
		l = MyLocust()
		
		t1_count = len([t for t in l.tasks if t == t1])
		t2_count = len([t for t in l.tasks if t == t2])
		
		self.assertEqual(t1_count, 5)
		self.assertEqual(t2_count, 2)
	
	def test_require_once(self):
		self.t1_executed = False
		self.t2_executed = False
		def t1(l):
			self.t1_executed = True
		
		@require_once(t1)
		def t2(l):
			self.t2_executed = True
		
		class MyLocust(Locust):
			tasks = [t2]
		
		l = MyLocust()
		l.schedule_task(l.get_next_task())
		l.execute_next_task()
		self.assertTrue(self.t1_executed)
		self.assertFalse(self.t2_executed)
		l.execute_next_task()
		self.assertTrue(self.t2_executed)
	
	def test_schedule_task(self):
		self.t1_executed = False
		self.t2_arg = None
		
		def t1(l):
			self.t1_executed = True
		
		def t2(l, arg):
			self.t2_arg = arg
		
		class MyLocust(Locust):
			tasks = [t1, t2]
		
		locust = MyLocust()
		locust.schedule_task(t1)
		locust.execute_next_task()
		self.assertTrue(self.t1_executed)
		
		locust.schedule_task(t2, "argument to t2")
		locust.execute_next_task()
		self.assertEqual("argument to t2", self.t2_arg)
	

class TestWebLocustClass(WebserverTestCase):
	def test_get_request(self):
		self.response = ""
		def t1(l):
			self.response = l.client.get("/ultra_fast")
		class MyLocust(WebLocust):
			tasks = [t1]
			host = "http://127.0.0.1:%i" % self.port
		
		my_locust = MyLocust()
		t1(my_locust)
		self.assertEqual(self.response, "This is an ultra fast response")
	
	def test_client_request_headers(self):
		class MyLocust(WebLocust):
			host = "http://127.0.0.1:%i" % self.port
		
		locust = MyLocust()
		self.assertEqual("hello", locust.client.get("/request_header_test", {"X-Header-Test":"hello"}))
	
	def test_client_get(self):
		class MyLocust(WebLocust):
			host = "http://127.0.0.1:%i" % self.port
		
		locust = MyLocust()
		self.assertEqual("GET", locust.client.get("/request_method"))
	
	def test_client_post(self):
		class MyLocust(WebLocust):
			host = "http://127.0.0.1:%i" % self.port
		
		locust = MyLocust()
		self.assertEqual("POST", locust.client.post("/request_method", {"arg":"hello world"}))
		self.assertEqual("hello world", locust.client.post("/post", {"arg":"hello world"}))
	
