// Package config reads the API's settings from environment variables.
package config

import (
	"os"
	"time"
)

// Config holds everything the server needs at startup.
type Config struct {
	Port         string        // where this API listens, e.g. "8080"
	AIServiceURL string        // base URL of the Python AI service
	AITimeout    time.Duration // max wait for one /v1/classify call (two LLM calls can take a while)
}

// Load reads the environment, falling back to local-development defaults.
func Load() Config {
	return Config{
		Port:         getenv("PORT", "8080"),
		AIServiceURL: getenv("AI_SERVICE_URL", "http://127.0.0.1:8001"),
		AITimeout:    getDuration("AI_TIMEOUT", 45*time.Second),
	}
}

func getenv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func getDuration(key string, fallback time.Duration) time.Duration {
	if d, err := time.ParseDuration(os.Getenv(key)); err == nil {
		return d
	}
	return fallback
}
