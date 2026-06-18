1. Install PostgreSQL
Download:
PostgreSQL Download
During installation remember:
Username: postgres
Password: your_password
Port: 5432

CREATE DATABASE expense_tracker;

CREATE USER expense_user
WITH PASSWORD 'StrongPassword123';

GRANT ALL PRIVILEGES
ON DATABASE expense_tracker
TO expense_user;

CREATE SCHEMA expense;

CREATE DATABASE keycloak;

-- update secret_user and secret_password to actual values.
CREATE USER secret_user
WITH PASSWORD 'secret_password';

GRANT ALL PRIVILEGES ON DATABASE keycloak TO secret_user;

GRANT ALL ON SCHEMA public TO secret_user;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO secret_user;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO secret_user;

GRANT CREATE ON SCHEMA public TO secret_user;