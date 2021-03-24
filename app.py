import os

os.system("python setup.py build")
os.system("python setup.py install")
os.system("locust -f locust_test.py --web-port 8080")
