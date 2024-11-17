# Detailed changelog
The most important changes can also be found in [the documentation](https://docs.locust.io/en/latest/changelog.html).

## [2.32.3](https://github.com/locustio/locust/tree/2.32.3) (2024-11-17)

[Full Changelog](https://github.com/locustio/locust/compare/2.32.2...2.32.3)

**Fixed bugs:**

- Setuptools CVE-2022-40897 [\#2986](https://github.com/locustio/locust/issues/2986)
- master crash with different version worker [\#2975](https://github.com/locustio/locust/issues/2975)

**Merged pull requests:**

- Ensure we never use old version of setuptools [\#2988](https://github.com/locustio/locust/pull/2988) ([cyberw](https://github.com/cyberw))
- README Themed Screenshots [\#2985](https://github.com/locustio/locust/pull/2985) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- When specifying locustfile fia url, output start of response text when it wasnt valid python [\#2983](https://github.com/locustio/locust/pull/2983) ([cyberw](https://github.com/cyberw))
- Use debug log level for first 5s of waiting for workers to be ready. [\#2982](https://github.com/locustio/locust/pull/2982) ([cyberw](https://github.com/cyberw))
- Add option for Extra Options to be Required [\#2981](https://github.com/locustio/locust/pull/2981) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Update ruff mypy [\#2978](https://github.com/locustio/locust/pull/2978) ([tdadela](https://github.com/tdadela))
- Fix crash with older worker version requesting locustfile from master [\#2976](https://github.com/locustio/locust/pull/2976) ([cyberw](https://github.com/cyberw))
- Use f-strings instead of old style string interpolation [\#2974](https://github.com/locustio/locust/pull/2974) ([tdadela](https://github.com/tdadela))

## [2.32.2](https://github.com/locustio/locust/tree/2.32.2) (2024-11-08)

[Full Changelog](https://github.com/locustio/locust/compare/2.32.1...2.32.2)

**Fixed bugs:**

- Requests not ramping up after switching to using pydantic in django project [\#2960](https://github.com/locustio/locust/issues/2960)
- The locust chart shows that data is still being recorded after the timed run time expires [\#2910](https://github.com/locustio/locust/issues/2910)

**Closed issues:**

- Downloading report should provide a meaningful human name [\#2931](https://github.com/locustio/locust/issues/2931)
- Hard coded path make it impossible to host the UI on a path \(instead of the domain root\) [\#2909](https://github.com/locustio/locust/issues/2909)

**Merged pull requests:**

- Fix Incorrectly Updating Stat History [\#2972](https://github.com/locustio/locust/pull/2972) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Webui Add Markdown Support for Auth Page [\#2969](https://github.com/locustio/locust/pull/2969) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Fix Web Base Path Env Variable [\#2967](https://github.com/locustio/locust/pull/2967) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Locust Configurable Web Base Path [\#2966](https://github.com/locustio/locust/pull/2966) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Fix Auth Args Type [\#2965](https://github.com/locustio/locust/pull/2965) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Webui Add Auth Info to Auth Page [\#2963](https://github.com/locustio/locust/pull/2963) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Fix doc link [\#2961](https://github.com/locustio/locust/pull/2961) ([tjandy98](https://github.com/tjandy98))
- Report name [\#2947](https://github.com/locustio/locust/pull/2947) ([obriat](https://github.com/obriat))

## [2.32.1](https://github.com/locustio/locust/tree/2.32.1) (2024-10-29)

[Full Changelog](https://github.com/locustio/locust/compare/2.32.0...2.32.1)

**Closed issues:**

- Add option to enable different statistics in the chart menu [\#2946](https://github.com/locustio/locust/issues/2946)

**Merged pull requests:**

- Webui Echarts Redraw Request Lines if Changed [\#2953](https://github.com/locustio/locust/pull/2953) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Webui Add Custom Form to Auth Page [\#2952](https://github.com/locustio/locust/pull/2952) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Webui Override Markdown HTML Link with MUI Link [\#2951](https://github.com/locustio/locust/pull/2951) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Webui Fix Echarts Axis Formatting [\#2950](https://github.com/locustio/locust/pull/2950) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Webui Echarts Time Axis Should be Localized [\#2949](https://github.com/locustio/locust/pull/2949) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Add Google Analytics to docs.locust.io [\#2948](https://github.com/locustio/locust/pull/2948) ([heyman](https://github.com/heyman))
- LocustBadStatusCode without url param in fasthttp [\#2944](https://github.com/locustio/locust/pull/2944) ([swaalt](https://github.com/swaalt))
- Web UI Remove Default Value for Select if Value is Provided [\#2943](https://github.com/locustio/locust/pull/2943) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Web UI Auth Add Password Visibility Toggle [\#2941](https://github.com/locustio/locust/pull/2941) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.32.0](https://github.com/locustio/locust/tree/2.32.0) (2024-10-15)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.8...2.32.0)

**Fixed bugs:**

- logfile is erroniously written when there are many workers.   [\#2927](https://github.com/locustio/locust/issues/2927)
- Form field for users, spawn rate, and run time still visible in UI although CustomShape defined without use\_common\_options. [\#2924](https://github.com/locustio/locust/issues/2924)
- --html with --process 4 then get ValueError: StatsEntry.use\_response\_times\_cache must be set to True  [\#2908](https://github.com/locustio/locust/issues/2908)
- IPV6 check doesn't work as expected on AWS EKS [\#2787](https://github.com/locustio/locust/issues/2787)

**Merged pull requests:**

- Log deprecation warning for Python 3.9 [\#2940](https://github.com/locustio/locust/pull/2940) ([cyberw](https://github.com/cyberw))
- Run tests on python 3.13 too [\#2939](https://github.com/locustio/locust/pull/2939) ([cyberw](https://github.com/cyberw))
- Web UI - Fix Line Chart [\#2935](https://github.com/locustio/locust/pull/2935) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Modern UI - Fix Hide Common Options [\#2934](https://github.com/locustio/locust/pull/2934) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Allow alerts and errors on new and edit form [\#2932](https://github.com/locustio/locust/pull/2932) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Add error message to swarm form [\#2930](https://github.com/locustio/locust/pull/2930) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Disable --csv for workers when using --processes. [\#2929](https://github.com/locustio/locust/pull/2929) ([cyberw](https://github.com/cyberw))
- Decide if ipv6 can work [\#2923](https://github.com/locustio/locust/pull/2923) ([nc-marco](https://github.com/nc-marco))
- Webui Add Form Alert [\#2922](https://github.com/locustio/locust/pull/2922) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Add faq item: Basic auth \(Authorization header\) does not work after redirection [\#2921](https://github.com/locustio/locust/pull/2921) ([obriat](https://github.com/obriat))
- Add CSRF example [\#2920](https://github.com/locustio/locust/pull/2920) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Web UI Add Exports for Library [\#2919](https://github.com/locustio/locust/pull/2919) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- lower log level for unnecessary --autostart argument [\#2918](https://github.com/locustio/locust/pull/2918) ([cyberw](https://github.com/cyberw))

## [2.31.8](https://github.com/locustio/locust/tree/2.31.8) (2024-09-28)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.7...2.31.8)

**Merged pull requests:**

- Log locust-cloud version if it is installed [\#2916](https://github.com/locustio/locust/pull/2916) ([cyberw](https://github.com/cyberw))
- Web UI Auth submit should submit a POST request [\#2915](https://github.com/locustio/locust/pull/2915) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Url in template arg [\#2914](https://github.com/locustio/locust/pull/2914) ([fletelli42](https://github.com/fletelli42))
- Fix RTD versioning with a deep git clone [\#2913](https://github.com/locustio/locust/pull/2913) ([mquinnfd](https://github.com/mquinnfd))

## [2.31.7](https://github.com/locustio/locust/tree/2.31.7) (2024-09-25)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.6...2.31.7)

**Merged pull requests:**

- Fix Dependabot Complaints [\#2912](https://github.com/locustio/locust/pull/2912) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Improve Web UI Logging [\#2911](https://github.com/locustio/locust/pull/2911) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Pin python versions to avoid gh caching issue + always Install Dependencies, even when it looks like there was a cache hit [\#2907](https://github.com/locustio/locust/pull/2907) ([cyberw](https://github.com/cyberw))
- Fix Login Manager Error Message [\#2905](https://github.com/locustio/locust/pull/2905) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Log locust version earlier [\#2904](https://github.com/locustio/locust/pull/2904) ([cyberw](https://github.com/cyberw))
- Add Mongodb test example [\#2903](https://github.com/locustio/locust/pull/2903) ([guel-codes](https://github.com/guel-codes))

## [2.31.6](https://github.com/locustio/locust/tree/2.31.6) (2024-09-15)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.5...2.31.6)

**Fixed bugs:**

- RPS vs Total Running Users [\#2895](https://github.com/locustio/locust/issues/2895)
- Overwriting weight by config-users may lead to crash [\#2852](https://github.com/locustio/locust/issues/2852)
- FastHttpSession requests typing for the json argument should support lists [\#2842](https://github.com/locustio/locust/issues/2842)
- Dockerfile warning [\#2811](https://github.com/locustio/locust/issues/2811)

**Closed issues:**

- Cleaning up the build process [\#2857](https://github.com/locustio/locust/issues/2857)
- Simplify GitHub Actions using install-poetry [\#2822](https://github.com/locustio/locust/issues/2822)

**Merged pull requests:**

- Add Error Message for Accessing Login Manager without --web-login [\#2902](https://github.com/locustio/locust/pull/2902) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Update Webui README [\#2901](https://github.com/locustio/locust/pull/2901) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Add worker\_count = 1 to LocalRunner for parity with MasterRunner [\#2900](https://github.com/locustio/locust/pull/2900) ([tarkatronic](https://github.com/tarkatronic))
- Remove redundant None in Any | None annotations [\#2892](https://github.com/locustio/locust/pull/2892) ([tdadela](https://github.com/tdadela))
- Fix \_kl\_generator by filtering nonpositive User weights [\#2891](https://github.com/locustio/locust/pull/2891) ([tdadela](https://github.com/tdadela))
- Update README.md [\#2889](https://github.com/locustio/locust/pull/2889) ([JonanOribe](https://github.com/JonanOribe))
- Filename from URL Should Strip Query Params [\#2887](https://github.com/locustio/locust/pull/2887) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Simplify Generator annotations - PEP 696 [\#2886](https://github.com/locustio/locust/pull/2886) ([tdadela](https://github.com/tdadela))
- Fix FastHttpSession.request json typing [\#2885](https://github.com/locustio/locust/pull/2885) ([tdadela](https://github.com/tdadela))

## [2.31.5](https://github.com/locustio/locust/tree/2.31.5) (2024-08-30)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.4...2.31.5)

**Fixed bugs:**

- Pressure testing is over, but RPS and Users still have data [\#2870](https://github.com/locustio/locust/issues/2870)

**Merged pull requests:**

- Ensure we don't accidentally hide errors while importing in locust-cloud or locust-plugins [\#2881](https://github.com/locustio/locust/pull/2881) ([cyberw](https://github.com/cyberw))
- Add publishing dependency on build package step [\#2880](https://github.com/locustio/locust/pull/2880) ([mquinnfd](https://github.com/mquinnfd))
- Build pipeline tweaks - docker tagging [\#2879](https://github.com/locustio/locust/pull/2879) ([mquinnfd](https://github.com/mquinnfd))
- Webui Remove chart initial data fetch [\#2878](https://github.com/locustio/locust/pull/2878) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Document use with uvx and remove openssl version from  --version output [\#2877](https://github.com/locustio/locust/pull/2877) ([cyberw](https://github.com/cyberw))
- Web UI Remove Scroll to Zoom [\#2876](https://github.com/locustio/locust/pull/2876) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Cleaning and improvements in the Build Pipeline [\#2873](https://github.com/locustio/locust/pull/2873) ([mquinnfd](https://github.com/mquinnfd))
- WebUI: Correct types for form select [\#2872](https://github.com/locustio/locust/pull/2872) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.31.4](https://github.com/locustio/locust/tree/2.31.4) (2024-08-26)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.3...2.31.4)

**Merged pull requests:**

- Webui Allow changing select input size [\#2871](https://github.com/locustio/locust/pull/2871) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Webui Replace Logo SVG [\#2867](https://github.com/locustio/locust/pull/2867) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Add favicon that looks good in light color theme [\#2866](https://github.com/locustio/locust/pull/2866) ([heyman](https://github.com/heyman))
- Webui Add build lib command to package.json [\#2865](https://github.com/locustio/locust/pull/2865) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Web UI Github Action Publish steps must Build lib [\#2864](https://github.com/locustio/locust/pull/2864) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Fix npm publish issue [\#2863](https://github.com/locustio/locust/pull/2863) ([cyberw](https://github.com/cyberw))
- GH actions: Update names of publish steps. Don't run prerelease steps when no prerelease is actually going to be published [\#2862](https://github.com/locustio/locust/pull/2862) ([cyberw](https://github.com/cyberw))
- Webui Fix Version Tag in NPM Prerelease Step [\#2861](https://github.com/locustio/locust/pull/2861) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Webui Fix NPM Publish Step [\#2860](https://github.com/locustio/locust/pull/2860) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Web UI as a Library NPM Release [\#2858](https://github.com/locustio/locust/pull/2858) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Add PostgresUser to examples [\#2836](https://github.com/locustio/locust/pull/2836) ([guel-codes](https://github.com/guel-codes))

## [2.31.3](https://github.com/locustio/locust/tree/2.31.3) (2024-08-15)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.2...2.31.3)

**Fixed bugs:**

- Brew installed locust missing UI assets [\#2831](https://github.com/locustio/locust/issues/2831)
- response avg time is NaN [\#2829](https://github.com/locustio/locust/issues/2829)
- Windows Action Runs Wrong Version of Locust [\#2796](https://github.com/locustio/locust/issues/2796)

**Merged pull requests:**

- Web UI Remove Echarts startValue [\#2855](https://github.com/locustio/locust/pull/2855) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Update GitHub action versions [\#2853](https://github.com/locustio/locust/pull/2853) ([cyberw](https://github.com/cyberw))
- Improve docs for --class-picker/--config-users and give better error messages if json is bad [\#2851](https://github.com/locustio/locust/pull/2851) ([cyberw](https://github.com/cyberw))
- Add missing margin between Logo and Host in Navbar [\#2850](https://github.com/locustio/locust/pull/2850) ([heyman](https://github.com/heyman))
- Web UI Should use Built-In Echarts Time Axis [\#2847](https://github.com/locustio/locust/pull/2847) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Webui Notification Improvements [\#2846](https://github.com/locustio/locust/pull/2846) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Use new logo in web UI + some minor improvements [\#2844](https://github.com/locustio/locust/pull/2844) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Webui Add Scatterplot Support [\#2840](https://github.com/locustio/locust/pull/2840) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.31.2](https://github.com/locustio/locust/tree/2.31.2) (2024-08-06)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.1...2.31.2)

**Merged pull requests:**

- Prebuild UI in PyPi publish steps so that even source distributions contain web UI code [\#2839](https://github.com/locustio/locust/pull/2839) ([mquinnfd](https://github.com/mquinnfd))
- Add Tests for Web UI Line Chart [\#2838](https://github.com/locustio/locust/pull/2838) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Documentation: Configure html\_baseurl and jinja on RTD [\#2837](https://github.com/locustio/locust/pull/2837) ([plaindocs](https://github.com/plaindocs))

## [2.31.1](https://github.com/locustio/locust/tree/2.31.1) (2024-08-05)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.0...2.31.1)

**Merged pull requests:**

- Fix issue with downloading HTML report, update package.json for webui build [\#2834](https://github.com/locustio/locust/pull/2834) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.31.0](https://github.com/locustio/locust/tree/2.31.0) (2024-08-05)

[Full Changelog](https://github.com/locustio/locust/compare/2.30.0...2.31.0)

**Merged pull requests:**

- Fix docker build for release [\#2830](https://github.com/locustio/locust/pull/2830) ([cyberw](https://github.com/cyberw))
- Github Actions: Use node 20.x \(fix PyPI Release and pre-Release Steps\) [\#2828](https://github.com/locustio/locust/pull/2828) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Improve Echarts and Expose Line and Axis Configuration [\#2826](https://github.com/locustio/locust/pull/2826) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Bump Node [\#2825](https://github.com/locustio/locust/pull/2825) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Integrations for Locust Cloud [\#2824](https://github.com/locustio/locust/pull/2824) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Fix HTML Report Stats Table [\#2817](https://github.com/locustio/locust/pull/2817) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Locust UI Charts Should Change Color Based on Theme [\#2815](https://github.com/locustio/locust/pull/2815) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Locust UI as a Module [\#2804](https://github.com/locustio/locust/pull/2804) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Log a message if total fixed\_count is higher than number of users to spawn [\#2793](https://github.com/locustio/locust/pull/2793) ([cyberw](https://github.com/cyberw))
- Simplify fixed\_count Users generation in UsersDispatcher.\_user\_gen [\#2783](https://github.com/locustio/locust/pull/2783) ([tdadela](https://github.com/tdadela))
- URL Directory, and Multi-File Support for Locustfile Distribution [\#2766](https://github.com/locustio/locust/pull/2766) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.30.0](https://github.com/locustio/locust/tree/2.30.0) (2024-07-31)

[Full Changelog](https://github.com/locustio/locust/compare/2.29.1...2.30.0)

**Fixed bugs:**

- Locust / pypy fails with "AttributeError: module 'gc' has no attribute 'freeze'" error. [\#2818](https://github.com/locustio/locust/issues/2818)
- Worker sometimes fails to send heartbeat after upgrade to urllib3\>=1.26.16 [\#2812](https://github.com/locustio/locust/issues/2812)
- Web UI lacking asset [\#2781](https://github.com/locustio/locust/issues/2781)

**Closed issues:**

- Charts Update Is Delayed [\#2771](https://github.com/locustio/locust/issues/2771)
- Use `itertools.cycle` in `SequentialTaskSet` [\#2740](https://github.com/locustio/locust/issues/2740)
- `SequentialTaskSet` handles task weights in an inconsistent way [\#2739](https://github.com/locustio/locust/issues/2739)

**Merged pull requests:**

- Update poetry windows tests [\#2821](https://github.com/locustio/locust/pull/2821) ([mquinnfd](https://github.com/mquinnfd))
- Fix pypy gc.freeze\(\) AttributeError [\#2819](https://github.com/locustio/locust/pull/2819) ([jimoleary](https://github.com/jimoleary))
- Fix Dockerfile style warning [\#2814](https://github.com/locustio/locust/pull/2814) ([mehrdadbn9](https://github.com/mehrdadbn9))
- Avoid deadlock in gevent/urllib3 connection pool \(fixes occasional worker heartbeat timeouts\) [\#2813](https://github.com/locustio/locust/pull/2813) ([tdadela](https://github.com/tdadela))
- Replace total avg response time with 50 percentile \(avg was broken\) [\#2806](https://github.com/locustio/locust/pull/2806) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Add example of a bottlenecked server and use that test to make a new graph for the docs [\#2805](https://github.com/locustio/locust/pull/2805) ([cyberw](https://github.com/cyberw))
- Fix tests on windows [\#2803](https://github.com/locustio/locust/pull/2803) ([mquinnfd](https://github.com/mquinnfd))
- Provide warning for local installs where yarn is not present [\#2801](https://github.com/locustio/locust/pull/2801) ([mquinnfd](https://github.com/mquinnfd))
- Fix Extend Webui Example [\#2800](https://github.com/locustio/locust/pull/2800) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Correctly set version from Poetry in published builds [\#2791](https://github.com/locustio/locust/pull/2791) ([mquinnfd](https://github.com/mquinnfd))
- Fix StatsEntry docstring [\#2784](https://github.com/locustio/locust/pull/2784) ([tdadela](https://github.com/tdadela))
- dispatch benchmark test improvements [\#2780](https://github.com/locustio/locust/pull/2780) ([tdadela](https://github.com/tdadela))
- Typing: strict optional in dispatch.py [\#2779](https://github.com/locustio/locust/pull/2779) ([tdadela](https://github.com/tdadela))
- new events for heartbeat and usage monitor [\#2777](https://github.com/locustio/locust/pull/2777) ([mgor](https://github.com/mgor))
- FastHttpSession requests typing  [\#2775](https://github.com/locustio/locust/pull/2775) ([tdadela](https://github.com/tdadela))
- Remove Line Chart Default Zoom [\#2774](https://github.com/locustio/locust/pull/2774) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- FastHttpSession: Enable passing json as a positional argument for post\(\) and stop converting response times to int [\#2772](https://github.com/locustio/locust/pull/2772) ([tdadela](https://github.com/tdadela))
- SequentialTaskSet: Allow weighted tasks and dict in .tasks [\#2742](https://github.com/locustio/locust/pull/2742) ([bakhtos](https://github.com/bakhtos))
- Implement Poetry build system \(mainly so we don't have to commit dynamically generated front end bundles to git\) [\#2725](https://github.com/locustio/locust/pull/2725) ([mquinnfd](https://github.com/mquinnfd))

## [2.29.1](https://github.com/locustio/locust/tree/2.29.1) (2024-06-25)

[Full Changelog](https://github.com/locustio/locust/compare/2.29.0...2.29.1)

**Fixed bugs:**

- locust/webui/dist/index.html script errors. [\#2753](https://github.com/locustio/locust/issues/2753)

**Merged pull requests:**

- Option to Skip Monkey Patching with LOCUST\_SKIP\_MONKEY\_PATCH [\#2765](https://github.com/locustio/locust/pull/2765) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- HttpSession: Improve error message when someone forgot to pass catch\_response=True + small optimization [\#2762](https://github.com/locustio/locust/pull/2762) ([cyberw](https://github.com/cyberw))
- Add JavaScript to MIME types for Windows Operating Systems [\#2759](https://github.com/locustio/locust/pull/2759) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Add proxy support for FastHttpUser [\#2758](https://github.com/locustio/locust/pull/2758) ([NicoAdrian](https://github.com/NicoAdrian))
- Httpsession requests typing [\#2699](https://github.com/locustio/locust/pull/2699) ([tdadela](https://github.com/tdadela))

## [2.29.0](https://github.com/locustio/locust/tree/2.29.0) (2024-06-07)

[Full Changelog](https://github.com/locustio/locust/compare/2.28.0...2.29.0)

**Fixed bugs:**

- The time of the downloaded html report is not correct [\#2691](https://github.com/locustio/locust/issues/2691)
- Event spawning\_complete fires every time a user is created [\#2671](https://github.com/locustio/locust/issues/2671)
- Delay at startup and high cpu usage on Windows in Python 3.12 [\#2555](https://github.com/locustio/locust/issues/2555)

**Closed issues:**

- Log a warning if getting locustfile from master takes more than 60s [\#2748](https://github.com/locustio/locust/issues/2748)
- Show the reset button even after stopping a test [\#2723](https://github.com/locustio/locust/issues/2723)
- Add date to charts in web UI [\#2678](https://github.com/locustio/locust/issues/2678)

**Merged pull requests:**

- Send logs from workers to master and improve log viewer tab in the Web UI [\#2750](https://github.com/locustio/locust/pull/2750) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Add Logging to download\_locustfile\_from\_master [\#2749](https://github.com/locustio/locust/pull/2749) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Modify timestamp generation to remove deprecation warning [\#2738](https://github.com/locustio/locust/pull/2738) ([JavierUhagon](https://github.com/JavierUhagon))
- Docs: Fix API TOC [\#2737](https://github.com/locustio/locust/pull/2737) ([plaindocs](https://github.com/plaindocs))
- Docs: Fix sphinx and theme upgrade [\#2736](https://github.com/locustio/locust/pull/2736) ([plaindocs](https://github.com/plaindocs))
- Docs: Fix theme [\#2735](https://github.com/locustio/locust/pull/2735) ([plaindocs](https://github.com/plaindocs))
- Docs: Import wiki to docs [\#2734](https://github.com/locustio/locust/pull/2734) ([plaindocs](https://github.com/plaindocs))
- Mention installing Locust in Building the Docs [\#2733](https://github.com/locustio/locust/pull/2733) ([plaindocs](https://github.com/plaindocs))
- Docs: Upgrade Sphinx to latest version \(7.3.7\) [\#2732](https://github.com/locustio/locust/pull/2732) ([plaindocs](https://github.com/plaindocs))
- Add date and zoom to charts in web UI [\#2731](https://github.com/locustio/locust/pull/2731) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Use requests 2.32.2 or higher for Python 3.12 [\#2730](https://github.com/locustio/locust/pull/2730) ([cyberw](https://github.com/cyberw))
- The time of the downloaded HTML report is not correct [\#2729](https://github.com/locustio/locust/pull/2729) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Ensure spawning\_complete only happens once on workers [\#2728](https://github.com/locustio/locust/pull/2728) ([cyberw](https://github.com/cyberw))
- Improve confusing log messages if someone accidentally accesses the Web UI over HTTPS [\#2727](https://github.com/locustio/locust/pull/2727) ([cyberw](https://github.com/cyberw))
- Show Reset Button when Test is Stopped [\#2726](https://github.com/locustio/locust/pull/2726) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.28.0](https://github.com/locustio/locust/tree/2.28.0) (2024-05-23)

[Full Changelog](https://github.com/locustio/locust/compare/2.27.0...2.28.0)

**Fixed bugs:**

- The Charts presentation in the report downloaded by locust is problematic [\#2706](https://github.com/locustio/locust/issues/2706)
- Locust insists on using IPv6 despite being in an IPv4 stack. [\#2689](https://github.com/locustio/locust/issues/2689)
- When there is an error in the FAILURES of the front-end page when there is a worker, there is no escape. [\#2674](https://github.com/locustio/locust/issues/2674)

**Closed issues:**

- Pin the headers and aggregated row to the top and bottom of the window [\#2688](https://github.com/locustio/locust/issues/2688)
- Remove legacy UI [\#2673](https://github.com/locustio/locust/issues/2673)
- TaskSet's `_task_queue` should be a `collections.deque`? [\#2653](https://github.com/locustio/locust/issues/2653)

**Merged pull requests:**

- Pin the headers to the top of the window [\#2717](https://github.com/locustio/locust/pull/2717) ([JavierUhagon](https://github.com/JavierUhagon))
- Dont enable ipv6 for zmq if no ipv6 stack exists [\#2715](https://github.com/locustio/locust/pull/2715) ([cyberw](https://github.com/cyberw))
- Give better error message if User subclass doesnt call base constructor [\#2713](https://github.com/locustio/locust/pull/2713) ([cyberw](https://github.com/cyberw))
- Stop quoting error messages an extra time in distributed mode [\#2712](https://github.com/locustio/locust/pull/2712) ([cyberw](https://github.com/cyberw))
- Lower log levels for exceptions in flask [\#2711](https://github.com/locustio/locust/pull/2711) ([cyberw](https://github.com/cyberw))
- Stop HTML escaping errors for /stats/requests endpoint [\#2710](https://github.com/locustio/locust/pull/2710) ([cyberw](https://github.com/cyberw))
- Update Stats History on HTML Report [\#2709](https://github.com/locustio/locust/pull/2709) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Logging: Only print hostname instead of FQDN [\#2705](https://github.com/locustio/locust/pull/2705) ([cyberw](https://github.com/cyberw))
- Remove legacy UI [\#2703](https://github.com/locustio/locust/pull/2703) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- WebUI: update users, spawn\_rate, host and run\_time in `parsed_options` \(for LoadShapes that might access it\) [\#2656](https://github.com/locustio/locust/pull/2656) ([raulparada](https://github.com/raulparada))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
