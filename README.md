# Kubernetes GitOps Platform

## Overview

This repository demonstrate a complete cloud native GitOps platform with `Docker` and `Kubernetes`. The project contains a full-stack application (web frontend, REST API backend, and Postgres database) supporting automated Helm package and deployment with quality and security scans.

The project is designed using latest cloud-native DevOps best practices using real-world use cases.


## Architecture

**Components:**
- **Database (apps/db)**: PostgreSQL with init.sql schema for feedback management.
- **Containerization**: Each service runs in its own Docker container; multi-stage builds for lean production images.
- **Infrastructure-as-Code:**
  - **Docker Compose** for local development & orchestration.
  - **Helm Charts** as the package manager for Kubernetes.
  - **Helmfile** (helmfiles/dev) for release management and environment consistency.
  - **GitOps**: All infrastructure and manifests are versioned; manifests generated automatically via CI.
- **CI/CD:** GitHub Actions automate build, packaging, release, and security.
- **Frontend (apps/frontend)**: Static web app built with HTML, CSS, and JavaScript, served via Nginx.
- **Backend (apps/backend)**: Node.js/Express API for feedback CRUD, PostgreSQL client (`pg`), and rate-limiting (`express-rate-limit`).

**Service Flow:**
Frontend → Backend (REST API) → PostgreSQL

---

## Tech Stack
- **Containerization:** Docker, Docker Compose
- **Orchestration & Packaging:** Helm, Helmfile, Kubernetes
- **CI/CD:** GitHub Actions, Python Scripting
- **Database:** PostgreSQL
- **Security:** Trivy, GitHub Security Integration
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Node.js, Express

---

## Prerequisites

**Local (Docker Compose):**
- Docker (v20+ recommended)
- Docker Compose

**Kubernetes Platform:**
- Access to a Kubernetes cluster (local or cloud)
- kubectl
- Helm v3.14+
- Helmfile v0.163+
- Python 3.11+ (for manifest generator)

---

## Deployment Steps

### Local Development (Docker Compose)
1. Clone repository:
   ```bash
   git clone <repo-url>
   cd kubernetes-gitops-platform
   ```
2. Start all services:
   ```bash
   docker-compose up --build
   ```
3. Access:
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:3000/feedback
   - Database: localhost:5432 (see docker-compose.yml for credentials)
4. Stop:
   ```bash
   docker-compose down -v
   ```

### Kubernetes Deployment (Cloud or Minikube)
1. Install dependencies (see Prerequisites).
2. Configure Helmfile values in `helmfiles/dev/values.yaml` as needed.
3. Apply with Helmfile:
   ```bash
   helmfile -f helmfiles/dev/helmfile.yaml apply
   ```
4. Monitor pods/services in the `dev-namespace` namespace via kubectl.

---

## CI/CD Flow

- **Build and Push Docker Images**:
  - Automated via `.github/workflows/docker-build.yaml` (dispatch triggered)
  - Builds and pushes frontend/backend images to GitHub Container Registry (GHCR) with unique tags

- **Helm Chart Packaging & Publishing**:
  - `.github/workflows/helm-charts-publish.yml` packages Helm charts for backend/frontend and pushes them to GHCR

- **GitOps Manifest Generation & Continuous Delivery**:
  - `.github/workflows/gitops-cd.yml` runs on changes to infra/manifests and generates release manifests using Python generator, Helm, Helmfile
  - Automatically commits and pushes GitOps manifests on update

- **Security Scanning**:
  - `.github/workflows/trivy-code-scan.yaml` runs Trivy on PRs for both frontend and backend
  - Results uploaded to GitHub Security dashboard for review

---

## Security Considerations

- **Static scanning:** Trivy scans all code for vulnerabilities, secrets, and misconfigurations on each PR
- **Non-root containers:** Backend runs as a non-root user; frontend and database use official images
- **Rate limiting:** Express rate limiter protects backend from brute force and abuse
- **Environment isolation:** Each service runs as a separate container and can run in isolated Kubernetes namespaces
- **Secrets management:** Avoid hardcoding secrets; use environment variables and cluster secrets in production
- **Port exposure:** Only required ports are exposed (frontend: 80/8080, backend: 3000, db: 5432)
- **Image minimization:** Multi-stage builds deliver smaller, less vulnerable images

---

---

## Author

[Nimesha Premaraja](https://github.com/NimeshaDil)
