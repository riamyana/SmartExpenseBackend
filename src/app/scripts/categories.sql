CREATE TABLE IF NOT EXISTS public.category
(
    id integer NOT NULL DEFAULT nextval('category_id_seq'::regclass),
    name character varying COLLATE pg_catalog."default",
    description character varying COLLATE pg_catalog."default",
    is_system integer,
    created_at timestamp without time zone,
    CONSTRAINT category_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.category
    OWNER to postgres;
-- Index: ix_category_id

-- DROP INDEX IF EXISTS public.ix_category_id;

CREATE INDEX IF NOT EXISTS ix_category_id
    ON public.category USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default;

INSERT INTO category (name, description, is_system, created_at)
VALUES
('Food', 'Expenses related to food and dining', 1, NOW()),
('Travel', 'Expenses related to travel and transportation', 1, NOW()),
('Shopping', 'Expenses related to shopping and retail', 1, NOW()),
('Bills', 'Regular bills and utilities', 1, NOW()),
('Salary', 'Income from employment', 1, NOW()),
('Investment', 'Expenses related to investments', 1, NOW()),
('Health', 'Expenses related to healthcare', 1, NOW()),
('Entertainment', 'Expenses related to entertainment', 1, NOW()),
('Transfer', 'Transfers between accounts', 1, NOW()),
('Other', 'Other expenses', 1, NOW());