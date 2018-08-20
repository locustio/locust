## Release Process

 * Run github_changelog_generator to update `CHANGELOG.md`
 * update `locust/__init__.py` with new version number: `__version__ = "0.9.0.rc1"`
 * set milestone to 0.9.0 on all included PR's
 * update changelog in docs: `locust/docs/changelog.rst`
 * tag master as "0.9.0.rc1" in git
 * build 0.9.0.rc1 package and upload to PyPI
