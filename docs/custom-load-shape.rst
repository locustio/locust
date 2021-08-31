.. _custom-load-shape:

==================
Custom load shapes
==================

Sometimes a completely custom shaped load test is required that cannot be achieved by simply setting or changing the user count and spawn rate. For example, you might want to generate a load spike or ramp up and down at custom times. By using a `LoadTestShape` class you have full control over the user count and spawn rate at all times.

Define a class inheriting the LoadTestShape class in your locust file. If this type of class is found then it will be automatically used by Locust.

In this class you define a `tick()` method that returns a tuple with the desired user count and spawn rate (or `None` to stop the test). Locust will call the `tick()` method approximately once per second.

In the class you also have access to the `get_run_time()` method, for checking how long the test has run for.

Example
-------

This shape class will increase user count in blocks of 100 and then stop the load test after 10 minutes:

.. code-block:: python

    class MyCustomShape(LoadTestShape):
        time_limit = 600
        spawn_rate = 20
        
        def tick(self):
            run_time = self.get_run_time()

            if run_time < self.time_limit:
                # User count rounded to nearest hundred.
                user_count = round(run_time, -2)
                return (user_count, spawn_rate)

            return None

This functionality is further demonstrated in the `examples on github <https://github.com/locustio/locust/tree/master/examples/custom_shape>`_ including:

- Generating a double wave shape
- Time based stages like K6
- Step load pattern like Visual Studio

One further method may be helpful for your custom load shapes: `get_current_user_count()`, which returns the total number of active users. This method can be used to prevent advancing to subsequent steps until the desired number of users has been reached. This is especially useful if the initialization process for each user is slow or erratic in how long it takes. If this sounds like your use case, see the `example on github <https://github.com/locustio/locust/tree/master/examples/custom_shape/wait_user_count.py>`_.
