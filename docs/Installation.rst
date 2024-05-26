Some common installation issues
===============================

psutil/\_psutil_common.c:9:10: fatal error: Python.h: No such file or directory
-------------------------------------------------------------------------------

   https://stackoverflow.com/questions/63440765/locust-installation-error-using-pip3-error-command-errored-out-with-exit-statu

ERROR: Failed building wheel for xxx
------------------------------------

While Locust itself is a pure Python package, it has some dependencies
(e.g. gevent and geventhttpclient) that are compiled from C code. Pretty
much all common platforms have binary packages on PyPi, but sometimes
there is a new release that doesnt, or you are running on some exotic
platform. You have two options:

-  (on macos) Install xcode: ``xcode-select --install``
-  Use ``pip install --prefer-binary locust`` to select a pre-compiled
   version of packages even if there is a more recent version available
   as source.
-  Try googling the error message for the specific package that failed
   (not Locust), ensure you have the appropriate build tools installed
   etc.

Windows
-------

   https://stackoverflow.com/questions/61592069/locust-is-not-installing-on-my-windows-10-for-load-testing

Installation works, but the ``locust`` command is not found
-----------------------------------------------------------

   When running pip, did you get a warning saying
   ``The script locust is installed in '...' which is not on PATH``? Add
   that directory to your PATH environment variable.

Increasing Maximum Number of Open Files Limit
---------------------------------------------

   Every User/HTTP connection from Locust opens a new file (technically
   a file descriptor). Many operating systems by default set a low limit
   for the maximum number of files that can be open at the same time.
   Locust will try to adjust this automatically for you, but in a lot of
   cases your operating system will not allow it (in which case you will
   get a warning in the log). Instead you will have to do it manually.

   How to do this depends on your operating system, but you might find
   some useful information here:
   https://www.tecmint.com/increase-set-open-file-limits-in-linux/ and
   practical examples
   https://www.ibm.com/support/knowledgecenter/SS8NLW_11.0.2/com.ibm.discovery.es.in.doc/iiysiulimits.html

   For systemd-based systems (e.g. Debian/Ubuntu) different limits are
   used for graphical login sessions. See
   https://unix.stackexchange.com/a/443467 for additional settings.

Deploy on local enviroment
--------------------------

For those who want to deploy a local environment, follow the steps
below.

.. raw:: html

   <h4>

:construction: Work enviroment:

.. raw:: html

   </h4>

.. raw:: html

   <li>

Create Python’s enviroment: py -m venv env

.. raw:: html

   </li>

.. raw:: html

   <li>

Activate the enviroment on WINDOWS:
env:raw-latex:`\Scripts`:raw-latex:`\activate`

.. raw:: html

   </li>

.. raw:: html

   <li>

Activate the enviroment on MAC: source env/bin/activate

.. raw:: html

   </li>

.. raw:: html

   <h4>

:books: Dependencies

.. raw:: html

   </h4>

.. raw:: html

   <li>

Install dependencies with: pip3 install -r requirements.txt

.. raw:: html

   </li>

.. raw:: html

   <h4>

:signal_strength: Load testing

.. raw:: html

   </h4>

.. raw:: html

   <li>

Launch locust -f scripts/locustfile.py

.. raw:: html

   </li>

.. raw:: html

   <li>

Open http://localhost:8089/ on your browser

.. raw:: html

   </li>

.. _some-common-installation-issues-1:

Some common installation issues
===============================

.. _psutil_psutil_common.c910-fatal-error-python.h-no-such-file-or-directory-1:

psutil/\_psutil_common.c:9:10: fatal error: Python.h: No such file or directory
-------------------------------------------------------------------------------

   https://stackoverflow.com/questions/63440765/locust-installation-error-using-pip3-error-command-errored-out-with-exit-statu

.. _error-failed-building-wheel-for-xxx-1:

ERROR: Failed building wheel for xxx
------------------------------------

While Locust itself is a pure Python package, it has some dependencies
(e.g. gevent and geventhttpclient) that are compiled from C code. Pretty
much all common platforms have binary packages on PyPi, but sometimes
there is a new release that doesnt, or you are running on some exotic
platform. You have two options:

-  (on macos) Install xcode: ``xcode-select --install``
-  Use ``pip install --prefer-binary locust`` to select a pre-compiled
   version of packages even if there is a more recent version available
   as source.
-  Try googling the error message for the specific package that failed
   (not Locust), ensure you have the appropriate build tools installed
   etc.

.. _windows-1:

Windows
-------

   https://stackoverflow.com/questions/61592069/locust-is-not-installing-on-my-windows-10-for-load-testing

.. _installation-works-but-the-locust-command-is-not-found-1:

Installation works, but the ``locust`` command is not found
-----------------------------------------------------------

   When running pip, did you get a warning saying
   ``The script locust is installed in '...' which is not on PATH``? Add
   that directory to your PATH environment variable.

.. _increasing-maximum-number-of-open-files-limit-1:

Increasing Maximum Number of Open Files Limit
---------------------------------------------

   Every User/HTTP connection from Locust opens a new file (technically
   a file descriptor). Many operating systems by default set a low limit
   for the maximum number of files that can be open at the same time.
   Locust will try to adjust this automatically for you, but in a lot of
   cases your operating system will not allow it (in which case you will
   get a warning in the log). Instead you will have to do it manually.

   How to do this depends on your operating system, but you might find
   some useful information here:
   https://www.tecmint.com/increase-set-open-file-limits-in-linux/ and
   practical examples
   https://www.ibm.com/support/knowledgecenter/SS8NLW_11.0.2/com.ibm.discovery.es.in.doc/iiysiulimits.html

   For systemd-based systems (e.g. Debian/Ubuntu) different limits are
   used for graphical login sessions. See
   https://unix.stackexchange.com/a/443467 for additional settings.

.. _deploy-on-local-enviroment-1:

Deploy on local enviroment
--------------------------

For those who want to deploy a local environment, follow the steps
below.

.. raw:: html

   <h4>

:construction: Work enviroment:

.. raw:: html

   </h4>

.. raw:: html

   <li>

Create Python’s enviroment: py -m venv env

.. raw:: html

   </li>

.. raw:: html

   <li>

Activate the enviroment on WINDOWS:
env:raw-latex:`\Scripts`:raw-latex:`\activate`

.. raw:: html

   </li>

.. raw:: html

   <li>

Activate the enviroment on MAC: source env/bin/activate

.. raw:: html

   </li>

.. raw:: html

   <h4>

:books: Dependencies

.. raw:: html

   </h4>

.. raw:: html

   <li>

Install dependencies with: pip3 install -r requirements.txt

.. raw:: html

   </li>

.. raw:: html

   <h4>

:signal_strength: Load testing

.. raw:: html

   </h4>

.. raw:: html

   <li>

Launch locust -f scripts/locustfile.py

.. raw:: html

   </li>

.. raw:: html

   <li>

Open http://localhost:8089/ on your browser

.. raw:: html

   </li>
