## Release Process

 * Install github_changelog_generator (https://github.com/github-changelog-generator/github-changelog-generator/) if not installed 
 * Run github_changelog_generator to update `CHANGELOG.md`
  - `make changelog`
 * Update `locust/__init__.py` with new version number: `__version__ = "VERSION"`
 * Make git tag
 * Push git tag
 * Update Automated Builds configuration in Docker Hub so that the newly created 
   git tag is built as the "latest" docker tag
