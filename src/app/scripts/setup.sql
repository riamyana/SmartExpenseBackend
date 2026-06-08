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