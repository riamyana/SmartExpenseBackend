-- Table: public.budgets

-- DROP TABLE IF EXISTS public.budgets;

CREATE TABLE IF NOT EXISTS public.budgets
(
    id integer NOT NULL DEFAULT nextval('budgets_id_seq'::regclass),
    amount double precision,
    month character varying COLLATE pg_catalog."default",
    category_id integer,
    is_recurring boolean DEFAULT false,
    created_at timestamp without time zone,
    CONSTRAINT budgets_pkey PRIMARY KEY (id),
    CONSTRAINT budgets_category_id_fkey FOREIGN KEY (category_id)
        REFERENCES public.category (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.budgets
    OWNER to postgres;
-- Index: ix_budgets_id

-- DROP INDEX IF EXISTS public.ix_budgets_id;

CREATE INDEX IF NOT EXISTS ix_budgets_id
    ON public.budgets USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default;

ALTER TABLE budgets
ADD COLUMN user_id UUID;

ALTER TABLE budgets
ADD CONSTRAINT fk_budgets_user
FOREIGN KEY (user_id)
REFERENCES "user"(id)
ON DELETE CASCADE;