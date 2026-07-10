# CHANGELOG

<!-- version list -->

## v1.10.2-rc.4 (2026-07-10)

### Bug Fixes

- **deps**: Bump soupsieve to 2.8.4 to fix CVE-2026-49476/49477
  ([#1023](https://github.com/nics-dp/petsard/pull/1023),
  [`06109dd`](https://github.com/nics-dp/petsard/commit/06109dd14f0576ffcd4b1c2eb62538bbbe56915d))


## v1.10.2-rc.3 (2026-07-03)

### Chores

- **ci.deps**: Bump the actions-dependencies group with 7 updates
  ([#1021](https://github.com/nics-dp/petsard/pull/1021),
  [`0394132`](https://github.com/nics-dp/petsard/commit/039413285ed59f6aa944ae821c9dfa2b8d80ca69))


## v1.10.2-rc.2 (2026-06-26)

### Chores

- **ci.deps**: Bump actions/cache from 5.0.5 to 6.0.0
  ([#1019](https://github.com/nics-dp/petsard/pull/1019),
  [`6b348ee`](https://github.com/nics-dp/petsard/commit/6b348ee7a4110dd26c6a8cd6bc28f308c33e9ff9))

- **ci.deps**: Bump the actions-dependencies group with 2 updates
  ([#1018](https://github.com/nics-dp/petsard/pull/1018),
  [`adca6e0`](https://github.com/nics-dp/petsard/commit/adca6e0858c79b9b41e52508e446af763e45a2c2))


## v1.10.2-rc.1 (2026-06-13)

### Bug Fixes

- **ci**: Address copilot review on release workflow
  ([#1000](https://github.com/nics-dp/petsard/pull/1000),
  [`3d5a843`](https://github.com/nics-dp/petsard/commit/3d5a843775a17512c916cf9ed8983e8d92b5129d))

- **ci**: Pin trivy-action to existing v0.36.0 tag
  ([#989](https://github.com/nics-dp/petsard/pull/989),
  [`8b789f2`](https://github.com/nics-dp/petsard/commit/8b789f2f270e4ef5275b6de7864466ca593799fb))

- **ci**: Pin trivy-action to existing v0.36.0 tag
  ([#986](https://github.com/nics-dp/petsard/pull/986),
  [`6fea281`](https://github.com/nics-dp/petsard/commit/6fea281bab6c28deaa82bdb0906b5d8984c7a66d))

- **ci**: Serialize releases and skip self-triggered version commit
  ([#1000](https://github.com/nics-dp/petsard/pull/1000),
  [`3d5a843`](https://github.com/nics-dp/petsard/commit/3d5a843775a17512c916cf9ed8983e8d92b5129d))

- **ci**: Use github app token for semantic-release push
  ([#1000](https://github.com/nics-dp/petsard/pull/1000),
  [`3d5a843`](https://github.com/nics-dp/petsard/commit/3d5a843775a17512c916cf9ed8983e8d92b5129d))

- **deps**: Bump 12 vulnerable dependencies to patched versions
  ([#989](https://github.com/nics-dp/petsard/pull/989),
  [`8b789f2`](https://github.com/nics-dp/petsard/commit/8b789f2f270e4ef5275b6de7864466ca593799fb))

- **deps**: Bump 12 vulnerable dependencies to patched versions
  ([#986](https://github.com/nics-dp/petsard/pull/986),
  [`6fea281`](https://github.com/nics-dp/petsard/commit/6fea281bab6c28deaa82bdb0906b5d8984c7a66d))

- **deps**: Bump gitpython and pip to patched versions
  ([#989](https://github.com/nics-dp/petsard/pull/989),
  [`8b789f2`](https://github.com/nics-dp/petsard/commit/8b789f2f270e4ef5275b6de7864466ca593799fb))

- **deps**: Patch remaining gitpython and pip CVEs
  ([#989](https://github.com/nics-dp/petsard/pull/989),
  [`8b789f2`](https://github.com/nics-dp/petsard/commit/8b789f2f270e4ef5275b6de7864466ca593799fb))

- **deps,ci**: Patch 25 CVEs, repair + harden vulnerability-scan CI
  ([#989](https://github.com/nics-dp/petsard/pull/989),
  [`8b789f2`](https://github.com/nics-dp/petsard/commit/8b789f2f270e4ef5275b6de7864466ca593799fb))

- **deps,ci**: Patch 25 CVEs, repair + harden vulnerability-scan CI
  ([#986](https://github.com/nics-dp/petsard/pull/986),
  [`6fea281`](https://github.com/nics-dp/petsard/commit/6fea281bab6c28deaa82bdb0906b5d8984c7a66d))

### Chores

- Integrate dev into main — CI security hardening & dependency CVE patches
  ([#986](https://github.com/nics-dp/petsard/pull/986),
  [`6fea281`](https://github.com/nics-dp/petsard/commit/6fea281bab6c28deaa82bdb0906b5d8984c7a66d))

- **ci**: Pin all actions to commit SHA and add least-privilege permissions
  ([#989](https://github.com/nics-dp/petsard/pull/989),
  [`8b789f2`](https://github.com/nics-dp/petsard/commit/8b789f2f270e4ef5275b6de7864466ca593799fb))

- **ci**: Pin all actions to commit SHA and add least-privilege permissions
  ([#986](https://github.com/nics-dp/petsard/pull/986),
  [`6fea281`](https://github.com/nics-dp/petsard/commit/6fea281bab6c28deaa82bdb0906b5d8984c7a66d))

- **ci.deps**: Bump actions/cache from 4 to 5 ([#989](https://github.com/nics-dp/petsard/pull/989),
  [`8b789f2`](https://github.com/nics-dp/petsard/commit/8b789f2f270e4ef5275b6de7864466ca593799fb))

- **ci.deps**: Bump actions/cache from 4 to 5 ([#986](https://github.com/nics-dp/petsard/pull/986),
  [`6fea281`](https://github.com/nics-dp/petsard/commit/6fea281bab6c28deaa82bdb0906b5d8984c7a66d))

- **ci.deps**: Bump actions/checkout from 5 to 6
  ([#989](https://github.com/nics-dp/petsard/pull/989),
  [`8b789f2`](https://github.com/nics-dp/petsard/commit/8b789f2f270e4ef5275b6de7864466ca593799fb))

- **ci.deps**: Bump actions/checkout from 5 to 6
  ([#986](https://github.com/nics-dp/petsard/pull/986),
  [`6fea281`](https://github.com/nics-dp/petsard/commit/6fea281bab6c28deaa82bdb0906b5d8984c7a66d))

- **ci.deps**: Bump actions/upload-artifact from 5 to 6
  ([#989](https://github.com/nics-dp/petsard/pull/989),
  [`8b789f2`](https://github.com/nics-dp/petsard/commit/8b789f2f270e4ef5275b6de7864466ca593799fb))

- **ci.deps**: Bump actions/upload-artifact from 5 to 6
  ([#986](https://github.com/nics-dp/petsard/pull/986),
  [`6fea281`](https://github.com/nics-dp/petsard/commit/6fea281bab6c28deaa82bdb0906b5d8984c7a66d))

- **ci.deps**: Bump the actions-dependencies group across 1 directory with 3 updates
  ([#989](https://github.com/nics-dp/petsard/pull/989),
  [`8b789f2`](https://github.com/nics-dp/petsard/commit/8b789f2f270e4ef5275b6de7864466ca593799fb))

- **ci.deps**: Bump the actions-dependencies group across 1 directory with 3 updates
  ([#986](https://github.com/nics-dp/petsard/pull/986),
  [`6fea281`](https://github.com/nics-dp/petsard/commit/6fea281bab6c28deaa82bdb0906b5d8984c7a66d))

- **deps**: Bump aquasecurity/trivy-action ([#989](https://github.com/nics-dp/petsard/pull/989),
  [`8b789f2`](https://github.com/nics-dp/petsard/commit/8b789f2f270e4ef5275b6de7864466ca593799fb))

- **deps**: Bump aquasecurity/trivy-action ([#986](https://github.com/nics-dp/petsard/pull/986),
  [`6fea281`](https://github.com/nics-dp/petsard/commit/6fea281bab6c28deaa82bdb0906b5d8984c7a66d))

- **deps**: Bump aquasecurity/trivy-action from 0.33.1 to 0.34.0 in /.github/workflows in the
  github_actions group across 1 directory ([#989](https://github.com/nics-dp/petsard/pull/989),
  [`8b789f2`](https://github.com/nics-dp/petsard/commit/8b789f2f270e4ef5275b6de7864466ca593799fb))

- **deps**: Bump aquasecurity/trivy-action from 0.33.1 to 0.34.0 in /.github/workflows in the
  github_actions group across 1 directory ([#986](https://github.com/nics-dp/petsard/pull/986),
  [`6fea281`](https://github.com/nics-dp/petsard/commit/6fea281bab6c28deaa82bdb0906b5d8984c7a66d))

- **github**: Add CODEOWNERS ([#989](https://github.com/nics-dp/petsard/pull/989),
  [`8b789f2`](https://github.com/nics-dp/petsard/commit/8b789f2f270e4ef5275b6de7864466ca593799fb))

- **github**: Add CODEOWNERS ([#986](https://github.com/nics-dp/petsard/pull/986),
  [`6fea281`](https://github.com/nics-dp/petsard/commit/6fea281bab6c28deaa82bdb0906b5d8984c7a66d))


## v1.10.1 (2025-11-20)

- No changes since v1.10.1-rc.6.
## v1.10.1-rc.6 (2025-11-20)


## v1.10.1-rc.5 (2025-11-20)


## v1.10.1-rc.4 (2025-11-20)


## v1.10.1-rc.3 (2025-11-20)


## v1.10.1-rc.2 (2025-11-20)

### Bug Fixes

- **demo**: Resolve Colab execution errors and update docs
  ([`319aedc`](https://github.com/nics-dp/petsard/commit/319aedc7a549a4c12465f40035799c17265ad4a5))


## v1.10.1-rc.1 (2025-11-20)


## v1.10.0-rc.5 (2025-11-20)

### Bug Fixes

- **ci**: Allow cleanup step to fail if package doesn't exist
  ([`012f4f5`](https://github.com/nics-dp/petsard/commit/012f4f57d37e00942eedf06c7ff25d10b6694851))


## v1.10.0-rc.4 (2025-11-20)

### Bug Fixes

- Correct repository check in image-publish workflow
  ([`5a97897`](https://github.com/nics-dp/petsard/commit/5a97897a045f5746d5a0c6fc49b3fc43261d9042))

- Correct repository URLs in pyproject.toml
  ([`d4a0a33`](https://github.com/nics-dp/petsard/commit/d4a0a33c414ef1557ed94421171e1c67db1fe7d7))

- **ci**: Always build and publish packages on branch push
  ([`a2dfe50`](https://github.com/nics-dp/petsard/commit/a2dfe5023c37395b7943190d3affda2532a005e5))


## v1.10.0-rc.3 (2025-11-20)

### Bug Fixes

- **ci**: Correct Python syntax in test report generation
  ([`de583e0`](https://github.com/nics-dp/petsard/commit/de583e064935d764b1c828b06afe501703d0821b))

- **logging**: Replace print statements with logger in error handling
  ([`a829bd1`](https://github.com/nics-dp/petsard/commit/a829bd1143b445aa1b869839af4cf8253865a70b))

### Chores

- **release**: Remove changelog generation
  ([`2c8ddb3`](https://github.com/nics-dp/petsard/commit/2c8ddb3ca9ff0d578d835b035ec69685c191d743))

### Code Style

- **lint**: Apply ruff safe auto-fixes
  ([`d4a36f7`](https://github.com/nics-dp/petsard/commit/d4a36f7cf041b567a0e231db5165afd1daafba03))

### Documentation

- **dev-guide**: Add navigation links to subpages
  ([`193fd5e`](https://github.com/nics-dp/petsard/commit/193fd5e051a12d0e880d6a82f5c0455fd7313a66))

- **error-handling**: Rewrite error handling guide with error-code-first approach
  ([`2cba269`](https://github.com/nics-dp/petsard/commit/2cba2695a812187f14e152fee65c3baf47e4669e))

- **i18n**: Translate Chinese comments to English
  ([`7f0fe26`](https://github.com/nics-dp/petsard/commit/7f0fe26eb64bf17f973220fa819f167faeeb98c5))

### Refactoring

- **exceptions**: Establish hierarchical exception architecture with error codes
  ([`645bd96`](https://github.com/nics-dp/petsard/commit/645bd968be4b3f1b990c404012035cce6f060c0b))

- **logging**: Optimize log levels, formatting, and timing records
  ([`6ef1830`](https://github.com/nics-dp/petsard/commit/6ef1830f3bcbae7b90db64275f581f84246b013a))

- **synthesizer**: Remove SDV dependency
  ([`adbb407`](https://github.com/nics-dp/petsard/commit/adbb40732cac8e67b0a5efa276137f7e45444440))


## v1.10.0-rc.2 (2025-11-19)

### Documentation

- **adapter-api**: Complete API reference documentation
  ([`8111da7`](https://github.com/nics-dp/petsard/commit/8111da738a5423ae35b26e11106728b554d05f1a))

- **api**: Refactor internal API docs and consolidate YAML guides
  ([`02f5089`](https://github.com/nics-dp/petsard/commit/02f50890d5585cb51c177abdc4774c8121004ac3))

- **developer-guide**: Remove deprecated guides and simplify structure
  ([`e18b8ff`](https://github.com/nics-dp/petsard/commit/e18b8ff760c8f83250db18b5d08c60082b3b24ad))

### Refactoring

- **adapter**: Consolidate common patterns and add type annotations
  ([`3fe1c04`](https://github.com/nics-dp/petsard/commit/3fe1c043eab10531f38a952acd31d80f625f394d))

- **core**: Remove eval() usage and improve code quality
  ([`8c33292`](https://github.com/nics-dp/petsard/commit/8c33292551e825db1d58257bbcaf8194ab3de19e))

- **deps**: Optimize dependency groups and update install docs
  ([`2a68acb`](https://github.com/nics-dp/petsard/commit/2a68acb142e49e9419987fe7c1814bd490755109))

### Testing

- Achieve 100% pass rate and streamline docs
  ([`056afe5`](https://github.com/nics-dp/petsard/commit/056afe52c560478c6cb425ee3bfd90c1079f8c6a))


## v1.10.0-rc.1 (2025-11-19)


## v1.9.0 (2025-10-19)


## v1.8.1 (2025-10-18)

- Initial Release
