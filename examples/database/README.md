# Overview

Read the instruction below for your specific database

## PostgreSQL
### How to run the test
- Prerequisites:
    If you do not have them installed already
    - `pip3 install psycopg2` - https://pypi.org/project/psycopg2/

    - `pip3 install locust` - https://docs.locust.io/en/stable/installation.html

- Update line 47 of the `postgres_test.py` file, you can change `postgresql://postgres:postgres@localhost:5432/loadtesting_db` to the connection string for your database
#### Run test from browser:
- Open the terminal and run `locust -f postgres_test.py` this will give you a URL to follow. Likely `http://0.0.0.0:8089` from here, you can put in custom parameters to run your test

#### Run test from terminal:

- Insert this into your terminal `locust -f postgres_test.py --users=500 --spawn-rate=10 --run-time='15s' --autostart --autoquit 3`
- For a full list of all the configuration options that can be used run `locust --help` and visit https://docs.locust.io/en/stable/configuration.html#configuration

