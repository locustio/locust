.. _generating-custom-load-shape:

=================================
Generating a custom load shape using a `LoadTestShape` class
=================================

Sometimes a completely custom shaped load test is required that cannot be achieved by simply setting or changing the user count and hatch rate. For example, generating a spike during a test or ramping up and down at custom times. In these cases using the `LoadTestShape` class can give complete control over the user count and hatch rate at all times.

How does a `LoadTestShape` class work?
---------------------------------------------

Define your class inheriting the `LoadTestShape` class in your locust file. If this type of class is found then it will be automatically used by Locust. Add a `tick()` method to return either a tuple containing the user count and hatch rate or `None` to stop the load test. Locust will call the `tick()` method every second and update the load test with new settings or stop the test.

Examples
---------------------------------------------

There are also some [examples on github](https://github.com/locustio/locust/tree/master/examples/custom_shape) including:

- Generating a double wave shape
- Time based stages like K6
- Step load pattern like Visual Studio

Here is a simple example that will increase user count in blocks of 100 then stop the load test after 10 minutes:

```python
class MyCustomShape(LoadTestShape):
    time_limit = 600
    hatch_rate = 20
    
    def tick(self):
        run_time = self.get_run_time()

        if run_time < self.time_limit:
            user_count = round(run_time, -2)
            return (user_count, hatch_rate)

        return None
```
