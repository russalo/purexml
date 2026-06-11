# justfile — task runner for {{project_name}}.
# Standard: `just` is the russalo-wide command runner.
# List recipes: `just`.  Run a recipe: `just <name>`.

# Pass recipe parameters as shell positional args ($1, $2, …) instead of textual
# `{{ }}` interpolation, so an arg containing quotes/`;`/`$()` can't escape the
# command line and inject. Use `"$1"` etc. in recipes that take user input.
# (A recipe arg containing quotes/`;`/`$()` could otherwise inject through
# textual interpolation; this is the just-1.13+ replacement for the newer
# `[positional-arguments]` recipe attribute.)
set positional-arguments := true

# Prepend the Go toolchain + GOPATH/bin to the PATH that recipe shells inherit.
# Without this, `just build` / `just sqlc` silently fail with "go: not found"
# inside the /bin/sh subshell — even when the user's interactive shell has them
# on PATH. A real deploy-no-op was caused by this exact subshell-PATH gap (the
# next build step succeeded, the failure scrolled past, and `systemctl restart`
# re-launched the unchanged stale binary). Adding this line moots the class.
export PATH := "/usr/local/go/bin:" + env_var_or_default('HOME', '/root') + "/go/bin:" + env_var_or_default('PATH', '')

# TODO: rename `app` → your binary name when forking this template.
binary := "bin/app"
pkg    := "./cmd/app"

# Default: show the recipe list.
default:
    @just --list

# Run the server (dev).
run:
    go run {{pkg}}

# Build the single binary (static, CGO off; -s -w strips debug + symbol table
# for a smaller production binary).
build:
    CGO_ENABLED=0 go build -ldflags="-s -w" -o {{binary}} {{pkg}}

# Run all tests with the race detector. `-race` catches data races (universal
# good); `-count=1` bypasses the test result cache so the race build always
# actually executes (a cached PASS could otherwise mask a flaky race).
test:
    go test -race -count=1 ./...

# Run a single test or pattern: `just test-one ./internal/foo TestBar`.
test-one path pattern:
    go test "$1" -run "$2" -count=1 -v

# go vet.
vet:
    go vet ./...

# Tidy go modules.
tidy:
    go mod tidy

# Remove build artifacts.
clean:
    rm -rf bin
