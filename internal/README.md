# internal/

Compiler-enforced privacy boundary (Go 1.4+). Only the parent module may import `internal/...` packages. Anything intended for external consumers belongs in `pkg/` (not present by default — add only when you actually have a library to publish).
