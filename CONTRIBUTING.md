# Maintaining Hydra release lines

This feedstock maintains the names of [Hydra's upstream release branches](https://github.com/hydra-ecosystem/hydra/branches).

| Feedstock branch | Purpose |
| --- | --- |
| `main` | Bot configuration and release-line coordination; package uploads are disabled. |
| `1.3_branch` | All Hydra 1.3 releases and rebuilds. |
| `1.4_branch` | All Hydra 1.4 releases, prereleases, and rebuilds. |

These branches contain recipes for released source archives; they do not
automatically synchronize with upstream Git branches. Both recipes pin
`python_min` to 3.10 in `recipe/conda_build_config.yaml`. For 1.3, this preserves
the feedstock's existing minimum; for 1.4, it matches upstream's minimum.
Keep these pins when applying migrations so global pinning cannot raise them.

## Updating a release line

1. Create a working branch in your fork from `1.3_branch` or `1.4_branch`.
2. Update `recipe/meta.yaml` to the published release's version, source URL,
   checksum, and dependencies. Reset the build number to zero for a new version;
   increment it when rebuilding the same version. Verify PyPI source checksums
   against its release metadata when using a PyPI archive.
3. Check the `channel_targets` override in `recipe/conda_build_config.yaml`
   against the intended publication label. Stable inputs with no override
   inherit `conda-forge main`; release candidates use an explicit
   `channel_targets` value of `conda-forge hydra-core_rc`.
4. Rerender with `conda smithy rerender`, verify the effective
   `channel_targets` in generated `.ci_support`, and test locally with
   `python build-locally.py linux_64_`.
5. Open a PR from your fork targeting the matching feedstock release branch.
   Check CI before merging. Releases and recipe rebuilds do not target `main`.

Each release branch sets `upload_on_branch` to its own name. A merge triggers
publishing from that branch. Versions, build numbers, and channel labels
distinguish packages; branches do not inherently create separate channels.
Updates to `main` are not automatically copied to release branches.


## Prerelease publication

Release candidates use the same release-line branch as stable releases, with
`channel_targets: [conda-forge hydra-core_rc]` in
`recipe/conda_build_config.yaml`. The label is package-specific, following
[conda-forge guidance](https://conda-forge.org/docs/maintainer/knowledge_base/#pre-release-builds).
It keeps prereleases available explicitly without putting them on the normal
channel. For example, install the first Hydra 1.4 release candidate with:

```sh
conda install -c conda-forge/label/hydra-core_rc -c conda-forge "hydra-core=1.4.0rc1"
```

Stable inputs with no `channel_targets` override inherit `conda-forge main`.
For a stable release, change the version, source, checksum, and build number
as usual. When promoting an RC to stable, replace its explicit `hydra-core_rc`
override with explicit `channel_targets: [conda-forge main]` in the same PR.
Keep `upload_on_branch` pointing at the release-line branch. Rerender and
verify the effective target in generated `.ci_support` before merging.
Switching the target affects new builds; it does not relabel previously
published packages.

## Bot migrations and branch lifecycle

The bot reads `conda-forge.yml` on `main`. `bot.abi_migration_branches` lists
both release branches for migration PRs. `bot.version_updates.skip: true`
disables version-update PRs to `main`; maintainers submit new versions manually
to the matching release branch. Migration routing does not automate patch
version updates.

For a future release line, follow the [multiple-version maintenance guide](https://conda-forge.org/docs/how-to/advanced/several-versions/):
create a branch from the relevant recipe with an empty `[ci skip]` commit before
the initial upstream push. Set `github.branch_name` and `upload_on_branch` to
the new name, and add it to the migration list on `main`. Submit the first
release through a PR to the new branch. Remove retired lines from the migration
list. Keep the legacy `dev` and `rc` branches until the replacement publishing
setup has been verified with channel installs.

## Rerendering templates

The top-level README is generated. Maintain its branch-aware publishing text
in `templates/README.md.tmpl` and keep this file for release-line instructions.

`templates/github-actions.yml.tmpl` is based on conda-smithy 2026.9.23.
Preserve its quoted `UPLOAD_PACKAGES` values: upload scripts expect the
case-sensitive strings `"False"` and `"True"`, while GitHub serializes YAML
booleans to lowercase strings. Also preserve the `EMULATED` matrix field and
QEMU condition, which avoid pulling emulation tooling for native builds.
Refresh these overrides from the corresponding stock templates when upgrading
conda-smithy, and rerender every maintained branch.
