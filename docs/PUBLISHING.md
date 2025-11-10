# Publishing to GitHub Packages

This document explains how the package is published to GitHub Packages and how users can install it.

## Automatic Publishing

After a successful release created by release-please, the package is automatically published to GitHub Packages through the `publish.yml` workflow.

### Workflow Triggers

1. **Automatic**: Triggers when a new release is published (via release-please)
2. **Manual**: Can be triggered manually from the Actions tab

### Process

1. Release-please creates a new release
2. The `publish.yml` workflow is triggered
3. The workflow:
   - Checks out the code
   - Sets up Python 3.11
   - Installs build dependencies
   - Builds the distribution packages (wheel and sdist)
   - Publishes to GitHub Packages
   - Uploads build artifacts

## Package Visibility

To make your package visible on your GitHub profile:

1. Go to your repository on GitHub
2. Click on "Packages" in the right sidebar
3. Click on your package name (`firesands-auth-matrix`)
4. Click "Package settings"
5. Under "Danger Zone", change the package visibility to **Public**
6. Scroll to "Manage Actions access" and ensure the repository has write access

## Installing from GitHub Packages

### Standard Installation

Users can install your package from GitHub Packages:

```bash
pip install firesands-auth-matrix --index-url https://upload.pypi.org/legacy/
```

### Alternative: Configure pip permanently

Create or edit `~/.pip/pip.conf` (Linux/macOS) or `%APPDATA%\pip\pip.ini` (Windows):

```ini
[global]
extra-index-url = https://upload.pypi.org/legacy/
```

Then install normally:

```bash
pip install firesands-auth-matrix
```

### Using with requirements.txt

```text
firesands-auth-matrix
```

And install with the index URL:

```bash
pip install -r requirements.txt --index-url https://upload.pypi.org/legacy/
```

## Development Notes

### Testing the Workflow

You can test the publish workflow manually:

1. Go to Actions tab in GitHub
2. Select "Publish to GitHub Packages"
3. Click "Run workflow"
4. Select the branch
5. Click "Run workflow"

### Troubleshooting

**Issue**: Package not visible on profile
- **Solution**: Make sure package visibility is set to "Public" in package settings

**Issue**: Installation fails with authentication error
- **Solution**: Verify the index URL is correct and the package is public

**Issue**: Build fails
- **Solution**: Check the Actions logs for specific error messages. Common issues:
  - Missing dependencies in `pyproject.toml`
  - Syntax errors in the package files
  - Version conflicts

### Version Management

Versions are managed automatically by release-please:
- It updates the version in `pyproject.toml`
- Creates a new git tag
- Generates release notes
- The publish workflow uses the release event to trigger

### Package Metadata

Package metadata is defined in `pyproject.toml`:
- Name: `firesands-auth-matrix`
- Description
- Keywords
- Dependencies
- Entry points
- URLs (homepage, repository, bug tracker)

## Architecture

```
Release Flow:
1. Commits to `release` branch
2. release-please creates PR with version bump
3. Merge PR → release-please creates GitHub release
4. GitHub release triggers publish workflow
5. Package built and published to GitHub Packages
6. Package visible on GitHub profile (if public)
```

## Best Practices

1. **Semantic Versioning**: Use conventional commits for automatic versioning
2. **Testing**: Test the package locally before merging to release branch
3. **Documentation**: Keep README.md and CHANGELOG.md updated
4. **Dependencies**: Specify version constraints in `pyproject.toml`
5. **Security**: Never commit secrets or tokens
