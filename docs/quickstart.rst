=============
Quick start
=============

Below is a quick little example of a simple locustfile.py::

    from locust import WebLocust, require_once
    
    def login(l):
        l.client.post("/login", {"username":"ellen_key", "password":"education"})
    
    def index(l):
        l.client.get("/")
    
    @require_once(login)
    def profile(l):
        l.client.get("/profile")
    
    class WebsiteUser(WebLocust):
        tasks = {index:2, profile:1}
        min_wait=5000
        max_wait=9000

Here we define a number of locust tasks, which are normal Python callables that take one 
argument (a Locust class instance). These tasks are gathered under a Locust class in the *task* attribute. 

The Locust class also allows one to specify minimum and maximum wait time between the execution of 
tasks (per user/client) as well as other user behaviours.

To run Locust with the above locustfile we could run something like this::

    locust -c 100 -r 100 WebsiteUser

or if the locustfile is located elsewhere we could run::

    locust -c 100 -r 100 -f ../locust_files/my_locust_file.py WebsiteUser

The locust command must always get a Locust class argument. To list available Locust classes run::

    locust -l

or if the locustfile is located elsewhere run::

    locust -f ../locust_files/my_locust_file.py -l