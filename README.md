# Kubernetes GitOps Platform

This repository manages GitOps CI/CD pipeline that deploy Kubernetes manifests generated from Helmfile definitions. It is used to deploy the [Bug Tracker application](https://github.com/Nimesha-Premaraja/bug-tracker) by rendering its Helm chart into version-controlled Kubernetes YAML under `gitops/`.


## Key Directories

- `.github/workflows/gitops-cd.yml`: GitHub Actions workflow for GitOps manifest generation.
- `ci-cd/generator/gitops-generator.py`: Python generator that detects changed Helmfile environments and renders Kubernetes manifests.
- `helmfiles/<environment>/helmfile.yaml`: Helmfile release definitions for each environment.
- `helmfiles/<environment>/values.yaml`: Environment-specific Helm values. (Dev, QA, Staging, Production)
- `gitops/`: Generated Kubernetes manifests committed back to the repository.
- `Makefile`: Local and CI entry points for dependency checks and manifest generation.

## CI/CD Workflow

The GitOps Continuous Delivery workflow is defined in `.github/workflows/gitops-cd.yml`.

1. A pull request is opened or updated against `main`.
2. GitHub Actions checks out the PR branch with full Git history.
3. Python 3.11 is installed using `actions/setup-python`.
4. Helm v3.14.0 is installed using `azure/setup-helm`.
5. Helmfile v0.163.1 is downloaded and installed.
6. `make install-deps` validates required tools and installs the Python dependency `PyYAML`.
7. `make generate-gitops` runs `ci-cd/generator/gitops-generator.py`.
8. The generator detects changed folders under `helmfiles/` from the latest commit.
9. For each changed environment, Helmfile renders the configured Helm releases.
10. Rendered Kubernetes resources are split into individual YAML files and written under `gitops/<namespace>/<release>/`.
11. The workflow checks whether `gitops/` has changed using Git status.
12. If generated manifests changed, the workflow commits them with `gitops: regenerated [skip ci]`.
13. For same-repository pull requests, the workflow pushes the generated `gitops/` changes back to the PR branch.

## Deployed Application

This GitOps repository deploys the Bug Tracker application:

- Application repository: https://github.com/Nimesha-Premaraja/bug-tracker
- Helm chart source: `oci://ghcr.io/nimesha-premaraja/bug-tracker/helm-charts/bug-tracker`




## GitOps Generation Flow

```text
helmfiles/<environment>/values.yaml
        ↓
helmfiles/<environment>/helmfile.yaml
        ↓
helmfile template
        ↓
ci-cd/generator/gitops-generator.py
        ↓
gitops/<namespace>/<release>/<resource-name>-<Kind>.yaml
        ↓
GitHub Actions commits generated manifest changes to the PR branch
```

## Tools And Technologies

- Kubernetes: Target platform for generated manifests.
- Helm: Kubernetes package manager used to render charts.
- Helmfile: Declarative release management for each environment.
- GitHub Actions: CI/CD runner for automated GitOps generation.
- Python: Runtime for the GitOps generator.
- PyYAML: YAML parsing and manifest splitting in the generator.
- Make: Common command interface for CI and local workflows.
- GitHub Container Registry: OCI Helm chart registry used by the Bug Tracker chart.


## Generated Manifests

Generated files in `gitops/` are the desired Kubernetes state for each environment. These files should normally be updated through the GitOps generation workflow instead of being edited manually.
