#!/usr/bin/env bash
# new-project — spawn a new project on origin-core from the russalo template.
#
# Usage:
#   new-project <target-dir> [--lang python|go|all|none] [--name NAME] [--git]
#
# Examples:
#   new-project /srv/projects/foo --lang go
#   new-project /srv/projects/data-tool --lang python --git
#   new-project /srv/projects/scratch-thing --lang none
#   new-project /srv/projects/multi-stack --lang all
#
# Flags:
#   --lang   python | go | all | none  (default: all)
#   --name   override the project name (default: basename of target-dir)
#   --git    git init + initial commit after scaffolding
#   --help   show this and exit
#
# After running, cd into the new dir and read USE.md / CLAUDE.md.

set -euo pipefail

# Resolve the template's own location (this script lives at the template root).
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
TEMPLATE_DIR="$(dirname "$SCRIPT_PATH")"

# --- helpers --------------------------------------------------------------

usage() {
    sed -n '/^# Usage:/,/^# After running/p' "$SCRIPT_PATH" | sed 's/^# \?//'
}

# Strip a stack-section from the target's .gitignore. Section boundaries are
# the `# =====` separators with a `# <Stack> (` header line. Removes the
# header banner, the section body, AND any trailing blank lines up to the
# next `# =====` banner. The universal section is never matched (its header
# is `# Universal (`), so it always survives.
strip_gitignore_section() {
    local section="$1"   # "Python" | "Go" | "Node"
    local gif="$TARGET/.gitignore"
    [[ -f "$gif" ]] || return 0
    # Use awk to skip the [start, next-banner-or-EOF) range that contains the
    # named section.
    awk -v sect="$section" '
        BEGIN { skip = 0 }
        # Banner line (# ===): start of section. Check the NEXT line for the
        # section name to decide whether to skip this region.
        /^# =+$/ {
            getline header
            if (header ~ "^# " sect " ") {
                skip = 1
                next   # drop the banner line; the next iteration handles its body
            }
            # Not our section — emit banner + header normally.
            skip = 0
            print
            print header
            next
        }
        { if (!skip) print }
    ' "$gif" > "${gif}.tmp" && mv "${gif}.tmp" "$gif"
}

# --- defaults -------------------------------------------------------------

LANG_PICK="all"
TARGET=""
PROJECT_NAME=""
DO_GIT=0

# --- args -----------------------------------------------------------------

while [[ $# -gt 0 ]]; do
    case "$1" in
        --lang)  LANG_PICK="$2"; shift 2 ;;
        --name)  PROJECT_NAME="$2"; shift 2 ;;
        --git)   DO_GIT=1; shift ;;
        --help|-h) usage; exit 0 ;;
        -*)
            echo "new-project: unknown flag: $1" >&2
            usage >&2
            exit 1
            ;;
        *)
            if [[ -z "$TARGET" ]]; then
                TARGET="$1"
            else
                echo "new-project: unexpected positional arg: $1" >&2
                exit 1
            fi
            shift
            ;;
    esac
done

# --- validate -------------------------------------------------------------

if [[ -z "$TARGET" ]]; then
    echo "new-project: target directory is required." >&2
    usage >&2
    exit 1
fi

case "$LANG_PICK" in
    python|go|all|none) ;;
    *)
        echo "new-project: invalid --lang '$LANG_PICK' (must be python, go, all, or none)" >&2
        exit 1
        ;;
esac

if [[ -e "$TARGET" ]]; then
    echo "new-project: target already exists: $TARGET" >&2
    echo "  refusing to clobber. delete or pick another path." >&2
    exit 2
fi

if [[ -z "$PROJECT_NAME" ]]; then
    PROJECT_NAME="$(basename "$TARGET")"
fi

# Project name should be lowercase + safe for cross-tool friendliness (Python
# package names, Go module paths, file system).
if [[ ! "$PROJECT_NAME" =~ ^[a-z][a-z0-9_-]*$ ]]; then
    echo "new-project: project name '$PROJECT_NAME' should be lowercase letters/digits/underscore/hyphen, starting with a letter." >&2
    echo "  override with --name <name> if the target dir's basename doesn't fit." >&2
    exit 1
fi

# --- copy template --------------------------------------------------------

echo "→ scaffolding $TARGET (lang: $LANG_PICK, name: $PROJECT_NAME)"

cp -a "$TEMPLATE_DIR" "$TARGET"

# Strip template-development artifacts that don't belong in the spawned project.
rm -f "$TARGET/new-project.sh"
rm -f "$TARGET/scratch/notes.md" \
      "$TARGET/scratch/blog_go_audit_hunt_list.md" \
      "$TARGET/scratch/blog_go_patterns_lifted.md" \
      "$TARGET/scratch/blog_go_full_response_2026-06-08.md" \
      "$TARGET/scratch/draft_to_blog_claude_2026-06-08.md"

# --- pick CI workflow + strip stack-specific files ------------------------

case "$LANG_PICK" in
    python)
        rm -rf "$TARGET/cmd" "$TARGET/internal"
        rm -f "$TARGET/justfile" "$TARGET/.golangci.yml"
        mv "$TARGET/.github/workflows/tests-python.yml" "$TARGET/.github/workflows/tests.yml"
        rm -f "$TARGET/.github/workflows/tests-go.yml"
        strip_gitignore_section "Go"
        strip_gitignore_section "Node"
        ;;
    go)
        rm -f "$TARGET/pyproject.toml"
        rm -rf "$TARGET/src" "$TARGET/tests"
        mv "$TARGET/.github/workflows/tests-go.yml" "$TARGET/.github/workflows/tests.yml"
        rm -f "$TARGET/.github/workflows/tests-python.yml"
        strip_gitignore_section "Python"
        strip_gitignore_section "Node"
        if command -v go >/dev/null 2>&1; then
            (cd "$TARGET" && go mod init "github.com/russalo/$PROJECT_NAME" 2>&1 | sed 's/^/  /')
        else
            echo "  (skipping go mod init — go not on PATH; run: cd $TARGET && go mod init github.com/russalo/$PROJECT_NAME)"
        fi
        ;;
    all)
        # Keep both stacks. Both CI workflows coexist (tests-go.yml + tests-python.yml).
        # The user picks one when they commit to a stack — USE.md walks the cutover.
        :
        ;;
    none)
        # Language-agnostic skeleton only: docs + scratch + .review-canonical.
        rm -f "$TARGET/pyproject.toml" "$TARGET/justfile" "$TARGET/.golangci.yml"
        rm -rf "$TARGET/src" "$TARGET/tests" "$TARGET/cmd" "$TARGET/internal"
        rm -rf "$TARGET/.github"
        strip_gitignore_section "Python"
        strip_gitignore_section "Go"
        strip_gitignore_section "Node"
        ;;
esac

# --- placeholder substitutions --------------------------------------------

# Universal: deploy-time placeholders → real values across all text files
# (excludes .git, vendor/, and common binary extensions).
#
# DEPLOY-TIME placeholders (script auto-substitutes these on every spawn):
#   {{project_name}}      → $PROJECT_NAME             — the canonical project name (hyphens preserved)
#   {{your_binary_name}}  → $PROJECT_NAME             — Go binary name
#   {{cli_name}}          → $PROJECT_NAME             — CLI/command name shown in `--help` examples
#   {{name}}              → $PROJECT_NAME             — generic name slot (e.g. `go mod init github.com/russalo/{{name}}`)
#   {{your_package_name}} → underscored project name  — Python package directory (hyphens → underscores)
#
# AUTHOR-TIME / RUNTIME placeholders (the script LEAVES THESE ALONE so users /
# tools fill them in):
#   {{pkg}}, {{binary}}                — justfile recipe variables (just expands at runtime)
#   {{artifact_kind}}, {{X.Y.Z}}, {{YYYY-MM-DDThhmm}}, {{ext}} — doc examples
#   anything else                        — by design, user fills in manually
#
# To add a new deploy-time placeholder later: append to the SUBS array below and
# document the contract in this comment block.

PY_PKG_NAME="${PROJECT_NAME//-/_}"

# Each entry: 'PLACEHOLDER:REPLACEMENT'
SUBS=(
    "{{project_name}}:$PROJECT_NAME"
    "{{your_binary_name}}:$PROJECT_NAME"
    "{{cli_name}}:$PROJECT_NAME"
    "{{name}}:$PROJECT_NAME"
    "{{your_package_name}}:$PY_PKG_NAME"
)

find "$TARGET" \( -name ".git" -o -name "vendor" \) -prune -o -type f -print0 |
    while IFS= read -r -d '' f; do
        case "$f" in
            *.png|*.jpg|*.jpeg|*.gif|*.pdf|*.tar|*.gz|*.zip|*.tgz|*.bz2) continue ;;
        esac
        for sub in "${SUBS[@]}"; do
            placeholder="${sub%%:*}"
            replacement="${sub#*:}"
            if grep -qF "$placeholder" "$f" 2>/dev/null; then
                # Escape `/` and `&` in the replacement for safe use in sed
                esc="$(printf '%s\n' "$replacement" | sed 's/[&/\\]/\\&/g')"
                # Escape `{` `}` `.` in the placeholder for safe BRE matching
                pat="$(printf '%s\n' "$placeholder" | sed 's/[][\\.*^$/]/\\&/g')"
                sed -i "s/$pat/$esc/g" "$f"
            fi
        done
    done

# Python: rename src/example → src/$PY_PKG_NAME + update pyproject.toml refs.
# Python package directories MUST use underscores (hyphens aren't valid in import
# paths). The project name in pyproject.toml CAN have hyphens (PEP 503 normalizes
# to underscores at distribution time), so we keep the hyphenated name there for
# PyPI display and use the underscored variant for the package directory.
if [[ "$LANG_PICK" == "python" || "$LANG_PICK" == "all" ]]; then
    PY_PKG_NAME="${PROJECT_NAME//-/_}"
    if [[ -d "$TARGET/src/example" ]]; then
        mv "$TARGET/src/example" "$TARGET/src/$PY_PKG_NAME"
    fi
    if [[ -f "$TARGET/pyproject.toml" ]]; then
        # Replace the package-name literal "example" (quoted to avoid catching
        # the word "example" in comments/prose elsewhere in the file).
        sed -i "s/\"example\"/\"$PROJECT_NAME\"/g" "$TARGET/pyproject.toml"
    fi
fi

# Go: rename cmd/app → cmd/$PROJECT_NAME + update justfile vars.
if [[ "$LANG_PICK" == "go" || "$LANG_PICK" == "all" ]]; then
    if [[ -d "$TARGET/cmd/app" ]]; then
        mv "$TARGET/cmd/app" "$TARGET/cmd/$PROJECT_NAME"
    fi
    if [[ -f "$TARGET/justfile" ]]; then
        sed -i "s|bin/app|bin/$PROJECT_NAME|g; s|./cmd/app|./cmd/$PROJECT_NAME|g" "$TARGET/justfile"
    fi
fi

# --- optional git init ----------------------------------------------------

if [[ "$DO_GIT" -eq 1 ]]; then
    echo "→ git init + initial commit"
    (
        cd "$TARGET"
        git init -q -b main
        git add -A
        git commit -q -m "Initial scaffold from project-template (lang: $LANG_PICK)"
    )
fi

# --- done ------------------------------------------------------------------

echo
echo "✓ Created $TARGET"
echo "  Name:  $PROJECT_NAME"
echo "  Lang:  $LANG_PICK"
echo
echo "Next steps:"
echo "  cd $TARGET"
echo "  cat USE.md"
case "$LANG_PICK" in
    python)
        echo "  python -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'"
        echo "  pytest"
        ;;
    go)
        echo "  just test    # (or: go test ./...)"
        echo "  just build"
        ;;
    all)
        echo "  Pick your stack — see USE.md for the cutover (delete the other stack's files)."
        ;;
    none)
        echo "  Add your stack's boilerplate — see STACK.md for canonical Python/Go shapes."
        ;;
esac
