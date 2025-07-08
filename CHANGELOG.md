# Detailed changelog
The most important changes can also be found in [the documentation](https://docs.locust.io/en/latest/changelog.html).

## [2.37.12](https://github.com/locustio/locust/tree/2.37.12) (2025-07-08)

[Full Changelog](https://github.com/locustio/locust/compare/2.37.11...2.37.12)

**Fixed bugs:**

- Error shutting down when using processes [\#3161](https://github.com/locustio/locust/issues/3161)
- 1279 Locust instances makes master run at 100% continously [\#3142](https://github.com/locustio/locust/issues/3142)

**Merged pull requests:**

- Attempt to increase open file limit \(RLIMIT\_NOFILE\) even on master. [\#3162](https://github.com/locustio/locust/pull/3162) ([cyberw](https://github.com/cyberw))
- Bump brace-expansion from 1.1.11 to 1.1.12 in /locust/webui [\#3160](https://github.com/locustio/locust/pull/3160) ([dependabot[bot]](https://github.com/apps/dependabot))

## [2.37.11](https://github.com/locustio/locust/tree/2.37.11) (2025-06-23)

[Full Changelog](https://github.com/locustio/locust/compare/2.37.10...2.37.11)

**Fixed bugs:**

- FastHttpUser uses incorrect regex to hide home directory [\#3159](https://github.com/locustio/locust/issues/3159)

**Closed issues:**

- Define a list of paths to simulate an user journey [\#3150](https://github.com/locustio/locust/issues/3150)
- export the results as a json file [\#3089](https://github.com/locustio/locust/issues/3089)

**Merged pull requests:**

- Forward locustfiles to locust cloud [\#3157](https://github.com/locustio/locust/pull/3157) ([amadeuppereira](https://github.com/amadeuppereira))
- Web UI: Always Warn of Invalid Host [\#3155](https://github.com/locustio/locust/pull/3155) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.37.10](https://github.com/locustio/locust/tree/2.37.10) (2025-06-07)

[Full Changelog](https://github.com/locustio/locust/compare/2.37.9...2.37.10)

**Merged pull requests:**

- Revert accidental removal of --json-file option [\#3154](https://github.com/locustio/locust/pull/3154) ([brtkwr](https://github.com/brtkwr))

## [2.37.9](https://github.com/locustio/locust/tree/2.37.9) (2025-06-05)

[Full Changelog](https://github.com/locustio/locust/compare/2.37.8...2.37.9)

**Merged pull requests:**

- Web UI: Fix host field name missing if host is not required [\#3152](https://github.com/locustio/locust/pull/3152) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.37.8](https://github.com/locustio/locust/tree/2.37.8) (2025-06-05)

[Full Changelog](https://github.com/locustio/locust/compare/2.37.7...2.37.8)

**Closed issues:**

- Support gevent \>= 25.4.1 [\#3143](https://github.com/locustio/locust/issues/3143)

**Merged pull requests:**

- Bump locust-cloud dependency, allow 25.x versions of gevent [\#3151](https://github.com/locustio/locust/pull/3151) ([cyberw](https://github.com/cyberw))

## [2.37.7](https://github.com/locustio/locust/tree/2.37.7) (2025-06-03)

[Full Changelog](https://github.com/locustio/locust/compare/2.37.6...2.37.7)

**Merged pull requests:**

- Web Ui: Add host field validation [\#3149](https://github.com/locustio/locust/pull/3149) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.37.6](https://github.com/locustio/locust/tree/2.37.6) (2025-05-28)

[Full Changelog](https://github.com/locustio/locust/compare/2.37.5...2.37.6)

**Fixed bugs:**

- Documentation is Now Missing Table of "All available configuration options" [\#3144](https://github.com/locustio/locust/issues/3144)

**Merged pull requests:**

- Fix Docs Config Options [\#3145](https://github.com/locustio/locust/pull/3145) ([amadeuppereira](https://github.com/amadeuppereira))

## [2.37.5](https://github.com/locustio/locust/tree/2.37.5) (2025-05-22)

[Full Changelog](https://github.com/locustio/locust/compare/2.37.4...2.37.5)

**Fixed bugs:**

- Web UI Does Not Switch to Details Page Immediately on Test Start in Current Version [\#3128](https://github.com/locustio/locust/issues/3128)

**Merged pull requests:**

- Do not require locustfile on specific locust-cloud arguments [\#3141](https://github.com/locustio/locust/pull/3141) ([amadeuppereira](https://github.com/amadeuppereira))

## [2.37.4](https://github.com/locustio/locust/tree/2.37.4) (2025-05-19)

[Full Changelog](https://github.com/locustio/locust/compare/2.37.3...2.37.4)

## [2.37.3](https://github.com/locustio/locust/tree/2.37.3) (2025-05-14)

[Full Changelog](https://github.com/locustio/locust/compare/2.37.2...2.37.3)

**Merged pull requests:**

- Webui: Warn on Missing Host [\#3140](https://github.com/locustio/locust/pull/3140) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.37.2](https://github.com/locustio/locust/tree/2.37.2) (2025-05-13)

[Full Changelog](https://github.com/locustio/locust/compare/2.37.1...2.37.2)

**Fixed bugs:**

- p95 response time increases with the number of unique URLs [\#3134](https://github.com/locustio/locust/issues/3134)
- FastResponse.failure\(\) takes 1 positional argument but 2 were given [\#3084](https://github.com/locustio/locust/issues/3084)

**Merged pull requests:**

- Webui: Block Submitting SwarmForm in Distributed Mode with no Workers [\#3138](https://github.com/locustio/locust/pull/3138) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Fixes \#3134 - Improve the performance of the `/stats/requests` endpoint [\#3136](https://github.com/locustio/locust/pull/3136) ([orf](https://github.com/orf))
- Bump vite from 6.3.2 to 6.3.4 in /locust/webui [\#3132](https://github.com/locustio/locust/pull/3132) ([dependabot[bot]](https://github.com/apps/dependabot))

## [2.37.1](https://github.com/locustio/locust/tree/2.37.1) (2025-05-07)

[Full Changelog](https://github.com/locustio/locust/compare/2.37.0...2.37.1)

**Fixed bugs:**

- --json-file always creates empty file [\#3130](https://github.com/locustio/locust/issues/3130)

**Closed issues:**

- Forced Dependency Updates \(e.g., python-socketio\) May Cause Version Mismatch with Java Services [\#3129](https://github.com/locustio/locust/issues/3129)

**Merged pull requests:**

- Fix --json-file \(actually save data to file\) [\#3131](https://github.com/locustio/locust/pull/3131) ([zed](https://github.com/zed))

## [2.37.0](https://github.com/locustio/locust/tree/2.37.0) (2025-05-05)

[Full Changelog](https://github.com/locustio/locust/compare/2.36.2...2.37.0)

**Merged pull requests:**

- Webui: Fix Failing Tests [\#3126](https://github.com/locustio/locust/pull/3126) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Update uv to 0.7.2 [\#3125](https://github.com/locustio/locust/pull/3125) ([cyberw](https://github.com/cyberw))
- Add command line option to export json results into a file [\#3124](https://github.com/locustio/locust/pull/3124) ([ajt89](https://github.com/ajt89))
- Add locust exporter import \(used in Locust Cloud\) [\#3122](https://github.com/locustio/locust/pull/3122) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- fix error message to be idiomatically correct English [\#3121](https://github.com/locustio/locust/pull/3121) ([davidxia](https://github.com/davidxia))
- Web UI: Use mutations for state buttons [\#3120](https://github.com/locustio/locust/pull/3120) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.36.2](https://github.com/locustio/locust/tree/2.36.2) (2025-04-25)

[Full Changelog](https://github.com/locustio/locust/compare/2.36.1...2.36.2)

**Merged pull requests:**

- Remove circular dependency for locust-cloud [\#3119](https://github.com/locustio/locust/pull/3119) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.36.1](https://github.com/locustio/locust/tree/2.36.1) (2025-04-24)

[Full Changelog](https://github.com/locustio/locust/compare/2.36.0...2.36.1)

**Merged pull requests:**

- Fix setting version for tag and pre-release [\#3118](https://github.com/locustio/locust/pull/3118) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.36.0](https://github.com/locustio/locust/tree/2.36.0) (2025-04-24)

[Full Changelog](https://github.com/locustio/locust/compare/2.35.0...2.36.0)

**Merged pull requests:**

- Bump locust-cloud dependency to 1.20.0 and remove it from docs dependencies [\#3117](https://github.com/locustio/locust/pull/3117) ([cyberw](https://github.com/cyberw))
- Fix yarn publish [\#3116](https://github.com/locustio/locust/pull/3116) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Web Ui: Ensure form element has name [\#3115](https://github.com/locustio/locust/pull/3115) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Web UI: Add profile field [\#3113](https://github.com/locustio/locust/pull/3113) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Restrict gevent versions to ensure compatibility [\#3112](https://github.com/locustio/locust/pull/3112) ([amadeuppereira](https://github.com/amadeuppereira))
- Bump vite [\#3111](https://github.com/locustio/locust/pull/3111) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Web UI: Optionally Extend Advanced Options [\#3110](https://github.com/locustio/locust/pull/3110) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Yarn Berry: Update publish command [\#3108](https://github.com/locustio/locust/pull/3108) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Web UI: Fix npm publish failing [\#3107](https://github.com/locustio/locust/pull/3107) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- chore: set yarn to yarn berry [\#3104](https://github.com/locustio/locust/pull/3104) ([schwannden](https://github.com/schwannden))
- Refactoring: Extract locustfile content merger from main function [\#3102](https://github.com/locustio/locust/pull/3102) ([insspb](https://github.com/insspb))
- Refactoring: Extract validate stats configuration from main function [\#3101](https://github.com/locustio/locust/pull/3101) ([insspb](https://github.com/insspb))
- Add locust-cloud as a dependency, update sphinx and some other docs stuff [\#3097](https://github.com/locustio/locust/pull/3097) ([amadeuppereira](https://github.com/amadeuppereira))

## [2.35.0](https://github.com/locustio/locust/tree/2.35.0) (2025-04-16)

[Full Changelog](https://github.com/locustio/locust/compare/2.34.1...2.35.0)

**Merged pull requests:**

- Bump vite from 6.2.5 to 6.2.6 in /locust/webui [\#3098](https://github.com/locustio/locust/pull/3098) ([dependabot[bot]](https://github.com/apps/dependabot))
- Webui: Add credentials to stop and reset requests [\#3096](https://github.com/locustio/locust/pull/3096) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Webui: Add history fallback [\#3095](https://github.com/locustio/locust/pull/3095) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Web UI: Add optional base url for locust requests to an external API [\#3094](https://github.com/locustio/locust/pull/3094) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Webui: adding profile argument and display in html report [\#3093](https://github.com/locustio/locust/pull/3093) ([schwannden](https://github.com/schwannden))

## [2.34.1](https://github.com/locustio/locust/tree/2.34.1) (2025-04-09)

[Full Changelog](https://github.com/locustio/locust/compare/2.34.0...2.34.1)

**Merged pull requests:**

- Bump vite from 6.2.4 to 6.2.5 in /locust/webui [\#3091](https://github.com/locustio/locust/pull/3091) ([dependabot[bot]](https://github.com/apps/dependabot))
- Drop support for Python 3.9 [\#3090](https://github.com/locustio/locust/pull/3090) ([cyberw](https://github.com/cyberw))

## [2.34.0](https://github.com/locustio/locust/tree/2.34.0) (2025-04-06)

[Full Changelog](https://github.com/locustio/locust/compare/2.33.2...2.34.0)

**Merged pull requests:**

- Fix missing optional argument definitions in PostKwargs [\#3088](https://github.com/locustio/locust/pull/3088) ([kairi003](https://github.com/kairi003))
- Bump vite from 6.2.1 to 6.2.4 in /locust/webui [\#3087](https://github.com/locustio/locust/pull/3087) ([dependabot[bot]](https://github.com/apps/dependabot))
- Web UI: Offset Graph Legend so There's no Overlap on Mobile / Narrow Screens [\#3086](https://github.com/locustio/locust/pull/3086) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- FastHttpUser: Dont crash if parameters are passed to failure\(\) when someone forgot catch\_response=True [\#3085](https://github.com/locustio/locust/pull/3085) ([cyberw](https://github.com/cyberw))
- Make the Locust UI Responsive [\#3083](https://github.com/locustio/locust/pull/3083) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Add OpenAI User and example [\#3081](https://github.com/locustio/locust/pull/3081) ([cyberw](https://github.com/cyberw))

## [2.33.2](https://github.com/locustio/locust/tree/2.33.2) (2025-03-14)

[Full Changelog](https://github.com/locustio/locust/compare/2.33.1...2.33.2)

**Fixed bugs:**

- There was a heartbeat disconnect during the pressure test [\#3065](https://github.com/locustio/locust/issues/3065)

**Closed issues:**

- Error Logging in FastHttpUser [\#2937](https://github.com/locustio/locust/issues/2937)

**Merged pull requests:**

- Bump @babel/runtime from 7.22.15 to 7.26.10 in /locust/webui [\#3080](https://github.com/locustio/locust/pull/3080) ([dependabot[bot]](https://github.com/apps/dependabot))
- Update ruff to 0.10.0 [\#3079](https://github.com/locustio/locust/pull/3079) ([cyberw](https://github.com/cyberw))
- Optimize unit tests [\#3078](https://github.com/locustio/locust/pull/3078) ([cyberw](https://github.com/cyberw))
- Webui: Bump Vite Version for Dependabot [\#3074](https://github.com/locustio/locust/pull/3074) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Update uv to 0.6.5 and optimize docker start time [\#3073](https://github.com/locustio/locust/pull/3073) ([cyberw](https://github.com/cyberw))

## [2.33.1](https://github.com/locustio/locust/tree/2.33.1) (2025-03-08)

[Full Changelog](https://github.com/locustio/locust/compare/2.33.0...2.33.1)

**Fixed bugs:**

- --iterations with locust==2.33.0 and locust-plugins==4.5.3 [\#3071](https://github.com/locustio/locust/issues/3071)
- uv.lock ends up in root of site-packages [\#3053](https://github.com/locustio/locust/issues/3053)

**Merged pull requests:**

- Fix html file naming crash, simplify code [\#3072](https://github.com/locustio/locust/pull/3072) ([cyberw](https://github.com/cyberw))

## [2.33.0](https://github.com/locustio/locust/tree/2.33.0) (2025-02-22)

[Full Changelog](https://github.com/locustio/locust/compare/2.32.10...2.33.0)

**Fixed bugs:**

- UnboundLocalError: local variable 'user\_count' referenced before assignment [\#3051](https://github.com/locustio/locust/issues/3051)

**Merged pull requests:**

- docs: update python-requests documentation links [\#3059](https://github.com/locustio/locust/pull/3059) ([n0h0](https://github.com/n0h0))
- dos: correct venv activation path in docs [\#3058](https://github.com/locustio/locust/pull/3058) ([n0h0](https://github.com/n0h0))
- Use enter to automatically open web UI in default browser [\#3057](https://github.com/locustio/locust/pull/3057) ([cyberw](https://github.com/cyberw))
- Update vite to 6.0.11 [\#3056](https://github.com/locustio/locust/pull/3056) ([cyberw](https://github.com/cyberw))
- Remove uv lock file from build artifacts [\#3055](https://github.com/locustio/locust/pull/3055) ([mquinnfd](https://github.com/mquinnfd))
- Improve error message on missing user\_count or spawn\_rate in swarm payload [\#3052](https://github.com/locustio/locust/pull/3052) ([cyberw](https://github.com/cyberw))
- Enable HTML Report Filename Parsing [\#3049](https://github.com/locustio/locust/pull/3049) ([ktchani](https://github.com/ktchani))
- FastHttpUser: Accept brotli and zstd compression encoding [\#3048](https://github.com/locustio/locust/pull/3048) ([kamilbednarz](https://github.com/kamilbednarz))
- Bump vitest from 2.1.6 to 2.1.9 in /locust/webui [\#3044](https://github.com/locustio/locust/pull/3044) ([dependabot[bot]](https://github.com/apps/dependabot))

## [2.32.10](https://github.com/locustio/locust/tree/2.32.10) (2025-02-18)

[Full Changelog](https://github.com/locustio/locust/compare/2.32.9...2.32.10)

**Closed issues:**

- Switch from Poetry to uv [\#3033](https://github.com/locustio/locust/issues/3033)

**Merged pull requests:**

- Add uv lock file to builds [\#3047](https://github.com/locustio/locust/pull/3047) ([mquinnfd](https://github.com/mquinnfd))
- Use uv/hatch instead of Poetry [\#3039](https://github.com/locustio/locust/pull/3039) ([mquinnfd](https://github.com/mquinnfd))

## [2.32.9](https://github.com/locustio/locust/tree/2.32.9) (2025-02-10)

[Full Changelog](https://github.com/locustio/locust/compare/2.32.8...2.32.9)

**Fixed bugs:**

- Cannot Update Custom options in the Web UI when Default Value is None [\#3011](https://github.com/locustio/locust/issues/3011)

**Merged pull requests:**

- Update docs for stats.py file [\#3038](https://github.com/locustio/locust/pull/3038) ([gabriel-check24](https://github.com/gabriel-check24))
- Add iter\_lines Method to FastHttpSession Class [\#3024](https://github.com/locustio/locust/pull/3024) ([MasterKey-Pro](https://github.com/MasterKey-Pro))
- Fix issue where empty WebUI property is not parsed correctly [\#3012](https://github.com/locustio/locust/pull/3012) ([timhovius](https://github.com/timhovius))

## [2.32.8](https://github.com/locustio/locust/tree/2.32.8) (2025-01-30)

[Full Changelog](https://github.com/locustio/locust/compare/2.32.7...2.32.8)

## [2.32.7](https://github.com/locustio/locust/tree/2.32.7) (2025-01-30)

[Full Changelog](https://github.com/locustio/locust/compare/2.32.6...2.32.7)

**Merged pull requests:**

- Web UI: Allow Showing Only an Error Message on the Login Page [\#3037](https://github.com/locustio/locust/pull/3037) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Allow Empty Tables when Filtering [\#3036](https://github.com/locustio/locust/pull/3036) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Allow xAxis and Grid to be Configured in Echarts [\#3035](https://github.com/locustio/locust/pull/3035) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Code quality: Fix unused imports and switch on related ruff check [\#3034](https://github.com/locustio/locust/pull/3034) ([insspb](https://github.com/insspb))
- Add tab with locust cloud features [\#3032](https://github.com/locustio/locust/pull/3032) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- fix readme image ref links [\#3031](https://github.com/locustio/locust/pull/3031) ([changchaishi](https://github.com/changchaishi))

## [2.32.6](https://github.com/locustio/locust/tree/2.32.6) (2025-01-13)

[Full Changelog](https://github.com/locustio/locust/compare/2.32.5...2.32.6)

**Closed issues:**

- Suggestion to Add  "iter\_lines"  Support for  "FastHttpUser"  in Locust [\#3018](https://github.com/locustio/locust/issues/3018)

**Merged pull requests:**

- Update Dockerfile to use Python 3.12 as base [\#3029](https://github.com/locustio/locust/pull/3029) ([vejmoj1](https://github.com/vejmoj1))
- Update tests to check for hostname instead of fqdn [\#3027](https://github.com/locustio/locust/pull/3027) ([ajt89](https://github.com/ajt89))
- Move some argument parsing/validation from main.py to argument\_parser.py and remove deprecated parameter --hatch-rate [\#3026](https://github.com/locustio/locust/pull/3026) ([ftb-skry](https://github.com/ftb-skry))
- pin poetry-core version to \<2.0.0 in pyproject.toml [\#3025](https://github.com/locustio/locust/pull/3025) ([mgor](https://github.com/mgor))
- Optimize run time of some unit tests [\#3020](https://github.com/locustio/locust/pull/3020) ([cyberw](https://github.com/cyberw))

## [2.32.5](https://github.com/locustio/locust/tree/2.32.5) (2024-12-22)

[Full Changelog](https://github.com/locustio/locust/compare/2.32.4...2.32.5)

**Merged pull requests:**

- Make cpu usage check sleep BEFORE the first check, and make it slightly less frequent [\#3014](https://github.com/locustio/locust/pull/3014) ([cyberw](https://github.com/cyberw))
- FastHttpUser: Fix ssl loading performance issue by avoiding to load certs when they wont be used anyway [\#3013](https://github.com/locustio/locust/pull/3013) ([cyberw](https://github.com/cyberw))
- Treat exceptions in init event handler as fatal [\#3009](https://github.com/locustio/locust/pull/3009) ([cyberw](https://github.com/cyberw))
- Add create store export [\#3004](https://github.com/locustio/locust/pull/3004) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

## [2.32.4](https://github.com/locustio/locust/tree/2.32.4) (2024-12-01)

[Full Changelog](https://github.com/locustio/locust/compare/2.32.3...2.32.4)

**Fixed bugs:**

- Number of requests lower than expected in web UI [\#3000](https://github.com/locustio/locust/issues/3000)
- Reports download links do not contain web-base-path [\#2998](https://github.com/locustio/locust/issues/2998)
- Setuptools CVE-2024-6345  [\#2995](https://github.com/locustio/locust/issues/2995)
- When using exclude-tags to exclude more than two tags, this setting will not take effect [\#2994](https://github.com/locustio/locust/issues/2994)

**Merged pull requests:**

- Allow showing auth info on blank page [\#3002](https://github.com/locustio/locust/pull/3002) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Number of requests lower than expected in web UI [\#3001](https://github.com/locustio/locust/pull/3001) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Webui links should be relative [\#2999](https://github.com/locustio/locust/pull/2999) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Dependency and node version bump [\#2997](https://github.com/locustio/locust/pull/2997) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Fix example in docs [\#2993](https://github.com/locustio/locust/pull/2993) ([daniloakamine](https://github.com/daniloakamine))
- Add Input Type to Login Form [\#2992](https://github.com/locustio/locust/pull/2992) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Update configuration.rst to show minimalistic config example [\#2990](https://github.com/locustio/locust/pull/2990) ([vkuehn](https://github.com/vkuehn))
- Fix README Images for PyPi [\#2989](https://github.com/locustio/locust/pull/2989) ([andrewbaldwin44](https://github.com/andrewbaldwin44))

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

[Full Changelog](https://github.com/locustio/locust/compare/2.31.4.dev9994...2.31.7)

**Merged pull requests:**

- Fix Dependabot Complaints [\#2912](https://github.com/locustio/locust/pull/2912) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Improve Web UI Logging [\#2911](https://github.com/locustio/locust/pull/2911) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Pin python versions to avoid gh caching issue + always Install Dependencies, even when it looks like there was a cache hit [\#2907](https://github.com/locustio/locust/pull/2907) ([cyberw](https://github.com/cyberw))
- Fix Login Manager Error Message [\#2905](https://github.com/locustio/locust/pull/2905) ([andrewbaldwin44](https://github.com/andrewbaldwin44))
- Log locust version earlier [\#2904](https://github.com/locustio/locust/pull/2904) ([cyberw](https://github.com/cyberw))
- Add Mongodb test example [\#2903](https://github.com/locustio/locust/pull/2903) ([guel-codes](https://github.com/guel-codes))

## [2.31.4.dev9994](https://github.com/locustio/locust/tree/2.31.4.dev9994) (2024-09-16)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.4.dev9993...2.31.4.dev9994)

## [2.31.4.dev9993](https://github.com/locustio/locust/tree/2.31.4.dev9993) (2024-09-16)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.4.dev9992...2.31.4.dev9993)

## [2.31.4.dev9992](https://github.com/locustio/locust/tree/2.31.4.dev9992) (2024-09-16)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.4.dev9991...2.31.4.dev9992)

## [2.31.4.dev9991](https://github.com/locustio/locust/tree/2.31.4.dev9991) (2024-09-16)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.4.dev999...2.31.4.dev9991)

## [2.31.4.dev999](https://github.com/locustio/locust/tree/2.31.4.dev999) (2024-09-16)

[Full Changelog](https://github.com/locustio/locust/compare/2.31.6...2.31.4.dev999)

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
