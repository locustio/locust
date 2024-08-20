# Overview

Read the instruction below for your specific database

## PostgreSQL
### How to run the test
- Prerequisites:
    If you do not have them installed already
    - `pip3 install psycopg3` - https://www.psycopg.org/psycopg3/docs/basic/install.html

    - `pip3 install locust` - https://docs.locust.io/en/stable/installation.html

- Set your environment variables for: 
    - PGHOST
    - PGPORT
    - PGDATABASE
    - PGUSER
    - PGPASSWORD

    so they can be picked up from `postgres_test.py`

- Also, update the methods of the UserTasks class to run queries that will hit your database.

#### Run test from browser:
- Open the terminal and run `locust -f postgres_test.py` this will give you a URL to follow. Likely `http://0.0.0.0:8089` from here, you can put in custom parameters to run your test

#### Run test from terminal:

- Insert this into your terminal `locust -f name_of_test_file.py --users=500 --spawn-rate=10 --run-time='15s' --autostart --autoquit 3`
- For a full list of all the configuration options that can be used run `locust --help` and visit https://docs.locust.io/en/stable/configuration.html#configuration

