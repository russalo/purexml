// Command app is the {{project_name}} binary entrypoint.
// TODO: rename the `app` directory and this package comment when forking.
package main

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"
)

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, "fatal:", err)
		os.Exit(1)
	}
}

func run() error {
	// .env is convenience only — systemd / k8s / explicit env vars win.
	loadDotEnv(".env")

	// log/slog is the right default since Go 1.21+. Resist reaching for
	// zap/zerolog unless a measured need shows up (they win on benchmarks,
	// lose on cognitive load).
	log := slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))

	// Listen for BOTH SIGINT (dev Ctrl-C) AND SIGTERM (systemd/k8s). Either
	// one alone misses the other lifecycle. NotifyContext requires the
	// matching `defer stop()` to release the signal handler.
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	addr := envOr("ADDR", ":8080")

	httpSrv := &http.Server{
		Addr: addr,
		// TODO: replace with your real handler / router.
		Handler: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			fmt.Fprintln(w, "TODO: replace this handler.")
		}),
		// Sane defaults — production services should set these explicitly
		// to match their workload. Services serving large media uploads or
		// long-lived ranged video may need to leave Read/Write unset (or
		// set them much higher); most services should keep the limits.
		ReadHeaderTimeout: 15 * time.Second,
		ReadTimeout:       30 * time.Second,
		WriteTimeout:      30 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	// Buffered so the listen goroutine can exit cleanly after the select
	// below moves to ctx.Done — an unbuffered send would block forever.
	errCh := make(chan error, 1)
	go func() {
		log.Info("listening", "addr", addr)
		if err := httpSrv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			errCh <- err
		}
	}()

	select {
	case err := <-errCh:
		return err
	case <-ctx.Done():
		log.Info("shutting down")
	}

	// FRESH context for Shutdown — passing the already-cancelled signal ctx
	// would skip the graceful drain. Common bug, easy to miss in review.
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	if err := httpSrv.Shutdown(shutdownCtx); err != nil {
		log.Error("graceful shutdown failed", "err", err)
	}
	return nil
}

// envOr returns the value of the environment variable named key, or fallback
// if the variable is unset or empty.
func envOr(key, fallback string) string {
	if v, ok := os.LookupEnv(key); ok && v != "" {
		return v
	}
	return fallback
}

// loadDotEnv loads KEY=VALUE lines from a .env file into the process
// environment if the file exists. Existing env vars are NOT overwritten — the
// systemd unit / k8s manifest / explicit env always wins over .env.
func loadDotEnv(path string) {
	data, err := os.ReadFile(path)
	if err != nil {
		return
	}
	for _, line := range strings.Split(string(data), "\n") {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		key, val, ok := strings.Cut(line, "=")
		if !ok {
			continue
		}
		key = strings.TrimSpace(key)
		val = strings.Trim(strings.TrimSpace(val), `"'`)
		if _, exists := os.LookupEnv(key); !exists {
			_ = os.Setenv(key, val)
		}
	}
}
