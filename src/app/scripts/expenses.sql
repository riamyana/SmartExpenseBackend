CREATE TABLE IF NOT EXISTS public.expenses
(
    id integer NOT NULL DEFAULT nextval('expenses_id_seq'::regclass),
    transaction_date timestamp without time zone,
    withdrawal double precision,
    description character varying COLLATE pg_catalog."default",
    category_id integer,
    source_id integer,
    merchant_id integer,
    created_at timestamp without time zone,
    time_stamp timestamp without time zone,
    deposit double precision,
    CONSTRAINT expenses_pkey PRIMARY KEY (id),
    CONSTRAINT expenses_category_id_fkey FOREIGN KEY (category_id)
        REFERENCES public.category (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT expenses_merchant_id_fkey FOREIGN KEY (merchant_id)
        REFERENCES public.merchant (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT expenses_source_id_fkey FOREIGN KEY (source_id)
        REFERENCES public.source (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.expenses
    OWNER to postgres;
-- Index: ix_expenses_id

-- DROP INDEX IF EXISTS public.ix_expenses_id;

CREATE INDEX IF NOT EXISTS ix_expenses_id
    ON public.expenses USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default;

ALTER TABLE expenses
ADD COLUMN user_id UUID;

ALTER TABLE expenses
ADD CONSTRAINT fk_expenses_user
FOREIGN KEY (user_id)
REFERENCES "user"(id)
ON DELETE CASCADE;