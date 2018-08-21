## Release Process

 * Run github_changelog_generator to update `CHANGELOG.md`
 * Add highlights to changelog in docs: `locust/docs/changelog.rst`
 * Update `locust/__init__.py` with new version number: `__version__ = "VERSION"`
 * Tag master as "VERSION" in git
 * Build VERSION package and upload to PyPI
