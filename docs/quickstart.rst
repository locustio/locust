=============
Quick start
=============

Below is a quick little example of a simple **locustfile.py**::

    from locust import Locust, TaskSet
    
    def login(l):
        l.client.post("/login", {"username":"ellen_key", "password":"education"})
    
    def index(l):
        l.client.get("/")
    
    def profile(l):
        l.client.get("/profile")
    
    class UserBehavior(TaskSet):
        tasks = {index:2, profile:1}
        
        def on_start(self):
            login(self)
    
    class WebsiteUser(Locust):
        task_set = UserBehavior
        min_wait=5000
        max_wait=9000
    

Here we define a number of locust tasks, which are normal Python callables that take one argument 
(a Locust class instance). These tasks are gathered under a :py:class:`TaskSet <locust.core.TaskSet>` 
class in the *task* attribute. Then we have a :py:class:`Locust <locust.core.Locust>` class which 
represents a User, where we define how long a simulated user should wait between executing tasks, as 
well as what TaskSet class should define the user's "behaviour". TaskSets can be nested.

Another way we could declare tasks, which is usually more convenient, is to use the 
@task decorator. The following code is equivalent to the above::

    from locust import Locust, TaskSet, task
    
    class UserBehavior(TaskSet):
        def on_start(self):
            """ on_start is called when a Locust start before any task is scheduled """
            self.login()
        
        def login(self):
            self.client.post("/login", {"username":"ellen_key", "password":"education"})
        
        @task(2)
        def index(self):
            self.client.get("/")
        
        @task(1)
        def profile(self):
            self.client.get("/profile")
    
    class WebsiteUser(Locust):
        task_set = UserBehavior
        min_wait=5000
        max_wait=9000

The Locust class also allows one to specify minimum and maximum wait time - per simulated user -
between the execution of tasks (*min_wait* and *max_wait*) as well as other user behaviours.

To run Locust with the above locust file, if it was named *locustfile.py*, we could run 
(in the same directory as locustfile.py)::

    locust 

or if the locust file is located elsewhere we could run::

    locust -f ../locust_files/my_locust_file.py

To run Locust distributed across multiple processes we would start a master process by specifying --master::

    locust -f ../locust_files/my_locust_file.py --master

and then we would start an arbitrary number of slave processes::

    locust -f ../locust_files/my_locust_file.py --slave

If we want to run locust distributed on multiple machines we would also have to specify the master host when
starting the slaves (this is not needed when running locust distributed on a single machine, since the master 
host defaults to 127.0.0.1)::

    locust -f ../locust_files/my_locust_file.py --slave --master-host=192.168.0.100

.. note::

    To see all available options type
    
        locust --help
    
