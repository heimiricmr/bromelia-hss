FROM postgres:11-alpine

COPY init-db.sql /docker-entrypoint-initdb.d/init-db.sql
COPY pg_hba.conf /var/lib/postgresql/data/pg_hba.conf