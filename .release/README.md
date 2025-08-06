# Release Configuration

This directory contains all release and packaging related configurations.

## Directory Structure

```
.release/
├── README.md                    # This file
└── changelog-templates/         # Changelog generation templates
    └── CHANGELOG.md.j2         # Jinja2 template for CHANGELOG.md
```

## Files Description

### changelog-templates/
Contains templates used by `python-semantic-release` to generate the CHANGELOG.md file.

- **CHANGELOG.md.j2**: Jinja2 template that defines the format of the generated changelog
- Used by semantic release to automatically generate release notes based on conventional commits

## Configuration

The semantic release configuration in `pyproject.toml` references this directory:

```toml
[tool.semantic_release.changelog]
template_dir = ".release/changelog-templates"
```

## Usage

These templates are automatically used during the release process when:
1. Pushing commits to `main` or `dev` branches
2. Running `semantic-release version` command
3. The GitHub Actions workflow triggers semantic release

The generated CHANGELOG.md will be updated automatically with new version information.