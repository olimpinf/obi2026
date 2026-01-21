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

ALTER TABLE ONLY public.states DROP CONSTRAINT states_pkey;
ALTER TABLE public.states ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.states_id_seq;
DROP TABLE public.states;
SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: states; Type: TABLE; Schema: public; Owner: obi
--

CREATE TABLE public.states (
    id integer NOT NULL,
    name character varying(30) NOT NULL,
    short_name character varying(4)
);


ALTER TABLE public.states OWNER TO obi;

--
-- Name: states_id_seq; Type: SEQUENCE; Schema: public; Owner: obi
--

CREATE SEQUENCE public.states_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.states_id_seq OWNER TO obi;

--
-- Name: states_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: obi
--

ALTER SEQUENCE public.states_id_seq OWNED BY public.states.id;


--
-- Name: states id; Type: DEFAULT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.states ALTER COLUMN id SET DEFAULT nextval('public.states_id_seq'::regclass);


--
-- Data for Name: states; Type: TABLE DATA; Schema: public; Owner: obi
--

COPY public.states (id, name, short_name) FROM stdin;
11	Rondônia	RO
12	Acre	AC
13	Amazonas	AM
14	Roraima	RR
15	Pará	PA
16	Amapá	AP
17	Tocantins	TO
21	Maranhão	MA
22	Piauí	PI
23	Ceará	CE
24	Rio Grande do Norte	RN
25	Paraíba	PB
26	Pernambuco	PE
27	Alagoas	AL
28	Sergipe	SE
29	Bahia	BA
31	Minas Gerais	MG
32	Espírito Santo	ES
33	Rio de Janeiro	RJ
35	São Paulo	SP
41	Paraná	PR
42	Santa Catarina	SC
43	Rio Grande do Sul	RS
50	Mato Grosso do Sul	MS
51	Mato Grosso	MT
52	Goiás	GO
53	Distrito Federal	DF
\.


--
-- Name: states_id_seq; Type: SEQUENCE SET; Schema: public; Owner: obi
--

SELECT pg_catalog.setval('public.states_id_seq', 1, false);


--
-- Name: states states_pkey; Type: CONSTRAINT; Schema: public; Owner: obi
--

ALTER TABLE ONLY public.states
    ADD CONSTRAINT states_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

