--
-- PostgreSQL database dump
--

-- Dumped from database version 10.22 (Ubuntu 10.22-0ubuntu0.18.04.1)
-- Dumped by pg_dump version 10.22 (Ubuntu 10.22-0ubuntu0.18.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: certif_hash; Type: TABLE; Schema: public; Owner: obi
--

CREATE TABLE public.certif_hash (
    id integer NOT NULL,
    hash character varying(255) NOT NULL,
    colab_id integer,
    compet_id integer,
    school_id integer
);


ALTER TABLE public.certif_hash OWNER TO obi;

--
-- Name: certif_hash_id_seq; Type: SEQUENCE; Schema: public; Owner: obi
--

CREATE SEQUENCE public.certif_hash_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.certif_hash_id_seq OWNER TO obi;

--
-- Name: certif_hash_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: obi
--

ALTER SEQUENCE public.certif_hash_id_seq OWNED BY public.certif_hash.id;


--
-- Name: certif_hash id; Type: DEFAULT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.certif_hash ALTER COLUMN id SET DEFAULT nextval('public.certif_hash_id_seq'::regclass);


--
-- Name: certif_hash certif_hash_colab_id_key; Type: CONSTRAINT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.certif_hash
    ADD CONSTRAINT certif_hash_colab_id_key UNIQUE (colab_id);


--
-- Name: certif_hash certif_hash_compet_id_key; Type: CONSTRAINT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.certif_hash
    ADD CONSTRAINT certif_hash_compet_id_key UNIQUE (compet_id);


--
-- Name: certif_hash certif_hash_hash_key; Type: CONSTRAINT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.certif_hash
    ADD CONSTRAINT certif_hash_hash_key UNIQUE (hash);


--
-- Name: certif_hash certif_hash_pkey; Type: CONSTRAINT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.certif_hash
    ADD CONSTRAINT certif_hash_pkey PRIMARY KEY (id);


--
-- Name: certif_hash certif_hash_school_id_key; Type: CONSTRAINT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.certif_hash
    ADD CONSTRAINT certif_hash_school_id_key UNIQUE (school_id);


--
-- Name: certif_hash_hash_3df5aad9_like; Type: INDEX; Schema: public; Owner: obi
--

CREATE INDEX certif_hash_hash_3df5aad9_like ON public.certif_hash USING btree (hash varchar_pattern_ops);


--
-- Name: certif_hash certif_hash_colab_id_3c1d6227_fk_colab_colab_id; Type: FK CONSTRAINT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.certif_hash
    ADD CONSTRAINT certif_hash_colab_id_3c1d6227_fk_colab_colab_id FOREIGN KEY (colab_id) REFERENCES public.colab(colab_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: certif_hash certif_hash_compet_id_7a8f2db6_fk_compet_compet_id; Type: FK CONSTRAINT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.certif_hash
    ADD CONSTRAINT certif_hash_compet_id_7a8f2db6_fk_compet_compet_id FOREIGN KEY (compet_id) REFERENCES public.compet(compet_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: certif_hash certif_hash_school_id_a93510b7_fk_school_school_id; Type: FK CONSTRAINT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.certif_hash
    ADD CONSTRAINT certif_hash_school_id_a93510b7_fk_school_school_id FOREIGN KEY (school_id) REFERENCES public.school(school_id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

