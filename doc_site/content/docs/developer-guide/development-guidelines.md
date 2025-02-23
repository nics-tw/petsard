---
title: Development Guidelines
type: docs
weight: 81
prev: docs/developer-guide
next: docs/developer-guide/test-coverage
---

## Development Process

### Branch Protection

- `main` and `dev` branches are protected
- All merges require code review from at least one CAPE team member other than the author, except for special operations approved by the CAPE team

### Issue and Pull Request Guidelines

1. **Issue Management**
  - All feature changes must start with an Issue
  - Issues should clearly describe the purpose, expected behavior, and scope of changes

2. **Pull Request Requirements**
  - One Issue corresponds to one Pull Request
  - Each Pull Request should contain only one commit
  - PR titles must follow Angular commit conventions ([reference](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits))
  - Feature branches should be deleted after PR completion

3. **Feature Development Process**
  - Development should be conducted in task-specific feature branches
  - Ideally, new feature development should be split into three separate PRs:
    1. Feature implementation (feat)
    2. Documentation update (doc)
    3. Test implementation (test)
  - All components may be included in a single feature PR if necessary, but must be clearly documented in the commit message

## Key Package Version Tracking

The following lists the version information of key packages, manually verified periodically. Actual versions in use should refer to pyproject.toml.

| Package Name | Minimum Version | Current Version | Minimum Version Release | Current Version Release | Reference |
|-------------|----------------|-----------------|----------------------|---------------------|-----------|
| SDV | 1.17.4 | 1.17.4 | 2025/01/20 | 2025/01/20 | [GitHub](https://github.com/sdv-dev/SDV) |
| SDMetrics | 0.18.0 | 0.18.0 | 2024/12/14 | 2024/12/14 | [GitHub](https://github.com/sdv-dev/SDMetrics) |
| anonymeter | 1.0.0 | 1.0.0 | 2024/02/02 | 2024/02/02 | [GitHub](https://github.com/statice/anonymeter) |

## Development Environment Setup

### Package Management Notes

```bash
uv venv --python 3.10
uv sync
```

```bash
uv --project petsard add "urllib3>=2.2.2"
uv --project petsard add --group dev "tornado>=6.4.2"
```

```bash
uv export --format requirements-txt --no-group dev --no-editable > requirements.txt
uv export --format requirements-txt --all-groups --no-editable > requirements-dev.txt
```

## Version Control Notes

```bash
semantic-release generate-config -f toml --pyproject >> pyproject.toml
```

Following Angular commit conventions:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test-related changes
- `chore`: Build or tooling updates