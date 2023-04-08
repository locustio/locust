


-----------
Pytest Performance Testing
-----------

-----------
-----------

cd work

git clone git@github.com:buildcom/locust.git

-----------
-----------

pytest test-pytest-directory/

pytest test-pytest-setup/

pytest -m smoke

pytest -m crit

pytest -m norm


pytest test-pytest-directory/test_ran.py

pytest test-pytest-setup/test_run.py::TestGroup::test_setup_data

-----------
-----------

cd test-project/tests-locust
cd tests-locust
locust



https://en.wikipedia.org/wiki/Wiki

https://npntest.build.com/
#drawer-root


-----------
-----------

http://bsdcar-npn-t-1.sys.ds.wolseley.com:8082/build-webservices/customers


https://www.build.com/
https://npntest.build.com/account/login


-----------
-----------


example
https://medium.com/@mithun.kadyada/python-locust-for-load-testing-website-or-endpoint-url-b402eb3dbdf7


-----------
notes python check
-----------

which python3

if __name__ == '__main__':
    unittest.main()

-----------

source env/bin/activate


pytest -v -m smoke

---------

directory -> locustfile.py -> locust
cd locust-load-testing/library/test_group


locust --headless -u 10 -r 1 -t 0h1m -H https://storefront:FERfol2021@sfcc-qa.ferguson.com/