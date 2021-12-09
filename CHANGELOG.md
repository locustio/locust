# Changelog

## [2.5.1](https://github.com/locustio/locust/tree/2.5.1) (2021-12-09)

[Full Changelog](https://github.com/locustio/locust/compare/2.5.0...2.5.1)

**Fixed bugs:**

- User distribution should happen when new workers comes in [\#1884](https://github.com/locustio/locust/issues/1884)

**Merged pull requests:**

- Github changelog generator is broken, so the PR:s will only become visible on the next release

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
- Fix a typo [\#1665](https://github.com/locustio/locust/pull/1665) ([atktng](https://github.com/atktng))
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

## [0.9.0](https://github.com/locustio/locust/tree/0.9.0) (2018-09-01)

[Full Changelog](https://github.com/locustio/locust/compare/v0.8.1...0.9.0)

**Fixed bugs:**

- About displays improperly [\#696](https://github.com/locustio/locust/issues/696)
- Unclear how to interpret numbers [\#303](https://github.com/locustio/locust/issues/303)

**Closed issues:**

- a crash bug for master [\#869](https://github.com/locustio/locust/issues/869)
- I started 50 users, but i found there are 100 tomcat connections established at that time, why.... [\#866](https://github.com/locustio/locust/issues/866)
- Error is raised: AttributeError: 'RequestStats' object has no attribute 'log\_request' [\#865](https://github.com/locustio/locust/issues/865)
- Two locust packages in pypi [\#863](https://github.com/locustio/locust/issues/863)
- Locust "ConnectionError\(ProtocolError\('Connection aborted.', error\(111, 'Connection refused'\)\),\)" [\#862](https://github.com/locustio/locust/issues/862)
- Comparison of performance test results between locust and jmeter [\#859](https://github.com/locustio/locust/issues/859)
- Locust fails to execute from Windows 10 [\#854](https://github.com/locustio/locust/issues/854)
- Assign Locust Behavior Programmatically -- Code Example [\#847](https://github.com/locustio/locust/issues/847)
- Wrong statistic of total request count [\#846](https://github.com/locustio/locust/issues/846)
- Locust freezes after a while \(python 3.7\) [\#843](https://github.com/locustio/locust/issues/843)
- how to send post reqeusts body type is raw [\#840](https://github.com/locustio/locust/issues/840)
- Segmentation Fault \(core dumped\) under python 3.7 [\#839](https://github.com/locustio/locust/issues/839)
- Don't rely on obsolete msgpack-python [\#837](https://github.com/locustio/locust/issues/837)
- how to install locust 0.8 instead locust 0.8.1 hand  [\#834](https://github.com/locustio/locust/issues/834)
- does have url to get the response time distribution? [\#833](https://github.com/locustio/locust/issues/833)
- stats with all zeros for clients \> 1 [\#832](https://github.com/locustio/locust/issues/832)
- setup\(\) should always run after \_\_init\_\_\(\) [\#829](https://github.com/locustio/locust/issues/829)
- How locust calculate average response time and R/S for users [\#828](https://github.com/locustio/locust/issues/828)
- Please check my contribution. [\#824](https://github.com/locustio/locust/issues/824)
- Synthetic monitoring  [\#821](https://github.com/locustio/locust/issues/821)
- Locust slaves eat all available memory when working with a failing service [\#816](https://github.com/locustio/locust/issues/816)
- Using Python's multiprocessing on Master [\#812](https://github.com/locustio/locust/issues/812)
- How to perform basic authentication? [\#811](https://github.com/locustio/locust/issues/811)
- No module named pkg\_resources [\#810](https://github.com/locustio/locust/issues/810)
- Locust does not work because gevent has been updated to 1.3.2 [\#809](https://github.com/locustio/locust/issues/809)
- IndexError: Cannot choose from an empty sequence [\#803](https://github.com/locustio/locust/issues/803)
- self.locust.drop\_current\_runner\(\) [\#802](https://github.com/locustio/locust/issues/802)
- Scraping google search result [\#800](https://github.com/locustio/locust/issues/800)
- branch geventhttpclient need a update [\#795](https://github.com/locustio/locust/issues/795)
- locust inactivity after reaching 9000 user issue [\#791](https://github.com/locustio/locust/issues/791)
- Include LICENSE file in sdist [\#788](https://github.com/locustio/locust/issues/788)
- How to have Locust Master dynamically allocate users to slaves [\#787](https://github.com/locustio/locust/issues/787)
- slave run in docker didn't work. [\#784](https://github.com/locustio/locust/issues/784)
- How to call on\_start before each testcase, like setup in unittest? [\#781](https://github.com/locustio/locust/issues/781)
- Locust clusters, but workers never hatch [\#780](https://github.com/locustio/locust/issues/780)
- When maximum num=1 this will raise exception "Maximum number of requests reached" [\#778](https://github.com/locustio/locust/issues/778)
- 100% number smaller than 99% in Percentage of the requests completed within given times [\#777](https://github.com/locustio/locust/issues/777)
- Can't define unique characteristics for each locust [\#775](https://github.com/locustio/locust/issues/775)
- invaild Locust\(HttpLocust\) class attribute: host [\#773](https://github.com/locustio/locust/issues/773)
- URL requests containing “/\#/” are all seen as “/” then failing when running on Locust.io [\#768](https://github.com/locustio/locust/issues/768)
- Docker image and Kubernetes chart out of date at 0.7.5 [\#767](https://github.com/locustio/locust/issues/767)
- Wrong tasks weight calculation over several TaskSet's [\#766](https://github.com/locustio/locust/issues/766)
- Need multi level rampup pattern  [\#765](https://github.com/locustio/locust/issues/765)
- Documentation link at https://docs.locust.io doesn't point to current release docs [\#764](https://github.com/locustio/locust/issues/764)
- website down [\#763](https://github.com/locustio/locust/issues/763)
- TypeError: must be string or buffer, not None [\#754](https://github.com/locustio/locust/issues/754)
- Does POST request create a entry in the DB? [\#752](https://github.com/locustio/locust/issues/752)
- SSL Error when using Http Request [\#751](https://github.com/locustio/locust/issues/751)
- print statements are not appearing on console when -n is 1 [\#750](https://github.com/locustio/locust/issues/750)
- Error - Get\_next\_task return random.choice\(self.tasks\) and Random.py choice raise IndexError\('Cannot choose from an empty sequence'\) from None\) [\#748](https://github.com/locustio/locust/issues/748)
- Default implementation of on\_request\_success and \_failure lacks \*\*kwargs declaration [\#745](https://github.com/locustio/locust/issues/745)
- Question: https://pypi.python.org/pypi/locust/0.8 [\#744](https://github.com/locustio/locust/issues/744)
- Not able to record failures in report [\#739](https://github.com/locustio/locust/issues/739)
- Tested website unresponsive [\#737](https://github.com/locustio/locust/issues/737)
- New Connection in locust [\#736](https://github.com/locustio/locust/issues/736)
- Does locust creates a new instance/thread per locust user of httplocust class ? [\#734](https://github.com/locustio/locust/issues/734)
- How I share auth cookie with the rest of tasks only for current locust user? [\#733](https://github.com/locustio/locust/issues/733)
- how to run the master branch [\#732](https://github.com/locustio/locust/issues/732)
- On the same server，jmeter can run 20000rps，but locust only 5000rps [\#727](https://github.com/locustio/locust/issues/727)
- Connect slave nodes from remote server to master node on local machine [\#726](https://github.com/locustio/locust/issues/726)
- a report plugin.Anyone interested? [\#723](https://github.com/locustio/locust/issues/723)
- Severe difference in RPS when adding more than two URLs  [\#722](https://github.com/locustio/locust/issues/722)
- Start distributed test with multiple slaves with one command. [\#721](https://github.com/locustio/locust/issues/721)
- Logo changes [\#716](https://github.com/locustio/locust/issues/716)
- Locust does not count RPS if all requests fails [\#715](https://github.com/locustio/locust/issues/715)
- Looking for a different flavor of on\_start\(\) behavior [\#714](https://github.com/locustio/locust/issues/714)
- Option to Print Failure to Console? [\#711](https://github.com/locustio/locust/issues/711)
- Reach to 3k RPS [\#710](https://github.com/locustio/locust/issues/710)
- Rename RPS [\#709](https://github.com/locustio/locust/issues/709)
- AWS locust sitting idle  [\#707](https://github.com/locustio/locust/issues/707)
- Couldn't pass 200 request / second [\#705](https://github.com/locustio/locust/issues/705)
- Preparing a Linux server for Locust load tests [\#700](https://github.com/locustio/locust/issues/700)
- When a slave process crashes and restarts, the master counts and waits for input from both [\#699](https://github.com/locustio/locust/issues/699)
- SQL Locust adapter [\#691](https://github.com/locustio/locust/issues/691)
- Unusual behavior from graphs [\#690](https://github.com/locustio/locust/issues/690)
- Chart is wrong [\#689](https://github.com/locustio/locust/issues/689)
- ioerror cannot watch more than 1024 sockets [\#684](https://github.com/locustio/locust/issues/684)
- Locust distributed noweb does not honour --num-request option [\#682](https://github.com/locustio/locust/issues/682)
- Locust pure python RPC not working in distributed mode \(this makes, message seem confusing\) [\#680](https://github.com/locustio/locust/issues/680)
- Limit of 500 requests in /stats/requests end-point [\#679](https://github.com/locustio/locust/issues/679)
- No users count send in hatch\_complete [\#678](https://github.com/locustio/locust/issues/678)
- --no-reset-stats should be on by default  [\#672](https://github.com/locustio/locust/issues/672)
- 'Response' object has no attribute 'failure' in python3.5.3 [\#671](https://github.com/locustio/locust/issues/671)
- Sometimes the rps is 0 [\#670](https://github.com/locustio/locust/issues/670)
- Install breaks on Win7 Py3.3 Locust 0.8.1 [\#668](https://github.com/locustio/locust/issues/668)
- Inaccurate response time? [\#663](https://github.com/locustio/locust/issues/663)
- all tests results suddenly turned to all 0 [\#662](https://github.com/locustio/locust/issues/662)
- How do we control the Clients in Locust? [\#659](https://github.com/locustio/locust/issues/659)
-  failure to install the latest version locust [\#648](https://github.com/locustio/locust/issues/648)
- Always get errors when I run testing. [\#645](https://github.com/locustio/locust/issues/645)
- Locust test results [\#639](https://github.com/locustio/locust/issues/639)
- memory issue [\#636](https://github.com/locustio/locust/issues/636)
- Stderr connection error \( python3.6\), but no failures on UI [\#625](https://github.com/locustio/locust/issues/625)
- Ability to disable SSL certificate verify [\#619](https://github.com/locustio/locust/issues/619)
- tasks are not shown in locust UI statistics [\#591](https://github.com/locustio/locust/issues/591)
- Installation failure on Mac OS 10.12.4 [\#582](https://github.com/locustio/locust/issues/582)
- Specify host header and send request against IP [\#581](https://github.com/locustio/locust/issues/581)
- Ability to set a specific number of simulated users per Locust class [\#575](https://github.com/locustio/locust/issues/575)
- Slave hangs when started before master [\#571](https://github.com/locustio/locust/issues/571)
- Is there a way to setup/teardown before running the load tests [\#553](https://github.com/locustio/locust/issues/553)
- Never loads? [\#302](https://github.com/locustio/locust/issues/302)
- Retrieving stats when running with --no-web [\#290](https://github.com/locustio/locust/issues/290)
- In distributed mode, not all stats are collected/displayed in the 'main' UI  [\#217](https://github.com/locustio/locust/issues/217)
- URL\_PREFIX feature for web UI? [\#149](https://github.com/locustio/locust/issues/149)
- \(libev\) select: Invalid argument when trying to go past 1k users [\#121](https://github.com/locustio/locust/issues/121)
- Command line option to specify the duration to run [\#71](https://github.com/locustio/locust/issues/71)
- Setup/teardown hooks [\#59](https://github.com/locustio/locust/issues/59)
- Define wait times by function instead of variable [\#18](https://github.com/locustio/locust/issues/18)

**Merged pull requests:**

- update Makefile so build also creates a wheel [\#871](https://github.com/locustio/locust/pull/871) ([cgoldberg](https://github.com/cgoldberg))
- Fix deprecation warnings [\#870](https://github.com/locustio/locust/pull/870) ([cgoldberg](https://github.com/cgoldberg))
- Release 0.9.0 [\#867](https://github.com/locustio/locust/pull/867) ([aldenpeterson-wf](https://github.com/aldenpeterson-wf))
- Separate release into build and release steps [\#858](https://github.com/locustio/locust/pull/858) ([hoylemd](https://github.com/hoylemd))
- Install instructions [\#857](https://github.com/locustio/locust/pull/857) ([cgoldberg](https://github.com/cgoldberg))
- Specify seconds for the `timeout` parameter [\#856](https://github.com/locustio/locust/pull/856) ([hoylemd](https://github.com/hoylemd))
- bump dev version to 0.9.0.dev0 [\#855](https://github.com/locustio/locust/pull/855) ([cgoldberg](https://github.com/cgoldberg))
- Change name of msgpack dependency. [\#841](https://github.com/locustio/locust/pull/841) ([vamega](https://github.com/vamega))
- response time doesn't need to be cast to int, as this is implicit in … [\#830](https://github.com/locustio/locust/pull/830) ([efology](https://github.com/efology))
- Add tasks sequence support [\#827](https://github.com/locustio/locust/pull/827) ([Ramshell](https://github.com/Ramshell))
- Fix some typos in events.py [\#820](https://github.com/locustio/locust/pull/820) ([felixonmars](https://github.com/felixonmars))
- Update all pypi.python.org URLs to pypi.org [\#818](https://github.com/locustio/locust/pull/818) ([jdufresne](https://github.com/jdufresne))
- Update third-party-tools.rst [\#808](https://github.com/locustio/locust/pull/808) ([anhldbk](https://github.com/anhldbk))
- Remove unused nosetest settings [\#806](https://github.com/locustio/locust/pull/806) ([cgoldberg](https://github.com/cgoldberg))
- Drop Python 3.3 support [\#804](https://github.com/locustio/locust/pull/804) ([ps-george](https://github.com/ps-george))
- docs: Syntax highlight code and commands [\#797](https://github.com/locustio/locust/pull/797) ([joar](https://github.com/joar))
- Added user-defined wait\_function to locust and TaskSet [\#785](https://github.com/locustio/locust/pull/785) ([ps-george](https://github.com/ps-george))
- Remove compatibility workarounds for Python 2.6 [\#770](https://github.com/locustio/locust/pull/770) ([jdufresne](https://github.com/jdufresne))
- Enable pip cache in Travis CI [\#760](https://github.com/locustio/locust/pull/760) ([jdufresne](https://github.com/jdufresne))
- Use https:// URLs where available [\#758](https://github.com/locustio/locust/pull/758) ([jdufresne](https://github.com/jdufresne))
- Distribute package as a universal wheel [\#756](https://github.com/locustio/locust/pull/756) ([jdufresne](https://github.com/jdufresne))
- Docs: update test statistics page with example responses [\#747](https://github.com/locustio/locust/pull/747) ([aldenpeterson-wf](https://github.com/aldenpeterson-wf))
- Introduce \*\*kwargs to request\_success/failure parameter list [\#746](https://github.com/locustio/locust/pull/746) ([karol-brejna-i](https://github.com/karol-brejna-i))
- Change Locust website url to https [\#743](https://github.com/locustio/locust/pull/743) ([iassal](https://github.com/iassal))
- Fix typo in docstring [\#729](https://github.com/locustio/locust/pull/729) ([giantryansaul](https://github.com/giantryansaul))
- Changed the spelling of "occurences" on the output text [\#706](https://github.com/locustio/locust/pull/706) ([ethansmith-wf](https://github.com/ethansmith-wf))
- Merge 0.8 branch. [\#701](https://github.com/locustio/locust/pull/701) ([mbeacom](https://github.com/mbeacom))
- added introduction to Locust4j [\#698](https://github.com/locustio/locust/pull/698) ([myzhan](https://github.com/myzhan))
- Resolve improper display of About in Web UI [\#697](https://github.com/locustio/locust/pull/697) ([mbeacom](https://github.com/mbeacom))
- Make UI URL links relative [\#692](https://github.com/locustio/locust/pull/692) ([karol-brejna-i](https://github.com/karol-brejna-i))
- Small python 3 syntax improvement in docs [\#676](https://github.com/locustio/locust/pull/676) ([miki725](https://github.com/miki725))
- \#331:  Use rounded\_response\_time for min/max/total response times [\#558](https://github.com/locustio/locust/pull/558) ([jude](https://github.com/jude))
- Refactored stats code and display median as well as 95% percentile response times in web UI's charts [\#549](https://github.com/locustio/locust/pull/549) ([heyman](https://github.com/heyman))
- Added a slaves-tab to show the id, status and number of users running on each slave. [\#305](https://github.com/locustio/locust/pull/305) ([TZer0](https://github.com/TZer0))
- expand and re-order documentation index [\#779](https://github.com/locustio/locust/pull/779) ([cgoldberg](https://github.com/cgoldberg))
- drop unitt2 and use tox in 'make test' target [\#772](https://github.com/locustio/locust/pull/772) ([cgoldberg](https://github.com/cgoldberg))
- Fix bytes/text confusion with response objects [\#762](https://github.com/locustio/locust/pull/762) ([jdufresne](https://github.com/jdufresne))
- Remove unused environment variables form tox configuration [\#761](https://github.com/locustio/locust/pull/761) ([jdufresne](https://github.com/jdufresne))
- Update tox.ini so as to not respecify package dependency pyzmq [\#757](https://github.com/locustio/locust/pull/757) ([jdufresne](https://github.com/jdufresne))
- Remove test dependency unittest2 [\#755](https://github.com/locustio/locust/pull/755) ([jdufresne](https://github.com/jdufresne))
- Adding unit to Response Time chart [\#742](https://github.com/locustio/locust/pull/742) ([albertowar](https://github.com/albertowar))
- Use flask.jsonify for json responses [\#725](https://github.com/locustio/locust/pull/725) ([hyperair](https://github.com/hyperair))
- fix error message on invalid time format [\#717](https://github.com/locustio/locust/pull/717) ([cgoldberg](https://github.com/cgoldberg))
- Add codecov integration [\#687](https://github.com/locustio/locust/pull/687) ([mbeacom](https://github.com/mbeacom))
- Do not reset statistics on hatch complete  [\#674](https://github.com/locustio/locust/pull/674) ([hhowe29](https://github.com/hhowe29))
- Adds support for setup, teardown, and on\_stop methods [\#658](https://github.com/locustio/locust/pull/658) ([DeepHorizons](https://github.com/DeepHorizons))
- Remove --num-requests/-n in favor of --run-time/-t [\#656](https://github.com/locustio/locust/pull/656) ([heyman](https://github.com/heyman))

## [v0.8.1](https://github.com/locustio/locust/tree/v0.8.1) (2017-09-19)

[Full Changelog](https://github.com/locustio/locust/compare/v0.8...v0.8.1)

**Closed issues:**

- Release new Locust version [\#657](https://github.com/locustio/locust/issues/657)
- make test is failing on 0.7 tags due to Flask 0.12 [\#637](https://github.com/locustio/locust/issues/637)
- num-requests bug [\#512](https://github.com/locustio/locust/issues/512)
- Run the tests for the specified time [\#196](https://github.com/locustio/locust/issues/196)
- Remove support for plain sockets for master/slave communication [\#14](https://github.com/locustio/locust/issues/14)

## [v0.8](https://github.com/locustio/locust/tree/v0.8) (2017-09-19)

[Full Changelog](https://github.com/locustio/locust/compare/v0.8a3...v0.8)

**Closed issues:**

- Infinite recursion error when testing https sites [\#655](https://github.com/locustio/locust/issues/655)
- website SSL [\#644](https://github.com/locustio/locust/issues/644)
- Using locust to query Cassandra [\#569](https://github.com/locustio/locust/issues/569)

**Merged pull requests:**

- find locustfile in the root directory [\#609](https://github.com/locustio/locust/pull/609) ([arthurdarcet](https://github.com/arthurdarcet))

## [v0.8a3](https://github.com/locustio/locust/tree/v0.8a3) (2017-09-15)

[Full Changelog](https://github.com/locustio/locust/compare/v0.8a1...v0.8a3)

**Fixed bugs:**

- Web UI bug when url is very long [\#555](https://github.com/locustio/locust/issues/555)
- gevent.hub.LoopExit exeption, python threading and twisted reactor [\#397](https://github.com/locustio/locust/issues/397)
- OpenSSL handshake error [\#396](https://github.com/locustio/locust/issues/396)
- sending POST image in client.post\(\) never receives Request.FILES [\#364](https://github.com/locustio/locust/issues/364)
- Some of the requets total stats are missing when printing them to console [\#350](https://github.com/locustio/locust/issues/350)
- Web UI Freezing [\#309](https://github.com/locustio/locust/issues/309)
- Template request name too long  [\#263](https://github.com/locustio/locust/issues/263)
- Test file can not be named locust.py \(or any other name that is the same as an existing python package\) [\#138](https://github.com/locustio/locust/issues/138)
- Prohibits the locustfile from being named 'locust.py' [\#546](https://github.com/locustio/locust/pull/546) ([cgoldberg](https://github.com/cgoldberg))
- Truncate number of errors displayed in the web UI [\#532](https://github.com/locustio/locust/pull/532) ([justiniso](https://github.com/justiniso))

**Closed issues:**

- Move Locust to the Erlang BEAM [\#653](https://github.com/locustio/locust/issues/653)
- Libev over libevent and gevent suggested wsgi? [\#649](https://github.com/locustio/locust/issues/649)
- How to filter certain requests when generating reports? [\#647](https://github.com/locustio/locust/issues/647)
- Can't find new charts in v0.8a2 [\#643](https://github.com/locustio/locust/issues/643)
- Have anyone tried setting up locust on Azure scale set ? [\#642](https://github.com/locustio/locust/issues/642)
- Issue with indendation on a PUT request \(Newbie\)  [\#641](https://github.com/locustio/locust/issues/641)
- How to know why the server is down ? [\#640](https://github.com/locustio/locust/issues/640)
- Locust throwing connection error failures  [\#638](https://github.com/locustio/locust/issues/638)
- Can't run test via locust command line [\#635](https://github.com/locustio/locust/issues/635)
- ImportError if there is a "core" module in project [\#630](https://github.com/locustio/locust/issues/630)
- ModuleNotFoundError in Python 3.6 OSX 10.12 [\#627](https://github.com/locustio/locust/issues/627)
- the edit has bugs in distributed mode [\#623](https://github.com/locustio/locust/issues/623)
- No Locust class found [\#621](https://github.com/locustio/locust/issues/621)
- Display website on dashboard [\#620](https://github.com/locustio/locust/issues/620)
- Latest 0.8a2 version build doesn't meet changelog [\#618](https://github.com/locustio/locust/issues/618)
- locust doesn't record all the requests [\#615](https://github.com/locustio/locust/issues/615)
- Question: debugging in pycharm \(or other arbitrary IDE\) [\#613](https://github.com/locustio/locust/issues/613)
- Summary shows 0 when request\(num\_request\) completed before all users get hatched [\#610](https://github.com/locustio/locust/issues/610)
- Unable to run the locustfile example  [\#607](https://github.com/locustio/locust/issues/607)
- How many locust-workers can I add to a locust-master? [\#605](https://github.com/locustio/locust/issues/605)
- Distributed mode question/concern [\#600](https://github.com/locustio/locust/issues/600)
- bump gevent version [\#598](https://github.com/locustio/locust/issues/598)
- unlimited users [\#597](https://github.com/locustio/locust/issues/597)
- Windows Authentication support? [\#595](https://github.com/locustio/locust/issues/595)
- Non-200 i.e. 202 status codes are note logged as successes [\#594](https://github.com/locustio/locust/issues/594)
- Running locust tests as a list of scenarios [\#590](https://github.com/locustio/locust/issues/590)
- Port locust.io to HTTPS [\#589](https://github.com/locustio/locust/issues/589)
- reqs/sec is lower than other tools result [\#586](https://github.com/locustio/locust/issues/586)
- Inform users about unsuccessful POST requests [\#585](https://github.com/locustio/locust/issues/585)
- HttpSession can't handle HTTP 301 with Location: `https,https://` [\#584](https://github.com/locustio/locust/issues/584)
- Not have option --no-reset-stats [\#583](https://github.com/locustio/locust/issues/583)
- ModuleNotFoundError: No module named 'cobra.core.model' in python3 [\#580](https://github.com/locustio/locust/issues/580)
- Summary result [\#578](https://github.com/locustio/locust/issues/578)
- OSX limited to running ~200 users [\#574](https://github.com/locustio/locust/issues/574)
- How to create multiple task\_set in http locust class? [\#573](https://github.com/locustio/locust/issues/573)
- ImportError: No module named 'core - Python 3.5.0, 3.5.2 [\#572](https://github.com/locustio/locust/issues/572)
- Successfully installed but locust command not found on macOS Sierra 10.12 [\#568](https://github.com/locustio/locust/issues/568)
- How to stop once a user finishes it's set of Tasks. [\#567](https://github.com/locustio/locust/issues/567)
- rendezvous implementation of Locust? [\#563](https://github.com/locustio/locust/issues/563)
- Missing not reset stats option. [\#562](https://github.com/locustio/locust/issues/562)
- Is there a way to share data among emmulated users? [\#561](https://github.com/locustio/locust/issues/561)
- locust run in windows 10 ,error: failed to create process [\#559](https://github.com/locustio/locust/issues/559)
- 【Question】"Address family not supported by protocol" when start the test [\#556](https://github.com/locustio/locust/issues/556)
- Where to find the RPS chart? [\#554](https://github.com/locustio/locust/issues/554)
- request: bandwidth consumption [\#551](https://github.com/locustio/locust/issues/551)
- self.\_sleep\(\) should not be private. [\#550](https://github.com/locustio/locust/issues/550)
- MQTT with python over proxy [\#548](https://github.com/locustio/locust/issues/548)
- "Connection reset by peer"  failure When doing local test with lost \( \>1000\) concurent users [\#545](https://github.com/locustio/locust/issues/545)
- How to monitor cpu and memory? [\#544](https://github.com/locustio/locust/issues/544)
- Stress test with probobuf format? [\#543](https://github.com/locustio/locust/issues/543)
- Setting a CookieJar [\#542](https://github.com/locustio/locust/issues/542)
- Bugs in show\_task\_ratio and show\_task\_ratio\_json [\#540](https://github.com/locustio/locust/issues/540)
- Incorrect calculation of avg\_response\_time and current\_rps in no\_web mode [\#538](https://github.com/locustio/locust/issues/538)
- Release for 0.8.0 [\#533](https://github.com/locustio/locust/issues/533)
- No module named 'core' error [\#531](https://github.com/locustio/locust/issues/531)
- on\_start function calls for every hatch [\#529](https://github.com/locustio/locust/issues/529)
- Add Python 3.6 to build pipeline [\#527](https://github.com/locustio/locust/issues/527)
- Python v2 exception on import ipdb - StdOutWrapper has no attribute 'flush' [\#526](https://github.com/locustio/locust/issues/526)
- SSL error:self signed certificate [\#524](https://github.com/locustio/locust/issues/524)
- How to use locust? [\#522](https://github.com/locustio/locust/issues/522)
- Sending multipart/form-data   [\#521](https://github.com/locustio/locust/issues/521)
- How to display QOS metrics ? [\#520](https://github.com/locustio/locust/issues/520)
- Allow importing swagger files [\#519](https://github.com/locustio/locust/issues/519)
- stats & counters are reset during test [\#513](https://github.com/locustio/locust/issues/513)
- slack channel for locust dev [\#511](https://github.com/locustio/locust/issues/511)
- Variance/Standard Dev. or something [\#508](https://github.com/locustio/locust/issues/508)
- RPS value drops after a long run [\#507](https://github.com/locustio/locust/issues/507)
- raise an error in Python3 [\#506](https://github.com/locustio/locust/issues/506)
- Function result does not get saved into variable if function call spans two lines [\#505](https://github.com/locustio/locust/issues/505)
- calling taskset and tasks on if else conditions [\#504](https://github.com/locustio/locust/issues/504)
- pip install old version [\#502](https://github.com/locustio/locust/issues/502)
- Documentation for directory structure and working directory for complex locust projects [\#500](https://github.com/locustio/locust/issues/500)
- pydoc.locate breaks after importing locust [\#499](https://github.com/locustio/locust/issues/499)
- How to build locust on local machine  [\#498](https://github.com/locustio/locust/issues/498)
- Secure data transfer between master/slave in different geographical regions [\#491](https://github.com/locustio/locust/issues/491)
- Closing old issues and PRs [\#490](https://github.com/locustio/locust/issues/490)
- Proposal: apdex in reports [\#489](https://github.com/locustio/locust/issues/489)
- Problem with nested dictionary [\#488](https://github.com/locustio/locust/issues/488)
- \[question\] how do you quantify your master/slave need [\#486](https://github.com/locustio/locust/issues/486)
- user spawn too slow [\#482](https://github.com/locustio/locust/issues/482)
- Overly strict dependency on gevent==1.1.1 [\#479](https://github.com/locustio/locust/issues/479)
- Unique user id per locust [\#476](https://github.com/locustio/locust/issues/476)
- Random Resets and Invalid Stats [\#446](https://github.com/locustio/locust/issues/446)
- SSL errors when testing certain HTTPS sites [\#417](https://github.com/locustio/locust/issues/417)
- How to get more info from the load test? [\#413](https://github.com/locustio/locust/issues/413)
- Export exceptions to CSV didn't work [\#412](https://github.com/locustio/locust/issues/412)
- Replaying access pattern [\#411](https://github.com/locustio/locust/issues/411)
- Make logging timestamps etc optional [\#405](https://github.com/locustio/locust/issues/405)
- The pycurl client [\#393](https://github.com/locustio/locust/issues/393)
- Working with long running user flows [\#386](https://github.com/locustio/locust/issues/386)
- cookies [\#373](https://github.com/locustio/locust/issues/373)
- How to understand the requests in main webui? [\#370](https://github.com/locustio/locust/issues/370)
- Test performance of predictionio [\#369](https://github.com/locustio/locust/issues/369)
- Reviewing PRs [\#355](https://github.com/locustio/locust/issues/355)
- Optional HTTP Request failure step down [\#344](https://github.com/locustio/locust/issues/344)
- Unix timestamp in stats/requests [\#332](https://github.com/locustio/locust/issues/332)
- Web UI Freezing [\#307](https://github.com/locustio/locust/issues/307)
- Inconsistent stats resetting [\#299](https://github.com/locustio/locust/issues/299)
- Don't warn about pure Python socket when not using distributed mode [\#276](https://github.com/locustio/locust/issues/276)
- Web UI should show what host is being used [\#270](https://github.com/locustio/locust/issues/270)
- locust support testing against HTTP/2 servers ? [\#264](https://github.com/locustio/locust/issues/264)
- Error to login to webapp in Locust [\#246](https://github.com/locustio/locust/issues/246)
- Support for custom time metrics [\#243](https://github.com/locustio/locust/issues/243)
- recommended AWS EC2 instance types? [\#242](https://github.com/locustio/locust/issues/242)
- how to deploy it in heroku or aws ? [\#241](https://github.com/locustio/locust/issues/241)
- How to retrieve host argument for custom client [\#238](https://github.com/locustio/locust/issues/238)
- Extra / at start of request paths [\#235](https://github.com/locustio/locust/issues/235)
- SSL broken on Python 2.7.9 [\#234](https://github.com/locustio/locust/issues/234)
- Parameterizing each Locust on a distributed load test [\#233](https://github.com/locustio/locust/issues/233)
- Suggest Python version  [\#231](https://github.com/locustio/locust/issues/231)
- Be able to define bursty traffic  [\#225](https://github.com/locustio/locust/issues/225)
- How to serve templates for custom routes ? [\#224](https://github.com/locustio/locust/issues/224)
- Changing locustfile.py on master via UI and having  master / slave replication [\#209](https://github.com/locustio/locust/issues/209)
- Option to prevent stats from being reset when all locusts are hatched [\#205](https://github.com/locustio/locust/issues/205)
- PUT requests are shown as GET [\#204](https://github.com/locustio/locust/issues/204)
- Cannot simulate one single user [\#178](https://github.com/locustio/locust/issues/178)
- Feature request: Stepped hatch rate [\#168](https://github.com/locustio/locust/issues/168)
- Having a locust "die" or stop after one task [\#161](https://github.com/locustio/locust/issues/161)
- Request: support concurrent and hatch for web-based startups [\#153](https://github.com/locustio/locust/issues/153)
- Run individual tasks at the same time [\#151](https://github.com/locustio/locust/issues/151)
- Graphical interface to see individual request level graph [\#144](https://github.com/locustio/locust/issues/144)
- Configure target host from web interface [\#135](https://github.com/locustio/locust/issues/135)
- Fixed seed, non-random chance [\#127](https://github.com/locustio/locust/issues/127)
- any objection to making  task take a float as opposed to an int? [\#119](https://github.com/locustio/locust/issues/119)
- Feature request: "run through" each test once. [\#98](https://github.com/locustio/locust/issues/98)
- Add Timer / Timers to Web Interface [\#78](https://github.com/locustio/locust/issues/78)
- Recording of rps over time [\#32](https://github.com/locustio/locust/issues/32)
- Add date when test started to run [\#30](https://github.com/locustio/locust/issues/30)
- Make the table header in the web interface sticky [\#2](https://github.com/locustio/locust/issues/2)

**Merged pull requests:**

- Bump version to 0.8a3 for another pre-release candidate [\#654](https://github.com/locustio/locust/pull/654) ([aldenpeterson-wf](https://github.com/aldenpeterson-wf))
- Standardize utf8 file coding declarations [\#652](https://github.com/locustio/locust/pull/652) ([mbeacom](https://github.com/mbeacom))
- Sort all Python imports [\#651](https://github.com/locustio/locust/pull/651) ([mbeacom](https://github.com/mbeacom))
- Modify gevent wsgi and libev dependencies [\#650](https://github.com/locustio/locust/pull/650) ([mbeacom](https://github.com/mbeacom))
- Add GH issue template and update readme [\#614](https://github.com/locustio/locust/pull/614) ([aldenpeterson-wf](https://github.com/aldenpeterson-wf))
- Add ability to write csv stats files   [\#612](https://github.com/locustio/locust/pull/612) ([aldenpeterson-wf](https://github.com/aldenpeterson-wf))
- Fix spelling error in README.md [\#606](https://github.com/locustio/locust/pull/606) ([fiso](https://github.com/fiso))
- Bump gevent version [\#599](https://github.com/locustio/locust/pull/599) ([ed1d1a8d](https://github.com/ed1d1a8d))
- Fix formatting issue combining double dashes into single dash [\#577](https://github.com/locustio/locust/pull/577) ([swoodford](https://github.com/swoodford))
- Add slack signup link to readme [\#570](https://github.com/locustio/locust/pull/570) ([aldenpeterson-wf](https://github.com/aldenpeterson-wf))
- Fix off by 1 error in stats.py resulting in additional request always being off [\#566](https://github.com/locustio/locust/pull/566) ([aldenpeterson-wf](https://github.com/aldenpeterson-wf))
- Add more formatting and class links to quickstart page. [\#557](https://github.com/locustio/locust/pull/557) ([alimony](https://github.com/alimony))
- Remove unused imports [\#552](https://github.com/locustio/locust/pull/552) ([mbeacom](https://github.com/mbeacom))
- Update installation doc with supported py versions [\#547](https://github.com/locustio/locust/pull/547) ([mirskiy](https://github.com/mirskiy))
- Started working on a more modern and \(hopefully\) better looking design [\#541](https://github.com/locustio/locust/pull/541) ([heyman](https://github.com/heyman))
- Styling of charts + only show charts for total stats + clean up & refactoring of charts JS code [\#539](https://github.com/locustio/locust/pull/539) ([heyman](https://github.com/heyman))
- Add units to table [\#537](https://github.com/locustio/locust/pull/537) ([benrudolph](https://github.com/benrudolph))
- Web UI: Free up header space [\#534](https://github.com/locustio/locust/pull/534) ([justiniso](https://github.com/justiniso))
- Python 3.6 [\#528](https://github.com/locustio/locust/pull/528) ([mbeacom](https://github.com/mbeacom))
- seems sane to not support py26 anymore [\#515](https://github.com/locustio/locust/pull/515) ([ticosax](https://github.com/ticosax))
- Added introduction of Boomer [\#510](https://github.com/locustio/locust/pull/510) ([myzhan](https://github.com/myzhan))
- Add charts for RPS and average response time in the WebUI [\#509](https://github.com/locustio/locust/pull/509) ([myzhan](https://github.com/myzhan))
- docs: clarify locust invocation norms [\#501](https://github.com/locustio/locust/pull/501) ([pwnage101](https://github.com/pwnage101))
- Improve the language in writing-a-locustfile.rst [\#470](https://github.com/locustio/locust/pull/470) ([aknuds1](https://github.com/aknuds1))
- Adds host name to the header [\#447](https://github.com/locustio/locust/pull/447) ([thaffenden](https://github.com/thaffenden))
- Allow --no-web together with --master for automation [\#333](https://github.com/locustio/locust/pull/333) ([undera](https://github.com/undera))

## [v0.8a1](https://github.com/locustio/locust/tree/v0.8a1) (2016-11-24)

[Full Changelog](https://github.com/locustio/locust/compare/v0.7.5...v0.8a1)

**Closed issues:**

- Header not entirely on camel case [\#503](https://github.com/locustio/locust/issues/503)
- Locust starts throwing failures when users \> 130 \(OS X\) [\#496](https://github.com/locustio/locust/issues/496)
- Multiple Locust swarms override each-others stats [\#493](https://github.com/locustio/locust/issues/493)
- loop\(\) got unexpected keyword argument [\#485](https://github.com/locustio/locust/issues/485)
- Problems installing on Mac 10.11.6 [\#483](https://github.com/locustio/locust/issues/483)
- Cannot decode 502 [\#481](https://github.com/locustio/locust/issues/481)
- Locust can not count failure request number in WEB GUI [\#480](https://github.com/locustio/locust/issues/480)
- 【Question】How locust allocate the user number with distributed mode? [\#478](https://github.com/locustio/locust/issues/478)
- Python v3 error: 'StdOutWrapper' object has no attribute 'flush' [\#475](https://github.com/locustio/locust/issues/475)
- \[Question\] How can I set up a thousand concurrent http server as soon as possible with python? [\#473](https://github.com/locustio/locust/issues/473)
- \[Question\] How can I control the speed of sending requests? [\#472](https://github.com/locustio/locust/issues/472)
- Get exception during simulating 5000 users on one mechine [\#471](https://github.com/locustio/locust/issues/471)
- 【Question】Can I make request with python requests lib? [\#469](https://github.com/locustio/locust/issues/469)
- 【Question】How can I send https request with locust? [\#468](https://github.com/locustio/locust/issues/468)
- 401 Unauthorized Error using HTTPLocust [\#466](https://github.com/locustio/locust/issues/466)
- Import issue when the locustfile.py contains importing self-defined class sentence [\#465](https://github.com/locustio/locust/issues/465)
- Embedded html resources [\#464](https://github.com/locustio/locust/issues/464)
- Could not find any locustfile! Ensure file ends in '.py' [\#463](https://github.com/locustio/locust/issues/463)
- Contradiction on supported versions [\#461](https://github.com/locustio/locust/issues/461)
- How do I set cookies [\#458](https://github.com/locustio/locust/issues/458)
- Preserve Locust Stats? [\#457](https://github.com/locustio/locust/issues/457)
- locust RPS too low [\#454](https://github.com/locustio/locust/issues/454)
- Python 3.4,run locust error：No module named 'core' [\#453](https://github.com/locustio/locust/issues/453)
- Failure grouping in UI [\#452](https://github.com/locustio/locust/issues/452)
- TypeError: 'str' object is not callable [\#450](https://github.com/locustio/locust/issues/450)
- ERROR/locust.main: No Locust class found! [\#449](https://github.com/locustio/locust/issues/449)
- Locust won't run http request and instead just, skips ahead to the next line in the code??? [\#444](https://github.com/locustio/locust/issues/444)
- add an ability for click actions such as video play button [\#442](https://github.com/locustio/locust/issues/442)
- access to locust frontend from another computer [\#441](https://github.com/locustio/locust/issues/441)
- how can i add some methods to test but don't want restart locust [\#440](https://github.com/locustio/locust/issues/440)
- selenium web driver giving error 'Fire fox has stopped working' while opening firefox window [\#439](https://github.com/locustio/locust/issues/439)
- Location [\#437](https://github.com/locustio/locust/issues/437)
- Locust web interface not starting on Windows [\#436](https://github.com/locustio/locust/issues/436)
- aborting task in on\_start  [\#435](https://github.com/locustio/locust/issues/435)
- Can I use locust for live streaming load testing [\#434](https://github.com/locustio/locust/issues/434)
- URLs with `#` in them are not evaluated [\#433](https://github.com/locustio/locust/issues/433)
- In light of \#431, is it ok to migrate to pytest? [\#432](https://github.com/locustio/locust/issues/432)
- AttributeError: 'NoneType' object has no attribute 'replace' [\#431](https://github.com/locustio/locust/issues/431)
- Missing tags for versions above v0.7.2 [\#428](https://github.com/locustio/locust/issues/428)
- using interrupt while respecting the min\_time [\#427](https://github.com/locustio/locust/issues/427)
- Locust, NTLM, & Requests Sessions  [\#426](https://github.com/locustio/locust/issues/426)
- Is their any plan to support python 3.x? [\#425](https://github.com/locustio/locust/issues/425)
- TypeError: \_\_init\_\_\(\) got an unexpected keyword argument 'server\_hostname' [\#424](https://github.com/locustio/locust/issues/424)
- Test failures [\#422](https://github.com/locustio/locust/issues/422)
- Automate validation of locust [\#420](https://github.com/locustio/locust/issues/420)
- Unable to install on Mac OS X due to errors with greenlet [\#404](https://github.com/locustio/locust/issues/404)
- Factor out remote execution engine [\#403](https://github.com/locustio/locust/issues/403)
- requests library uses "wheel" file [\#134](https://github.com/locustio/locust/issues/134)

**Merged pull requests:**

- Match min/max\_weight equal sign style across project [\#497](https://github.com/locustio/locust/pull/497) ([alimony](https://github.com/alimony))
- Use super\(\) for HttpSession init call [\#494](https://github.com/locustio/locust/pull/494) ([detzgk](https://github.com/detzgk))
- Update gevent==1.1.2 [\#462](https://github.com/locustio/locust/pull/462) ([di](https://github.com/di))
- Fix document bug concerning '--host' option. [\#460](https://github.com/locustio/locust/pull/460) ([d6e](https://github.com/d6e))
- Python 3 compatibility with --no-web option [\#456](https://github.com/locustio/locust/pull/456) ([mrsanders](https://github.com/mrsanders))
- Changes to consolidate errors [\#451](https://github.com/locustio/locust/pull/451) ([schuSF](https://github.com/schuSF))
- Typo fix in locust API documentation [\#448](https://github.com/locustio/locust/pull/448) ([frntn](https://github.com/frntn))
- Python 3 compatibility for slave mode. \(Fixes 'locust --slave'\) [\#443](https://github.com/locustio/locust/pull/443) ([mrsanders](https://github.com/mrsanders))
- Python 3 support [\#363](https://github.com/locustio/locust/pull/363) ([pmdarrow](https://github.com/pmdarrow))

## [v0.7.5](https://github.com/locustio/locust/tree/v0.7.5) (2016-05-31)

[Full Changelog](https://github.com/locustio/locust/compare/v0.7.4...v0.7.5)

**Closed issues:**

- SSO on different site support [\#423](https://github.com/locustio/locust/issues/423)
- Mac install locust by pip in error of gevent [\#421](https://github.com/locustio/locust/issues/421)
- can someone help me to build a http request  content header [\#419](https://github.com/locustio/locust/issues/419)
- v0.7.4 [\#407](https://github.com/locustio/locust/issues/407)
- Python 3 support [\#279](https://github.com/locustio/locust/issues/279)

## [v0.7.4](https://github.com/locustio/locust/tree/v0.7.4) (2016-05-17)

[Full Changelog](https://github.com/locustio/locust/compare/v0.7.3...v0.7.4)

**Fixed bugs:**

- requests.exceptions.ConnectionError: \('Connection aborted.', ResponseNotReady\('Request-sent',\)\) [\#273](https://github.com/locustio/locust/issues/273)

**Closed issues:**

- locust not making any request when deployed on docker [\#415](https://github.com/locustio/locust/issues/415)
- Simulating multiple independent user web behaviour [\#409](https://github.com/locustio/locust/issues/409)
- Webclient authentication [\#406](https://github.com/locustio/locust/issues/406)
- Install error on ubuntu 14.04 [\#402](https://github.com/locustio/locust/issues/402)
- Python 3 support needed. [\#398](https://github.com/locustio/locust/issues/398)
- Quick start example using l for a variable name [\#392](https://github.com/locustio/locust/issues/392)
- Could you give me some examples of the schedule tasks? [\#390](https://github.com/locustio/locust/issues/390)
- The data between the different locusts [\#389](https://github.com/locustio/locust/issues/389)
- Rich report format [\#388](https://github.com/locustio/locust/issues/388)
- Pinging and benchmarking utilities [\#387](https://github.com/locustio/locust/issues/387)
- Integration with CI and test frameworks [\#385](https://github.com/locustio/locust/issues/385)
- Does locust support DB connection? [\#383](https://github.com/locustio/locust/issues/383)
- multisession confusion [\#382](https://github.com/locustio/locust/issues/382)
- why used the requests module [\#378](https://github.com/locustio/locust/issues/378)
- Have you compared the Locust with the Tsung? [\#377](https://github.com/locustio/locust/issues/377)
- Web GUI can't handle many unique URLs - Is it possible to aggregate stats entries? [\#375](https://github.com/locustio/locust/issues/375)
- Gevent gcc error. Unable to install locust [\#368](https://github.com/locustio/locust/issues/368)
- pip install failed mac el capitan  [\#366](https://github.com/locustio/locust/issues/366)
- Error during installation [\#362](https://github.com/locustio/locust/issues/362)
- does not work in python 3.4 virtualenv [\#359](https://github.com/locustio/locust/issues/359)
- How do I start a new session [\#356](https://github.com/locustio/locust/issues/356)
- Integrating Locust API with python requests [\#353](https://github.com/locustio/locust/issues/353)
- ar [\#342](https://github.com/locustio/locust/issues/342)
- Unable to install locust on OS X [\#340](https://github.com/locustio/locust/issues/340)
- Simulate chunk upload [\#339](https://github.com/locustio/locust/issues/339)
- Locust 0.7.3: TypeError trying to run test [\#338](https://github.com/locustio/locust/issues/338)
- Unable to install locusio [\#336](https://github.com/locustio/locust/issues/336)
- Separate TCP connection for each virtual user [\#334](https://github.com/locustio/locust/issues/334)
- url of this command /web/{var}  should have one final output in browser [\#327](https://github.com/locustio/locust/issues/327)
- Load testing a site whose domain name is not pointed/registered .  [\#326](https://github.com/locustio/locust/issues/326)
- Load Testing multiple sites on a single VPS. [\#325](https://github.com/locustio/locust/issues/325)
- Python3 support [\#324](https://github.com/locustio/locust/issues/324)
- Support for websockets? [\#323](https://github.com/locustio/locust/issues/323)
- step through locust source [\#322](https://github.com/locustio/locust/issues/322)
- rps degradation when using https. [\#320](https://github.com/locustio/locust/issues/320)
- Status reports only shown in terminal, not on the Web interface. [\#319](https://github.com/locustio/locust/issues/319)
- percentiles in /stats/requests? [\#318](https://github.com/locustio/locust/issues/318)
- real-time graphing [\#317](https://github.com/locustio/locust/issues/317)
- locust google group [\#316](https://github.com/locustio/locust/issues/316)
- unlikely response times  [\#315](https://github.com/locustio/locust/issues/315)
- rps bottleneck  [\#313](https://github.com/locustio/locust/issues/313)
- Are requests asynchronous? [\#312](https://github.com/locustio/locust/issues/312)
- run each task in sequence [\#311](https://github.com/locustio/locust/issues/311)
- ImportError: No module named 'core' [\#310](https://github.com/locustio/locust/issues/310)
- ConnectionError\(ProtocolError\('Connection aborted.', BadStatusLine\("''",\)\),\) [\#308](https://github.com/locustio/locust/issues/308)
- Support multiple test files [\#304](https://github.com/locustio/locust/issues/304)
- Tasks running, no stats collected. [\#301](https://github.com/locustio/locust/issues/301)
- OpenSSL errors when testing HTTPS [\#300](https://github.com/locustio/locust/issues/300)
- Web UI freezes [\#297](https://github.com/locustio/locust/issues/297)
- 250 users on single machine fails [\#296](https://github.com/locustio/locust/issues/296)
- slave not connecting to master and no error reported [\#294](https://github.com/locustio/locust/issues/294)
- Can't start swarming when in master/slave mode on Ubuntu 14.04 [\#293](https://github.com/locustio/locust/issues/293)
- How to interpret RPS on distributed setup? [\#292](https://github.com/locustio/locust/issues/292)
- problem with select library [\#274](https://github.com/locustio/locust/issues/274)
- Slaves can't connect to Master [\#265](https://github.com/locustio/locust/issues/265)
- list supported Python versions in README and setup.py. [\#260](https://github.com/locustio/locust/issues/260)
- Getting import requests.packages.urllib3 error in Google App Engine [\#259](https://github.com/locustio/locust/issues/259)
- Documentation on retrieving real-time stats  [\#230](https://github.com/locustio/locust/issues/230)
- Support for scenarios [\#171](https://github.com/locustio/locust/issues/171)
- Would love a swarm\_complete event [\#26](https://github.com/locustio/locust/issues/26)

**Merged pull requests:**

- Release updates for v0.7.4 [\#418](https://github.com/locustio/locust/pull/418) ([justiniso](https://github.com/justiniso))
- bump version of requests module in setup.py [\#401](https://github.com/locustio/locust/pull/401) ([cgoldberg](https://github.com/cgoldberg))
- \[\#62\] Correctly update slave count when drops below 1. [\#381](https://github.com/locustio/locust/pull/381) ([KashifSaadat](https://github.com/KashifSaadat))
- Documentation: Update writing-a-locustfile.rst [\#365](https://github.com/locustio/locust/pull/365) ([Valve](https://github.com/Valve))
- doc fixes [\#361](https://github.com/locustio/locust/pull/361) ([gward](https://github.com/gward))
- Update writing-a-locustfile.rst [\#337](https://github.com/locustio/locust/pull/337) ([reduxionist](https://github.com/reduxionist))
- Lock gevent version [\#335](https://github.com/locustio/locust/pull/335) ([nollbit](https://github.com/nollbit))
- Fix handler argument names. [\#314](https://github.com/locustio/locust/pull/314) ([doctoryes](https://github.com/doctoryes))
- Update writing-a-locustfile.rst [\#306](https://github.com/locustio/locust/pull/306) ([reduxionist](https://github.com/reduxionist))
- Introduce docs for increasing the max number of open files limit [\#298](https://github.com/locustio/locust/pull/298) ([ericandrewlewis](https://github.com/ericandrewlewis))

## [v0.7.3](https://github.com/locustio/locust/tree/v0.7.3) (2015-05-30)

[Full Changelog](https://github.com/locustio/locust/compare/v0.7.2...v0.7.3)

**Closed issues:**

- Rounding of percentiles \(premature optimization?\) [\#255](https://github.com/locustio/locust/issues/255)
- Feature request: initiate a test without entering the browser [\#253](https://github.com/locustio/locust/issues/253)
- Environment Variables for Locust playbooks [\#244](https://github.com/locustio/locust/issues/244)
- Failures not detected when web server is shutdown [\#240](https://github.com/locustio/locust/issues/240)
- client.post is not working for https [\#239](https://github.com/locustio/locust/issues/239)
- confused by multiple requests in on\_start [\#236](https://github.com/locustio/locust/issues/236)
- Empty stats on get aggregated stats [\#232](https://github.com/locustio/locust/issues/232)
- return\_response a valid request argument  [\#229](https://github.com/locustio/locust/issues/229)
- Allow developer to reduce unique URLs to their paths for reporting purposes [\#228](https://github.com/locustio/locust/issues/228)
- Locust never gets past 10 req/s, despite the server being much quicker than that [\#223](https://github.com/locustio/locust/issues/223)
- How to send Ajax requestes ? [\#219](https://github.com/locustio/locust/issues/219)
- Trigger UI events [\#218](https://github.com/locustio/locust/issues/218)
- Clients support gzip / deflate ? [\#215](https://github.com/locustio/locust/issues/215)
- nodequery api integration & charting ? [\#214](https://github.com/locustio/locust/issues/214)
- Test run time number of requests / rps ? [\#213](https://github.com/locustio/locust/issues/213)
- Clients support keepalive connections ? [\#212](https://github.com/locustio/locust/issues/212)
- master slave config, master not doing any work ? [\#211](https://github.com/locustio/locust/issues/211)
- multiple slaves of different server specs ? [\#210](https://github.com/locustio/locust/issues/210)
- multiple url tests ? [\#208](https://github.com/locustio/locust/issues/208)
- how to get the recorded data  [\#206](https://github.com/locustio/locust/issues/206)
- http proxy support [\#203](https://github.com/locustio/locust/issues/203)
- error report is not included in `--logfile` nor is it available for download as a csv [\#202](https://github.com/locustio/locust/issues/202)
- Stats get corrupted when the number of swarm users reaches the objective [\#201](https://github.com/locustio/locust/issues/201)
- API for invoking load [\#191](https://github.com/locustio/locust/issues/191)
- Locust slaves slowing dying and then coming back to life? [\#190](https://github.com/locustio/locust/issues/190)
- IndexError: list index out of range [\#166](https://github.com/locustio/locust/issues/166)
- Post with JSON data [\#157](https://github.com/locustio/locust/issues/157)
- Python Crash when running with slaves [\#156](https://github.com/locustio/locust/issues/156)

**Merged pull requests:**

- Update writing-a-locustfile.rst [\#268](https://github.com/locustio/locust/pull/268) ([ghost](https://github.com/ghost))
- changed how request\_meta\["method"\] is set [\#267](https://github.com/locustio/locust/pull/267) ([dantagg](https://github.com/dantagg))
- list supported Python versions [\#261](https://github.com/locustio/locust/pull/261) ([cgoldberg](https://github.com/cgoldberg))
- add host cli arg to quickstart [\#250](https://github.com/locustio/locust/pull/250) ([groovecoder](https://github.com/groovecoder))
- Update what-is-locust.rst [\#247](https://github.com/locustio/locust/pull/247) ([frvi](https://github.com/frvi))
- Fixed typo in the quickstart doc. [\#245](https://github.com/locustio/locust/pull/245) ([hirokiky](https://github.com/hirokiky))
- Fixed link to ESN's Twitter page [\#227](https://github.com/locustio/locust/pull/227) ([gentlecat](https://github.com/gentlecat))
- Fix a missing backtick [\#221](https://github.com/locustio/locust/pull/221) ([chrisramsay](https://github.com/chrisramsay))
- Fix typo in docs [\#216](https://github.com/locustio/locust/pull/216) ([gregeinfrank](https://github.com/gregeinfrank))
- Typos in docs. [\#193](https://github.com/locustio/locust/pull/193) ([jfacorro](https://github.com/jfacorro))
- recieve -\> receive; locsutfile -\> locustfile [\#183](https://github.com/locustio/locust/pull/183) ([stevetjoa](https://github.com/stevetjoa))

## [v0.7.2](https://github.com/locustio/locust/tree/v0.7.2) (2014-09-25)

[Full Changelog](https://github.com/locustio/locust/compare/v0.7.1...v0.7.2)

**Closed issues:**

- Parallel tasks? [\#198](https://github.com/locustio/locust/issues/198)
- Ability to schedule a call [\#197](https://github.com/locustio/locust/issues/197)
- Execution order? task lifetime? [\#195](https://github.com/locustio/locust/issues/195)
- CPU bound from locust vs CPU bound from the web app? [\#188](https://github.com/locustio/locust/issues/188)
- testing single page application [\#187](https://github.com/locustio/locust/issues/187)
- failed with AttributeError [\#185](https://github.com/locustio/locust/issues/185)
- Problem running tests [\#184](https://github.com/locustio/locust/issues/184)
- Web UI doesn't work in Firefox [\#179](https://github.com/locustio/locust/issues/179)
- Request name not pertinent in case of redirection [\#174](https://github.com/locustio/locust/issues/174)
- Reuse the code [\#173](https://github.com/locustio/locust/issues/173)
- RPS droping to 0 at the end of the user ramp-up period [\#172](https://github.com/locustio/locust/issues/172)
- Recorder and script generator [\#170](https://github.com/locustio/locust/issues/170)
- got AttributeError while using "with client.get\(...\) as response" [\#165](https://github.com/locustio/locust/issues/165)
- Request time doesn't include download time. [\#162](https://github.com/locustio/locust/issues/162)
- Error for requests version 2.2.1 [\#154](https://github.com/locustio/locust/issues/154)
- Request: non-zero exit when running --no-web and errors found [\#152](https://github.com/locustio/locust/issues/152)
- Support for tests that use multiple hosts [\#150](https://github.com/locustio/locust/issues/150)
- ImportError: No module named packages.urllib3.response [\#148](https://github.com/locustio/locust/issues/148)
- Slaves not closing the TCP connections properly [\#137](https://github.com/locustio/locust/issues/137)
- Locust support for SNI [\#136](https://github.com/locustio/locust/issues/136)
- User numbers going up and down [\#131](https://github.com/locustio/locust/issues/131)
- Automatically fork into multiple processes when running in --slave mode [\#12](https://github.com/locustio/locust/issues/12)

**Merged pull requests:**

- Add start and stop hatching events [\#199](https://github.com/locustio/locust/pull/199) ([skinp](https://github.com/skinp))
- fixed typo: your're -\> you are [\#182](https://github.com/locustio/locust/pull/182) ([stevetjoa](https://github.com/stevetjoa))
- choosed -\> chosen [\#181](https://github.com/locustio/locust/pull/181) ([mrjf](https://github.com/mrjf))
- Include method name in percentile distribution reports [\#176](https://github.com/locustio/locust/pull/176) ([fordhurley](https://github.com/fordhurley))
- Redefine err message for locustfile [\#164](https://github.com/locustio/locust/pull/164) ([illogicalextend](https://github.com/illogicalextend))
- Fixed typos in events.py example [\#159](https://github.com/locustio/locust/pull/159) ([nawaidshamim](https://github.com/nawaidshamim))
- Added: favicon, fixed paths. [\#158](https://github.com/locustio/locust/pull/158) ([dotpot](https://github.com/dotpot))
- Exit 1 when errors are found [\#155](https://github.com/locustio/locust/pull/155) ([jpotter](https://github.com/jpotter))

## [v0.7.1](https://github.com/locustio/locust/tree/v0.7.1) (2014-04-29)

[Full Changelog](https://github.com/locustio/locust/compare/v0.7...v0.7.1)

**Closed issues:**

- Min response time after reset is always 0 [\#147](https://github.com/locustio/locust/issues/147)
- locust shell client does not work in zsh [\#142](https://github.com/locustio/locust/issues/142)
- should catch exceptions by default [\#141](https://github.com/locustio/locust/issues/141)
- question about putting a delay [\#139](https://github.com/locustio/locust/issues/139)
- web ui uses a lot of mem and is quite sluggish at times [\#133](https://github.com/locustio/locust/issues/133)
- Add ability to select which Task to run [\#130](https://github.com/locustio/locust/issues/130)
- Move the download links to the top and make sticky [\#129](https://github.com/locustio/locust/issues/129)
- locust.weight supported, just undocumented? [\#123](https://github.com/locustio/locust/issues/123)
- Support for custom clients [\#83](https://github.com/locustio/locust/issues/83)

**Merged pull requests:**

- Fixed Docs Homebrew Link [\#143](https://github.com/locustio/locust/pull/143) ([saulshanabrook](https://github.com/saulshanabrook))
- Fix typo [\#132](https://github.com/locustio/locust/pull/132) ([rafax](https://github.com/rafax))
- Fix task ratio [\#125](https://github.com/locustio/locust/pull/125) ([sanga](https://github.com/sanga))

## [v0.7](https://github.com/locustio/locust/tree/v0.7) (2014-01-20)

[Full Changelog](https://github.com/locustio/locust/compare/v0.6.2...v0.7)

**Fixed bugs:**

- gc refcount related crash when loading web UI under Python 2.6.6 [\#49](https://github.com/locustio/locust/issues/49)

**Closed issues:**

- Different Users [\#126](https://github.com/locustio/locust/issues/126)
- doc updates for main class change from Locust to HttpLocust [\#116](https://github.com/locustio/locust/issues/116)
- collection of exceptions broken since 4ca0eef5 [\#114](https://github.com/locustio/locust/issues/114)
- number locusts must be a multiple of the number of slaves [\#112](https://github.com/locustio/locust/issues/112)
- changing port for distributed zeromq mode [\#111](https://github.com/locustio/locust/issues/111)
- error when running in master mode [\#110](https://github.com/locustio/locust/issues/110)
- python3 compatibility? [\#107](https://github.com/locustio/locust/issues/107)
- ramping.py calls RequestStats.sum\_stats\(\) which is no longer a valid call [\#104](https://github.com/locustio/locust/issues/104)
- line endings [\#101](https://github.com/locustio/locust/issues/101)
- Multiple Hosts, Host Function [\#99](https://github.com/locustio/locust/issues/99)
- Sorting does not work on \# requests column [\#97](https://github.com/locustio/locust/issues/97)
- Issues with localhost and domain configured in hosts file [\#96](https://github.com/locustio/locust/issues/96)
- Allow self.interrupt\(\) inside on\_start [\#95](https://github.com/locustio/locust/issues/95)
- hooking locust and graphite together as a plugin [\#94](https://github.com/locustio/locust/issues/94)
- Serve static files in web.app.route? [\#93](https://github.com/locustio/locust/issues/93)
- Error: Too many files open [\#92](https://github.com/locustio/locust/issues/92)
- stats reset after hatch completes [\#91](https://github.com/locustio/locust/issues/91)
- locust/test/test\_average.py present but never run [\#85](https://github.com/locustio/locust/issues/85)
- Add detailed request failure information to the web UI [\#84](https://github.com/locustio/locust/issues/84)
- remove \_send\_request\_safe\_mode [\#82](https://github.com/locustio/locust/issues/82)
- Enable different sessions for different users [\#81](https://github.com/locustio/locust/issues/81)
- Does locust support ‘CSV Data Set Config‘ feature like jmeter [\#79](https://github.com/locustio/locust/issues/79)
-  fatal error: 'event.h' file not found while installing in virtualenv on OSX 10.8.3 [\#77](https://github.com/locustio/locust/issues/77)
- Testing "Any" system [\#75](https://github.com/locustio/locust/issues/75)
- Custom http\_code stats [\#73](https://github.com/locustio/locust/issues/73)
- Need Clarification [\#70](https://github.com/locustio/locust/issues/70)
- It'd be nice to include the machine that a logging message came from [\#67](https://github.com/locustio/locust/issues/67)
- Allowing custom options to passed into tests? [\#65](https://github.com/locustio/locust/issues/65)
- requests \>1.0 [\#61](https://github.com/locustio/locust/issues/61)
- pyzmq 13.0.0 breaks distribution [\#58](https://github.com/locustio/locust/issues/58)
- Locust web interface not starting on Windows [\#57](https://github.com/locustio/locust/issues/57)
- Web interface doesn't work [\#56](https://github.com/locustio/locust/issues/56)
- Unit tests LocustRunner\(s\) and distributed mode [\#20](https://github.com/locustio/locust/issues/20)
- Proclaim Locust HTTP only [\#17](https://github.com/locustio/locust/issues/17)

**Merged pull requests:**

- fix typo [\#117](https://github.com/locustio/locust/pull/117) ([sanga](https://github.com/sanga))
- fix module and variable name clash \(traceback refers to a mod so it's a ... [\#115](https://github.com/locustio/locust/pull/115) ([sanga](https://github.com/sanga))
- Removes duplicate attribute documentation [\#106](https://github.com/locustio/locust/pull/106) ([djoume](https://github.com/djoume))
- Fixes typo in example code [\#105](https://github.com/locustio/locust/pull/105) ([djoume](https://github.com/djoume))
- fix typo in downloadable CSV [\#100](https://github.com/locustio/locust/pull/100) ([sghill](https://github.com/sghill))
- Documented more 0.7 changes [\#90](https://github.com/locustio/locust/pull/90) ([EnTeQuAk](https://github.com/EnTeQuAk))
- include hostname in log messages [\#89](https://github.com/locustio/locust/pull/89) ([sanga](https://github.com/sanga))
- Cleanups \(deprecated code, unused imports\) [\#88](https://github.com/locustio/locust/pull/88) ([EnTeQuAk](https://github.com/EnTeQuAk))
-  Merged gevent/zmq updates, ported to requests \>= 1.2  [\#87](https://github.com/locustio/locust/pull/87) ([EnTeQuAk](https://github.com/EnTeQuAk))
- Added option '--only-summary' for only printing stats at the end. [\#80](https://github.com/locustio/locust/pull/80) ([dougblack](https://github.com/dougblack))
- bump requests dependency to most recent pre 1.0 version \(i.e. most recen... [\#76](https://github.com/locustio/locust/pull/76) ([sanga](https://github.com/sanga))
- Stats refactoring [\#74](https://github.com/locustio/locust/pull/74) ([heyman](https://github.com/heyman))
- Enhancement/url error [\#72](https://github.com/locustio/locust/pull/72) ([krallin](https://github.com/krallin))
- Include method name in command line logging [\#66](https://github.com/locustio/locust/pull/66) ([amandasaurus](https://github.com/amandasaurus))
- use correct python special method name [\#64](https://github.com/locustio/locust/pull/64) ([amandasaurus](https://github.com/amandasaurus))
- Small fixes [\#63](https://github.com/locustio/locust/pull/63) ([sanga](https://github.com/sanga))
- Use shutdown function when num\_requests are done [\#60](https://github.com/locustio/locust/pull/60) ([afajl](https://github.com/afajl))
- Update docs/api.rst [\#55](https://github.com/locustio/locust/pull/55) ([cbrinley](https://github.com/cbrinley))
- Added argument to options parser indicating on which port to run the web UI [\#54](https://github.com/locustio/locust/pull/54) ([manova](https://github.com/manova))

## [v0.6.2](https://github.com/locustio/locust/tree/v0.6.2) (2013-01-10)

[Full Changelog](https://github.com/locustio/locust/compare/v0.6.1...v0.6.2)

**Closed issues:**

- greenlet error when used distributed locust under Python2.6 [\#53](https://github.com/locustio/locust/issues/53)
- Get fails in clean install on Ubuntu: KeyError: 'start\_time' [\#52](https://github.com/locustio/locust/issues/52)

**Merged pull requests:**

- add docs: Installing Locust on Mac OS [\#51](https://github.com/locustio/locust/pull/51) ([yurtaev](https://github.com/yurtaev))
- Add parent to TaskSet to enable state sharing among hierarchical TaskSets [\#50](https://github.com/locustio/locust/pull/50) ([daubman](https://github.com/daubman))

## [v0.6.1](https://github.com/locustio/locust/tree/v0.6.1) (2012-12-04)

[Full Changelog](https://github.com/locustio/locust/compare/v0.6...v0.6.1)

**Closed issues:**

- Locust throwing error when reaching  NUM\_REQUESTS parameter [\#47](https://github.com/locustio/locust/issues/47)

## [v0.6](https://github.com/locustio/locust/tree/v0.6) (2012-11-29)

[Full Changelog](https://github.com/locustio/locust/compare/v0.5.1...v0.6)

**Fixed bugs:**

- Master node fails to start if a slave node is still running [\#15](https://github.com/locustio/locust/issues/15)

**Closed issues:**

- Drop the require\_once decorator [\#42](https://github.com/locustio/locust/issues/42)
- Improve catch\_response feature \(was previous: Remove catch\_response feature from HttpBrowser\) [\#39](https://github.com/locustio/locust/issues/39)
- RPS count drops when master and slaves drift in time [\#38](https://github.com/locustio/locust/issues/38)
- FEAT: add stat support for chunked transfer-encoding [\#33](https://github.com/locustio/locust/issues/33)
- Date or timer for automatic shutdown of test [\#31](https://github.com/locustio/locust/issues/31)
- Option to ignore query parameters on stats [\#29](https://github.com/locustio/locust/issues/29)
- Remove SubLocust and merge into Locust class [\#16](https://github.com/locustio/locust/issues/16)
- Add support for shutting down slaves without restarting master [\#6](https://github.com/locustio/locust/issues/6)

**Merged pull requests:**

- Change Locust/SubLocust API [\#43](https://github.com/locustio/locust/pull/43) ([heyman](https://github.com/heyman))
- Quickstart example was missing import task [\#41](https://github.com/locustio/locust/pull/41) ([natancox](https://github.com/natancox))
- Use python-requests as HTTP client in Locust [\#40](https://github.com/locustio/locust/pull/40) ([heyman](https://github.com/heyman))
- Addfix [\#36](https://github.com/locustio/locust/pull/36) ([jukart](https://github.com/jukart))

## [v0.5.1](https://github.com/locustio/locust/tree/v0.5.1) (2012-07-01)

[Full Changelog](https://github.com/locustio/locust/compare/v0.5...v0.5.1)

**Closed issues:**

- loglevel and logfile don't seem to work [\#25](https://github.com/locustio/locust/issues/25)

## [v0.5](https://github.com/locustio/locust/tree/v0.5) (2012-07-01)

[Full Changelog](https://github.com/locustio/locust/compare/v0.4...v0.5)

**Closed issues:**

- Remove Confluence specific task ratio formatter [\#13](https://github.com/locustio/locust/issues/13)
- Add HTTP request method \(GET/POST/PUT, etc\) to statistics table [\#3](https://github.com/locustio/locust/issues/3)

**Merged pull requests:**

- Refactoring \(separation\) of ramping code; Added tooltips for ramping form in ui [\#28](https://github.com/locustio/locust/pull/28) ([HeyHugo](https://github.com/HeyHugo))
- Support Basic HTTP Authorization for https requests [\#27](https://github.com/locustio/locust/pull/27) ([corbinbs](https://github.com/corbinbs))
- Add content-disposition with a filename. Fix missing import \(warnings\). [\#24](https://github.com/locustio/locust/pull/24) ([benjaminws](https://github.com/benjaminws))
- Fixed CSV stats export order [\#23](https://github.com/locustio/locust/pull/23) ([quosa](https://github.com/quosa))
- request timing csv endpoint was returning Internal Error  [\#22](https://github.com/locustio/locust/pull/22) ([pedronis](https://github.com/pedronis))
- fix continuous resetting on of stats in master+slaves mode [\#19](https://github.com/locustio/locust/pull/19) ([pedronis](https://github.com/pedronis))

## [v0.4](https://github.com/locustio/locust/tree/v0.4) (2011-12-05)

[Full Changelog](https://github.com/locustio/locust/compare/7cfe62cee36dee34fe4d23aed5bdd00c4f42b3d0...v0.4)

**Fixed bugs:**

- Total RPS counter does not work [\#9](https://github.com/locustio/locust/issues/9)
- Total median value is zero in the web interface [\#7](https://github.com/locustio/locust/issues/7)
- Wrong failure percentage in statistics [\#5](https://github.com/locustio/locust/issues/5)
- Raising InterruptLocust within with statement + catch\_response causes failure [\#4](https://github.com/locustio/locust/issues/4)

**Closed issues:**

- Add sorting capabilities in web UI [\#8](https://github.com/locustio/locust/issues/8)
- Add/improve support for running Locust distributed [\#1](https://github.com/locustio/locust/issues/1)

**Merged pull requests:**

- optional ramping feature; sorting stats by column [\#11](https://github.com/locustio/locust/pull/11) ([HeyHugo](https://github.com/HeyHugo))
- Dynamic changing of locust count [\#10](https://github.com/locustio/locust/pull/10) ([HeyHugo](https://github.com/HeyHugo))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
