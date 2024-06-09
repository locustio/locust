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

Note that if you want to defined your own custom base shape, you need to define the `abstract` attribute to `True` to avoid it being picked as Shape when imported:

.. code-block:: python

    class MyBaseShape(LoadTestShape):
        abstract = True
        
        def tick(self):
            # Something reusable but needing inheritance
            return None


Combining Users with different load profiles
--------------------------------------------

If you use the Web UI, you can add the :ref:`---class-picker <class-picker>` parameter to select which shape to use. But it often more flexible to have your User definitions in one file and your LoadTestShape in a separate one. For example, if you a high/low load Shape class defined in low_load.py and high_load.py respectively:

.. code-block:: console

    $ locust -f locustfile.py,low_load.py

    $ locust -f locustfile.py,high_load.py

Restricting which user types to spawn in each tick
--------------------------------------------------

Adding the element ``user_classes`` to the return value gives you more detailed control:

.. code-block:: python

    class StagesShapeWithCustomUsers(LoadTestShape):

        stages = [
            {"duration": 10, "users": 10, "spawn_rate": 10, "user_classes": [UserA]},
            {"duration": 30, "users": 50, "spawn_rate": 10, "user_classes": [UserA, UserB]},
            {"duration": 60, "users": 100, "spawn_rate": 10, "user_classes": [UserB]},
            {"duration": 120, "users": 100, "spawn_rate": 10, "user_classes": [UserA,UserB]},
        ]

        def tick(self):
            run_time = self.get_run_time()

            for stage in self.stages:
                if run_time < stage["duration"]:
                    try:
                        tick_data = (stage["users"], stage["spawn_rate"], stage["user_classes"])
                    except:
                        tick_data = (stage["users"], stage["spawn_rate"])
                    return tick_data

            return None

This shape would create create in the first 10 seconds 10 User of ``UserA``. In the next twenty seconds 40 of type ``UserA / UserB`` and this continues until the stages end.


.. _use-common-options:

Reusing common options in custom shapes
---------------------------------------

When using shapes, the the *Users*, *Spawn Rate* and *Run Time* options will be hidden from the UI, and if you specify them on command line Locust will log a warning. This is because those options dont directly apply to shapes, and specifying them might be a mistake.

If you really want to combine a shape with these options, set the ``use_common_options`` attribute and access them from ``self.runner.environment.parsed_options``:

.. code-block:: python

    class MyCustomShape(LoadTestShape):
        use_common_options = True
        
        def tick(self):
            run_time = self.get_run_time()
            if run_time < self.runner.environment.parsed_options.run_time:
                # User count rounded to nearest hundred, just like in previous example
                user_count = round(run_time, -2)
                return (user_count, self.runner.environment.parsed_options.spawn_rate)
                
            return None
