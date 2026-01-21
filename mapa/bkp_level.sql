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

DROP TABLE public.level;
SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: level; Type: TABLE; Schema: public; Owner: obi
--

CREATE TABLE public.level (
    level_id integer,
    level_short_name character varying(60),
    level_name character(32)
);


ALTER TABLE public.level OWNER TO obi;

--
-- Data for Name: level; Type: TABLE DATA; Schema: public; Owner: obi
--

COPY public.level (level_id, level_short_name, level_name) FROM stdin;
1	Iniciação 1	I1                              
2	Iniciação 2	I2                              
7	Iniciação Júnior	IJ                              
5	Programação Júnior	PJ                              
3	Programação 1	P1                              
4	Programação 2	P2                              
6	Programação Sênior	PS                              
\.


--
-- PostgreSQL database dump complete
--

