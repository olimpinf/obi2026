--
-- PostgreSQL database dump
--

-- Dumped from database version 10.8
-- Dumped by pg_dump version 11.4

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

--
-- Data for Name: calendar_competition; Type: TABLE DATA; Schema: public; Owner: obi
--

COPY public.calendar_competition (id, name, name_abbrev, name_uniq, color, link) FROM stdin;
2	Modalidade Programação	Programação	Modalidade Programação	light-red-bkgd	\N
1	Semana Olímpica	Semana Olímpica	Semana Olímpica	dark-red-bkgd	\N
3	Modalidade Iniciação	Iniciação	Modalidade Iniciação	dark-blue-bkgd	\N
\.


--
-- Data for Name: calendar_event; Type: TABLE DATA; Schema: public; Owner: obi
--

COPY public.calendar_event (id, name, name_abbrev, name_uniq, start, finish, comment, competition_id) FROM stdin;
4	Modalidade Iniciação - Fase Estadual	Iniciação - Fase 2	Iniciação - Fase 2	2020-06-11 06:00:00-03	2020-06-11 18:00:00-03	Horário à escolha da escola	2
3	Modalidade Programação - Fase Estadual	Programação - Fase 2	Programação - Fase 2	2020-06-17 06:00:00-03	2020-06-17 18:00:00-03	Horário à escolha da escola	2
5	Fase Nacional	Fase Nacional	Fase 3	2020-09-26 06:00:00-03	2020-09-26 18:00:00-03	NívelJúnior: 9:00 -- 12:00; Nível 1:  8:00 -- 12:00; Níveis 2 e Sênior: 13:00 -- 19:00	2
6	Semana Olímpica	Semana	Semana	2020-12-06 07:00:00-02	2020-12-12 19:00:00-02	\N	1
2	Fase Local	Iniciação - Fase 1	Iniciação - Fase 1	2020-05-18 06:00:00-03	2020-05-19 18:00:00-03	Horário a escolha da escola	3
1	Fase Local	Programação - Fase 1	Programação - Fase 1	2020-05-11 06:00:00-03	2020-05-12 18:00:00-03	Horário a escolha da escola	2
\.


--
-- Data for Name: calendar_national_competition; Type: TABLE DATA; Schema: public; Owner: obi
--

COPY public.calendar_national_competition (id, name, name_abbrev, name_uniq, color, link) FROM stdin;
7	Olimpíada Brasileira de Informática	OBI	OBI	dark-green-bkgd	https://olimpiada.ic.unicamp.br
11	Olimpíada Brasileira de Saúde e Meio Ambiente	OBSMA	OBSMA	yellow-bkgd	https://olimpiada.fiocruz.br
10	Olimpíada Brasileira de Física das Escolas Públicas	OBFEP	OBFEP	brown-bkgd	http://www.sbfisica.org.br/~obfep/
9	Olimpíada Nacional em História do Brasil	ONHB	ONHB	light-green-bkgd	https://www.olimpiadadehistoria.com.br/
8	Olimpíada Brasileira de Astronomia e Astronáutica	OBA	OBA	dark-blue-bkgd	http://www.oba.org.br/site/
6	Olimpíada Brasileira de Robótica	OBR	OBR	light-purple-bkgd	http://www.obr.org.br
5	Olimpíada Nacional de Ciências	ONC	ONC	dark-purple-bkgd	https://onciencias.org
4	Olimpíada Brasileira de Física	OBF	OBF	light-blue-bkgd	http://www.sbfisica.org.br/v1/olimpiada/2020
3	Olimpíada Brasileira de Química Júnior	OBQJr	OBQJr	orange-bkgd	https://www.obquimica.org/olimpiadas/index/olimpiada-brasileira-de-quimica-junior
2	Olimpíada Brasileira de Química	OBQ	OBQ	light-red-bkgd	http://www.obquimica.org/olimpiadas/index/olimpiada-brasileira-de-quimica
1	Exame Nacional do Ensino Médio	ENEM	ENEM	dark-red-bkgd	https://enem.inep.gov.br
12	Feriado Nacional	Feriado Nacional	Feriado Nacional	grey-bkgd	\N
\.


--
-- Data for Name: calendar_national_event; Type: TABLE DATA; Schema: public; Owner: obi
--

COPY public.calendar_national_event (id, name, name_abbrev, name_uniq, start, finish, comment, competition_id) FROM stdin;
8	Fase I	Fase 1	Fase 1	2020-08-13 06:00:00-03	2020-08-15 18:00:00-03	\N	3
9	Fase 2	Fase 2	Fase 2	2020-09-19 13:00:00-03	2020-09-19 18:00:00-03	\N	3
10	Fase 1	Fase 1	Fase 1	2020-05-07 06:00:00-03	2020-05-07 18:00:00-03	\N	4
11	Fase 2	Fase 2	Fase 2	2020-08-15 06:00:00-03	2020-08-15 12:00:00-03	\N	4
12	Fase 3	Fase 3	Fase 3	2020-10-17 13:00:00-03	2020-10-17 18:00:00-03	\N	4
13	Fase 1 - Modalidade Iniciação	Fase 1 - Modalidade Iniciação	Fase 1 - Modalidade Iniciação	2020-05-18 06:00:00-03	2020-05-19 18:00:00-03	Horário à escolha da escola, duração uma hora.	7
2	Enem Digital Dia 2	Enem Digital Dia 2	Enem Digital Dia 2	2020-10-18 13:00:00-03	2020-10-18 18:00:00-03	\N	1
1	Enem digital	Enem Digital Dia 1	Enem Digital Dia 1	2020-10-11 13:00:00-03	2020-10-11 18:00:00-03	\N	1
14	Modalidade Teórica - Fase 1	Modalidade Teórica - Fase 1	Modalidade Teórica - Fase 1	2020-06-05 06:00:00-03	2020-06-05 18:00:00-03	Horário à escolha da escola, duração variável de acordo com o nível.	6
15	Modalidade Teórica - Fase 2	Modalidade Teórica - Fase 2	Modalidade Teórica - Fase 2	2020-08-21 06:00:00-03	2020-08-21 18:00:00-03	Local: sedes regionais	6
16	Modalidade Prática - Etapa Nacional	Modalidade Prática - Etapa Nacio	Modalidade Prática - Etapa Nacio	2020-11-14 07:00:00-02	2020-11-14 19:00:00-02	\N	6
17	Primeira Fase	Primeira Fase	Primeira Fase	2020-08-13 06:00:00-03	2020-08-13 18:00:00-03	\N	10
18	Segunda Fase	Segunda Fase	Segunda Fase	2020-10-24 13:00:00-03	2020-10-24 17:00:00-03	\N	10
19	Independência	Independência	Independência	2020-09-07 00:00:00-03	2020-09-07 23:59:59-03	\N	12
20	Sexta-feira Santa	Sexta-feira Santa	Sexta-feira Santa	2020-04-10 00:00:00-03	2020-04-10 23:59:59-03	\N	12
21	Tiradentes	Tiradentes	Tiradentes	2020-04-21 00:00:00-03	2020-04-21 23:59:59-03	\N	12
22	Dia do Trabalho	Dia do Trabalho	Dia do Trabalho	2020-05-01 00:00:00-03	2020-05-01 23:59:59-03	\N	12
23	Corpus Christi	Corpus Christi	Corpus Christi	2020-06-11 00:00:00-03	2020-06-11 23:59:59-03	\N	12
24	Nossa Senhora Aparecida	Nossa Senhora Aparecida	Nossa Senhora Aparecida	2020-10-12 00:00:00-03	2020-10-12 23:59:59-03	\N	12
25	Finados	Finados	Finados	2020-11-02 01:00:00-02	2020-11-03 00:59:59-02	\N	12
26	Proclamação da República	Proclamação da República	Proclamação da República	2020-11-15 01:00:00-02	2020-11-16 00:59:59-02	\N	12
27	Natal	Natal	Natal	2020-12-25 01:00:00-02	2020-12-26 00:59:59-02	\N	12
28	Dia das Mães	Dia das Mães	Dia das Mães	2020-05-10 00:00:00-03	2020-05-10 23:59:59-03	\N	12
29	Dia dos Pais	Dia dos Pais	Dia dos Pais	2020-08-09 00:00:00-03	2020-08-09 23:59:59-03	\N	12
4	Dia 2	Dia 2	Dia 2	2020-11-08 14:00:00-02	2020-11-08 19:00:00-02	\N	1
3	Dia 1	Dia 1	Dia 1	2020-11-01 14:00:00-02	2020-11-01 19:00:00-02	\N	1
7	Fase III	Fase III	Fase III	2020-08-22 14:00:00-03	2020-08-22 18:00:00-03	\N	2
5	Fase IV	Fase IV	Fase IV	2020-02-07 15:00:00-02	2020-02-07 19:00:00-02	\N	2
6	Fase VI	Fase VI	Fase VI	2020-04-30 09:00:00-03	2020-04-30 14:00:00-03	\N	2
31	Prova	Prova	Prova	2020-05-15 06:00:00-03	2020-05-15 18:00:00-03	Horário à escolha da escola, duração dependente do nível.	8
30	Provas Seletivas	Provas Seletivas	Provas Seletivas	2020-03-04 06:00:00-03	2020-03-04 18:00:00-03	Horário à escolha da escola.	8
32	Premiação Nacional	Premiação Nacional	Premiação Nacional	2020-11-27 19:00:00-02	2020-11-27 19:00:00-02	Local: Brasília	2
33	Premiação Nacional	Premiação Nacional	Premiação Nacional	2020-11-26 19:00:00-02	2020-11-26 19:00:00-02	Local: Brasília	5
34	Prova Presencial	Prova Presencial	Prova Presencial	2020-08-15 06:00:00-03	2020-08-16 18:00:00-03	Local: Unicamp	9
\.


--
-- Name: calendar_competition_id_seq; Type: SEQUENCE SET; Schema: public; Owner: obi
--

SELECT pg_catalog.setval('public.calendar_competition_id_seq', 3, true);


--
-- Name: calendar_event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: obi
--

SELECT pg_catalog.setval('public.calendar_event_id_seq', 6, true);


--
-- Name: calendar_national_competition_id_seq; Type: SEQUENCE SET; Schema: public; Owner: obi
--

SELECT pg_catalog.setval('public.calendar_national_competition_id_seq', 12, true);


--
-- Name: calendar_national_event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: obi
--

SELECT pg_catalog.setval('public.calendar_national_event_id_seq', 34, true);


--
-- PostgreSQL database dump complete
--

