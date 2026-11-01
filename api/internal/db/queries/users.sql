-- Queries for the users table. sqlc turns each "-- name:" block into a typed Go function.
-- :one = returns one row, :many = a slice, :exec = no rows.

-- name: CreateUser :one
INSERT INTO users (email, auth_provider, password_hash)
VALUES ($1, $2, $3)
RETURNING *;

-- name: GetUserByEmail :one
SELECT * FROM users
WHERE email = $1;

-- name: DeleteUser :exec
-- Cascades to goals, sessions, verdicts, appeals and daily_stats ("delete my data").
DELETE FROM users
WHERE id = $1;
