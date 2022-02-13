# Changelog
Note that PRs for the latest version are sometimes missing here, check [github](https://github.com/locustio/locust/releases) for the latest info.

## [2.8.0](https://github.com/locustio/locust/tree/2.8.0) (2022-02-13)

[Full Changelog](https://github.com/locustio/locust/compare/2.7.3...2.8.0)

**Closed issues:**

- Add type hints [\#2000](https://github.com/locustio/locust/issues/2000)
- 'Tasks' section remains empty for html on v 2.7.0 [\#1994](https://github.com/locustio/locust/issues/1994)

**Merged pull requests:**

- Dockerfile: only install build dependencies on arm64 \(everyone else has pre-built wheels\) [\#2011](https://github.com/locustio/locust/pull/2011) ([cyberw](https://github.com/cyberw))
- Shrink docker image, mainly by switching base image to python3.9-slim [\#2009](https://github.com/locustio/locust/pull/2009) ([cyberw](https://github.com/cyberw))
- Fix link to distributed load generation documentation in CPU log warning [\#2007](https://github.com/locustio/locust/pull/2007) ([mayaCostantini](https://github.com/mayaCostantini))
- Mark package as being typed and add some missing type hints [\#2003](https://github.com/locustio/locust/pull/2003) ([RobertCraigie](https://github.com/RobertCraigie))
- Fix empty tasks section in UI and static report bug [\#2001](https://github.com/locustio/locust/pull/2001) ([EzR1d3r](https://github.com/EzR1d3r))

## [2.7.3](https://github.com/locustio/locust/tree/2.7.3) (2022-02-06)

[Full Changelog](https://github.com/locustio/locust/compare/2.7.2...2.7.3)

**Merged pull requests:**

- Support locust-plugin's Playwright User: Import trio before gevent patching if LOCUST\_PLAYWRIGHT is set [\#1999](https://github.com/locustio/locust/pull/1999) ([cyberw](https://github.com/cyberw))
- \#1994 Fixing to fallback in case of local execution [\#1997](https://github.com/locustio/locust/pull/1997) ([tyge68](https://github.com/tyge68))

## [2.7.2](https://github.com/locustio/locust/tree/2.7.2) (2022-02-03)

[Full Changelog](https://github.com/locustio/locust/compare/2.7.1...2.7.2)

**Fixed bugs:**

- locust:2.7.1 exits when clicking "Stop Tests" in the UI [\#1995](https://github.com/locustio/locust/issues/1995)

**Merged pull requests:**

- Reverse parts of PR \#1992 [\#1996](https://github.com/locustio/locust/pull/1996) ([cyberw](https://github.com/cyberw))

## [2.7.1](https://github.com/locustio/locust/tree/2.7.1) (2022-02-02)

[Full Changelog](https://github.com/locustio/locust/compare/2.7.0...2.7.1)

**Fixed bugs:**

- --html doesnt work in web mode [\#1944](https://github.com/locustio/locust/issues/1944)

**Merged pull requests:**

- Allow repeated runs of run\_single\_user  [\#1993](https://github.com/locustio/locust/pull/1993) ([cyberw](https://github.com/cyberw))
- fix --html report in web mode [\#1992](https://github.com/locustio/locust/pull/1992) ([uddmorningsun](https://github.com/uddmorningsun))

## [2.7.0](https://github.com/locustio/locust/tree/2.7.0) (2022-01-29)

[Full Changelog](https://github.com/locustio/locust/compare/2.6.1...2.7.0)

**Closed issues:**

- I hope to add a column of 99%ile on the Web UI [\#1966](https://github.com/locustio/locust/issues/1966)

**Merged pull requests:**

- Fix "socket operation on non-socket" at shutdown, by reverting \#1935 [\#1991](https://github.com/locustio/locust/pull/1991) ([cyberw](https://github.com/cyberw))
- unit tests: add extra validations in integration tests [\#1990](https://github.com/locustio/locust/pull/1990) ([cyberw](https://github.com/cyberw))
- Add 99%ile for Web UI [\#1989](https://github.com/locustio/locust/pull/1989) ([FooQoo](https://github.com/FooQoo))
- Add run\_single\_user and documentation on how to debug Users/locustfiles [\#1985](https://github.com/locustio/locust/pull/1985) ([cyberw](https://github.com/cyberw))
- hardening Environment.shape\_class for distinct usage [\#1983](https://github.com/locustio/locust/pull/1983) ([uddmorningsun](https://github.com/uddmorningsun))
- Fixing issue \#1961 with incorrect "All users spawned" log messages wh… [\#1977](https://github.com/locustio/locust/pull/1977) ([EzR1d3r](https://github.com/EzR1d3r))

## [2.6.1](https://github.com/locustio/locust/tree/2.6.1) (2022-01-26)

[Full Changelog](https://github.com/locustio/locust/compare/2.6.0...2.6.1)

**Merged pull requests:**

- Fire requests through Environment.events [\#1982](https://github.com/locustio/locust/pull/1982) ([BonelessPi](https://github.com/BonelessPi))
- Fix docs with underscore postfix for hyperlink? [\#1979](https://github.com/locustio/locust/pull/1979) ([jeroenhendricksen](https://github.com/jeroenhendricksen))
- Repair broken hyperlinks in documentation [\#1978](https://github.com/locustio/locust/pull/1978) ([jeroenhendricksen](https://github.com/jeroenhendricksen))

## [2.6.0](https://github.com/locustio/locust/tree/2.6.0) (2022-01-23)

[Full Changelog](https://github.com/locustio/locust/compare/2.5.1...2.6.0)

**Fixed bugs:**

- Docs: Missing locustfile.py in code structure example [\#1959](https://github.com/locustio/locust/issues/1959)
- Error when setting multiple host values [\#1957](https://github.com/locustio/locust/issues/1957)

**Closed issues:**

- Possibility to set the exact number of users to spawn \(instead weight\) [\#1939](https://github.com/locustio/locust/issues/1939)

**Merged pull requests:**

- Pass tags and exclude-tags to workers.  [\#1976](https://github.com/locustio/locust/pull/1976) ([cyberw](https://github.com/cyberw))
- WorkerRunner: read --expect-workers from job parameters [\#1975](https://github.com/locustio/locust/pull/1975) ([cyberw](https://github.com/cyberw))
- Update README.md [\#1974](https://github.com/locustio/locust/pull/1974) ([eltociear](https://github.com/eltociear))
- Clean up some logging messages [\#1973](https://github.com/locustio/locust/pull/1973) ([cyberw](https://github.com/cyberw))
- Ensure heartbeat\_worker doesnt try to re-establish connection to workers when quit has been called [\#1972](https://github.com/locustio/locust/pull/1972) ([cyberw](https://github.com/cyberw))
- fixed\_count: ability to spawn a specific number of users \(as opposed to just using weights\) [\#1964](https://github.com/locustio/locust/pull/1964) ([EzR1d3r](https://github.com/EzR1d3r))
- Update running-cloud-integration.rst [\#1958](https://github.com/locustio/locust/pull/1958) ([DieBauer](https://github.com/DieBauer))
- fix master runner not close rpc server [\#1935](https://github.com/locustio/locust/pull/1935) ([lizhaode](https://github.com/lizhaode))

## [2.5.1](https://github.com/locustio/locust/tree/2.5.1) (2021-12-09)

[Full Changelog](https://github.com/locustio/locust/compare/2.5.0...2.5.1)

**Fixed bugs:**

- User distribution should happen when new workers comes in [\#1884](https://github.com/locustio/locust/issues/1884)

**Merged pull requests:**

- Fix running the web UI with class defined hosts [\#1956](https://github.com/locustio/locust/pull/1956) ([chaen](https://github.com/chaen))
- Throw exception when calling response.success\(\)/.failure\(\) if with-block has not been entered [\#1955](https://github.com/locustio/locust/pull/1955) ([cyberw](https://github.com/cyberw))
- Gracefully fail to resize stats command line output if terminal doesnt support it, instead of crashing [\#1951](https://github.com/locustio/locust/pull/1951) ([cyberw](https://github.com/cyberw))
- Stop declaring "fake" class level variables in Environment, User and StatsEntry [\#1948](https://github.com/locustio/locust/pull/1948) ([cyberw](https://github.com/cyberw))
- fix misspellings in doc \(mostly "it's"\) [\#1945](https://github.com/locustio/locust/pull/1945) ([deronnax](https://github.com/deronnax))
- Fixed typo in writing-a-locustfile.rst [\#1943](https://github.com/locustio/locust/pull/1943) ([Maffey](https://github.com/Maffey))
- Fix docs issues from distributed execution with IaC [\#1934](https://github.com/locustio/locust/pull/1934) ([marcosborges](https://github.com/marcosborges))
- New Provisioning Example for Distributed Execution Using IaC - Terraform/AWS/EC2 [\#1933](https://github.com/locustio/locust/pull/1933) ([marcosborges](https://github.com/marcosborges))
- Ensure terminal is restored at exit [\#1932](https://github.com/locustio/locust/pull/1932) ([cyberw](https://github.com/cyberw))
- Fix issue \#1915 [\#1916](https://github.com/locustio/locust/pull/1916) ([EzR1d3r](https://github.com/EzR1d3r))

## [2.5.0](https://github.com/locustio/locust/tree/2.5.0) (2021-11-05)

[Full Changelog](https://github.com/locustio/locust/compare/2.4.3...2.5.0)

**Merged pull requests:**

- Change request event url field to contain absolute URL not just path. [\#1927](https://github.com/locustio/locust/pull/1927) ([cyberw](https://github.com/cyberw))
- Suppress warnings for patch version mismatch between master and worker \(and make them debug level instead\) [\#1926](https://github.com/locustio/locust/pull/1926) ([cyberw](https://github.com/cyberw))

## [2.4.3](https://github.com/locustio/locust/tree/2.4.3) (2021-11-02)

[Full Changelog](https://github.com/locustio/locust/compare/2.4.2...2.4.3)

**Fixed bugs:**

- module 'signal' has no attribute 'SIGWINCH'  on 2.4.2     [\#1924](https://github.com/locustio/locust/issues/1924)

## [2.4.2](https://github.com/locustio/locust/tree/2.4.2) (2021-11-01)

[Full Changelog](https://github.com/locustio/locust/compare/2.4.1...2.4.2)

**Fixed bugs:**

- the report cant show the right time [\#1909](https://github.com/locustio/locust/issues/1909)
- cant show html chart version locust 2.4.0 [\#1908](https://github.com/locustio/locust/issues/1908)

**Closed issues:**

- Update locustio/locust Docker image to Python 3.9.6 [\#1821](https://github.com/locustio/locust/issues/1821)

**Merged pull requests:**

- Add --expect-workers-max-wait parameter [\#1922](https://github.com/locustio/locust/pull/1922) ([cyberw](https://github.com/cyberw))
- Fixed \#1909 -- Return UTC datetime with the POSIX timestamp for API /stats/report [\#1918](https://github.com/locustio/locust/pull/1918) ([uddmorningsun](https://github.com/uddmorningsun))
- Track worker memory [\#1917](https://github.com/locustio/locust/pull/1917) ([solowalker27](https://github.com/solowalker27))
- Auto-resize stats table when terminal window is resized [\#1914](https://github.com/locustio/locust/pull/1914) ([cyberw](https://github.com/cyberw))
- Fix typos in documentation [\#1912](https://github.com/locustio/locust/pull/1912) ([mnigh](https://github.com/mnigh))
- Fix missing data in stats\_history/HTML chart when running LoadShape [\#1911](https://github.com/locustio/locust/pull/1911) ([AlexisC0de](https://github.com/AlexisC0de))

## [2.4.1](https://github.com/locustio/locust/tree/2.4.1) (2021-10-19)

[Full Changelog](https://github.com/locustio/locust/compare/2.4.0...2.4.1)

**Fixed bugs:**

- No longer logging interval stats when using LoadTestShape after 2.1.x [\#1906](https://github.com/locustio/locust/issues/1906)

**Merged pull requests:**

- Fix stat printing when using shapes [\#1907](https://github.com/locustio/locust/pull/1907) ([cyberw](https://github.com/cyberw))
- Change docker image to use Python 3.9 [\#1904](https://github.com/locustio/locust/pull/1904) ([cyberw](https://github.com/cyberw))

## [2.4.0](https://github.com/locustio/locust/tree/2.4.0) (2021-10-11)

[Full Changelog](https://github.com/locustio/locust/compare/2.2.3...2.4.0)

**Fixed bugs:**

- Locust will not work, if there is a custom 'run' @task / function  [\#1893](https://github.com/locustio/locust/issues/1893)
- MasterRunner target\_user\_count no longer set for test\_start event listeners [\#1883](https://github.com/locustio/locust/issues/1883)

**Merged pull requests:**

- Missing colons after else keyword in Event Hooks doc [\#1902](https://github.com/locustio/locust/pull/1902) ([TatchNicolas](https://github.com/TatchNicolas))
- Support \(and test\) Python 3.10 [\#1901](https://github.com/locustio/locust/pull/1901) ([cyberw](https://github.com/cyberw))
- Add start\_time and url parameters to request event. [\#1900](https://github.com/locustio/locust/pull/1900) ([cyberw](https://github.com/cyberw))
- Make User.run/TaskSet.run final and raise an exception if someone marks it with @task [\#1895](https://github.com/locustio/locust/pull/1895) ([cyberw](https://github.com/cyberw))
- Ensure target\_user\_count is set before test\_start event is fired [\#1894](https://github.com/locustio/locust/pull/1894) ([mboutet](https://github.com/mboutet))
- Ensure target\_user\_count is set before ramping-up or down [\#1891](https://github.com/locustio/locust/pull/1891) ([mboutet](https://github.com/mboutet))
- Release docker image for arm64. [\#1889](https://github.com/locustio/locust/pull/1889) ([odidev](https://github.com/odidev))
- \#1884 User distribution should happen when new workers comes in [\#1886](https://github.com/locustio/locust/pull/1886) ([tyge68](https://github.com/tyge68))

## [2.2.3](https://github.com/locustio/locust/tree/2.2.3) (2021-09-20)

[Full Changelog](https://github.com/locustio/locust/compare/2.2.2...2.2.3)

**Merged pull requests:**

- Fix issue with custom arguments in config file when not running headless [\#1888](https://github.com/locustio/locust/pull/1888) ([cyberw](https://github.com/cyberw))

## [2.2.2](https://github.com/locustio/locust/tree/2.2.2) (2021-09-15)

[Full Changelog](https://github.com/locustio/locust/compare/2.2.1...2.2.2)

**Fixed bugs:**

- Version information in Docker image is incorrect [\#1885](https://github.com/locustio/locust/issues/1885)

**Closed issues:**

- Ability to explicitly set which arguments will be exposed/visible in the web ui [\#1876](https://github.com/locustio/locust/issues/1876)

**Merged pull requests:**

- Ability to hide extra args from web ui [\#1881](https://github.com/locustio/locust/pull/1881) ([fabito](https://github.com/fabito))
- Refactor \(remove duplication\) headless/autostart mechanism. [\#1880](https://github.com/locustio/locust/pull/1880) ([cyberw](https://github.com/cyberw))
- Wait for --expect-workers when running --autostart [\#1879](https://github.com/locustio/locust/pull/1879) ([cyberw](https://github.com/cyberw))
- Dont launch autostart greenlet on workers, even if they happened to get the --autostart flag [\#1878](https://github.com/locustio/locust/pull/1878) ([cyberw](https://github.com/cyberw))
- Added documentation for start\_shape [\#1874](https://github.com/locustio/locust/pull/1874) ([daniel135790](https://github.com/daniel135790))
- Fix Regression in Full History CSV Percentiles [\#1873](https://github.com/locustio/locust/pull/1873) ([TaylorSMarks](https://github.com/TaylorSMarks))
- Ability to inject custom html elements in the `head` element [\#1872](https://github.com/locustio/locust/pull/1872) ([fabito](https://github.com/fabito))

## [2.2.1](https://github.com/locustio/locust/tree/2.2.1) (2021-09-02)

[Full Changelog](https://github.com/locustio/locust/compare/2.2.0...2.2.1)

**Fixed bugs:**

- Importing any locust plugin breaks the UI and distributed load generation. [\#1870](https://github.com/locustio/locust/issues/1870)

**Merged pull requests:**

- Disable setting custom parameters of None or boolean type in web UI. Fixes \#1870 [\#1871](https://github.com/locustio/locust/pull/1871) ([cyberw](https://github.com/cyberw))

## [2.2.0](https://github.com/locustio/locust/tree/2.2.0) (2021-09-01)

[Full Changelog](https://github.com/locustio/locust/compare/2.2.0b0...2.2.0)

## [2.2.0b0](https://github.com/locustio/locust/tree/2.2.0b0) (2021-09-01)

[Full Changelog](https://github.com/locustio/locust/compare/2.1.0...2.2.0b0)

**Fixed bugs:**

- time display in live charts switches to the local time upon refresh [\#1835](https://github.com/locustio/locust/issues/1835)
- Part of response times chart lines are missing [\#1702](https://github.com/locustio/locust/issues/1702)

**Closed issues:**

- Response times get graphed as zero before first request is made [\#1852](https://github.com/locustio/locust/issues/1852)
- Add flag to run with uniform weights [\#1838](https://github.com/locustio/locust/issues/1838)
- Starting load test from the cli but monitoring from the web UI [\#831](https://github.com/locustio/locust/issues/831)

**Merged pull requests:**

- \#1832 Displaying locustfile and tasks ratio information on index.html [\#1868](https://github.com/locustio/locust/pull/1868) ([tyge68](https://github.com/tyge68))
- Add --autostart and --autoquit parameters, fixes \#831 [\#1864](https://github.com/locustio/locust/pull/1864) ([cyberw](https://github.com/cyberw))
- Add constant\_throughput wait time \(the inverse of constant\_pacing\) [\#1863](https://github.com/locustio/locust/pull/1863) ([cyberw](https://github.com/cyberw))
- Improve some of the doc issues that were missed from the previous PR [\#1861](https://github.com/locustio/locust/pull/1861) ([Serhiy1](https://github.com/Serhiy1))
- Handle user classes with weight = 0 [\#1860](https://github.com/locustio/locust/pull/1860) ([mboutet](https://github.com/mboutet))
- fix\(examples\): fix multiple\_hosts.py example [\#1859](https://github.com/locustio/locust/pull/1859) ([obradovichv](https://github.com/obradovichv))
- Alternative grouping [\#1858](https://github.com/locustio/locust/pull/1858) ([Serhiy1](https://github.com/Serhiy1))
- HttpUser: Unpack known exceptions [\#1855](https://github.com/locustio/locust/pull/1855) ([cyberw](https://github.com/cyberw))
- fix\(charts\): prevent displaying stats before requests are made [\#1853](https://github.com/locustio/locust/pull/1853) ([obradovichv](https://github.com/obradovichv))
- Use UTC time for server stats history, localize times on the client [\#1851](https://github.com/locustio/locust/pull/1851) ([obradovichv](https://github.com/obradovichv))
- FastHttpUser: Add it directly under locust package, make the documentation less scary. [\#1849](https://github.com/locustio/locust/pull/1849) ([cyberw](https://github.com/cyberw))
- Adjust github actions [\#1848](https://github.com/locustio/locust/pull/1848) ([cyberw](https://github.com/cyberw))
- Auto-generate version number using setuptools\_scm and git tags [\#1847](https://github.com/locustio/locust/pull/1847) ([cyberw](https://github.com/cyberw))
- Add equal weights flag [\#1842](https://github.com/locustio/locust/pull/1842) ([shekar-stripe](https://github.com/shekar-stripe))
- Show custom arguments in web ui and forward them to worker [\#1841](https://github.com/locustio/locust/pull/1841) ([cyberw](https://github.com/cyberw))
- Return the new users on Runner.spawn\_users [\#1791](https://github.com/locustio/locust/pull/1791) ([pappacena](https://github.com/pappacena))

## [2.1.0](https://github.com/locustio/locust/tree/2.1.0) (2021-08-08)

[Full Changelog](https://github.com/locustio/locust/compare/2.0.0...2.1.0)

**Fixed bugs:**

- OOM error with master/slaves setup \(zeromq, windows\) [\#1372](https://github.com/locustio/locust/issues/1372)

**Closed issues:**

- locust should add extending blocks to index.html to change the start test and edit test options [\#1822](https://github.com/locustio/locust/issues/1822)

**Merged pull requests:**

- Fix docker builds [\#1845](https://github.com/locustio/locust/pull/1845) ([cyberw](https://github.com/cyberw))
- Bump dependency on pyzmq to fix \#1372 \(OOM on windows\) [\#1839](https://github.com/locustio/locust/pull/1839) ([cyberw](https://github.com/cyberw))
- Use 1 as default in web UI start form + lots of documentation updates [\#1836](https://github.com/locustio/locust/pull/1836) ([cyberw](https://github.com/cyberw))

## [2.0.0](https://github.com/locustio/locust/tree/2.0.0) (2021-08-01)

[Full Changelog](https://github.com/locustio/locust/compare/2.0.0b4...2.0.0)

**Fixed bugs:**

- User Count Drops when Worker Abruptly Leaves The Test In Distributed Mode [\#1766](https://github.com/locustio/locust/issues/1766)

**Merged pull requests:**

- update grpc example, because grpc gevent issue has been fixed [\#1834](https://github.com/locustio/locust/pull/1834) ([cyberw](https://github.com/cyberw))
- Speed up tests [\#1831](https://github.com/locustio/locust/pull/1831) ([mboutet](https://github.com/mboutet))
- Allow workers to bypass version check by sending -1 as version [\#1830](https://github.com/locustio/locust/pull/1830) ([cyberw](https://github.com/cyberw))

## [2.0.0b4](https://github.com/locustio/locust/tree/2.0.0b4) (2021-07-28)

[Full Changelog](https://github.com/locustio/locust/compare/2.0.0b3...2.0.0b4)

**Merged pull requests:**

- Improve logging messages and clean up code after dispatch refactoring \(\#1809\) [\#1826](https://github.com/locustio/locust/pull/1826) ([mboutet](https://github.com/mboutet))
- Remove `user_classes_count` from heartbeat payload [\#1825](https://github.com/locustio/locust/pull/1825) ([mboutet](https://github.com/mboutet))

## [2.0.0b3](https://github.com/locustio/locust/tree/2.0.0b3) (2021-07-16)

[Full Changelog](https://github.com/locustio/locust/compare/2.0.0b2...2.0.0b3)

**Fixed bugs:**

- FastHttpUser requests are blocking [\#1810](https://github.com/locustio/locust/issues/1810)

**Closed issues:**

- Restore locust\_start\_hatching functionality [\#1776](https://github.com/locustio/locust/issues/1776)

**Merged pull requests:**

- Add option to set concurrency of FastHttpUser/Session [\#1812](https://github.com/locustio/locust/pull/1812) ([soitinj](https://github.com/soitinj))
- Fire test\_start and test\_stop events on worker nodes [\#1777](https://github.com/locustio/locust/pull/1777) ([nathan-beam](https://github.com/nathan-beam))

## [2.0.0b2](https://github.com/locustio/locust/tree/2.0.0b2) (2021-07-12)

[Full Changelog](https://github.com/locustio/locust/compare/2.0.0b1...2.0.0b2)

**Merged pull requests:**

- Auto shrink request stats table to fit terminal [\#1811](https://github.com/locustio/locust/pull/1811) ([cyberw](https://github.com/cyberw))
- Refactoring of the dispatch logic to improve performance [\#1809](https://github.com/locustio/locust/pull/1809) ([mboutet](https://github.com/mboutet))

## [2.0.0b1](https://github.com/locustio/locust/tree/2.0.0b1) (2021-07-05)

[Full Changelog](https://github.com/locustio/locust/compare/2.0.0b0...2.0.0b1)

**Merged pull requests:**

- Check version of workers when they connect. Warn if there is a mismatch, refuse 1.x workers to connect [\#1805](https://github.com/locustio/locust/pull/1805) ([cyberw](https://github.com/cyberw))
- Change the default User weight to 1 instead of 10. [\#1803](https://github.com/locustio/locust/pull/1803) ([cyberw](https://github.com/cyberw))
- Upgrade to flask 2 [\#1764](https://github.com/locustio/locust/pull/1764) ([corenting](https://github.com/corenting))

## [2.0.0b0](https://github.com/locustio/locust/tree/2.0.0b0) (2021-07-05)

[Full Changelog](https://github.com/locustio/locust/compare/1.6.0...2.0.0b0)

**Fixed bugs:**

- Distribution of user classes is not respected and some user classes are just never spawned [\#1618](https://github.com/locustio/locust/issues/1618)

**Closed issues:**

- Hatch rate in distributed mode spawns users in batches equal to number of slaves [\#896](https://github.com/locustio/locust/issues/896)

**Merged pull requests:**

- Move User selection responsibility from worker to master in order to fix unbalanced distribution of users and uneven ramp-up [\#1621](https://github.com/locustio/locust/pull/1621) ([mboutet](https://github.com/mboutet))

## [1.6.0](https://github.com/locustio/locust/tree/1.6.0) (2021-06-26)

[Full Changelog](https://github.com/locustio/locust/compare/1.5.3...1.6.0)

**Fixed bugs:**

- status "stopped" instead of "spawning", tick\(\) method of LoadShape called only once [\#1762](https://github.com/locustio/locust/issues/1762)

**Closed issues:**

- Allow master node to supply data to worker nodes directly [\#1780](https://github.com/locustio/locust/issues/1780)

**Merged pull requests:**

- Add CORS functionality to Locust [\#1793](https://github.com/locustio/locust/pull/1793) ([KasimAhmic](https://github.com/KasimAhmic))
- Make FastHttpUser use the same name for request\_meta as HttpUser \(no leading underscore\) [\#1788](https://github.com/locustio/locust/pull/1788) ([cyberw](https://github.com/cyberw))
- Ensure that the exception dictionaries are not mutated when generating a html report [\#1784](https://github.com/locustio/locust/pull/1784) ([mboutet](https://github.com/mboutet))
- Allow cross process communication using custom messages [\#1782](https://github.com/locustio/locust/pull/1782) ([nathan-beam](https://github.com/nathan-beam))
- modified check\_stopped condition [\#1769](https://github.com/locustio/locust/pull/1769) ([stanislawskwark](https://github.com/stanislawskwark))

## [1.5.3](https://github.com/locustio/locust/tree/1.5.3) (2021-05-17)

[Full Changelog](https://github.com/locustio/locust/compare/1.5.2...1.5.3)

**Merged pull requests:**

- Register stats from request\_success and request\_failure [\#1761](https://github.com/locustio/locust/pull/1761) ([DennisKrone](https://github.com/DennisKrone))

## [1.5.2](https://github.com/locustio/locust/tree/1.5.2) (2021-05-12)

[Full Changelog](https://github.com/locustio/locust/compare/1.5.1...1.5.2)

**Fixed bugs:**

- Locust stopped working after Flast 2.0 got released [\#1759](https://github.com/locustio/locust/issues/1759)
- GRPC compatibility : Locust load test throws greenlet.GreenletExit exception on reaching test time limit [\#1676](https://github.com/locustio/locust/issues/1676)

**Merged pull requests:**

- Pin flask version to 1.1.2. Fixes \#1759 [\#1760](https://github.com/locustio/locust/pull/1760) ([cyberw](https://github.com/cyberw))
- Measure elapsed time using time.perf\_counter\(\)  [\#1758](https://github.com/locustio/locust/pull/1758) ([cyberw](https://github.com/cyberw))
- Add gRPC load test example [\#1755](https://github.com/locustio/locust/pull/1755) ([beandrad](https://github.com/beandrad))

## [1.5.1](https://github.com/locustio/locust/tree/1.5.1) (2021-05-04)

[Full Changelog](https://github.com/locustio/locust/compare/1.5.0...1.5.1)

**Merged pull requests:**

- remove accidentally added start\_time parameter to request event [\#1754](https://github.com/locustio/locust/pull/1754) ([cyberw](https://github.com/cyberw))

## [1.5.0](https://github.com/locustio/locust/tree/1.5.0) (2021-05-04)

[Full Changelog](https://github.com/locustio/locust/compare/1.4.4...1.5.0)

**Merged pull requests:**

- Add response object to request event [\#1752](https://github.com/locustio/locust/pull/1752) ([cyberw](https://github.com/cyberw))
- Updated request event with context and deprecate request\_failure/success [\#1750](https://github.com/locustio/locust/pull/1750) ([DennisKrone](https://github.com/DennisKrone))

## [1.4.4](https://github.com/locustio/locust/tree/1.4.4) (2021-04-04)

[Full Changelog](https://github.com/locustio/locust/compare/1.4.3...1.4.4)

**Fixed bugs:**

- self.quit\(\) fails test doesn't stop [\#1726](https://github.com/locustio/locust/issues/1726)
- LoadTestShape run\_time broken when using test\_start and test\_stop decorators [\#1718](https://github.com/locustio/locust/issues/1718)
- Distributed test stopped despite workers running [\#1707](https://github.com/locustio/locust/issues/1707)
- Charts not working well in version 1.4.2 [\#1690](https://github.com/locustio/locust/issues/1690)

**Closed issues:**

- A simple TypeError（str + int） in runners.py [\#1737](https://github.com/locustio/locust/issues/1737)
- Dwell-time based load shape testing [\#1715](https://github.com/locustio/locust/issues/1715)

**Merged pull requests:**

- Fix test issue probably caused by updated configargparse version. [\#1739](https://github.com/locustio/locust/pull/1739) ([cyberw](https://github.com/cyberw))
- Call shape\_class.reset\_time\(\) after test\_start event so that tick time is correct [\#1738](https://github.com/locustio/locust/pull/1738) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Ensure runner.quit finishes even when users are broken [\#1728](https://github.com/locustio/locust/pull/1728) ([cyberw](https://github.com/cyberw))
- make runner / user count available to LoadTestShape [\#1719](https://github.com/locustio/locust/pull/1719) ([msarahan](https://github.com/msarahan))
- Fix typo in ~examples/dynamic\_user\_credentials.py [\#1714](https://github.com/locustio/locust/pull/1714) ([luke-h1](https://github.com/luke-h1))
- Fix automatic distributed test shutdown [\#1710](https://github.com/locustio/locust/pull/1710) ([enote-kane](https://github.com/enote-kane))
- fix type hinting on Events [\#1705](https://github.com/locustio/locust/pull/1705) ([mrijken](https://github.com/mrijken))
- updated double wave load shape docs to reflect peak times [\#1698](https://github.com/locustio/locust/pull/1698) ([pranavgupta1234](https://github.com/pranavgupta1234))
- add LoadTestShape to \_\_all\_\_ in order to fix warning "'LoadTestShape'… [\#1696](https://github.com/locustio/locust/pull/1696) ([amitwer](https://github.com/amitwer))

## [1.4.3](https://github.com/locustio/locust/tree/1.4.3) (2021-01-28)

[Full Changelog](https://github.com/locustio/locust/compare/1.4.2...1.4.3)

**Merged pull requests:**

- fix stats values for chart tooltips [\#1691](https://github.com/locustio/locust/pull/1691) ([aek](https://github.com/aek))

## [1.4.2](https://github.com/locustio/locust/tree/1.4.2) (2021-01-26)

[Full Changelog](https://github.com/locustio/locust/compare/1.4.1...1.4.2)

**Fixed bugs:**

- Report charts plot data points after the test has ended [\#1677](https://github.com/locustio/locust/issues/1677)
- SetConsoleMode throws an error when locust is run from Jenkins Powershell [\#1654](https://github.com/locustio/locust/issues/1654)
- locust should exit when a load shape returns None in headless mode [\#1653](https://github.com/locustio/locust/issues/1653)
- test\_stop is fired twice when Locust is running in –master/worker mode [\#1638](https://github.com/locustio/locust/issues/1638)

**Closed issues:**

- currently locust is supporting for stas, failures, stas history in csv format while running without web [\#1673](https://github.com/locustio/locust/issues/1673)
- /swarm web endpoint should not require user\_count and spawn\_rate when shape\_class is used [\#1670](https://github.com/locustio/locust/issues/1670)
- Show legends on charts [\#1651](https://github.com/locustio/locust/issues/1651)

**Merged pull requests:**

- Verify docker build & create PyPI releases through Github Actions when tags are pushed [\#1687](https://github.com/locustio/locust/pull/1687) ([heyman](https://github.com/heyman))
- Use Github Actions for CI [\#1686](https://github.com/locustio/locust/pull/1686) ([heyman](https://github.com/heyman))
- Shutdown workers when using LoadTestShape and headless mode [\#1683](https://github.com/locustio/locust/pull/1683) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Stats charts data persistance [\#1681](https://github.com/locustio/locust/pull/1681) ([aek](https://github.com/aek))
- Fix issues with render\_template [\#1680](https://github.com/locustio/locust/pull/1680) ([aek](https://github.com/aek))
- Improve stats data sharing from python to js [\#1679](https://github.com/locustio/locust/pull/1679) ([aek](https://github.com/aek))
- Feature chart sync [\#1678](https://github.com/locustio/locust/pull/1678) ([aek](https://github.com/aek))
- Feature stats exceptions csv [\#1674](https://github.com/locustio/locust/pull/1674) ([aek](https://github.com/aek))
- /swarm adjusted for tests with shape class [\#1671](https://github.com/locustio/locust/pull/1671) ([stanislawskwark](https://github.com/stanislawskwark))
- Fix a typo [\#1665](https://github.com/locustio/locust/pull/1665) ([atken](https://github.com/atken))
- Feature chart tooltip custom values - show user count [\#1658](https://github.com/locustio/locust/pull/1658) ([aek](https://github.com/aek))
- Check if running from a tty on windows [\#1657](https://github.com/locustio/locust/pull/1657) ([DennisKrone](https://github.com/DennisKrone))
- Bump Echarts version to show charts legends [\#1655](https://github.com/locustio/locust/pull/1655) ([aek](https://github.com/aek))
- Add example that manually adds stats entries [\#1645](https://github.com/locustio/locust/pull/1645) ([heyman](https://github.com/heyman))
- Use SASS for CSS styling + UI improvements [\#1644](https://github.com/locustio/locust/pull/1644) ([heyman](https://github.com/heyman))
- Fix bug causing test\_stop event to be fired twice in master node [\#1641](https://github.com/locustio/locust/pull/1641) ([heyman](https://github.com/heyman))
- Added --html option to save HTML report [\#1637](https://github.com/locustio/locust/pull/1637) ([rloomans](https://github.com/rloomans))

## [1.4.1](https://github.com/locustio/locust/tree/1.4.1) (2020-11-16)

[Full Changelog](https://github.com/locustio/locust/compare/1.4.0...1.4.1)

**Fixed bugs:**

- Locust docker version 1.4.0 using 100% CPU on idle [\#1629](https://github.com/locustio/locust/issues/1629)

**Merged pull requests:**

- Fix 100% cpu usage when running in docker/non-tty terminal [\#1631](https://github.com/locustio/locust/pull/1631) ([DennisKrone](https://github.com/DennisKrone))

## [1.4.0](https://github.com/locustio/locust/tree/1.4.0) (2020-11-13)

[Full Changelog](https://github.com/locustio/locust/compare/1.3.2...1.4.0)

**Closed issues:**

- Control user count from terminal [\#1600](https://github.com/locustio/locust/issues/1600)
- Introduce sensible default settings for run time [\#1598](https://github.com/locustio/locust/issues/1598)
- Make wait\_time default to zero \(vote up/down for this ticket please :\) [\#1308](https://github.com/locustio/locust/issues/1308)

**Merged pull requests:**

- Improve logging about users spawned/stopped [\#1628](https://github.com/locustio/locust/pull/1628) ([cyberw](https://github.com/cyberw))
- Make zero wait time the default [\#1626](https://github.com/locustio/locust/pull/1626) ([cyberw](https://github.com/cyberw))
- Make infinite run time the default when running headless [\#1625](https://github.com/locustio/locust/pull/1625) ([cyberw](https://github.com/cyberw))
- issue-1571 : Added a logging line when workers connect [\#1617](https://github.com/locustio/locust/pull/1617) ([zdannar](https://github.com/zdannar))
- Add key commands for increasing and stopping users  [\#1612](https://github.com/locustio/locust/pull/1612) ([DennisKrone](https://github.com/DennisKrone))

## [1.3.2](https://github.com/locustio/locust/tree/1.3.2) (2020-11-03)

[Full Changelog](https://github.com/locustio/locust/compare/1.3.1...1.3.2)

**Merged pull requests:**

- Run builds for python 3.9 [\#1607](https://github.com/locustio/locust/pull/1607) ([cyberw](https://github.com/cyberw))
- Add note and link to k8s Helm chart [\#1606](https://github.com/locustio/locust/pull/1606) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Replace '\<' and '\>' for swarm 'host' field. Fix for XSS attack. [\#1603](https://github.com/locustio/locust/pull/1603) ([lhupfeldt](https://github.com/lhupfeldt))

## [1.3.1](https://github.com/locustio/locust/tree/1.3.1) (2020-10-15)

[Full Changelog](https://github.com/locustio/locust/compare/1.3.0...1.3.1)

## [1.3.0](https://github.com/locustio/locust/tree/1.3.0) (2020-10-12)

[Full Changelog](https://github.com/locustio/locust/compare/1.2.3...1.3.0)

**Fixed bugs:**

- After starting and then stopping a load test, master is updating state in a loop [\#1577](https://github.com/locustio/locust/issues/1577)
- Misleading log message in distributed mode [\#1572](https://github.com/locustio/locust/issues/1572)
- LoadTestShape.get\_run\_time is not relative to start of test [\#1557](https://github.com/locustio/locust/issues/1557)
- On Stop causes the task to continue [\#1552](https://github.com/locustio/locust/issues/1552)

**Closed issues:**

- Remove step load feature now that LoadTestShape is possible? [\#1575](https://github.com/locustio/locust/issues/1575)
- Add ability to easily extend Locust web UI [\#1530](https://github.com/locustio/locust/issues/1530)
- Type hinting for common functions [\#1260](https://github.com/locustio/locust/issues/1260)

**Merged pull requests:**

- Start web\_ui later to avoid race adding UI routes [\#1585](https://github.com/locustio/locust/pull/1585) ([solowalker27](https://github.com/solowalker27))
- Remove step load feature [\#1584](https://github.com/locustio/locust/pull/1584) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Add more type hints [\#1582](https://github.com/locustio/locust/pull/1582) ([cyberw](https://github.com/cyberw))
- Run time relative to start when using LoadTestShape [\#1581](https://github.com/locustio/locust/pull/1581) ([DennisKrone](https://github.com/DennisKrone))
- Don't log state change if it's the same [\#1580](https://github.com/locustio/locust/pull/1580) ([max-rocket-internet](https://github.com/max-rocket-internet))
- SequentialTaskSet improvements [\#1579](https://github.com/locustio/locust/pull/1579) ([cyberw](https://github.com/cyberw))
- Fixed documentation for tags to link properly. [\#1578](https://github.com/locustio/locust/pull/1578) ([Trouv](https://github.com/Trouv))
- More easily extend web UI [\#1574](https://github.com/locustio/locust/pull/1574) ([solowalker27](https://github.com/solowalker27))
- Only warn about open file limit when not running as master [\#1573](https://github.com/locustio/locust/pull/1573) ([parberge](https://github.com/parberge))
- Adding more debug logging for runners.py [\#1570](https://github.com/locustio/locust/pull/1570) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Add friendlier message about expected limit [\#1566](https://github.com/locustio/locust/pull/1566) ([parberge](https://github.com/parberge))
- Update documentation for schedule\_task parameters in TaskSet \(task.py\) [\#1565](https://github.com/locustio/locust/pull/1565) ([kmels](https://github.com/kmels))
- Added comment for clarity [\#1561](https://github.com/locustio/locust/pull/1561) ([raiyankamal](https://github.com/raiyankamal))
- Refactor and fix delayed user stopping in combination with on\_stop [\#1560](https://github.com/locustio/locust/pull/1560) ([cyberw](https://github.com/cyberw))
- Remove legacy code that was only needed for py2 [\#1559](https://github.com/locustio/locust/pull/1559) ([cyberw](https://github.com/cyberw))
- Clean up code and tighten flake8 linting [\#1558](https://github.com/locustio/locust/pull/1558) ([cyberw](https://github.com/cyberw))

## [1.2.3](https://github.com/locustio/locust/tree/1.2.3) (2020-08-28)

[Full Changelog](https://github.com/locustio/locust/compare/1.2.2...1.2.3)

**Fixed bugs:**

- Unable to install packages using pip [\#1548](https://github.com/locustio/locust/issues/1548)
- Cant start: Werkzeug: TypeError: code\(\) takes at least 14 arguments \(13 given\) [\#1545](https://github.com/locustio/locust/issues/1545)
- use\_as\_lib.py example getting stuck when running [\#1542](https://github.com/locustio/locust/issues/1542)
- Locust stuck in "Shape worker starting" when restarting a test from the webUI [\#1540](https://github.com/locustio/locust/issues/1540)

**Closed issues:**

- Let's fix code to be PEP8 compliant? [\#1489](https://github.com/locustio/locust/issues/1489)

**Merged pull requests:**

- Various linting fixes [\#1549](https://github.com/locustio/locust/pull/1549) ([cyberw](https://github.com/cyberw))
- Reformat code using black. Also add black --check to build. [\#1547](https://github.com/locustio/locust/pull/1547) ([cyberw](https://github.com/cyberw))
- fix use\_as\_lib example [\#1543](https://github.com/locustio/locust/pull/1543) ([taojy123](https://github.com/taojy123))
- Fix stopping and restarting of LoadTestShape test [\#1541](https://github.com/locustio/locust/pull/1541) ([max-rocket-internet](https://github.com/max-rocket-internet))

## [1.2.2](https://github.com/locustio/locust/tree/1.2.2) (2020-08-22)

[Full Changelog](https://github.com/locustio/locust/compare/1.2.1...1.2.2)

**Merged pull requests:**

- Fix load shape worker in headless. [\#1539](https://github.com/locustio/locust/pull/1539) ([cyberw](https://github.com/cyberw))
- Add test case for stats\_history [\#1538](https://github.com/locustio/locust/pull/1538) ([taojy123](https://github.com/taojy123))
- Update README.md to have full links to images [\#1536](https://github.com/locustio/locust/pull/1536) ([max-rocket-internet](https://github.com/max-rocket-internet))

## [1.2.1](https://github.com/locustio/locust/tree/1.2.1) (2020-08-20)

[Full Changelog](https://github.com/locustio/locust/compare/1.2...1.2.1)

**Fixed bugs:**

- ValueError: StatsEntry.use\_response\_times\_cache must be set to True [\#1531](https://github.com/locustio/locust/issues/1531)

**Merged pull requests:**

- fix \#1531 \(ValueError: StatsEntry.use\_response\_times\_cache must be set to True\) [\#1534](https://github.com/locustio/locust/pull/1534) ([cyberw](https://github.com/cyberw))
- Add missing parameter to render\_template to grey out UI fields [\#1533](https://github.com/locustio/locust/pull/1533) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Update repo README with new wording, locust example, screenshots [\#1532](https://github.com/locustio/locust/pull/1532) ([max-rocket-internet](https://github.com/max-rocket-internet))

## [1.2](https://github.com/locustio/locust/tree/1.2) (2020-08-19)

[Full Changelog](https://github.com/locustio/locust/compare/1.1.1...1.2)

**Fixed bugs:**

- Excessive precision of metrics in losust csv stats  [\#1501](https://github.com/locustio/locust/issues/1501)
- WorkerRunner spawns heartbeat before setting worker\_state [\#1500](https://github.com/locustio/locust/issues/1500)
- Negative min\_response\_time shown in stats [\#1487](https://github.com/locustio/locust/issues/1487)
- Unhandled exception:  ConnectionResetError, Connection reset by peer \(FastHttpUser\) [\#1472](https://github.com/locustio/locust/issues/1472)

**Closed issues:**

- Change the position of dividers in command line report [\#1514](https://github.com/locustio/locust/issues/1514)
- Allow negative hatch rate for ramping down [\#1488](https://github.com/locustio/locust/issues/1488)
- Missing URL to download full csv history [\#1468](https://github.com/locustio/locust/issues/1468)
- Support for completely custom load pattern / shape [\#1432](https://github.com/locustio/locust/issues/1432)
- rename "hatch rate" to "spawn rate" [\#1405](https://github.com/locustio/locust/issues/1405)

**Merged pull requests:**

- Doc review changes [\#1528](https://github.com/locustio/locust/pull/1528) ([phil-davis](https://github.com/phil-davis))
- Major rework of documentation & many small fixes [\#1527](https://github.com/locustio/locust/pull/1527) ([cyberw](https://github.com/cyberw))
- Make hatch-rate parameter deprecated instead of killing it right away. [\#1526](https://github.com/locustio/locust/pull/1526) ([cyberw](https://github.com/cyberw))
- Move dividers \(pipe characters\) in stats command line output. Also shrink percentiles output and remove 99.999 percentile by default Fixes \#1514 [\#1525](https://github.com/locustio/locust/pull/1525) ([cyberw](https://github.com/cyberw))
- Grey out UI input fields when LoadTestShape is in use [\#1524](https://github.com/locustio/locust/pull/1524) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Rename hatch rate to spawn rate. Fixes \#1405 [\#1523](https://github.com/locustio/locust/pull/1523) ([cyberw](https://github.com/cyberw))
- Keep csv files open [\#1522](https://github.com/locustio/locust/pull/1522) ([lhupfeldt](https://github.com/lhupfeldt))
- Fix issue with non str, non Exception type failure messages [\#1517](https://github.com/locustio/locust/pull/1517) ([cyberw](https://github.com/cyberw))
-  Add Feature: Download Report File [\#1516](https://github.com/locustio/locust/pull/1516) ([taojy123](https://github.com/taojy123))
- Fix typos [\#1512](https://github.com/locustio/locust/pull/1512) ([phil-davis](https://github.com/phil-davis))
- Fix typo of failure\_percentage in test\_stats.py [\#1511](https://github.com/locustio/locust/pull/1511) ([phil-davis](https://github.com/phil-davis))
- Fix old HttpLocust reference in docs [\#1508](https://github.com/locustio/locust/pull/1508) ([phil-davis](https://github.com/phil-davis))
- Adding ability to generate any custom load shape with LoadTestShape class [\#1505](https://github.com/locustio/locust/pull/1505) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Download full history - see issue 1468 [\#1504](https://github.com/locustio/locust/pull/1504) ([lhupfeldt](https://github.com/lhupfeldt))
- Fix csv stats precision [\#1503](https://github.com/locustio/locust/pull/1503) ([vstepanov-lohika-tix](https://github.com/vstepanov-lohika-tix))
- Allow ramping down of users [\#1502](https://github.com/locustio/locust/pull/1502) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Add 2 things to .gitignore [\#1498](https://github.com/locustio/locust/pull/1498) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Print valid URL when --web-host is not specified [\#1496](https://github.com/locustio/locust/pull/1496) ([dmitrytokarev](https://github.com/dmitrytokarev))
- Replace time.time\(\) with time.monotonic\(\) [\#1492](https://github.com/locustio/locust/pull/1492) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Remove "Loadgen" from CPU warning log messages [\#1491](https://github.com/locustio/locust/pull/1491) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Fix small typo in docker docs [\#1490](https://github.com/locustio/locust/pull/1490) ([max-rocket-internet](https://github.com/max-rocket-internet))
- fade into the running screen before getting a response from the server [\#1479](https://github.com/locustio/locust/pull/1479) ([camilojimenez](https://github.com/camilojimenez))
- Refactoring stats to handle custom percentiles [\#1477](https://github.com/locustio/locust/pull/1477) ([vstepanov-lohika-tix](https://github.com/vstepanov-lohika-tix))
- Handle connection reset error in fast http client [\#1475](https://github.com/locustio/locust/pull/1475) ([bendizen](https://github.com/bendizen))

## [1.1.1](https://github.com/locustio/locust/tree/1.1.1) (2020-07-07)

[Full Changelog](https://github.com/locustio/locust/compare/1.1...1.1.1)

**Fixed bugs:**

- --run-time flag is not respected if there is an exception in a test\_stop listener [\#1461](https://github.com/locustio/locust/issues/1461)
- Unhandled exception: stream ended at an unexpected time [\#1457](https://github.com/locustio/locust/issues/1457)
-  Unhandled `UnicodeDecodeError` exception if response with status 400 and request contains binary payload \(for FastHttpUser\) [\#1447](https://github.com/locustio/locust/issues/1447)

**Closed issues:**

- FastHttpUser: Show error codes on 'Failures' page for 'BadStatusCode' exception [\#1460](https://github.com/locustio/locust/issues/1460)

**Merged pull requests:**

- Improve logging when locust master port is busy. [\#1471](https://github.com/locustio/locust/pull/1471) ([cyberw](https://github.com/cyberw))
- Handle http parse exceptions [\#1464](https://github.com/locustio/locust/pull/1464) ([magupov](https://github.com/magupov))
- Gracefully handle exceptions in event listeners [\#1462](https://github.com/locustio/locust/pull/1462) ([camilojimenez](https://github.com/camilojimenez))

## [1.1](https://github.com/locustio/locust/tree/1.1) (2020-06-28)

[Full Changelog](https://github.com/locustio/locust/compare/1.0.3...1.1)

**Fixed bugs:**

- Charts are twice as high as they need to [\#1440](https://github.com/locustio/locust/issues/1440)
- Master-host IP is not overrided by environment variable. [\#1424](https://github.com/locustio/locust/issues/1424)
- Two test\_stop events triggered when --run-time expires [\#1421](https://github.com/locustio/locust/issues/1421)
- Locust Installation error on Ubuntu 16.04 and Debian Stretch [\#1418](https://github.com/locustio/locust/issues/1418)
- locust doesn't escape the double quotes in the csv output  [\#1417](https://github.com/locustio/locust/issues/1417)
- on\_master\_stop\_hatching is not triggered on master when hatching terminates [\#1295](https://github.com/locustio/locust/issues/1295)
- Installing 0.12.1 requires "pipenv lock --pre" [\#1116](https://github.com/locustio/locust/issues/1116)

**Closed issues:**

- Ability to run test\_start on workers. [\#1408](https://github.com/locustio/locust/issues/1408)
- Ability to Stop Locust Client from within the test script [\#1192](https://github.com/locustio/locust/issues/1192)

**Merged pull requests:**

- Fixes a typo [\#1454](https://github.com/locustio/locust/pull/1454) ([Waples](https://github.com/Waples))
- minor typos in docs [\#1453](https://github.com/locustio/locust/pull/1453) ([howardosborne](https://github.com/howardosborne))
- fixed up environment.parsed\_options [\#1450](https://github.com/locustio/locust/pull/1450) ([pentop](https://github.com/pentop))
- Allow Users to stop the runner by calling self.environment.runner.quit\(\) \(without deadlocking sometimes\) [\#1448](https://github.com/locustio/locust/pull/1448) ([cyberw](https://github.com/cyberw))
- Cut to only 5% free space on the top of the graphs [\#1443](https://github.com/locustio/locust/pull/1443) ([benallard](https://github.com/benallard))
- Base Locust Docker image on non-alpine python image [\#1435](https://github.com/locustio/locust/pull/1435) ([heyman](https://github.com/heyman))
- Quickstart documentation clarification. [\#1434](https://github.com/locustio/locust/pull/1434) ([JamesB41](https://github.com/JamesB41))
- Use csv module to generate csv data [\#1428](https://github.com/locustio/locust/pull/1428) ([ajt89](https://github.com/ajt89))
- Add simple documentation with use case for init event [\#1415](https://github.com/locustio/locust/pull/1415) ([Zooce](https://github.com/Zooce))
- Simplify documentation of catch\_response & add example of response time validation. [\#1414](https://github.com/locustio/locust/pull/1414) ([cyberw](https://github.com/cyberw))

## [1.0.3](https://github.com/locustio/locust/tree/1.0.3) (2020-06-05)

[Full Changelog](https://github.com/locustio/locust/compare/1.0.2...1.0.3)

**Fixed bugs:**

- Search is broken on readthedocs [\#1391](https://github.com/locustio/locust/issues/1391)

**Closed issues:**

- Custom Request/sec exit code [\#587](https://github.com/locustio/locust/issues/587)

**Merged pull requests:**

- Remove Bad Apostrophe [\#1411](https://github.com/locustio/locust/pull/1411) ([curtisgibby](https://github.com/curtisgibby))
- update \_\_init\_\_ file [\#1409](https://github.com/locustio/locust/pull/1409) ([manifiko](https://github.com/manifiko))
- Rename 3 remaining instances of slave to worker [\#1400](https://github.com/locustio/locust/pull/1400) ([ibrahima](https://github.com/ibrahima))
- The format for providing host can be confusing at times [\#1398](https://github.com/locustio/locust/pull/1398) ([jo19in1](https://github.com/jo19in1))
- Ability to control the Locust process' exit code [\#1396](https://github.com/locustio/locust/pull/1396) ([heyman](https://github.com/heyman))

## [1.0.2](https://github.com/locustio/locust/tree/1.0.2) (2020-05-25)

[Full Changelog](https://github.com/locustio/locust/compare/1.0.1...1.0.2)

**Fixed bugs:**

- Update flask version [\#1394](https://github.com/locustio/locust/issues/1394)
- Got "unknown user exception" when use --step-load and --step-clients [\#1385](https://github.com/locustio/locust/issues/1385)
- SequentialTaskSet is broken when using local class members \(headless mode\) [\#1379](https://github.com/locustio/locust/issues/1379)
- FastHttpLocust + SNI [\#1369](https://github.com/locustio/locust/issues/1369)

**Closed issues:**

- We should check limits \(ulimit\) and warn if they are too low [\#1368](https://github.com/locustio/locust/issues/1368)
- Run locust as a job but still have access to the API. [\#1305](https://github.com/locustio/locust/issues/1305)
- error: argument --master-port: invalid int value bug [\#1226](https://github.com/locustio/locust/issues/1226)

**Merged pull requests:**

- Update flask requirement. Fixes \#1394 [\#1395](https://github.com/locustio/locust/pull/1395) ([cyberw](https://github.com/cyberw))
- Bump geventhttpclient and switch back to use its original repo + fix windows issue with resource module [\#1388](https://github.com/locustio/locust/pull/1388) ([cyberw](https://github.com/cyberw))
- Rework quickstart documentation and update some documentation for 1.0 [\#1384](https://github.com/locustio/locust/pull/1384) ([cyberw](https://github.com/cyberw))
- Make TaskSet .user and .parent read only properties, avoids / fixes \#1379 [\#1380](https://github.com/locustio/locust/pull/1380) ([cyberw](https://github.com/cyberw))
- Fixed typo [\#1378](https://github.com/locustio/locust/pull/1378) ([rahulrai-in](https://github.com/rahulrai-in))
- Try to increase open files limit and warn if it is still too low afterwards [\#1375](https://github.com/locustio/locust/pull/1375) ([cyberw](https://github.com/cyberw))

## [1.0.1](https://github.com/locustio/locust/tree/1.0.1) (2020-05-16)

[Full Changelog](https://github.com/locustio/locust/compare/1.0...1.0.1)

**Merged pull requests:**

- Add metadata for the locust PyPI package that marks the locustio package as obsolete [\#1377](https://github.com/locustio/locust/pull/1377) ([heyman](https://github.com/heyman))

## [1.0](https://github.com/locustio/locust/tree/1.0) (2020-05-16)

[Full Changelog](https://github.com/locustio/locust/compare/1.0b2...1.0)

**Fixed bugs:**

- FastHttpUser doesn't use the SNI TLS extension [\#1360](https://github.com/locustio/locust/issues/1360)
- DEBUG output in docker is not working [\#1337](https://github.com/locustio/locust/issues/1337)
- Can't run Locust distributed with --csv-full-history  [\#1315](https://github.com/locustio/locust/issues/1315)
- \[Nested TaskSet\] Child TaskSet's on\_stop method is not called when GreenletExit [\#1206](https://github.com/locustio/locust/issues/1206)

**Closed issues:**

- Add @only decorator to TaskSets [\#1275](https://github.com/locustio/locust/issues/1275)
- resp.failure\(\) shouldnt immediately log a failed request, just mark it a such [\#1335](https://github.com/locustio/locust/issues/1335)
- Change CSV column names [\#1317](https://github.com/locustio/locust/issues/1317)
- Remove @seq\_task and instead add a SequentialTaskSet class [\#1286](https://github.com/locustio/locust/issues/1286)
- Change how logging is handled [\#1285](https://github.com/locustio/locust/issues/1285)
- Remove the Locust.setup and Locust.teardown hooks in favour of adding test\_start and test\_stop events [\#1284](https://github.com/locustio/locust/issues/1284)
- Rename Locust to User/LocustUser [\#1283](https://github.com/locustio/locust/issues/1283)
- Clean up among the command line arguments [\#1282](https://github.com/locustio/locust/issues/1282)
- Docker image should not require TARGET\_URL [\#1247](https://github.com/locustio/locust/issues/1247)
- Duplicate/confusing entry in pypi [\#817](https://github.com/locustio/locust/issues/817)
- How to run test programatically [\#222](https://github.com/locustio/locust/issues/222)
- Alternative terminology for "slave" [\#220](https://github.com/locustio/locust/issues/220)

**Merged pull requests:**

- Remove task arguments [\#1370](https://github.com/locustio/locust/pull/1370) ([heyman](https://github.com/heyman))
- Add task marking for running more specific tests [\#1358](https://github.com/locustio/locust/pull/1358) ([Trouv](https://github.com/Trouv))
- Add User count to CSV history stats [\#1316](https://github.com/locustio/locust/pull/1316) ([heyman](https://github.com/heyman))
- Rename locust to user [\#1314](https://github.com/locustio/locust/pull/1314) ([anuj-ssharma](https://github.com/anuj-ssharma))

## [1.0b2](https://github.com/locustio/locust/tree/1.0b2) (2020-05-01)

[Full Changelog](https://github.com/locustio/locust/compare/1.0b1...1.0b2)

**Closed issues:**

- Add --config parameter [\#1334](https://github.com/locustio/locust/issues/1334)
- clean up core.py & \_\_init\_\_.py [\#1328](https://github.com/locustio/locust/issues/1328)

**Merged pull requests:**

- Split core.py into two files in separate python package [\#1361](https://github.com/locustio/locust/pull/1361) ([heyman](https://github.com/heyman))
- --config command line argument [\#1359](https://github.com/locustio/locust/pull/1359) ([MattFisher](https://github.com/MattFisher))

## [1.0b1](https://github.com/locustio/locust/tree/1.0b1) (2020-04-29)

[Full Changelog](https://github.com/locustio/locust/compare/0.14.6...1.0b1)

**Fixed bugs:**

- Docker image: worker mode not starting correctly [\#1322](https://github.com/locustio/locust/issues/1322)
- Exception throws on attempt to report request results to master [\#1293](https://github.com/locustio/locust/issues/1293)
- Can't access web interface [\#1288](https://github.com/locustio/locust/issues/1288)
- Web page is confused when I shutdown the only slave [\#1279](https://github.com/locustio/locust/issues/1279)
- \[Documentation\] Bleeding Edge link is broken [\#1278](https://github.com/locustio/locust/issues/1278)
- Locust Web Dashboard Charts, Slaves sections not working after certain time [\#1276](https://github.com/locustio/locust/issues/1276)
- Connection pool is full, discarding connection | 'Connection aborted.', RemoteDisconnected\('Remote end closed connection without response [\#1263](https://github.com/locustio/locust/issues/1263)

**Closed issues:**

- Retrieving response time on Master while execution is going on through custom code in no-web mode [\#1351](https://github.com/locustio/locust/issues/1351)
- "Order of events" clarification [\#1349](https://github.com/locustio/locust/issues/1349)
- More information in csv reports [\#1292](https://github.com/locustio/locust/issues/1292)
- Rename and restructure Locust/TaskSet [\#1264](https://github.com/locustio/locust/issues/1264)
- Add `allow_redirects` option to FastHttpSession.request [\#1238](https://github.com/locustio/locust/issues/1238)
- Retrieve failures.csv in --no-web mode [\#1237](https://github.com/locustio/locust/issues/1237)
- command line arguments for clients and spawn rate should populate ui in the same way as url [\#1186](https://github.com/locustio/locust/issues/1186)

**Merged pull requests:**

- Environment variable configuration changes [\#1355](https://github.com/locustio/locust/pull/1355) ([heyman](https://github.com/heyman))
- Add CLI params for TLS cert and key - serves over HTTPS [\#1354](https://github.com/locustio/locust/pull/1354) ([mattdodge](https://github.com/mattdodge))
- Add allow\_redirects parameter to FastHttpLocust.client.request\(\). Fixes \#1238 [\#1344](https://github.com/locustio/locust/pull/1344) ([cyberw](https://github.com/cyberw))
- Give better error message when kubernetes env vars collide with locust's [\#1343](https://github.com/locustio/locust/pull/1343) ([cyberw](https://github.com/cyberw))
- Fix web options [\#1340](https://github.com/locustio/locust/pull/1340) ([Trouv](https://github.com/Trouv))
- Populate UI fields with -c, -r, --step-clients, and --step-time options [\#1339](https://github.com/locustio/locust/pull/1339) ([Trouv](https://github.com/Trouv))
- Remove docker\_start.sh and set locust as entrypoint for official Docker image [\#1338](https://github.com/locustio/locust/pull/1338) ([heyman](https://github.com/heyman))
- Allow multiple calls to response.failure\(\) or response.success\(\) within the same with block [\#1336](https://github.com/locustio/locust/pull/1336) ([heyman](https://github.com/heyman))
- Removed double consideration of same timestamp [\#1332](https://github.com/locustio/locust/pull/1332) ([Oribow](https://github.com/Oribow))
- Make all LocustRunners aware of their target\_user\_count, not just MasterLocustRunner [\#1331](https://github.com/locustio/locust/pull/1331) ([cyberw](https://github.com/cyberw))
- Import wait functions from locust instead of locust.wait\_time [\#1330](https://github.com/locustio/locust/pull/1330) ([cyberw](https://github.com/cyberw))
- Stop exposing exceptions on locust module, remove old wait api \(step 1 of fixing \#1328\) [\#1329](https://github.com/locustio/locust/pull/1329) ([cyberw](https://github.com/cyberw))
- Add Runners, WebUI and Environment to the public API [\#1327](https://github.com/locustio/locust/pull/1327) ([heyman](https://github.com/heyman))
- Update main.py about gevent.signal\(\) [\#1326](https://github.com/locustio/locust/pull/1326) ([test-bai-cpu](https://github.com/test-bai-cpu))
- Improve how we do logging [\#1325](https://github.com/locustio/locust/pull/1325) ([heyman](https://github.com/heyman))
- Worker quitting then stopping via web UI bug fix [\#1324](https://github.com/locustio/locust/pull/1324) ([Trouv](https://github.com/Trouv))
- Fixed some spelling/grammar on docstrings in core.py [\#1323](https://github.com/locustio/locust/pull/1323) ([Trouv](https://github.com/Trouv))
- Add basic auth for webui [\#1313](https://github.com/locustio/locust/pull/1313) ([anuj-ssharma](https://github.com/anuj-ssharma))
- Group related command line options together [\#1311](https://github.com/locustio/locust/pull/1311) ([heyman](https://github.com/heyman))
- Replace TaskSequence and @seq\_task with SequentialTaskSet [\#1310](https://github.com/locustio/locust/pull/1310) ([heyman](https://github.com/heyman))
- Replace locust setup teardown with events [\#1309](https://github.com/locustio/locust/pull/1309) ([heyman](https://github.com/heyman))
- Decouple Runner and Locust code by introducing Locust.start and Locust.stop methods [\#1306](https://github.com/locustio/locust/pull/1306) ([heyman](https://github.com/heyman))
- Allow tasks to be declared directly under Locust classes [\#1304](https://github.com/locustio/locust/pull/1304) ([heyman](https://github.com/heyman))
- Rename slave to worker \(except changelog\) [\#1303](https://github.com/locustio/locust/pull/1303) ([anuj-ssharma](https://github.com/anuj-ssharma))
- Support parametrization of FastHttpLocust  [\#1299](https://github.com/locustio/locust/pull/1299) ([cyberw](https://github.com/cyberw))
- Fix typo in running-locust-in-step-load-mode.rst [\#1298](https://github.com/locustio/locust/pull/1298) ([sgajjar](https://github.com/sgajjar))
- Add reference to LocustRunner instance and WebUI instance on Environment [\#1291](https://github.com/locustio/locust/pull/1291) ([heyman](https://github.com/heyman))
- Give a more descriptive error when the Locust or TaskSet has no tasks. [\#1287](https://github.com/locustio/locust/pull/1287) ([cyberw](https://github.com/cyberw))
- ensure the connection between master and slave in heartbeat [\#1280](https://github.com/locustio/locust/pull/1280) ([delulu](https://github.com/delulu))
- Fix simple typo: betwen -\> between [\#1269](https://github.com/locustio/locust/pull/1269) ([timgates42](https://github.com/timgates42))
- Work towards 1.0. Refactoring of runners/events/web ui. Getting rid of global state. [\#1266](https://github.com/locustio/locust/pull/1266) ([heyman](https://github.com/heyman))

## [0.14.6](https://github.com/locustio/locust/tree/0.14.6) (2020-02-25)

[Full Changelog](https://github.com/locustio/locust/compare/0.14.5...0.14.6)

**Closed issues:**

- Fix simple typo: betwen -\> between [\#1268](https://github.com/locustio/locust/issues/1268)

## [0.14.5](https://github.com/locustio/locust/tree/0.14.5) (2020-02-25)

[Full Changelog](https://github.com/locustio/locust/compare/0.14.4...0.14.5)

**Fixed bugs:**

- Code blocks in docs not rendered [\#1258](https://github.com/locustio/locust/issues/1258)
- Unable to install on windows [\#1254](https://github.com/locustio/locust/issues/1254)

**Closed issues:**

- Remove support for Python 2.7 & 3.5 [\#1120](https://github.com/locustio/locust/issues/1120)

**Merged pull requests:**

- add json\(\) method to FastHttpLocust \(to match regular HttpLocust\) [\#1259](https://github.com/locustio/locust/pull/1259) ([cyberw](https://github.com/cyberw))
- docs: remove the description of port 5558 [\#1255](https://github.com/locustio/locust/pull/1255) ([orisano](https://github.com/orisano))
- Remove six and other 2.7 compatibility code [\#1253](https://github.com/locustio/locust/pull/1253) ([cyberw](https://github.com/cyberw))

## [0.14.4](https://github.com/locustio/locust/tree/0.14.4) (2020-02-03)

[Full Changelog](https://github.com/locustio/locust/compare/0.14.3...0.14.4)

**Fixed bugs:**

- FastHttpLocust times out when HttpLocust does not [\#1246](https://github.com/locustio/locust/issues/1246)

## [0.14.3](https://github.com/locustio/locust/tree/0.14.3) (2020-02-03)

[Full Changelog](https://github.com/locustio/locust/compare/0.14.2...0.14.3)

## [0.14.2](https://github.com/locustio/locust/tree/0.14.2) (2020-02-03)

[Full Changelog](https://github.com/locustio/locust/compare/0.14.1...0.14.2)

## [0.14.1](https://github.com/locustio/locust/tree/0.14.1) (2020-02-03)

[Full Changelog](https://github.com/locustio/locust/compare/0.14.0...0.14.1)

## [0.14.0](https://github.com/locustio/locust/tree/0.14.0) (2020-02-03)

[Full Changelog](https://github.com/locustio/locust/compare/0.13.5...0.14.0)

**Fixed bugs:**

- FastHttpLocust gives error when using valid url. [\#1222](https://github.com/locustio/locust/issues/1222)
- Error generating request statistics CSV in master–slave mode [\#1191](https://github.com/locustio/locust/issues/1191)
- Stats are reset when re-balancing users across slave nodes [\#1168](https://github.com/locustio/locust/issues/1168)
- Slave count stuck at 3 instead of decreasing to 1 due to "missing" [\#1158](https://github.com/locustio/locust/issues/1158)

**Closed issues:**

- scale clients up and down during a run [\#1185](https://github.com/locustio/locust/issues/1185)
- Locust should warn if CPU usage is too high [\#1161](https://github.com/locustio/locust/issues/1161)
- Support Step Load Pattern \(up & down\) [\#1001](https://github.com/locustio/locust/issues/1001)
- Provide a way to specify locust counts and hatch rate per locust class [\#683](https://github.com/locustio/locust/issues/683)

**Merged pull requests:**

- Save failures.csv in --no-web mode [\#1245](https://github.com/locustio/locust/pull/1245) ([ajt89](https://github.com/ajt89))
- Drop support for pre 3.6 Python versions \(give error during installation\) [\#1243](https://github.com/locustio/locust/pull/1243) ([cyberw](https://github.com/cyberw))
- Warn if CPU usage is too high \(\>90%\) \#1161 [\#1236](https://github.com/locustio/locust/pull/1236) ([cyberw](https://github.com/cyberw))
- Update docs for running locust in Step Load Mode [\#1235](https://github.com/locustio/locust/pull/1235) ([delulu](https://github.com/delulu))
- allow 1 percent codecov degradation before failing build \(because it is flaky\) [\#1230](https://github.com/locustio/locust/pull/1230) ([cyberw](https://github.com/cyberw))
- Disable codecov patch analysis, because it fails all the time [\#1229](https://github.com/locustio/locust/pull/1229) ([cyberw](https://github.com/cyberw))
- Relax host checking for FastHttpLocust to be more in line with HttpLocust. Fixes \#1222 [\#1227](https://github.com/locustio/locust/pull/1227) ([cyberw](https://github.com/cyberw))
- Add "Running Locust with Docker" to the TOC [\#1221](https://github.com/locustio/locust/pull/1221) ([TBBle](https://github.com/TBBle))
- Fix link formatting for the Helm chart [\#1219](https://github.com/locustio/locust/pull/1219) ([TBBle](https://github.com/TBBle))
- fix: change typo UserBehavior to UserBehaviour [\#1218](https://github.com/locustio/locust/pull/1218) ([aasmpro](https://github.com/aasmpro))
- Fix 'd rop-in' typo to 'drop-in' [\#1215](https://github.com/locustio/locust/pull/1215) ([jenglamlow](https://github.com/jenglamlow))
- Update running-locust-distributed.rst [\#1212](https://github.com/locustio/locust/pull/1212) ([Neamar](https://github.com/Neamar))
- Warn if spawn rate is too high. Adresses bug \#1174 for example. [\#1211](https://github.com/locustio/locust/pull/1211) ([cyberw](https://github.com/cyberw))
- Allow users to override encoding when decoding requests \(maybe using chardet, as was the default before\) [\#1204](https://github.com/locustio/locust/pull/1204) ([cyberw](https://github.com/cyberw))
- Allow min\_wait and max\_wait times of 0 [\#1199](https://github.com/locustio/locust/pull/1199) ([Aresius423](https://github.com/Aresius423))

## [0.13.5](https://github.com/locustio/locust/tree/0.13.5) (2019-12-17)

[Full Changelog](https://github.com/locustio/locust/compare/0.13.4...0.13.5)

**Fixed bugs:**

- Fix percentiles printed in \_stats.csv file [\#1198](https://github.com/locustio/locust/issues/1198)
- set default Accept-Encoding to "gzip, deflate" in FastHttpLocust to match HttpLocust behaviour [\#1195](https://github.com/locustio/locust/issues/1195)
- FastHttpLocust is very slow at returning the response text [\#1193](https://github.com/locustio/locust/issues/1193)

**Merged pull requests:**

- Use `response_time_percentile` for \<name\>\_stats.csv file instead of `current_response_time_percentile` [\#1197](https://github.com/locustio/locust/pull/1197) ([mehta-ankit](https://github.com/mehta-ankit))
- Send Accept-Encoding: gzip, deflate as default in FastHttpLocust. [\#1196](https://github.com/locustio/locust/pull/1196) ([cyberw](https://github.com/cyberw))
- Get encoding from content-type header instead of autodetecting using chardet \(which is slow\) [\#1194](https://github.com/locustio/locust/pull/1194) ([cyberw](https://github.com/cyberw))

## [0.13.4](https://github.com/locustio/locust/tree/0.13.4) (2019-12-16)

[Full Changelog](https://github.com/locustio/locust/compare/0.13.3...0.13.4)

## [0.13.3](https://github.com/locustio/locust/tree/0.13.3) (2019-12-13)

[Full Changelog](https://github.com/locustio/locust/compare/0.13.2...0.13.3)

**Fixed bugs:**

- Time response graph is not working on master/slave configuration [\#1182](https://github.com/locustio/locust/issues/1182)
- Unable to properly connect multiple slaves,  master  [\#1176](https://github.com/locustio/locust/issues/1176)
- Zero exit code on exception [\#1172](https://github.com/locustio/locust/issues/1172)
- `--stop-timeout` is not respected when changing number of running Users in distributed mode [\#1162](https://github.com/locustio/locust/issues/1162)

**Closed issues:**

- "Percentage of the requests.." table has missing column headers [\#1180](https://github.com/locustio/locust/issues/1180)
- Set locust parameters via env vars & config file [\#1166](https://github.com/locustio/locust/issues/1166)

**Merged pull requests:**

- Use ConfigArgParse instead of argparse, to support getting parameters from config file and/or env vars. [\#1167](https://github.com/locustio/locust/pull/1167) ([cyberw](https://github.com/cyberw))
- Add toolbox control for for downloading chart as png [\#1165](https://github.com/locustio/locust/pull/1165) ([skivis](https://github.com/skivis))
- Allow locust to get SIGTERM\(aka Ctrl+C\) messages. [\#1159](https://github.com/locustio/locust/pull/1159) ([turgayozgur](https://github.com/turgayozgur))
- Stats: New argument "--csv-full-history" appends stats entries every interval in a new "\_stats\_history.csv" File [\#1146](https://github.com/locustio/locust/pull/1146) ([mehta-ankit](https://github.com/mehta-ankit))
- Support Step Load Pattern [\#1002](https://github.com/locustio/locust/pull/1002) ([delulu](https://github.com/delulu))

## [0.13.2](https://github.com/locustio/locust/tree/0.13.2) (2019-11-18)

[Full Changelog](https://github.com/locustio/locust/compare/0.13.1...0.13.2)

**Fixed bugs:**

- Response Times graph broken \(drops to 0 after a while\) [\#1157](https://github.com/locustio/locust/issues/1157)
- TaskSet min\_wait and max\_wait are ignored [\#891](https://github.com/locustio/locust/issues/891)

**Closed issues:**

- Add charts for number of failures in the Web UI [\#952](https://github.com/locustio/locust/issues/952)

## [0.13.1](https://github.com/locustio/locust/tree/0.13.1) (2019-11-16)

[Full Changelog](https://github.com/locustio/locust/compare/0.13.0...0.13.1)

**Fixed bugs:**

- Web UI doesn't start on Python 3.8.0 [\#1154](https://github.com/locustio/locust/issues/1154)
- When locust exits the current RPS is outputted instead of the total RPS [\#1152](https://github.com/locustio/locust/issues/1152)
- Missing headline columns in response time percentile stats printed to console [\#1151](https://github.com/locustio/locust/issues/1151)

**Closed issues:**

- Be able to install pip packages using the docker image [\#1149](https://github.com/locustio/locust/issues/1149)

**Merged pull requests:**

- Docker: add home directory for locust user to install pip packages [\#1150](https://github.com/locustio/locust/pull/1150) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Revert "update build\_url function in Locust HttpSession " [\#1148](https://github.com/locustio/locust/pull/1148) ([vstepanov-lohika-tix](https://github.com/vstepanov-lohika-tix))

## [0.13.0](https://github.com/locustio/locust/tree/0.13.0) (2019-11-14)

[Full Changelog](https://github.com/locustio/locust/compare/0.12.2...0.13.0)

**Fixed bugs:**

- autoscaling slaves resets users [\#1143](https://github.com/locustio/locust/issues/1143)
- Repeated secure requests with FastHttpLocust crashes in cookie management [\#1138](https://github.com/locustio/locust/issues/1138)
- FastHttpLocust gives ssl error with let's encrypt certs [\#1137](https://github.com/locustio/locust/issues/1137)
- stop\_timeout defined in Locust class takes precedence over --run-time option [\#1117](https://github.com/locustio/locust/issues/1117)
- Test metrics are not preserved on Stop click in the UI [\#883](https://github.com/locustio/locust/issues/883)
- locust stuck in hatching state [\#146](https://github.com/locustio/locust/issues/146)

**Closed issues:**

- To improve build\_url method in Locust HttpSession [\#1133](https://github.com/locustio/locust/issues/1133)
- Duplicate API section in navigation of document [\#1132](https://github.com/locustio/locust/issues/1132)
- Locust with custom clients only displays maximum response time [\#1084](https://github.com/locustio/locust/issues/1084)
- Stop locusts graceful [\#1062](https://github.com/locustio/locust/issues/1062)
- could we report 99.9% percentile in CSV file? [\#1040](https://github.com/locustio/locust/issues/1040)
- Provide an official Docker image [\#849](https://github.com/locustio/locust/issues/849)
- Number of Users Dependent on Number of slaves ?  [\#724](https://github.com/locustio/locust/issues/724)
- Allow a fixed RPS rate [\#646](https://github.com/locustio/locust/issues/646)
- Unique task id available ? [\#349](https://github.com/locustio/locust/issues/349)
- nitpick: "\# requests" should be "\# successful requests"? [\#145](https://github.com/locustio/locust/issues/145)
- Display percentiles in the UI instead of just min, max and average [\#140](https://github.com/locustio/locust/issues/140)

**Merged pull requests:**

- Add response\_length to request\_failure event [\#1144](https://github.com/locustio/locust/pull/1144) ([cyberw](https://github.com/cyberw))
- Add failure per seconds as a series in the chart [\#1140](https://github.com/locustio/locust/pull/1140) ([alercunha](https://github.com/alercunha))
- Fix AttributeError: 'CompatRequest' object has no attribute 'type' in Cookiejar [\#1139](https://github.com/locustio/locust/pull/1139) ([cyberw](https://github.com/cyberw))
- update build\_url function in Locust HttpSession  [\#1134](https://github.com/locustio/locust/pull/1134) ([vstepanov-lohika-tix](https://github.com/vstepanov-lohika-tix))
- Fix and add test for when locusts fail to exit at end of iteration during stop timeout. [\#1127](https://github.com/locustio/locust/pull/1127) ([cyberw](https://github.com/cyberw))
- Let's stop calling the package beta! [\#1126](https://github.com/locustio/locust/pull/1126) ([cyberw](https://github.com/cyberw))
- Add p99.9 and p99.99 to request stats distribution csv [\#1125](https://github.com/locustio/locust/pull/1125) ([cyberw](https://github.com/cyberw))
- New API for specifying wait time [\#1118](https://github.com/locustio/locust/pull/1118) ([heyman](https://github.com/heyman))
- Add errors grouping for dynamic endpoint [\#993](https://github.com/locustio/locust/pull/993) ([dduleba](https://github.com/dduleba))
- add 90th %ile to the stats page [\#945](https://github.com/locustio/locust/pull/945) ([myzhan](https://github.com/myzhan))
- Make stdout/stderr wrappers identify themselves as not being a tty [\#929](https://github.com/locustio/locust/pull/929) ([michaelboulton](https://github.com/michaelboulton))
- Specify host in web ui [\#523](https://github.com/locustio/locust/pull/523) ([PayscaleNateW](https://github.com/PayscaleNateW))
- make sure the current working dir is in the sys.path [\#484](https://github.com/locustio/locust/pull/484) ([pwnage101](https://github.com/pwnage101))

## [0.12.2](https://github.com/locustio/locust/tree/0.12.2) (2019-10-26)

[Full Changelog](https://github.com/locustio/locust/compare/0.12.1...0.12.2)

**Fixed bugs:**

- Strange behavior of "Total Requests per Second" chart [\#889](https://github.com/locustio/locust/issues/889)
- Response time graph seems to be an average of all data [\#667](https://github.com/locustio/locust/issues/667)
- Totals Clarity in Web Results [\#629](https://github.com/locustio/locust/issues/629)
- on\_request\_xxx checks exiting condition against the wrong number [\#399](https://github.com/locustio/locust/issues/399)
- \[0.7.3\] Total fails percentage calculated wrong on console [\#384](https://github.com/locustio/locust/issues/384)
- URL names in dashboard are not HTML escaped [\#374](https://github.com/locustio/locust/issues/374)
- Percentage of fails in Total line is greater than 100% [\#357](https://github.com/locustio/locust/issues/357)
- Exceptions tab not working for on\_start method [\#269](https://github.com/locustio/locust/issues/269)
- Percentile response time anomalies at 100% [\#254](https://github.com/locustio/locust/issues/254)
- log.py's StdErrWrapper swallows fatal stacktraces [\#163](https://github.com/locustio/locust/issues/163)
- Slave count doesn't get updated in the UI if no more slaves are alive [\#62](https://github.com/locustio/locust/issues/62)

**Closed issues:**

- 0.12 released on GitHub but not on PyPI [\#1109](https://github.com/locustio/locust/issues/1109)
- Samples with response\_time None crashes stats.py [\#1087](https://github.com/locustio/locust/issues/1087)
- Requests Per Second Plot Breaks When There are too Many Unique URLs [\#1059](https://github.com/locustio/locust/issues/1059)
- UI 'stop' button does not stop test [\#1047](https://github.com/locustio/locust/issues/1047)
- Performance degradation for constant wait time [\#1042](https://github.com/locustio/locust/issues/1042)
- Locust decorators [\#1036](https://github.com/locustio/locust/issues/1036)
- Failure percentage being reported incorrectly [\#1006](https://github.com/locustio/locust/issues/1006)
- Start on\_stop not before on\_start has finished [\#969](https://github.com/locustio/locust/issues/969)
- Locust slaves are never become ready and get null responce \(locust 0.9.0\) [\#950](https://github.com/locustio/locust/issues/950)
- Possible typo in docs [\#946](https://github.com/locustio/locust/issues/946)
- New release to PyPi for gevent 1.3 compatibility [\#793](https://github.com/locustio/locust/issues/793)
- Control time window for RPS calculation [\#792](https://github.com/locustio/locust/issues/792)
- 500 URL limit [\#786](https://github.com/locustio/locust/issues/786)
- Save responses to a file [\#774](https://github.com/locustio/locust/issues/774)
- custom client from locust documentation doesn't work at all [\#771](https://github.com/locustio/locust/issues/771)
- separate charts for requests per second and average response time [\#688](https://github.com/locustio/locust/issues/688)
- schedule\_task and data driven load test methodology [\#633](https://github.com/locustio/locust/issues/633)
- stop/interrupt weighting/logic for nested tasks that execute a single task [\#632](https://github.com/locustio/locust/issues/632)
- self interrupt for inline nested TaskSets? [\#631](https://github.com/locustio/locust/issues/631)
- Add new members to Committers Team in the Locust.io Organization [\#628](https://github.com/locustio/locust/issues/628)
- locust's statistic collect N/A records [\#626](https://github.com/locustio/locust/issues/626)
- how to make all locust users wait after executing on\_start method ? [\#611](https://github.com/locustio/locust/issues/611)
- Adding name argument in the http post call with catch response argument [\#608](https://github.com/locustio/locust/issues/608)
- EventHook\(\) fired when locust user has stopped [\#604](https://github.com/locustio/locust/issues/604)
- Is there a way to de-register slave with master on a slave node shutdown? [\#603](https://github.com/locustio/locust/issues/603)
- Unable to Stop locust from Web interface occasionally [\#602](https://github.com/locustio/locust/issues/602)
- no-web performance data saved [\#601](https://github.com/locustio/locust/issues/601)
- Can you add or can I create a Pull Request to accept a command line option that would enable ALL events \(http requests\) to be logged to a file/location? [\#576](https://github.com/locustio/locust/issues/576)
- Median response times off [\#565](https://github.com/locustio/locust/issues/565)
- Dedicated Vuser for each API [\#564](https://github.com/locustio/locust/issues/564)
- 'module' object has no attribute 'NSIG' [\#518](https://github.com/locustio/locust/issues/518)
- running-locust-distributed missing information on worker model [\#492](https://github.com/locustio/locust/issues/492)
- locust executes more number of times than I expected [\#455](https://github.com/locustio/locust/issues/455)
- Cannot pass the arguments to the tasks [\#380](https://github.com/locustio/locust/issues/380)
- Some uncertain for RPS [\#367](https://github.com/locustio/locust/issues/367)
- Support for distributing arbitrary arguments to Locust \[Proposal\] [\#345](https://github.com/locustio/locust/issues/345)
- Error running distributed mode on Fedora and CentOS  [\#271](https://github.com/locustio/locust/issues/271)
- RPS for Total shows the instant RPS [\#262](https://github.com/locustio/locust/issues/262)
- grouping requests after redirect [\#251](https://github.com/locustio/locust/issues/251)
-  Locust can not run distributed with the web interface disabled [\#189](https://github.com/locustio/locust/issues/189)
- Documentation on how to best configure a \(linux\) machine to run locust [\#128](https://github.com/locustio/locust/issues/128)
- See what request generated a failure  [\#103](https://github.com/locustio/locust/issues/103)
- Support for plugins [\#34](https://github.com/locustio/locust/issues/34)

**Merged pull requests:**

- fix self.client call in code examples [\#1123](https://github.com/locustio/locust/pull/1123) ([cyberw](https://github.com/cyberw))
- Escape HTML entities in endpoint names \#374 [\#1119](https://github.com/locustio/locust/pull/1119) ([peterdemin](https://github.com/peterdemin))
- Table layout fix to use available space better [\#1114](https://github.com/locustio/locust/pull/1114) ([heyman](https://github.com/heyman))
- Fix rounding error when spawning users from multiple locust classes [\#1113](https://github.com/locustio/locust/pull/1113) ([heyman](https://github.com/heyman))
- Add \_\_main\_\_.py file [\#1112](https://github.com/locustio/locust/pull/1112) ([jdufresne](https://github.com/jdufresne))
- Remove 'dist: xenial' from Travis configuration [\#1111](https://github.com/locustio/locust/pull/1111) ([jdufresne](https://github.com/jdufresne))
- Add Python 3.8 to the test matrix [\#1110](https://github.com/locustio/locust/pull/1110) ([jdufresne](https://github.com/jdufresne))
- Fix empty bytearray\(b''\) returned when using catch\_response=True [\#1105](https://github.com/locustio/locust/pull/1105) ([skivis](https://github.com/skivis))
- Add an option \(--stop-timeout\) to allow tasks to finish running their iteration before exiting  [\#1099](https://github.com/locustio/locust/pull/1099) ([cyberw](https://github.com/cyberw))
- Allow None response time for requests [\#1088](https://github.com/locustio/locust/pull/1088) ([cyberw](https://github.com/cyberw))
- Fixed issue with Total Requests Per Second plot [\#1060](https://github.com/locustio/locust/pull/1060) ([williamlhunter](https://github.com/williamlhunter))
- Tox: Add flake8 tests to find Python syntax errors and undefined names [\#1039](https://github.com/locustio/locust/pull/1039) ([cclauss](https://github.com/cclauss))
- Fix frontend bugs. [\#822](https://github.com/locustio/locust/pull/822) ([omittones](https://github.com/omittones))
- Switch from using optparse to argparse for command line arguments [\#769](https://github.com/locustio/locust/pull/769) ([jdufresne](https://github.com/jdufresne))
- Allow skipping the logging setup [\#738](https://github.com/locustio/locust/pull/738) ([Exide](https://github.com/Exide))
- Added link to an Ansible role as a 3rd party tool. [\#704](https://github.com/locustio/locust/pull/704) ([tinx](https://github.com/tinx))

## [0.12.1](https://github.com/locustio/locust/tree/0.12.1) (2019-10-18)

[Full Changelog](https://github.com/locustio/locust/compare/0.12.0...0.12.1)

**Fixed bugs:**

- AttributeError: 'module' object has no attribute 'sleep' [\#1023](https://github.com/locustio/locust/issues/1023)

**Closed issues:**

- Throughput \(RPS\) value is not same in Locust WEBUI and http://localhost:8089/stats/requests/csv for same number of requests [\#1108](https://github.com/locustio/locust/issues/1108)
- Disable SSL: CERITIFICATE\_VERIFY\_FAILED [\#1104](https://github.com/locustio/locust/issues/1104)
- How do i control diving into nested tasksets? [\#1097](https://github.com/locustio/locust/issues/1097)

**Merged pull requests:**

- Remove concurrency from coverage [\#1102](https://github.com/locustio/locust/pull/1102) ([mbeacom](https://github.com/mbeacom))
- Adding TCP Keep Alive to guarantee master-slave communication after i… [\#1101](https://github.com/locustio/locust/pull/1101) ([albertowar](https://github.com/albertowar))
- Resolve time import error in exception\_handler [\#1095](https://github.com/locustio/locust/pull/1095) ([ajt89](https://github.com/ajt89))

## [0.12.0](https://github.com/locustio/locust/tree/0.12.0) (2019-10-01)

[Full Changelog](https://github.com/locustio/locust/compare/0.11.1...0.12.0)

**Fixed bugs:**

- response time has too many decimal places in the web statistics page [\#1081](https://github.com/locustio/locust/issues/1081)
- Fail ratio calculation for individual requests is incorrect [\#991](https://github.com/locustio/locust/issues/991)

**Closed issues:**

- Distributed load test k8s and openshift [\#1100](https://github.com/locustio/locust/issues/1100)
- Official docker image does not actually exist [\#1092](https://github.com/locustio/locust/issues/1092)
- Connection Refused for http://localhost:8089/stats/requests  in Locust non web UI mode [\#1086](https://github.com/locustio/locust/issues/1086)
- Sequence does not get past first nested sequence. [\#1080](https://github.com/locustio/locust/issues/1080)
- Support for asynchronous requests [\#1079](https://github.com/locustio/locust/issues/1079)
- Monitoring of server system information being tested [\#1076](https://github.com/locustio/locust/issues/1076)
- Logged stats show incorrect failure percentage [\#1074](https://github.com/locustio/locust/issues/1074)
- Identical exceptions are not aggregated and counted together [\#1073](https://github.com/locustio/locust/issues/1073)
- --no-web -r 1 -c 10 -t 5s  --expect-slaves=1 [\#1071](https://github.com/locustio/locust/issues/1071)
- Is it possible to start all tests in locust immediately?  [\#1070](https://github.com/locustio/locust/issues/1070)
- UI stops updating stats/charts when connection is interupted [\#1068](https://github.com/locustio/locust/issues/1068)
- When running distributed, stop the test if certain condition is met [\#1067](https://github.com/locustio/locust/issues/1067)
- Is it possible to autoscale slaves? [\#1066](https://github.com/locustio/locust/issues/1066)
- docs.locust.io out of date [\#1064](https://github.com/locustio/locust/issues/1064)
- unable to load testing of webmethod \(.asmx\) [\#1061](https://github.com/locustio/locust/issues/1061)
- Distributed master hangs [\#1058](https://github.com/locustio/locust/issues/1058)
- locust swarm can not control the machine over internet [\#1056](https://github.com/locustio/locust/issues/1056)
- Total Requests per Second not plotting [\#1055](https://github.com/locustio/locust/issues/1055)
- No module named 'HTTPLocust' [\#1054](https://github.com/locustio/locust/issues/1054)
- Call wait function in on\_start [\#1053](https://github.com/locustio/locust/issues/1053)
- The locust interface does not start [\#1050](https://github.com/locustio/locust/issues/1050)
- why drop the "-n "prameter after version 0.8 [\#1048](https://github.com/locustio/locust/issues/1048)
- Looking for proxy settings will slow down the default http client [\#1044](https://github.com/locustio/locust/issues/1044)
- Does the statistic data use int type? [\#1043](https://github.com/locustio/locust/issues/1043)
- simplejson.errors.JSONDecodeError: Expecting value: line 1 column 1 \(char 0\) [\#1041](https://github.com/locustio/locust/issues/1041)
- Locust load testing for websites [\#1034](https://github.com/locustio/locust/issues/1034)
- Failure Control [\#1033](https://github.com/locustio/locust/issues/1033)
- Number of users reduce after running for 1min [\#1031](https://github.com/locustio/locust/issues/1031)
- Even with min\_wait and max\_wait == 0, I cannot break 100 requests per second. Why is that? [\#1030](https://github.com/locustio/locust/issues/1030)
- some Strongly expectation of Locust as a Senior performance test engineer [\#1029](https://github.com/locustio/locust/issues/1029)
- The “FAILURES” show on  Web UI is error  [\#1028](https://github.com/locustio/locust/issues/1028)
- Is  there any approach to share a file among hatched users? [\#1022](https://github.com/locustio/locust/issues/1022)
- Does the web UI has authentication? [\#1021](https://github.com/locustio/locust/issues/1021)
- what dose total number means in distribution csv? [\#1019](https://github.com/locustio/locust/issues/1019)
- What does hatch\_rate mean? [\#1018](https://github.com/locustio/locust/issues/1018)
- Multi tenancy? [\#1017](https://github.com/locustio/locust/issues/1017)
- 500 RPS per client limit? [\#1015](https://github.com/locustio/locust/issues/1015)
- locustfile as configmap -\> Could not find any locustfile! Ensure file ends in '.py' [\#1012](https://github.com/locustio/locust/issues/1012)
- Add easy way to use FastHttpLocust [\#1011](https://github.com/locustio/locust/issues/1011)
- Allow custom options to be passed to locust test [\#1010](https://github.com/locustio/locust/issues/1010)
- How to custom the Web UI [\#1009](https://github.com/locustio/locust/issues/1009)
- Run results show tasks action ratio may be incomprehensible。 [\#1003](https://github.com/locustio/locust/issues/1003)
- Start on stop bugged [\#998](https://github.com/locustio/locust/issues/998)
- RPS always lower than User counts [\#997](https://github.com/locustio/locust/issues/997)
- springboot restapi HTTPError 500 [\#996](https://github.com/locustio/locust/issues/996)
- help: I think my result is False? [\#995](https://github.com/locustio/locust/issues/995)
- Website: broken links to ESN and Younited [\#988](https://github.com/locustio/locust/issues/988)
- Request: automatic RPS \ max workers [\#986](https://github.com/locustio/locust/issues/986)
- Multi-threading Tasks? [\#985](https://github.com/locustio/locust/issues/985)
- When time to run \(-t\) timed out, pending requests seems to be aborted, and the \(latest\) responses get lost [\#984](https://github.com/locustio/locust/issues/984)
- error: no commands supplied ....!!!!! [\#983](https://github.com/locustio/locust/issues/983)
- Unable to stop load from web UI with 0.11.0 [\#981](https://github.com/locustio/locust/issues/981)
- Failure events not being recorded  [\#979](https://github.com/locustio/locust/issues/979)
- RPS will become to 0 in distributed mode [\#971](https://github.com/locustio/locust/issues/971)
- Stddev and SEM [\#959](https://github.com/locustio/locust/issues/959)
- ERROR: manifest for locustio/locust:latest not found [\#958](https://github.com/locustio/locust/issues/958)
- support async tasks? [\#924](https://github.com/locustio/locust/issues/924)
- Web UI does not stop slave servers [\#911](https://github.com/locustio/locust/issues/911)
- Request template [\#879](https://github.com/locustio/locust/issues/879)
- Reset failures and/or exceptions [\#826](https://github.com/locustio/locust/issues/826)
- Add support for downloading all failures to a CSV [\#675](https://github.com/locustio/locust/issues/675)
- Locust exits with 1 on timeouts / errors [\#560](https://github.com/locustio/locust/issues/560)
- Why the "RPS" generated by locust is much fewer than other performance testing tools ? [\#277](https://github.com/locustio/locust/issues/277)

**Merged pull requests:**

- Improvements for Dockerfile [\#1093](https://github.com/locustio/locust/pull/1093) ([coderanger](https://github.com/coderanger))
- Using docker multi-stage for 50% smaller image [\#1091](https://github.com/locustio/locust/pull/1091) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Min and max response times rounded to nearest int in web view [\#1089](https://github.com/locustio/locust/pull/1089) ([ajt89](https://github.com/ajt89))
- Allow options to be passed to locust in docker, update docs [\#1083](https://github.com/locustio/locust/pull/1083) ([max-rocket-internet](https://github.com/max-rocket-internet))
- Fix error percentage cli output [\#1082](https://github.com/locustio/locust/pull/1082) ([raiyankamal](https://github.com/raiyankamal))
- Use docker\_start.sh in docker image [\#1078](https://github.com/locustio/locust/pull/1078) ([raiyankamal](https://github.com/raiyankamal))
- drop Python 3.4 support [\#1072](https://github.com/locustio/locust/pull/1072) ([cgoldberg](https://github.com/cgoldberg))
- Typo fix [\#1051](https://github.com/locustio/locust/pull/1051) ([natanlao](https://github.com/natanlao))
- stop looking for proxy settings [\#1046](https://github.com/locustio/locust/pull/1046) ([myzhan](https://github.com/myzhan))
- Use print\(\) function in both Python 2 and Python 3 [\#1038](https://github.com/locustio/locust/pull/1038) ([cclauss](https://github.com/cclauss))
- Travis CI: The sudo tag is now depricated in Travis CI [\#1037](https://github.com/locustio/locust/pull/1037) ([cclauss](https://github.com/cclauss))
- Ensure that the last samples get sent by slave and received by master. [\#1025](https://github.com/locustio/locust/pull/1025) ([cyberw](https://github.com/cyberw))
- Fix grammatical error in statistic reporting [\#1024](https://github.com/locustio/locust/pull/1024) ([MaxVanDeursen](https://github.com/MaxVanDeursen))
- FastHttpLocust [\#1014](https://github.com/locustio/locust/pull/1014) ([skivis](https://github.com/skivis))
- Fix for the examples regarding semaphore\_wait.py [\#1008](https://github.com/locustio/locust/pull/1008) ([ryan-WORK](https://github.com/ryan-WORK))
- Reset exceptions and failures when stats are reset [\#1000](https://github.com/locustio/locust/pull/1000) ([ajt89](https://github.com/ajt89))
- Add failures csv download [\#999](https://github.com/locustio/locust/pull/999) ([ajt89](https://github.com/ajt89))
- Correct fail ratio calculation. Fixes \#991. [\#994](https://github.com/locustio/locust/pull/994) ([genericmoniker](https://github.com/genericmoniker))
- Add command line argument to specify exit code on response errors [\#992](https://github.com/locustio/locust/pull/992) ([Stateford](https://github.com/Stateford))
- Geventhttpclientmergeconflicts [\#838](https://github.com/locustio/locust/pull/838) ([SpencerPinegar](https://github.com/SpencerPinegar))

## [0.11.1](https://github.com/locustio/locust/tree/0.11.1) (2019-03-19)

[Full Changelog](https://github.com/locustio/locust/compare/0.11.0...0.11.1)

**Closed issues:**

- locust master crashes on Python 3.7: AttributeError: 'bytes' object has no attribute 'encode' [\#980](https://github.com/locustio/locust/issues/980)
- Locust can not run in distributed mode in v0.10.0 [\#978](https://github.com/locustio/locust/issues/978)

**Merged pull requests:**

- Add "stopping" state. [\#982](https://github.com/locustio/locust/pull/982) ([solowalker27](https://github.com/solowalker27))

## [0.11.0](https://github.com/locustio/locust/tree/0.11.0) (2019-03-14)

[Full Changelog](https://github.com/locustio/locust/compare/0.10.0...0.11.0)

**Merged pull requests:**

- add retry in zmqrpc [\#973](https://github.com/locustio/locust/pull/973) ([delulu](https://github.com/delulu))
- fix inconsistency in zmqrpc [\#972](https://github.com/locustio/locust/pull/972) ([delulu](https://github.com/delulu))

## [0.10.0](https://github.com/locustio/locust/tree/0.10.0) (2019-03-13)

[Full Changelog](https://github.com/locustio/locust/compare/0.9.0...0.10.0)

**Fixed bugs:**

- filenames with several dots fails [\#940](https://github.com/locustio/locust/issues/940)
- Percentiles rounding error [\#331](https://github.com/locustio/locust/issues/331)

**Closed issues:**

- Installed in virtualenv but locust command not found \(macOS Mojave 10.14\) [\#976](https://github.com/locustio/locust/issues/976)
- how can I send https request  with locust when I already have been authentication.. [\#966](https://github.com/locustio/locust/issues/966)
- How to understand -c when I run locust with no-web mode? [\#965](https://github.com/locustio/locust/issues/965)
- FunctionNotFound\('random\_uuid is not found.',\) [\#964](https://github.com/locustio/locust/issues/964)
- add users 1 time per minute [\#961](https://github.com/locustio/locust/issues/961)
- HttpLocust class instance variable not set for all users during setup [\#957](https://github.com/locustio/locust/issues/957)
- locust.runners.MasterLocustRunner failed with ExtraData [\#956](https://github.com/locustio/locust/issues/956)
- Time limit reached,but test does not stop,throw GreenletExit exception [\#953](https://github.com/locustio/locust/issues/953)
- Bug: Locust master doesn't remove killed slave [\#951](https://github.com/locustio/locust/issues/951)
- How to pass multiple request under same @task. Eg: If I need to pass diferrent key for same get, how to do that? Is parameterization exist? [\#948](https://github.com/locustio/locust/issues/948)
- multiple user behaviour  [\#947](https://github.com/locustio/locust/issues/947)
- seq\_task does not work [\#937](https://github.com/locustio/locust/issues/937)
- locust no-web mode [\#933](https://github.com/locustio/locust/issues/933)
- reqs/sec is much lower than expected [\#931](https://github.com/locustio/locust/issues/931)
- --only-summary does not show the summary results [\#922](https://github.com/locustio/locust/issues/922)
- locust http request size [\#921](https://github.com/locustio/locust/issues/921)
- Retrieving/saving current number of users [\#920](https://github.com/locustio/locust/issues/920)
- OpenVAS - ERROR: \('Connection aborted.', BadStatusLine\("''",\)\) [\#918](https://github.com/locustio/locust/issues/918)
- git changelog page on v0.9.0 return 404 [\#913](https://github.com/locustio/locust/issues/913)
- locust: error: no such option: -n [\#912](https://github.com/locustio/locust/issues/912)
- Next version plans [\#907](https://github.com/locustio/locust/issues/907)
- Need a way for "Device" Locust class to pass a value to the TaskSet [\#906](https://github.com/locustio/locust/issues/906)
- --only-summary does not show the summary results [\#905](https://github.com/locustio/locust/issues/905)
- Locust Report Ui Last column is not displaying [\#903](https://github.com/locustio/locust/issues/903)
- mogul，help me，when i use “sudo pip install locustio”to install， after i use“locust --help”，What should I do if I give an error [\#902](https://github.com/locustio/locust/issues/902)
- Unable to Get Statistics with --csv or Web Mode when running distributed. [\#901](https://github.com/locustio/locust/issues/901)
- Locust slave will not start when attempting to start via Node.js SSH2 connection. [\#900](https://github.com/locustio/locust/issues/900)
- Changelog page in github referenced from docs.locust.io returns a 404  [\#898](https://github.com/locustio/locust/issues/898)
- slave client\_id collisions in large environments [\#894](https://github.com/locustio/locust/issues/894)
- Put a big sign "you must reload this page before any stats are displayed" somewhere on the web interface [\#893](https://github.com/locustio/locust/issues/893)
- Wrong statistic of total request count with 0.9.0 [\#892](https://github.com/locustio/locust/issues/892)
- Questions:  [\#890](https://github.com/locustio/locust/issues/890)
- Strange behavior of "Total Requests per Second" chart [\#888](https://github.com/locustio/locust/issues/888)
- Locust 0.9.0 slave TypeError: \_\_init\_\_\(\) takes exactly 1 argument \(2 given\) [\#887](https://github.com/locustio/locust/issues/887)
- KeyError on weighted tasks [\#886](https://github.com/locustio/locust/issues/886)
- How do I view the maximum concurrency in 1 second during runtime? [\#880](https://github.com/locustio/locust/issues/880)
- locust command is not found on parrot security, even when it is successfully installed [\#878](https://github.com/locustio/locust/issues/878)
- use the FastHttpLocust,how to get cookies ? [\#861](https://github.com/locustio/locust/issues/861)
- Immediate crash under python 3.7 [\#852](https://github.com/locustio/locust/issues/852)
- Release 0.9.0 and document release steps [\#842](https://github.com/locustio/locust/issues/842)
- Extended socket protocol [\#776](https://github.com/locustio/locust/issues/776)
- Feature request: on\_quit\(\) [\#248](https://github.com/locustio/locust/issues/248)

**Merged pull requests:**

- remove references to submitting feature requests [\#975](https://github.com/locustio/locust/pull/975) ([cgoldberg](https://github.com/cgoldberg))
- balance/recover the load distribution when new slave joins [\#970](https://github.com/locustio/locust/pull/970) ([delulu](https://github.com/delulu))
- Ui headings [\#963](https://github.com/locustio/locust/pull/963) ([cgoldberg](https://github.com/cgoldberg))
- better horizontal scrolling [\#962](https://github.com/locustio/locust/pull/962) ([myzhan](https://github.com/myzhan))
- Update change logs & release 0.10.0 [\#960](https://github.com/locustio/locust/pull/960) ([aldenpeterson-wf](https://github.com/aldenpeterson-wf))
- Allow loading of a locustfile with multiple dots in filename [\#941](https://github.com/locustio/locust/pull/941) ([raiyankamal](https://github.com/raiyankamal))
- Both succeeded and failed requests are counted in total number of requests [\#939](https://github.com/locustio/locust/pull/939) ([raiyankamal](https://github.com/raiyankamal))
- Support horizontal scrolling for the stats table [\#938](https://github.com/locustio/locust/pull/938) ([mingrammer](https://github.com/mingrammer))
- Remove repeated imports of mock [\#936](https://github.com/locustio/locust/pull/936) ([Jonnymcc](https://github.com/Jonnymcc))
- Speed up task sequence tests [\#935](https://github.com/locustio/locust/pull/935) ([Jonnymcc](https://github.com/Jonnymcc))
- Add heartbeat to detect down slaves [\#927](https://github.com/locustio/locust/pull/927) ([Jonnymcc](https://github.com/Jonnymcc))
- clarifying locust class usage when no classes specified on CLI [\#925](https://github.com/locustio/locust/pull/925) ([smadness](https://github.com/smadness))
- Include LICENSE in the sdist. [\#919](https://github.com/locustio/locust/pull/919) ([benjaminp](https://github.com/benjaminp))
- fix About link [\#914](https://github.com/locustio/locust/pull/914) ([cgoldberg](https://github.com/cgoldberg))
- Fixed \#903 to allow requests/sec UI column to display. [\#908](https://github.com/locustio/locust/pull/908) ([devmonkey22](https://github.com/devmonkey22))
- Update browse\_docs\_sequence\_test [\#904](https://github.com/locustio/locust/pull/904) ([Realsid](https://github.com/Realsid))
- Use uuid4 to generate slave client\_id [\#895](https://github.com/locustio/locust/pull/895) ([mattbailey](https://github.com/mattbailey))
- Python37 [\#885](https://github.com/locustio/locust/pull/885) ([cgoldberg](https://github.com/cgoldberg))
- Official Docker image and documentation V2 [\#882](https://github.com/locustio/locust/pull/882) ([spayeur207](https://github.com/spayeur207))
- Fix links to changelog in changelog [\#877](https://github.com/locustio/locust/pull/877) ([dmand](https://github.com/dmand))
- Fix Sphinx build warnings [\#875](https://github.com/locustio/locust/pull/875) ([jdufresne](https://github.com/jdufresne))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
