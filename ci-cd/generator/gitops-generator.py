import os
import subprocess
import shutil
from pathlib import Path
import yaml
import time
# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

# Ensure we're working from the repository root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(REPO_ROOT)
TMP_DIR = os.getenv("TMP_DIR", "templates")
CONCURRENCY = os.getenv("CONCURRENCY", "20")
GITOPS_DIR = REPO_ROOT / "gitops"
GITOPS_DIR.mkdir(exist_ok=True)

# -----------------------------------------------------------------------------
# Get changed namespaces
# -----------------------------------------------------------------------------

get_changes = subprocess.run(
    'git log -m -1 --name-only --pretty=format: | grep "^helmfiles/" | cut -d "/" -f 2 | sort -u',
    shell=True,
    capture_output=True,
    text=True
)

raw_namespaces = get_changes.stdout.strip().splitlines()
changed_namespace = []

for ns in raw_namespaces:
    # Skip empty or hidden entries
    if not ns or ns.startswith("."):
        continue

    helmfile_path = Path(f"helmfiles/{ns}/helmfile.yaml")
    if helmfile_path.exists():
        changed_namespace.append(ns)
    else:
        print(f"⚠️  Skipping folder '{ns}' — Because helmfile.yaml not found!")

# -----------------------------------------------------------------------------
# Process each namespace
# -----------------------------------------------------------------------------

if not changed_namespace:
    print("\n❌ No changed namespaces detected. \n")
else:
    for ns in changed_namespace:
        print(f"\n🔶 Start Helm templating for namespace: {ns} \n")

        ROOT_DIR = Path(f"helmfiles/{ns}/")
        HELMFILE = ROOT_DIR / "helmfile.yaml"

        # Render Helm templates
        result = subprocess.run([
            "helmfile",
            "--file", str(HELMFILE),
            "template",
            "--allow-no-matching-release",
            "--include-crds",
            "--output-dir-template", f"{TMP_DIR}/{{{{.Release.Namespace}}}}/{{{{.Release.Name}}}}",
            "--concurrency", CONCURRENCY
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"\n❌ Helmfile failed for namespace: {ns}")
            print("\n--- STDOUT ---\n", result.stdout)
            print("\n--- STDERR ---\n", result.stderr)
            continue  # skip this namespace but continue others

        print(result.stdout)

        # Copy files to GitOps folder
        tmp_path = ROOT_DIR / TMP_DIR

        if not tmp_path.exists():
            print(f"\n🛑 No templates generated under {tmp_path} \n")
            continue

        for yaml_file in tmp_path.rglob("*.yaml"):
            # Determine namespace and release from folder structure
            namespace = yaml_file.parents[3].name
            release = yaml_file.parents[2].name

            namespace_dir = GITOPS_DIR / namespace / release
            namespace_dir.mkdir(parents=True, exist_ok=True)

            # Load multi-doc YAML
            try:
                with open(yaml_file, "r") as f:
                    docs = list(yaml.safe_load_all(f))
            except yaml.YAMLError as e:
                print(f"⚠️ YAML parse error in {yaml_file}: {e}")
                continue

            # Write each doc to a separate file
            for doc in docs:
                if not doc:
                    continue
                name = doc.get("metadata", {}).get("name", "unknown")
                kind = doc.get("kind", "UnknownKind")
                filename = f"{name}-{kind}.yaml"
                output_file = namespace_dir / filename
                with open(output_file, "w") as out_f:
                    yaml.dump(doc, out_f, default_flow_style=False)
                print(f"✅ Created {output_file}")

        # Clean up temporary folder
        print(f"\n\nCleaning {tmp_path} in 5 seconds...\n")
        time.sleep(5)
        shutil.rmtree(tmp_path, ignore_errors=True)
        print(f"🆗 Removed temporary folder {tmp_path} \n")
