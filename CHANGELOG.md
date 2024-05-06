# Detailed changelog
The most important changes can also be found in [the documentation](https://docs.locust.io/en/latest/changelog.html).

## [2.27.0](https://github.com/locustio/locust/tree/2.27.0) (2024-05-06)

[Full Changelog](https://github.com/locustio/locust/compare/2.26.0...2.27.0)

**Fixed bugs:**

- User Classes with Empty Tasks Results in TypeError: 'NoneType' object is not iterable [\#2694](https://github.com/locustio/locust/issues/2694)

**Closed issues:**

- Why defining run\_time on worker node raises an error [\#2683](https://github.com/locustio/locust/issues/2683)

**Merged pull requests:**

- annotate return types of a few functions to enable more mypy check [\#2702](https://github.com/locustio/locust/pull/2702) ([tdadela](https://github.com/tdadela))
- refactor\(WindowsKeyPoller\): change implementation of captured\_chars  [\#2701](https://github.com/locustio/locust/pull/2701) ([tdadela](https://github.com/tdadela))
- refactor: replace deprecated utcfromtimestamp function [\#2700](https://github.com/locustio/locust/pull/2700) ([tdadela](https://github.com/tdadela))
- Use deque for tasks in taskset instead of plain list [\#2698](https://github.com/locustio/locust/pull/2698) ([cyberw](https://github.com/cyberw))
- fix: Ensure locust does not crash when an User class has no task [\#2696](https://github.com/locustio/locust/pull/2696) ([hangonlyra](https://github.com/hangonlyra))
- Fix various spelling errors using codespell [\#2687](https://github.com/locustio/locust/pull/2687) ([cyberw](https://github.com/cyberw))
- Dispatch/user distribution calculation using Kullback-Leibler divergence [\#2686](https://github.com/locustio/locust/pull/2686) ([tdadela](https://github.com/tdadela))
- Allow worker process to run with --run-time specified, just log a warning about it being ignored [\#2685](https://github.com/locustio/locust/pull/2685) ([Sawiq](https://github.com/Sawiq))
- Small cleanup: mypy type-ignore and dev deps [\#2684](https://github.com/locustio/locust/pull/2684) ([tdadela](https://github.com/tdadela))
- Simplify how locustfiles are found \(using -f\). Don’t automatically append .py [\#2655](https://github.com/locustio/locust/pull/2655) ([DennisKrone](https://github.com/DennisKrone))

## [2.26.0](https://github.com/locustio/locust/tree/2.26.0) (2024-04-18)

[Full Changelog](https://github.com/locustio/locust/compare/2.25.0...2.26.0)

**Merged pull requests:**

- Reformat and lint stuff. And pin gevenhttpclient version [\#2682](https://github.com/locustio/locust/pull/2682) ([cyberw](https://github.com/cyberw))
- Add ruff pre commit hook [\#2680](https://github.com/locustio/locust/pull/2680) ([cyberw](https://github.com/cyberw))
- Remove python 3.8 compatibility code [\#2679](https://github.com/locustio/locust/pull/2679) ([cyberw](https://github.com/cyberw))
- Drop support for Python 3.8 [\#2677](https://github.com/locustio/locust/pull/2677) ([cyberw](https://github.com/cyberw))
- Update geventhttpclient and adjust FastHttpUser max\_retries / max\_redirects [\#2676](https://github.com/locustio/locust/pull/2676) ([cyberw](https://github.com/cyberw))

## [2.25.0](https://github.com/locustio/locust/tree/2.25.0) (2024-04-14)

[Full Changelog](https://github.com/locustio/locust/compare/2.24.1...2.25.0)

**Fixed bugs:**

- Wrong distribution of virtual users by user classes [\#2662](https://github.com/locustio/locust/issues/2662)
- Monkey patching error [\#2661](https://github.com/locustio/locust/issues/2661)
- cannot specify task of UserClass when locust run on distributed mode [\#2657](https://github.com/locustio/locust/issues/2657)
- \[ModernUI\] HTML entities are incorrectly escaped in generated report [\#2635](https://github.com/locustio/locust/issues/2635)
- Bug / Feature request: Time intensive `custom_messages` functions trigger heartbeat timeout [\#2608](https://github.com/locustio/locust/issues/2608)

**Closed issues:**

- Add an UI extension exemple that display proxy cache hit/miss [\#2644](https://github.com/locustio/locust/issues/2644)

**Merged pull requests:**

- Log deprecation warning for --legacy-ui [\#2670](https://github.com/locustio/locust/pull/2670) ([cyberw](https://github.com/cyberw))
- Add an example that displays cache stats using the new UI. [\#2669](https://github.com/locustio/locust/pull/2669) ([obriat](https://github.com/obriat))
- Update User Classes in Distributed Mode [\#2666](https://github.com/locustio/locust/pull/2666) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- fix\(dispatch\): UserClasses weight distribution with gcd [\#2663](https://github.com/locustio/locust/pull/2663) ([llirrikk](https://github.com/llirrikk))
- Fix issue with concurrent custom messages and docs [\#2654](https://github.com/locustio/locust/pull/2654) ([cyberw](https://github.com/cyberw))
- Add functionality to run listener functions for `custom_messages` concurrently [\#2650](https://github.com/locustio/locust/pull/2650) ([samuelspagl](https://github.com/samuelspagl))
- \[Modern UI\] Escape HTML Entities correctly in Exceptions Table [\#2648](https://github.com/locustio/locust/pull/2648) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.24.1](https://github.com/locustio/locust/tree/2.24.1) (2024-03-20)

[Full Changelog](https://github.com/locustio/locust/compare/2.24.0...2.24.1)

**Fixed bugs:**

- `'NoneType' object has no attribute 'get'` when `stream=True` in `FastHttpSession.request` [\#2640](https://github.com/locustio/locust/issues/2640)
- Locust --processes argument generating multiple html reports [\#2639](https://github.com/locustio/locust/issues/2639)
- cannot open dashboard and console error shows 'the server responded with a MIME type of "text/plain".' [\#2632](https://github.com/locustio/locust/issues/2632)
- extend web ui not working since 2.22.0 [\#2629](https://github.com/locustio/locust/issues/2629)
- Custom parameters incomplete display [\#2628](https://github.com/locustio/locust/issues/2628)

**Closed issues:**

- pyproject.toml support for locust configuration [\#2298](https://github.com/locustio/locust/issues/2298)

**Merged pull requests:**

- Do not call blocking `content` property and lazily load response [\#2643](https://github.com/locustio/locust/pull/2643) ([neiser](https://github.com/neiser))
- Dont throw an exception in FastHttpUser if a request is made with stream=True and the connection fails [\#2642](https://github.com/locustio/locust/pull/2642) ([cyberw](https://github.com/cyberw))
- \[Modern UI\] Modal Can Extend Beyond Screen Limits [\#2631](https://github.com/locustio/locust/pull/2631) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- chore: remove repetitive words [\#2625](https://github.com/locustio/locust/pull/2625) ([tgolang](https://github.com/tgolang))
- Add documentation about manually closing TCP/HTTP connections [\#2623](https://github.com/locustio/locust/pull/2623) ([DennisKrone](https://github.com/DennisKrone))
- Update ruff to 0.3.0 [\#2619](https://github.com/locustio/locust/pull/2619) ([cyberw](https://github.com/cyberw))

## [2.24.0](https://github.com/locustio/locust/tree/2.24.0) (2024-02-29)

[Full Changelog](https://github.com/locustio/locust/compare/2.23.1...2.24.0)

**Fixed bugs:**

- Blank page when accessing Locust Web UI via reverse proxy with subpath [\#2614](https://github.com/locustio/locust/issues/2614)
- \[Report\]\[Modern-UI\] HTML report is blank [\#2603](https://github.com/locustio/locust/issues/2603)

**Closed issues:**

- SocketIOUser send method supports specific subscribe request [\#2616](https://github.com/locustio/locust/issues/2616)
- "Sticky" user types on workers [\#2522](https://github.com/locustio/locust/issues/2522)

**Merged pull requests:**

- Modern UI - Fix logo asset [\#2618](https://github.com/locustio/locust/pull/2618) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Bugfix/2614 relative assets and stats links [\#2615](https://github.com/locustio/locust/pull/2615) ([skyanth](https://github.com/skyanth))
- \[Modern UI\] Refactor and Add Tests for Entrypoints [\#2613](https://github.com/locustio/locust/pull/2613) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Implement pyproject.toml support for Locust configuration [\#2612](https://github.com/locustio/locust/pull/2612) ([alzex3](https://github.com/alzex3))
- Update Header Logo to Higher Resolution for the Modern UI [\#2611](https://github.com/locustio/locust/pull/2611) ([FooQoo](https://github.com/FooQoo))
- \[Report\]\[Modern-UI\] HTML report is blank [\#2609](https://github.com/locustio/locust/pull/2609) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- pluggable dispatcher logic [\#2606](https://github.com/locustio/locust/pull/2606) ([mgor](https://github.com/mgor))
- Modern UI: Change Footer to Static Positioning [\#2605](https://github.com/locustio/locust/pull/2605) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Check that locustfile downloaded from URL is valid Python code [\#2604](https://github.com/locustio/locust/pull/2604) ([DennisKrone](https://github.com/DennisKrone))

## [2.23.1](https://github.com/locustio/locust/tree/2.23.1) (2024-02-11)

[Full Changelog](https://github.com/locustio/locust/compare/2.23.0...2.23.1)

**Fixed bugs:**

- Modern UI: Average Response Time and 95th percentile have the same color [\#2598](https://github.com/locustio/locust/issues/2598)

**Closed issues:**

- Modern UI: Add exception message column on the Exception Statistics [\#2597](https://github.com/locustio/locust/issues/2597)

**Merged pull requests:**

- Modern UI: Add exception message column on the Exception Table [\#2601](https://github.com/locustio/locust/pull/2601) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Modern UI: Wrong chart's legend for overridden percentiles values [\#2600](https://github.com/locustio/locust/pull/2600) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Change download-from-master to use temp file dir [\#2599](https://github.com/locustio/locust/pull/2599) ([cyberw](https://github.com/cyberw))

## [2.23.0](https://github.com/locustio/locust/tree/2.23.0) (2024-02-11)

[Full Changelog](https://github.com/locustio/locust/compare/2.22.0...2.23.0)

**Closed issues:**

- Modern UI: ability to sort tables by column specific column [\#2593](https://github.com/locustio/locust/issues/2593)
- Modern UI -  User class picker - add option to enable/disable everything. [\#2585](https://github.com/locustio/locust/issues/2585)
- \[LocustLineChart\] Implement an option/configuration for users to customize the color of the LocustLineChart. [\#2578](https://github.com/locustio/locust/issues/2578)

**Merged pull requests:**

- Tables are Sortable by Default [\#2596](https://github.com/locustio/locust/pull/2596) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Allow getting locust files from http urls [\#2595](https://github.com/locustio/locust/pull/2595) ([DennisKrone](https://github.com/DennisKrone))
- Fixed typos in documentation [\#2592](https://github.com/locustio/locust/pull/2592) ([dorin131](https://github.com/dorin131))
- Remove no longer relevant documentation and \(already not working?\) checks for not loading locustfiles named locust.py [\#2591](https://github.com/locustio/locust/pull/2591) ([cyberw](https://github.com/cyberw))
- Add Select All / None Checkbox to User Class Picker [\#2590](https://github.com/locustio/locust/pull/2590) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Add New Colors for the Locust Charts [\#2589](https://github.com/locustio/locust/pull/2589) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Work around issue with locustfiles named "locust.py" [\#2587](https://github.com/locustio/locust/pull/2587) ([cyberw](https://github.com/cyberw))
- Update writing-a-locustfile.rst [\#2584](https://github.com/locustio/locust/pull/2584) ([KaushikPathak90](https://github.com/KaushikPathak90))
- Locustfile distribution from master to worker [\#2583](https://github.com/locustio/locust/pull/2583) ([cyberw](https://github.com/cyberw))
- Gh actions: Run tests on MacOS [\#2580](https://github.com/locustio/locust/pull/2580) ([cyberw](https://github.com/cyberw))
- Use defaultdict:s for stats dictionaries instead of setdefault [\#2579](https://github.com/locustio/locust/pull/2579) ([cyberw](https://github.com/cyberw))
- DeprecationWarning: the load\_module\(\) method is deprecated and slated for removal in Python 3.12; use exec\_module\(\) instead [\#2576](https://github.com/locustio/locust/pull/2576) ([mgor](https://github.com/mgor))
- docs\(running-distributed\): cores -\> logical cores [\#2570](https://github.com/locustio/locust/pull/2570) ([tdadela](https://github.com/tdadela))

## [2.22.0](https://github.com/locustio/locust/tree/2.22.0) (2024-02-04)

[Full Changelog](https://github.com/locustio/locust/compare/2.21.0...2.22.0)

**Fixed bugs:**

- Modern UI - new test modal not scrollable [\#2574](https://github.com/locustio/locust/issues/2574)

**Merged pull requests:**

- Fix Modern UI - new test modal not scrollable [\#2577](https://github.com/locustio/locust/pull/2577) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Fix Spawning State Never Updates to Running [\#2573](https://github.com/locustio/locust/pull/2573) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Update README.md Screenshots for Modern UI [\#2572](https://github.com/locustio/locust/pull/2572) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Use Modern UI by default [\#2569](https://github.com/locustio/locust/pull/2569) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- GH Actions: Run tests on windows [\#2567](https://github.com/locustio/locust/pull/2567) ([cyberw](https://github.com/cyberw))

## [2.21.0](https://github.com/locustio/locust/tree/2.21.0) (2024-01-27)

[Full Changelog](https://github.com/locustio/locust/compare/2.20.1...2.21.0)

**Fixed bugs:**

- 95th percentile line chart does not display correctly on the Response Times \(ms\) graph [\#2540](https://github.com/locustio/locust/issues/2540)
- ValueError: greenlet.greenlet size changed, may indicate binary incompatibility. Expected 152 from C header, got 40 from PyObject [\#2539](https://github.com/locustio/locust/issues/2539)
- TaskSet missing \_cp\_last\_run attribute [\#2532](https://github.com/locustio/locust/issues/2532)
- Modern UI "forgets" the selected user count and ramp up rate when starting a new test or editing a running one [\#2531](https://github.com/locustio/locust/issues/2531)
- Update dependency or remove support for Basic Auth for the Web UI [\#2517](https://github.com/locustio/locust/issues/2517)

**Closed issues:**

- Unifying percentile displays in Locust's statistics screens [\#2546](https://github.com/locustio/locust/issues/2546)
- Improve the Class Picker [\#2545](https://github.com/locustio/locust/issues/2545)
- Add `response.ok` support to `FastHttpUser`'s `FastResponse`, ala `HttpUser`/requests [\#2520](https://github.com/locustio/locust/issues/2520)

**Merged pull requests:**

- Optimize memory usage when using --processes [\#2564](https://github.com/locustio/locust/pull/2564) ([cyberw](https://github.com/cyberw))
- docs: update developing-locust.rst \(black, flake8\) -\> ruff [\#2562](https://github.com/locustio/locust/pull/2562) ([tdadela](https://github.com/tdadela))
- Allow User weight adjustment \(and task selection\) in UI when running with --class-picker, or on command line with --config-users argument [\#2559](https://github.com/locustio/locust/pull/2559) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Ruff enable isort \(with custom sections\) [\#2556](https://github.com/locustio/locust/pull/2556) ([tdadela](https://github.com/tdadela))
- update readthedocs-sphinx-search [\#2553](https://github.com/locustio/locust/pull/2553) ([cyberw](https://github.com/cyberw))
- Fix pedantic typo in the index.html template [\#2552](https://github.com/locustio/locust/pull/2552) ([marcelofern](https://github.com/marcelofern))
- Ruff set python version and enable more rules [\#2551](https://github.com/locustio/locust/pull/2551) ([tdadela](https://github.com/tdadela))
- Customization Feature for Percentile Display on Statistics Page [\#2550](https://github.com/locustio/locust/pull/2550) ([FooQoo](https://github.com/FooQoo))
- Use ruff instead of flake8 and black for linting and formatting [\#2549](https://github.com/locustio/locust/pull/2549) ([cyberw](https://github.com/cyberw))
- Fix mypy configuration & upgrade typing [\#2548](https://github.com/locustio/locust/pull/2548) ([tdadela](https://github.com/tdadela))
- Fix Web UI Chart History [\#2544](https://github.com/locustio/locust/pull/2544) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Web UI Modern Auth [\#2538](https://github.com/locustio/locust/pull/2538) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Modern UI: Fix Default Values for Edit / Start New Test [\#2537](https://github.com/locustio/locust/pull/2537) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Added response.ok support to FastHttpUser's FastResponse class similar to HttpUser's Response [\#2535](https://github.com/locustio/locust/pull/2535) ([PankajKhanwani](https://github.com/PankajKhanwani))
- Update shape class' runner when Web UI picker is used [\#2534](https://github.com/locustio/locust/pull/2534) ([wiatrak2](https://github.com/wiatrak2))
- setting initial \_cp\_last\_run on TaskSet in order to allow constant\_pacing wait time strategy [\#2533](https://github.com/locustio/locust/pull/2533) ([ionutab](https://github.com/ionutab))

## [2.20.1](https://github.com/locustio/locust/tree/2.20.1) (2024-01-03)

[Full Changelog](https://github.com/locustio/locust/compare/2.20.0...2.20.1)

**Fixed bugs:**

- Vite-version needs to be updated [\#2528](https://github.com/locustio/locust/issues/2528)
- Issue of 100% CPU usage when closing WebSocket connections. [\#2516](https://github.com/locustio/locust/issues/2516)

**Merged pull requests:**

- Update Vite to 4.5.1 [\#2530](https://github.com/locustio/locust/pull/2530) ([cyberw](https://github.com/cyberw))
- Bump vite from 4.4.9 to 4.4.12 in /locust/webui [\#2527](https://github.com/locustio/locust/pull/2527) ([dependabot[bot]](https://github.com/apps/dependabot))
- update docker actions to get rid of node12 deprecation warnings [\#2524](https://github.com/locustio/locust/pull/2524) ([mgor](https://github.com/mgor))
- Support IPv6 for zmq connection between master and worker [\#2521](https://github.com/locustio/locust/pull/2521) ([simonwu-sn](https://github.com/simonwu-sn))
- run\_single\_user improvements [\#2519](https://github.com/locustio/locust/pull/2519) ([cyberw](https://github.com/cyberw))
- Bump Requests to 2.26.0, remove explicit dependency on charset\_normalizer [\#2518](https://github.com/locustio/locust/pull/2518) ([cyberw](https://github.com/cyberw))

## [2.20.0](https://github.com/locustio/locust/tree/2.20.0) (2023-12-13)

[Full Changelog](https://github.com/locustio/locust/compare/2.19.1...2.20.0)

**Fixed bugs:**

- har2locust KeyError: '\_resourceType' [\#2503](https://github.com/locustio/locust/issues/2503)
- FastHTTPUser determines StatusCode 304 as Failed [\#2500](https://github.com/locustio/locust/issues/2500)
- FastHttpUser is stricter than HttpUser about the host attribute [\#2492](https://github.com/locustio/locust/issues/2492)
- Unable to modify custom parameters from UI using modern UI [\#2489](https://github.com/locustio/locust/issues/2489)
- Exception 'LookupError: unknown encoding:' when response contains `content-type` not handled by requests.utils.get\_encoding\_from\_headers [\#2482](https://github.com/locustio/locust/issues/2482)

**Merged pull requests:**

- Fix useSwarmUi Test with Mock Timers [\#2514](https://github.com/locustio/locust/pull/2514) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Custom messages: Throw an exception if someone tries to register twice for the same event [\#2513](https://github.com/locustio/locust/pull/2513) ([cyberw](https://github.com/cyberw))
- Fixed response failure for unsupported encoding [\#2512](https://github.com/locustio/locust/pull/2512) ([prince-melvin](https://github.com/prince-melvin))
- Add event.measure context manager for simpler firing of request event [\#2511](https://github.com/locustio/locust/pull/2511) ([cyberw](https://github.com/cyberw))
- Update Web UI About box [\#2510](https://github.com/locustio/locust/pull/2510) ([cyberw](https://github.com/cyberw))
- Chart Average Response Time in Modern UI [\#2509](https://github.com/locustio/locust/pull/2509) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Update the About Section [\#2508](https://github.com/locustio/locust/pull/2508) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Allow Boolean and Null Values to be Set from the Web UI [\#2507](https://github.com/locustio/locust/pull/2507) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- custom messages: Support sending datetimes and bson.ObjectId [\#2504](https://github.com/locustio/locust/pull/2504) ([cyberw](https://github.com/cyberw))
- Add Notifications for Log Viewer [\#2502](https://github.com/locustio/locust/pull/2502) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- FastHttpUser: Treat response code 304 as OK [\#2501](https://github.com/locustio/locust/pull/2501) ([cyberw](https://github.com/cyberw))
- Fix Warnings from the Web UI Tests [\#2499](https://github.com/locustio/locust/pull/2499) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Adjust "Starting web interface at"-output [\#2498](https://github.com/locustio/locust/pull/2498) ([cyberw](https://github.com/cyberw))
- Update mypy, some type hints, and some tiny updates to Runner classes [\#2497](https://github.com/locustio/locust/pull/2497) ([cyberw](https://github.com/cyberw))
- Remove Typecheck from Web UI Build Process and Update Github Actions [\#2496](https://github.com/locustio/locust/pull/2496) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Replace Vitest canvas mock library [\#2495](https://github.com/locustio/locust/pull/2495) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Implement Modern Web UI Tests [\#2494](https://github.com/locustio/locust/pull/2494) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Further relax FastHttpUser's host checking to match HttpUser's [\#2493](https://github.com/locustio/locust/pull/2493) ([pjenvey](https://github.com/pjenvey))
- Unable to modify custom parameters from the modern UI [\#2491](https://github.com/locustio/locust/pull/2491) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.19.1](https://github.com/locustio/locust/tree/2.19.1) (2023-11-27)

[Full Changelog](https://github.com/locustio/locust/compare/2.19.0...2.19.1)

**Closed issues:**

- SocketIOUser not support send BINARY data [\#2457](https://github.com/locustio/locust/issues/2457)

**Merged pull requests:**

- Change logging of call to sys.exit\(\) to info level [\#2490](https://github.com/locustio/locust/pull/2490) ([cyberw](https://github.com/cyberw))
- fix\(typing\): typing.DefaultDict in test\_interruptable\_task.py [\#2488](https://github.com/locustio/locust/pull/2488) ([tdadela](https://github.com/tdadela))
- Dont suppress StopUser or GreenletExit in on\_stop [\#2486](https://github.com/locustio/locust/pull/2486) ([ALagierski](https://github.com/ALagierski))
- FastResponse: Detect response text encoding when no information is present on the response headers. [\#2485](https://github.com/locustio/locust/pull/2485) ([MiltiadisKoutsokeras](https://github.com/MiltiadisKoutsokeras))
- Fix an edge case when no directory is part of csv-prefix [\#2483](https://github.com/locustio/locust/pull/2483) ([sillydan1](https://github.com/sillydan1))
- Create any directories as part of the CSV Prefix [\#2481](https://github.com/locustio/locust/pull/2481) ([sillydan1](https://github.com/sillydan1))

## [2.19.0](https://github.com/locustio/locust/tree/2.19.0) (2023-11-21)

[Full Changelog](https://github.com/locustio/locust/compare/2.18.4...2.19.0)

**Merged pull requests:**

- Fix issue with --processes: Stop parent process from trying to kill children too fast [\#2478](https://github.com/locustio/locust/pull/2478) ([cyberw](https://github.com/cyberw))
- Update command line argument descriptions and docs [\#2477](https://github.com/locustio/locust/pull/2477) ([cyberw](https://github.com/cyberw))
- Update minimum version of various dependencies [\#2476](https://github.com/locustio/locust/pull/2476) ([cyberw](https://github.com/cyberw))
- Stop worker from automatically quitting if connected to an older version master that doesnt send heartbeats [\#2475](https://github.com/locustio/locust/pull/2475) ([cyberw](https://github.com/cyberw))
- Shut down workers if master goes missing for too long [\#2474](https://github.com/locustio/locust/pull/2474) ([cyberw](https://github.com/cyberw))
- Add --processes parameter to automatically fork worker processes [\#2472](https://github.com/locustio/locust/pull/2472) ([cyberw](https://github.com/cyberw))

## [2.18.4](https://github.com/locustio/locust/tree/2.18.4) (2023-11-19)

[Full Changelog](https://github.com/locustio/locust/compare/2.18.3...2.18.4)

**Fixed bugs:**

- Total RPS Charts | Failures line chart does not display current number of failures [\#2469](https://github.com/locustio/locust/issues/2469)
- Modern UI: Lack of information about time and user count in charts [\#2467](https://github.com/locustio/locust/issues/2467)
- Modern UI: Wrong chart's legend for overridden percentiles values  [\#2463](https://github.com/locustio/locust/issues/2463)
- Modern UI: Can't sort columns on statistics page and downloaded report [\#2449](https://github.com/locustio/locust/issues/2449)
- Incorrect RPS when decreasing the number of users [\#2399](https://github.com/locustio/locust/issues/2399)

**Closed issues:**

- Improve UI of Sorting Columns [\#2466](https://github.com/locustio/locust/issues/2466)

**Merged pull requests:**

- Log deprecation warning in python 3.8 [\#2473](https://github.com/locustio/locust/pull/2473) ([cyberw](https://github.com/cyberw))
- Modern UI - Failures line chart does not display current number of failures [\#2471](https://github.com/locustio/locust/pull/2471) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Tiny optimization of StatsEntry.\_log\_response\_time [\#2470](https://github.com/locustio/locust/pull/2470) ([lailongwei](https://github.com/lailongwei))
- Modern UI: Add Time to Chart Tooltips [\#2468](https://github.com/locustio/locust/pull/2468) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Ensure to wait a second before next `tick()` [\#2465](https://github.com/locustio/locust/pull/2465) ([wiatrak2](https://github.com/wiatrak2))
- Modern UI: Wrong chart's legend for Response Times [\#2464](https://github.com/locustio/locust/pull/2464) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Replace Updating Stats useEffect Hook with useInterval [\#2462](https://github.com/locustio/locust/pull/2462) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.18.3](https://github.com/locustio/locust/tree/2.18.3) (2023-11-12)

[Full Changelog](https://github.com/locustio/locust/compare/2.18.2...2.18.3)

**Closed issues:**

- Add Modern UI HTML Report to --html Option [\#2458](https://github.com/locustio/locust/issues/2458)

**Merged pull requests:**

- List Andrew as maintainer of the Modern web UI [\#2460](https://github.com/locustio/locust/pull/2460) ([cyberw](https://github.com/cyberw))
- Add Modern UI HTML Report to --html Option [\#2459](https://github.com/locustio/locust/pull/2459) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Modern UI: Add sorting to columns on statistics page and downloaded report [\#2453](https://github.com/locustio/locust/pull/2453) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.18.2](https://github.com/locustio/locust/tree/2.18.2) (2023-11-10)

[Full Changelog](https://github.com/locustio/locust/compare/2.18.1...2.18.2)

**Fixed bugs:**

- 2.18 - fasthttp error for no content response [\#2450](https://github.com/locustio/locust/issues/2450)
- Segmentation fault running the locust command [\#2447](https://github.com/locustio/locust/issues/2447)

**Merged pull requests:**

- Add terraform variables [\#2455](https://github.com/locustio/locust/pull/2455) ([sdarwin](https://github.com/sdarwin))
- FastHttpUser: encoding return str when response is empty [\#2451](https://github.com/locustio/locust/pull/2451) ([scottARob](https://github.com/scottARob))
- Fix docs: modern UI developing guide [\#2446](https://github.com/locustio/locust/pull/2446) ([zifter](https://github.com/zifter))

## [2.18.1](https://github.com/locustio/locust/tree/2.18.1) (2023-11-01)

[Full Changelog](https://github.com/locustio/locust/compare/2.18.0...2.18.1)

**Fixed bugs:**

- Modern UI shows wrong \(old\) hostname when setting hostname in start dialog [\#2435](https://github.com/locustio/locust/issues/2435)
- Unable to load multiple custom shape classes in web UI from --class-picker [\#2412](https://github.com/locustio/locust/issues/2412)

**Closed issues:**

- Add Log Viewer to Modern UI [\#2437](https://github.com/locustio/locust/issues/2437)

**Merged pull requests:**

- Log unhandled exceptions thrown in User.on\_start [\#2442](https://github.com/locustio/locust/pull/2442) ([cyberw](https://github.com/cyberw))
- Fix for UserClass picker not loading all available Shape Classes [\#2441](https://github.com/locustio/locust/pull/2441) ([mikenester](https://github.com/mikenester))
- Add Log Viewer to Modern UI [\#2440](https://github.com/locustio/locust/pull/2440) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Modern UI shows wrong \(old\) hostname when setting hostname in start dialog [\#2436](https://github.com/locustio/locust/pull/2436) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.18.0](https://github.com/locustio/locust/tree/2.18.0) (2023-10-26)

[Full Changelog](https://github.com/locustio/locust/compare/2.17.0...2.18.0)

**Fixed bugs:**

- Pacing and RPS trouble [\#2427](https://github.com/locustio/locust/issues/2427)
- Content-Type with version information is not properly parsed [\#2415](https://github.com/locustio/locust/issues/2415)

**Closed issues:**

- Modernize the report.html when using the --modern-ui Flag [\#2419](https://github.com/locustio/locust/issues/2419)
- Proposal for Re-Writing the Web UI [\#2396](https://github.com/locustio/locust/issues/2396)

**Merged pull requests:**

- Revert support for argcomplete [\#2434](https://github.com/locustio/locust/pull/2434) ([cyberw](https://github.com/cyberw))
- refactor\(MasterRunner\): simplify condition in check\_stopped [\#2432](https://github.com/locustio/locust/pull/2432) ([tdadela](https://github.com/tdadela))
- Fix too long first wait time for constant\_pacing \(and constant\_throughput\) [\#2428](https://github.com/locustio/locust/pull/2428) ([cyberw](https://github.com/cyberw))
- Support argcomplete as an optional dependency [\#2423](https://github.com/locustio/locust/pull/2423) ([singingwolfboy](https://github.com/singingwolfboy))
- Stop supporting Python 3.7 [\#2421](https://github.com/locustio/locust/pull/2421) ([cyberw](https://github.com/cyberw))
- \[Feature/2419\] Modernize the report.html when using the --modern-ui Flag [\#2420](https://github.com/locustio/locust/pull/2420) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Add run\_single\_user to \_\_all\_\_ variable [\#2417](https://github.com/locustio/locust/pull/2417) ([tdadela](https://github.com/tdadela))
- Make FastHttpUser use requests encoding detection [\#2416](https://github.com/locustio/locust/pull/2416) ([cyberw](https://github.com/cyberw))
- Add a modern web UI based on React, MaterialUI and Vite [\#2405](https://github.com/locustio/locust/pull/2405) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.17.0](https://github.com/locustio/locust/tree/2.17.0) (2023-10-05)

[Full Changelog](https://github.com/locustio/locust/compare/2.16.1...2.17.0)

**Fixed bugs:**

- Cannot stop locust in case of exceptions in on\_stop\(\) [\#2401](https://github.com/locustio/locust/issues/2401)

**Closed issues:**

- Dropdown menu in web UI for custom arguments [\#2371](https://github.com/locustio/locust/issues/2371)

**Merged pull requests:**

- Test and explicitly support Python 3.12 [\#2411](https://github.com/locustio/locust/pull/2411) ([cyberw](https://github.com/cyberw))
- Improve performance for statistics handling [\#2410](https://github.com/locustio/locust/pull/2410) ([cyberw](https://github.com/cyberw))
- Log a deprecation warning in Python 3.7 [\#2403](https://github.com/locustio/locust/pull/2403) ([cyberw](https://github.com/cyberw))
- Catch exceptions in on\_stop [\#2402](https://github.com/locustio/locust/pull/2402) ([cyberw](https://github.com/cyberw))
- Allow LoadTestShapes to reuse run-time, spawn-rate and users parameters [\#2395](https://github.com/locustio/locust/pull/2395) ([noirbizarre](https://github.com/noirbizarre))
- Support user abstract load shape base classes [\#2393](https://github.com/locustio/locust/pull/2393) ([noirbizarre](https://github.com/noirbizarre))
- chore: bump dockerfile to 3.11-slim base image [\#2388](https://github.com/locustio/locust/pull/2388) ([vejmoj1](https://github.com/vejmoj1))
- Respect hard limit when setting open file limit \(NOFILE\) [\#2386](https://github.com/locustio/locust/pull/2386) ([benofbrown](https://github.com/benofbrown))

## [2.16.1](https://github.com/locustio/locust/tree/2.16.1) (2023-08-07)

[Full Changelog](https://github.com/locustio/locust/compare/2.16.0...2.16.1)

**Merged pull requests:**

- Delay importing locust-plugins to prevent circular import [\#2380](https://github.com/locustio/locust/pull/2380) ([cyberw](https://github.com/cyberw))
- Import locust\_plugins if available to give access to its custom arguments [\#2379](https://github.com/locustio/locust/pull/2379) ([cyberw](https://github.com/cyberw))
- Deprecate LOCUST\_PLAYWRIGHT env var [\#2378](https://github.com/locustio/locust/pull/2378) ([cyberw](https://github.com/cyberw))

## [2.16.0](https://github.com/locustio/locust/tree/2.16.0) (2023-08-04)

[Full Changelog](https://github.com/locustio/locust/compare/2.15.1...2.16.0)

**Fixed bugs:**

- Bug in StagesShapeWithCustomUsers [\#2358](https://github.com/locustio/locust/issues/2358)
- Fail to spawn fixed users when run with DoubleWave load shape [\#2345](https://github.com/locustio/locust/issues/2345)
- KeyboardInterrupt does not gracefully exit custom load shape [\#1910](https://github.com/locustio/locust/issues/1910)

**Merged pull requests:**

- Fix \#1910 KeyboardInterrupt with load shapes [\#2375](https://github.com/locustio/locust/pull/2375) ([JevonCowell](https://github.com/JevonCowell))
- update links to requests homepage [\#2373](https://github.com/locustio/locust/pull/2373) ([evgeni](https://github.com/evgeni))
- Web UI dropdown for custom args with choices [\#2372](https://github.com/locustio/locust/pull/2372) ([ktrnka](https://github.com/ktrnka))
- Fix passing host to user class when debugging [\#2365](https://github.com/locustio/locust/pull/2365) ([LKajan](https://github.com/LKajan))
- Allow selecting user classes using LOCUST\_USER\_CLASSES env var [\#2355](https://github.com/locustio/locust/pull/2355) ([ibarbech](https://github.com/ibarbech))
- Clarify documentation string for `total_content_length` [\#2354](https://github.com/locustio/locust/pull/2354) ([johenning](https://github.com/johenning))
- Update rest.py [\#2352](https://github.com/locustio/locust/pull/2352) ([BhattcharyaCodes](https://github.com/BhattcharyaCodes))
- Fixed the users dispatching when it got infinite loop \(fixes \#2345\) [\#2350](https://github.com/locustio/locust/pull/2350) ([EzR1d3r](https://github.com/EzR1d3r))
- Duplicated titles [\#2346](https://github.com/locustio/locust/pull/2346) ([Daemo00](https://github.com/Daemo00))
- Add worker\_connect event [\#2344](https://github.com/locustio/locust/pull/2344) ([cyberw](https://github.com/cyberw))
- Remove codecov from build [\#2337](https://github.com/locustio/locust/pull/2337) ([cyberw](https://github.com/cyberw))
- Put dependencies/project information in pyproject.toml instead of setup.cfg \(PEP621\) [\#2336](https://github.com/locustio/locust/pull/2336) ([JE-Chen](https://github.com/JE-Chen))
- Rename link text on README.md [\#2334](https://github.com/locustio/locust/pull/2334) ([JE-Chen](https://github.com/JE-Chen))
- Fix: show host url [\#2324](https://github.com/locustio/locust/pull/2324) ([zifter](https://github.com/zifter))

## [2.15.1](https://github.com/locustio/locust/tree/2.15.1) (2023-03-14)

[Full Changelog](https://github.com/locustio/locust/compare/2.15.0...2.15.1)

**Closed issues:**

- Ability to specify percentiles you need for response time chart [\#2311](https://github.com/locustio/locust/issues/2311)
- locust k8s operator [\#2188](https://github.com/locustio/locust/issues/2188)

**Merged pull requests:**

- Update helper text [\#2317](https://github.com/locustio/locust/pull/2317) ([rafaelhdr](https://github.com/rafaelhdr))
- Add PERCENTILES\_TO\_CHART param in stats.py to make the Response Time Chart configurable [\#2313](https://github.com/locustio/locust/pull/2313) ([A1BOCO](https://github.com/A1BOCO))

## [2.15.0](https://github.com/locustio/locust/tree/2.15.0) (2023-02-28)

[Full Changelog](https://github.com/locustio/locust/compare/2.14.2...2.15.0)

**Fixed bugs:**

- "Download as PNG" text gets cut off [\#2307](https://github.com/locustio/locust/issues/2307)
- New worker fails to connect until master restart [\#2302](https://github.com/locustio/locust/issues/2302)

**Merged pull requests:**

- Fix locustio/locust\#2302 unknown worker spawning message [\#2309](https://github.com/locustio/locust/pull/2309) ([ykvch](https://github.com/ykvch))
- Prevent Download as PNG text from getting cut off [\#2308](https://github.com/locustio/locust/pull/2308) ([allison-strandberg](https://github.com/allison-strandberg))
- Remove request\_success and request\_failure event handlers [\#2306](https://github.com/locustio/locust/pull/2306) ([cyberw](https://github.com/cyberw))
- Remove verbose FastHttpUser error messages [\#2301](https://github.com/locustio/locust/pull/2301) ([cyberw](https://github.com/cyberw))
- fix: docs describing running without web UI had improper flag -f. Cor… [\#2297](https://github.com/locustio/locust/pull/2297) ([adriangonciarz](https://github.com/adriangonciarz))
- Update performance estimates for modern Python and hardware [\#2295](https://github.com/locustio/locust/pull/2295) ([cyberw](https://github.com/cyberw))
- docs \(\#2188\):  Add Locust Kubernetes Operator [\#2288](https://github.com/locustio/locust/pull/2288) ([AbdelrhmanHamouda](https://github.com/AbdelrhmanHamouda))
- add events when initialize Environment [\#2285](https://github.com/locustio/locust/pull/2285) ([keegoo](https://github.com/keegoo))
- add is\_secret option for custom args to be shown in the web UI masked [\#2284](https://github.com/locustio/locust/pull/2284) ([mzhukovs](https://github.com/mzhukovs))

## [2.14.2](https://github.com/locustio/locust/tree/2.14.2) (2023-01-04)

[Full Changelog](https://github.com/locustio/locust/compare/2.14.1...2.14.2)

**Fixed bugs:**

- 2.14.1 release missing py.typed file [\#2282](https://github.com/locustio/locust/issues/2282)

## [2.14.1](https://github.com/locustio/locust/tree/2.14.1) (2023-01-03)

[Full Changelog](https://github.com/locustio/locust/compare/2.14.0...2.14.1)

**Fixed bugs:**

- SetuptoolsDeprecationWarning when building with setuptools/65.5.0 [\#2279](https://github.com/locustio/locust/issues/2279)
- Error installing locust using pipenv as a -- [\#2277](https://github.com/locustio/locust/issues/2277)

**Merged pull requests:**

- Fix setuptools deprecation warnings [\#2281](https://github.com/locustio/locust/pull/2281) ([heyman](https://github.com/heyman))
- Improve documentation structure [\#2278](https://github.com/locustio/locust/pull/2278) ([THUzxj](https://github.com/THUzxj))
- Fix exception grouping for requests with both catch\_response and name arguments [\#2276](https://github.com/locustio/locust/pull/2276) ([ianmetcalf](https://github.com/ianmetcalf))
- remove typo in running cloud integration docs [\#2275](https://github.com/locustio/locust/pull/2275) ([WordsofDefiance](https://github.com/WordsofDefiance))
- Stats in json to stdout \(new command line option --json\) [\#2269](https://github.com/locustio/locust/pull/2269) ([AndersSpringborg](https://github.com/AndersSpringborg))

## [2.14.0](https://github.com/locustio/locust/tree/2.14.0) (2022-12-13)

[Full Changelog](https://github.com/locustio/locust/compare/2.13.2...2.14.0)

**Merged pull requests:**

- Move the rest method into FastHttpUser instead of RestUser.  [\#2274](https://github.com/locustio/locust/pull/2274) ([cyberw](https://github.com/cyberw))
- Add RestUser [\#2273](https://github.com/locustio/locust/pull/2273) ([cyberw](https://github.com/cyberw))
- GRPC example - rewrite using interceptor [\#2272](https://github.com/locustio/locust/pull/2272) ([zifter](https://github.com/zifter))

## [2.13.2](https://github.com/locustio/locust/tree/2.13.2) (2022-12-09)

[Full Changelog](https://github.com/locustio/locust/compare/2.13.1...2.13.2)

**Fixed bugs:**

- docs: Small errors in docs [\#2253](https://github.com/locustio/locust/issues/2253)

**Closed issues:**

- UnboundLocalError after receiving ZMQ corrupted message [\#2260](https://github.com/locustio/locust/issues/2260)

**Merged pull requests:**

- Fix: Ask worker to reconnect if master gets a broken RPC message [\#2271](https://github.com/locustio/locust/pull/2271) ([marcinh](https://github.com/marcinh))

## [2.13.1](https://github.com/locustio/locust/tree/2.13.1) (2022-12-01)

[Full Changelog](https://github.com/locustio/locust/compare/2.13.0...2.13.1)

**Fixed bugs:**

- locust.io is down [\#2265](https://github.com/locustio/locust/issues/2265)
- locust 2.13.0 failed to run [\#2263](https://github.com/locustio/locust/issues/2263)
- Issue installing on M1 Mac [\#2249](https://github.com/locustio/locust/issues/2249)
- 'Namespace' object has no attribute 'stop\_timeout' in version 2.13.0 [\#2243](https://github.com/locustio/locust/issues/2243)

**Closed issues:**

- locust test flask application [\#2255](https://github.com/locustio/locust/issues/2255)

**Merged pull requests:**

- Dont reset connection to worker if master receives a corrupted zmq message [\#2266](https://github.com/locustio/locust/pull/2266) ([marcinh](https://github.com/marcinh))
- auto generated locustfiles from browser recordings using har2locust \(documentation\) [\#2259](https://github.com/locustio/locust/pull/2259) ([cyberw](https://github.com/cyberw))
- Small fixes to documentation [\#2254](https://github.com/locustio/locust/pull/2254) ([jscanlannyc](https://github.com/jscanlannyc))
- Added a better working docker command for Windows users [\#2248](https://github.com/locustio/locust/pull/2248) ([MagnusNordboe](https://github.com/MagnusNordboe))
- Update documentation for Environment.parsed\_options [\#2247](https://github.com/locustio/locust/pull/2247) ([klazuka](https://github.com/klazuka))
- Use C-style \(percent\) string formatting for all debug logging statements \(improves performance\) [\#2245](https://github.com/locustio/locust/pull/2245) ([cyberw](https://github.com/cyberw))
- Replace datetime.utcnow\(\) with datetime.now\(tz=timezone.utc\), as it is kind of an antipattern [\#2244](https://github.com/locustio/locust/pull/2244) ([cyberw](https://github.com/cyberw))
- Tiny performance enhancements [\#2240](https://github.com/locustio/locust/pull/2240) ([cyberw](https://github.com/cyberw))

## [2.13.0](https://github.com/locustio/locust/tree/2.13.0) (2022-10-28)

[Full Changelog](https://github.com/locustio/locust/compare/2.12.2...2.13.0)

**Fixed bugs:**

- `LoadTestShape` not included in the API docs [\#2232](https://github.com/locustio/locust/issues/2232)
- ImportError: cannot import name 'OrderedDict' from 'typing' [\#2223](https://github.com/locustio/locust/issues/2223)

**Merged pull requests:**

- Fix issue with --stop timeout parsing time strings [\#2239](https://github.com/locustio/locust/pull/2239) ([cyberw](https://github.com/cyberw))
- Make LoadTestShape a proper abstract class [\#2233](https://github.com/locustio/locust/pull/2233) ([cyberw](https://github.com/cyberw))
- Add the ability to set default\_headers on FastHttpUser [\#2231](https://github.com/locustio/locust/pull/2231) ([cyberw](https://github.com/cyberw))
- URL link on the host name for fast navigation to the API [\#2228](https://github.com/locustio/locust/pull/2228) ([JonanOribe](https://github.com/JonanOribe))

## [2.12.2](https://github.com/locustio/locust/tree/2.12.2) (2022-10-14)

[Full Changelog](https://github.com/locustio/locust/compare/2.12.1...2.12.2)

**Fixed bugs:**

- Class picker incorrectly populates Parsed Options [\#2192](https://github.com/locustio/locust/issues/2192)

**Closed issues:**

- Run time input for web-ui [\#2198](https://github.com/locustio/locust/issues/2198)

**Merged pull requests:**

- Run unit tests on Python 3.11 \(and explicitly support it\) [\#2225](https://github.com/locustio/locust/pull/2225) ([cyberw](https://github.com/cyberw))
- Fix exception when someone sets both --headless and --autostart [\#2224](https://github.com/locustio/locust/pull/2224) ([cyberw](https://github.com/cyberw))
- Delete the `CustomMessageListener` class for type consistency [\#2221](https://github.com/locustio/locust/pull/2221) ([samuelspagl](https://github.com/samuelspagl))
- Output install location and version info when called with -V  [\#2213](https://github.com/locustio/locust/pull/2213) ([cyberw](https://github.com/cyberw))

## [2.12.1](https://github.com/locustio/locust/tree/2.12.1) (2022-09-21)

[Full Changelog](https://github.com/locustio/locust/compare/2.12.0...2.12.1)

**Fixed bugs:**

- Editing a running test in the Web UI with class-picker restarts user count back at 0 [\#2204](https://github.com/locustio/locust/issues/2204)

**Closed issues:**

- Add logger when worker is waiting for master to connect [\#2199](https://github.com/locustio/locust/issues/2199)
- Python 3.10 available for the latest docker hub hosted image  [\#2196](https://github.com/locustio/locust/issues/2196)

**Merged pull requests:**

- black format info is added [\#2212](https://github.com/locustio/locust/pull/2212) ([SamPosh](https://github.com/SamPosh))
- Second fix for --class-picker resetting user\_count on edits [\#2210](https://github.com/locustio/locust/pull/2210) ([mikenester](https://github.com/mikenester))
- Bug Fix for User Class Count reset when editing a running test and using --class-picker [\#2207](https://github.com/locustio/locust/pull/2207) ([mikenester](https://github.com/mikenester))
- Modernize type hints [\#2205](https://github.com/locustio/locust/pull/2205) ([cyberw](https://github.com/cyberw))
- Allow setting run time from the web UI / http api [\#2202](https://github.com/locustio/locust/pull/2202) ([ajt89](https://github.com/ajt89))
- Fix parsed options user classes when using class picker [\#2201](https://github.com/locustio/locust/pull/2201) ([mikenester](https://github.com/mikenester))
- Bump docker base image to Python 3.10 [\#2197](https://github.com/locustio/locust/pull/2197) ([cyberw](https://github.com/cyberw))
- stats summary refactoring [\#2193](https://github.com/locustio/locust/pull/2193) ([SamPosh](https://github.com/SamPosh))

## [2.12.0](https://github.com/locustio/locust/tree/2.12.0) (2022-09-07)

[Full Changelog](https://github.com/locustio/locust/compare/2.11.1...2.12.0)

**Fixed bugs:**

- WebUI `Edit running load test` not carried `user_classes` when enabled `--class-picker` [\#2170](https://github.com/locustio/locust/issues/2170)

**Merged pull requests:**

- Log warning if tag filtering gets rid of all tasks [\#2186](https://github.com/locustio/locust/pull/2186) ([cyberw](https://github.com/cyberw))
- GitHub Workflows security hardening [\#2184](https://github.com/locustio/locust/pull/2184) ([sashashura](https://github.com/sashashura))
- ft: LoadTestShapes with custom user classes  [\#2181](https://github.com/locustio/locust/pull/2181) ([samuelspagl](https://github.com/samuelspagl))
- Bump FastHttpUser/geventhttpclient dependency to 2.0.2 [\#2180](https://github.com/locustio/locust/pull/2180) ([cyberw](https://github.com/cyberw))
- Allow more recent versions of pyzmq \(it was only 23.0.0 that was broken\) [\#2179](https://github.com/locustio/locust/pull/2179) ([cyberw](https://github.com/cyberw))
- Bump default concurrency for fast http user to 10 [\#2177](https://github.com/locustio/locust/pull/2177) ([cyberw](https://github.com/cyberw))
- Web UI style fixes: about dialog cannot be opened in the startup page  [\#2173](https://github.com/locustio/locust/pull/2173) ([alterhu2020](https://github.com/alterhu2020))

## [2.11.1](https://github.com/locustio/locust/tree/2.11.1) (2022-08-25)

[Full Changelog](https://github.com/locustio/locust/compare/2.11.0...2.11.1)

**Merged pull requests:**

- Use more clear wording in --run-time reached stopping log message. [\#2172](https://github.com/locustio/locust/pull/2172) ([cyberw](https://github.com/cyberw))
- fix: edit load test missing the userclasses data [\#2171](https://github.com/locustio/locust/pull/2171) ([alterhu2020](https://github.com/alterhu2020))
- Fix custom message example in documentation [\#2165](https://github.com/locustio/locust/pull/2165) ([aathan](https://github.com/aathan))
- Fix broken link in cpu warning message. [\#2164](https://github.com/locustio/locust/pull/2164) ([conghuiw](https://github.com/conghuiw))
- Allow multiple definitions of same user class name if they come from the same place [\#2160](https://github.com/locustio/locust/pull/2160) ([cyberw](https://github.com/cyberw))
- Include worker\_index in worker connection logging, and stop using the word "client" for what is actually a worker [\#2159](https://github.com/locustio/locust/pull/2159) ([cyberw](https://github.com/cyberw))
- Upgrade GitHub Actions [\#2158](https://github.com/locustio/locust/pull/2158) ([cclauss](https://github.com/cclauss))
- Fix typo [\#2157](https://github.com/locustio/locust/pull/2157) ([cclauss](https://github.com/cclauss))

## [2.11.0](https://github.com/locustio/locust/tree/2.11.0) (2022-08-12)

[Full Changelog](https://github.com/locustio/locust/compare/2.10.2...2.11.0)

**Fixed bugs:**

- Not able to achieve high RPS \(3000 users, 20 workers, 32 vcpu-64 GB RAM\) [\#2154](https://github.com/locustio/locust/issues/2154)
- Flask 2.2.0 Update breaks request\_stats\_full\_history\_csv in web.py [\#2147](https://github.com/locustio/locust/issues/2147)
- "New test" with different number of users [\#2135](https://github.com/locustio/locust/issues/2135)

**Closed issues:**

- Use of different LoadTestShape classes in the same locust file [\#2151](https://github.com/locustio/locust/issues/2151)

**Merged pull requests:**

- Add example launch.json for debugging the whole Locust runtime in vscode [\#2156](https://github.com/locustio/locust/pull/2156) ([SamPosh](https://github.com/SamPosh))
- feat: add 'worker\_index' to WorkerRunner [\#2155](https://github.com/locustio/locust/pull/2155) ([gdm85](https://github.com/gdm85))
- chore: Remove misleading docstring in test [\#2153](https://github.com/locustio/locust/pull/2153) ([mboutet](https://github.com/mboutet))
- fix: Ensure new test starts with specified number of users after previous test has been stopped [\#2152](https://github.com/locustio/locust/pull/2152) ([mboutet](https://github.com/mboutet))
- Pass multiple Locustfiles and allow selecting User and Shape class from the WebUI [\#2137](https://github.com/locustio/locust/pull/2137) ([mikenester](https://github.com/mikenester))

## [2.10.2](https://github.com/locustio/locust/tree/2.10.2) (2022-08-03)

[Full Changelog](https://github.com/locustio/locust/compare/2.10.1...2.10.2)

**Fixed bugs:**

- \[SocketIOUser\] - I have provided the code to turn off the SSL certification but still, I'm getting an SSL certification error [\#2144](https://github.com/locustio/locust/issues/2144)
- HTML Report does not correctly escape statistics data [\#2126](https://github.com/locustio/locust/issues/2126)
- "Stop" hang on "stopping" state  when there are more than one workers in distributed mode. [\#2111](https://github.com/locustio/locust/issues/2111)

**Closed issues:**

- Html report:  table should be sortable [\#2132](https://github.com/locustio/locust/issues/2132)
- Funny resource URL prefix disallows using locust behind nginx proxy [\#2030](https://github.com/locustio/locust/issues/2030)

**Merged pull requests:**

- Fix for Flask 2.2.0 breaking changes [\#2148](https://github.com/locustio/locust/pull/2148) ([mikenester](https://github.com/mikenester))
- style: add a report favicon [\#2145](https://github.com/locustio/locust/pull/2145) ([Pactortester](https://github.com/Pactortester))
- Better error message when User.task is set instead of User.tasks [\#2142](https://github.com/locustio/locust/pull/2142) ([cyberw](https://github.com/cyberw))
- Minor edits to the documentation [\#2140](https://github.com/locustio/locust/pull/2140) ([sosna](https://github.com/sosna))
- Small documentation correction [\#2138](https://github.com/locustio/locust/pull/2138) ([andybyrne](https://github.com/andybyrne))
- Log a warning for failed attempts to connect to master [\#2136](https://github.com/locustio/locust/pull/2136) ([gdm85](https://github.com/gdm85))
- Test Report: Implement table sorting [\#2134](https://github.com/locustio/locust/pull/2134) ([Likqez](https://github.com/Likqez))
- fix: Fix typo at user/wait\_time.py [\#2133](https://github.com/locustio/locust/pull/2133) ([DmytroLitvinov](https://github.com/DmytroLitvinov))
- Fix escaping for exceptions in normal web ui \(related to \#2126\) [\#2131](https://github.com/locustio/locust/pull/2131) ([herrmanntom](https://github.com/herrmanntom))
- Replace the MD5 usage by SHA256 [\#2130](https://github.com/locustio/locust/pull/2130) ([RenanGBarreto](https://github.com/RenanGBarreto))
- Escape user supplied data in html report \(\#2126\) [\#2127](https://github.com/locustio/locust/pull/2127) ([herrmanntom](https://github.com/herrmanntom))

## [2.10.1](https://github.com/locustio/locust/tree/2.10.1) (2022-06-28)

[Full Changelog](https://github.com/locustio/locust/compare/2.10.0...2.10.1)

**Merged pull requests:**

- Increase CONNECT\_RETRY\_COUNT to avoid workers giving up too soon if master is not up yet [\#2125](https://github.com/locustio/locust/pull/2125) ([cyberw](https://github.com/cyberw))

## [2.10.0](https://github.com/locustio/locust/tree/2.10.0) (2022-06-27)

[Full Changelog](https://github.com/locustio/locust/compare/2.9.0...2.10.0)

**Closed issues:**

- Add ACK for worker connection [\#2044](https://github.com/locustio/locust/issues/2044)

**Merged pull requests:**

- Remove timeout parameter from FastHttpUser unit tests [\#2123](https://github.com/locustio/locust/pull/2123) ([cyberw](https://github.com/cyberw))
- Convert url for getting tasks to relative [\#2121](https://github.com/locustio/locust/pull/2121) ([5imun](https://github.com/5imun))
- More robust handling of ZMQ/RPC errors [\#2120](https://github.com/locustio/locust/pull/2120) ([solowalker27](https://github.com/solowalker27))
- Update the link for reporting data to a database [\#2119](https://github.com/locustio/locust/pull/2119) ([AlexMooney](https://github.com/AlexMooney))
- fix: stopping state when running more than one worker node. [\#2116](https://github.com/locustio/locust/pull/2116) ([renato-farias](https://github.com/renato-farias))
- add support for custom SSLContext when using FastHttpUser [\#2113](https://github.com/locustio/locust/pull/2113) ([renato-farias](https://github.com/renato-farias))
- chore: Set permissions for GitHub actions [\#2107](https://github.com/locustio/locust/pull/2107) ([naveensrinivasan](https://github.com/naveensrinivasan))
- additional typing improvements [\#2106](https://github.com/locustio/locust/pull/2106) ([mgor](https://github.com/mgor))
- Stop client\_listener from raising a KeyError when receiving a client\_stopped message from unknown worker [\#2102](https://github.com/locustio/locust/pull/2102) ([BirdLearn](https://github.com/BirdLearn))
- Fix multiple resetting connection after RPCError [\#2096](https://github.com/locustio/locust/pull/2096) ([Nosibb](https://github.com/Nosibb))
- Add ack for worker connection [\#2077](https://github.com/locustio/locust/pull/2077) ([Nosibb](https://github.com/Nosibb))

## [2.9.0](https://github.com/locustio/locust/tree/2.9.0) (2022-05-19)

[Full Changelog](https://github.com/locustio/locust/compare/2.8.6...2.9.0)

**Fixed bugs:**

- Locust is not starting with pyzmq 23.0.0 [\#2099](https://github.com/locustio/locust/issues/2099)
- Users with `fixed_count` not being relocated after rebalance [\#2091](https://github.com/locustio/locust/issues/2091)
- jinja2.exceptions.TemplateAssertionError: no test named 'boolean' when attempting to visit UI [\#2087](https://github.com/locustio/locust/issues/2087)
- Output is not saved to CSV when using LoadTestShape [\#2075](https://github.com/locustio/locust/issues/2075)
- New jinja2 pinning makes it impossible to build our codebase [\#2061](https://github.com/locustio/locust/issues/2061)
- `test_start` event triggered multiple times on workers [\#1986](https://github.com/locustio/locust/issues/1986)

**Merged pull requests:**

- avoid using pyzmq 23. Fixes  \#2099 [\#2100](https://github.com/locustio/locust/pull/2100) ([cyberw](https://github.com/cyberw))
- dispatch: rebalance users with a fixed count [\#2093](https://github.com/locustio/locust/pull/2093) ([andydunstall](https://github.com/andydunstall))
- Remove explicit version requirement for jinja2 [\#2090](https://github.com/locustio/locust/pull/2090) ([cyberw](https://github.com/cyberw))
- print\_stats table width fix for \#2084 [\#2088](https://github.com/locustio/locust/pull/2088) ([mgor](https://github.com/mgor))
- Move CSV stats printer gevent spawn up a few lines [\#2085](https://github.com/locustio/locust/pull/2085) ([max-rocket-internet](https://github.com/max-rocket-internet))
- uniform style of stats/report ascii tables [\#2084](https://github.com/locustio/locust/pull/2084) ([mgor](https://github.com/mgor))
- FastHttpUser improvements \(including a rename of parameter "url" to "path"\) [\#2083](https://github.com/locustio/locust/pull/2083) ([mgor](https://github.com/mgor))
- Add table linkage, you can see the data of the three tables at the sa… [\#2082](https://github.com/locustio/locust/pull/2082) ([helloNice](https://github.com/helloNice))
- Drop support for Python 3.6 [\#2080](https://github.com/locustio/locust/pull/2080) ([cyberw](https://github.com/cyberw))
- Ensure `test_start` is run to completion on worker [\#2072](https://github.com/locustio/locust/pull/2072) ([mboutet](https://github.com/mboutet))
- modernized build [\#2070](https://github.com/locustio/locust/pull/2070) ([mgor](https://github.com/mgor))

## [2.8.6](https://github.com/locustio/locust/tree/2.8.6) (2022-04-07)

[Full Changelog](https://github.com/locustio/locust/compare/2.8.5...2.8.6)

**Merged pull requests:**

- Further slim docker image [\#2068](https://github.com/locustio/locust/pull/2068) ([cyberw](https://github.com/cyberw))
- Add cpu\_warning event, so listeners can do some action when CPU usage is too high [\#2067](https://github.com/locustio/locust/pull/2067) ([cyberw](https://github.com/cyberw))
- Fix typo in example in docs [\#2064](https://github.com/locustio/locust/pull/2064) ([chalex2k](https://github.com/chalex2k))
- Move lint tests to their own tox environments [\#2062](https://github.com/locustio/locust/pull/2062) ([kurtmckee](https://github.com/kurtmckee))
- Bump black version to 22.3.0 [\#2060](https://github.com/locustio/locust/pull/2060) ([miedzinski](https://github.com/miedzinski))
- Support sharing connection pools between users [\#2059](https://github.com/locustio/locust/pull/2059) ([miedzinski](https://github.com/miedzinski))

## [2.8.5](https://github.com/locustio/locust/tree/2.8.5) (2022-03-28)

[Full Changelog](https://github.com/locustio/locust/compare/2.8.4...2.8.5)

**Merged pull requests:**

- fix some typos [\#2052](https://github.com/locustio/locust/pull/2052) ([cuishuang](https://github.com/cuishuang))

## [2.8.4](https://github.com/locustio/locust/tree/2.8.4) (2022-03-15)

[Full Changelog](https://github.com/locustio/locust/compare/2.8.3...2.8.4)

**Fixed bugs:**

- Locust while running as library with grpc client not outputting stats [\#1969](https://github.com/locustio/locust/issues/1969)
- Locust does not stop all users [\#1947](https://github.com/locustio/locust/issues/1947)

**Closed issues:**

- Introduce test\_stopping event [\#2031](https://github.com/locustio/locust/issues/2031)

**Merged pull requests:**

- Add quit event, used for getting locust's exit code just before exit [\#2049](https://github.com/locustio/locust/pull/2049) ([DennisKrone](https://github.com/DennisKrone))
- Bugfix/1947 locust does not stop all users [\#2041](https://github.com/locustio/locust/pull/2041) ([marcinh](https://github.com/marcinh))
- fixing mypy errors with loosest rules [\#2040](https://github.com/locustio/locust/pull/2040) ([mgor](https://github.com/mgor))
- Add test\_stopping event [\#2033](https://github.com/locustio/locust/pull/2033) ([marcinh](https://github.com/marcinh))
- fixed load/users getting distributed to missing worker [\#2010](https://github.com/locustio/locust/pull/2010) ([radhakrishnaakamat](https://github.com/radhakrishnaakamat))

## [2.8.3](https://github.com/locustio/locust/tree/2.8.3) (2022-02-25)

[Full Changelog](https://github.com/locustio/locust/compare/2.8.2...2.8.3)

**Merged pull requests:**

- Ran pyupgrade on the code base, removing various "Python2-isms". [\#2032](https://github.com/locustio/locust/pull/2032) ([cyberw](https://github.com/cyberw))
- Ensure users are distributed evently across hosts during ramp up [\#2025](https://github.com/locustio/locust/pull/2025) ([cyberw](https://github.com/cyberw))
- Bump minimum required gevent version to 20.12.1 [\#2023](https://github.com/locustio/locust/pull/2023) ([cyberw](https://github.com/cyberw))
- Fix typos [\#2022](https://github.com/locustio/locust/pull/2022) ([kianmeng](https://github.com/kianmeng))

## [2.8.2](https://github.com/locustio/locust/tree/2.8.2) (2022-02-14)

[Full Changelog](https://github.com/locustio/locust/compare/2.8.1...2.8.2)

**Fixed bugs:**

- Issue to install python libraries inside locust container when using the locust docker image version 2.8.1 [\#2015](https://github.com/locustio/locust/issues/2015)

**Merged pull requests:**

- Dockerfile: Fix permissions in venv to allow installing packages in derived images [\#2016](https://github.com/locustio/locust/pull/2016) ([cyberw](https://github.com/cyberw))
- Fix locust version in docker image \(lose the .dev0\) [\#2014](https://github.com/locustio/locust/pull/2014) ([cyberw](https://github.com/cyberw))

## [2.8.1](https://github.com/locustio/locust/tree/2.8.1) (2022-02-13)

[Full Changelog](https://github.com/locustio/locust/compare/2.8.0...2.8.1)

**Fixed bugs:**

- Load being distributed to missing workers too Version 2.7.4.dev14 [\#2008](https://github.com/locustio/locust/issues/2008)

**Merged pull requests:**

- Dockerfile: use a builder image to further optimize image size [\#2013](https://github.com/locustio/locust/pull/2013) ([cyberw](https://github.com/cyberw))

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
- Fix docs with underscore postfix for hyperlink? [\#1979](https://github.com/locustio/locust/pull/1979) ([jeroenhe](https://github.com/jeroenhe))
- Repair broken hyperlinks in documentation [\#1978](https://github.com/locustio/locust/pull/1978) ([jeroenhe](https://github.com/jeroenhe))

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
- Fix a typo [\#1665](https://github.com/locustio/locust/pull/1665) ([atkei](https://github.com/atkei))
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
- update \_\_init\_\_ file [\#1409](https://github.com/locustio/locust/pull/1409) ([iamtechnomage](https://github.com/iamtechnomage))
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



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
