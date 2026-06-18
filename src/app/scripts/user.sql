-- Table: public.user

-- DROP TABLE IF EXISTS public."user";

CREATE TABLE IF NOT EXISTS public."user"
(
    id uuid NOT NULL,
    auth_id character varying COLLATE pg_catalog."default" NOT NULL,
    username character varying COLLATE pg_catalog."default",
    email character varying COLLATE pg_catalog."default",
    created_at timestamp without time zone,
    CONSTRAINT user_pkey PRIMARY KEY (id),
    CONSTRAINT unique_auth_id UNIQUE (auth_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."user"
    OWNER to postgres;

CREATE INDEX IF NOT EXISTS ix_user_id
    ON public."user" USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default;