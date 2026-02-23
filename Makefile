.PHONY: help install-deps generate-gitops clean

# Default target
help:
	@echo "GitOps Continuous Delivery Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  help           - Show this help message"
	@echo "  install-deps   - Install required dependencies (Helm, Helmfile, Python packages)"
	@echo "  generate-gitops - Run gitops-generator.py to template Helm charts"
	@echo "  clean          - Remove temporary template files (preserves gitops/)"
	@echo ""
	@echo "Environment Variables:"
	@echo "  TMP_DIR        - Temporary directory for helm templates (default: templates)"
	@echo "  CONCURRENCY    - Helmfile concurrency level (default: 20)"

# Install dependencies
install-deps:
	@echo "🔧 Installing dependencies..."
	@command -v helm >/dev/null 2>&1 || { echo "❌ Helm not found. Install from https://helm.sh/docs/intro/install/"; exit 1; }
	@command -v helmfile >/dev/null 2>&1 || { echo "❌ Helmfile not found. Install from https://github.com/helmfile/helmfile"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 not found. Please install Python 3.11+"; exit 1; }
	@echo "✅ Helm version: $$(helm version --short)"
	@echo "✅ Helmfile version: $$(helmfile version)"
	@echo "✅ Python version: $$(python3 --version)"
	@echo "📦 Installing Python dependencies..."
	@pip3 install --quiet pyyaml || { echo "❌ Failed to install PyYAML"; exit 1; }
	@echo "✅ All dependencies installed successfully"

# Generate GitOps manifests
generate-gitops:
	@echo "🚀 Generating GitOps manifests..."
	@python3 ci-cd/generator/gitops-generator.py
	@echo "✅ GitOps manifest generation complete"

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	@find helmfiles -type d -name "templates" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete (gitops/ directory preserved)"
