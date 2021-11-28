--
-- PostgreSQL database cluster dump
--

-- Started on 2021-11-27 22:01:15 UTC

SET default_transaction_read_only = off;

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

--
-- PostgreSQL database dump
--

-- Dumped from database version 11.14
-- Dumped by pg_dump version 11.13

-- Started on 2021-11-27 22:01:15 UTC

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

-- Completed on 2021-11-27 22:01:16 UTC

--
-- PostgreSQL database dump complete
--

\connect postgres

--
-- PostgreSQL database dump
--

-- Dumped from database version 11.14
-- Dumped by pg_dump version 11.13

-- Started on 2021-11-27 22:01:16 UTC

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

-- Completed on 2021-11-27 22:01:16 UTC

--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 11.14
-- Dumped by pg_dump version 11.13

-- Started on 2021-11-27 22:01:16 UTC

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
-- TOC entry 3003 (class 1262 OID 16384)
-- Name: subscribers; Type: DATABASE; Schema: -; Owner: postgres
--

CREATE DATABASE subscribers WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8';


ALTER DATABASE subscribers OWNER TO postgres;

\connect subscribers

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
-- TOC entry 200 (class 1259 OID 16511)
-- Name: apns_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.apns_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.apns_id_seq OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 197 (class 1259 OID 16393)
-- Name: apns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.apns (
    id bigint DEFAULT nextval('public.apns_id_seq'::regclass) NOT NULL,
    apn_id integer,
    apn_name character varying(50),
    pdn_type character varying(12),
    qci integer,
    priority_level integer,
    max_req_bw_ul bigint,
    max_req_bw_dl bigint
);


ALTER TABLE public.apns OWNER TO postgres;

--
-- TOC entry 203 (class 1259 OID 16519)
-- Name: mip6s; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mip6s (
    id bigint NOT NULL,
    context_id integer,
    service_selection character varying,
    destination_realm character varying,
    destination_host character varying
);


ALTER TABLE public.mip6s OWNER TO postgres;

--
-- TOC entry 202 (class 1259 OID 16517)
-- Name: mip6s_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mip6s_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mip6s_id_seq OWNER TO postgres;

--
-- TOC entry 3004 (class 0 OID 0)
-- Dependencies: 202
-- Name: mip6s_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mip6s_id_seq OWNED BY public.mip6s.id;


--
-- TOC entry 199 (class 1259 OID 16494)
-- Name: subscriber_apns; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscriber_apns (
    id bigint NOT NULL,
    subscriber_id bigint,
    apn_id bigint,
    mip6_id bigint
);


ALTER TABLE public.subscriber_apns OWNER TO postgres;

--
-- TOC entry 198 (class 1259 OID 16492)
-- Name: subscriber_apns_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subscriber_apns_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subscriber_apns_id_seq OWNER TO postgres;

--
-- TOC entry 3005 (class 0 OID 0)
-- Dependencies: 198
-- Name: subscriber_apns_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subscriber_apns_id_seq OWNED BY public.subscriber_apns.id;


--
-- TOC entry 205 (class 1259 OID 16541)
-- Name: subscriber_mip6s; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscriber_mip6s (
    id bigint NOT NULL,
    subscriber_id bigint,
    mip6_id bigint
);


ALTER TABLE public.subscriber_mip6s OWNER TO postgres;

--
-- TOC entry 204 (class 1259 OID 16539)
-- Name: subscriber_mip6s_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subscriber_mip6s_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subscriber_mip6s_id_seq OWNER TO postgres;

--
-- TOC entry 3006 (class 0 OID 0)
-- Dependencies: 204
-- Name: subscriber_mip6s_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subscriber_mip6s_id_seq OWNED BY public.subscriber_mip6s.id;


--
-- TOC entry 201 (class 1259 OID 16513)
-- Name: subscribers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subscribers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.subscribers_id_seq OWNER TO postgres;

--
-- TOC entry 196 (class 1259 OID 16385)
-- Name: subscribers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscribers (
    id bigint DEFAULT nextval('public.subscribers_id_seq'::regclass) NOT NULL,
    imsi bigint,
    key bytea,
    opc bytea,
    amf bytea,
    sqn bytea,
    msisdn bigint,
    stn_sr bigint,
    roaming_allowed boolean,
    schar integer,
    max_req_bw_ul bigint,
    max_req_bw_dl bigint,
    default_apn integer,
    mme_hostname character varying(100),
    mme_realm character varying(80),
    ue_srvcc_support boolean,
    odb character varying(60)
);


ALTER TABLE public.subscribers OWNER TO postgres;

--
-- TOC entry 2851 (class 2604 OID 16522)
-- Name: mip6s id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mip6s ALTER COLUMN id SET DEFAULT nextval('public.mip6s_id_seq'::regclass);


--
-- TOC entry 2850 (class 2604 OID 16497)
-- Name: subscriber_apns id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriber_apns ALTER COLUMN id SET DEFAULT nextval('public.subscriber_apns_id_seq'::regclass);


--
-- TOC entry 2852 (class 2604 OID 16544)
-- Name: subscriber_mip6s id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriber_mip6s ALTER COLUMN id SET DEFAULT nextval('public.subscriber_mip6s_id_seq'::regclass);


--
-- TOC entry 2989 (class 0 OID 16393)
-- Dependencies: 197
-- Data for Name: apns; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.apns (id, apn_id, apn_name, pdn_type, qci, priority_level, max_req_bw_ul, max_req_bw_dl) FROM stdin;
4	5	xcap	IPv4v6	9	8	256	256
5	824	ims	IPv4v6	5	8	256	256
1	1	internet	IPv4	9	8	999999999	999999999
2	4	internetlte	IPv4v6	9	8	999999999	999999999
3	3	mms	IPv4	9	8	256	256
\.


--
-- TOC entry 2995 (class 0 OID 16519)
-- Dependencies: 203
-- Data for Name: mip6s; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mip6s (id, context_id, service_selection, destination_realm, destination_host) FROM stdin;
1	1	\N	\N	\N
4	824	\N	\N	\N
2	4	\N	epc.mncXXX.mccYYY.3gppnetwork.org	topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org
3	3	\N	epc.mncXXX.mccYYY.3gppnetwork.org	topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org
5	1	\N	\N	\N
6	4	\N	\N	\N
7	3	\N	\N	\N
8	824	\N	\N	\N
9	1	\N	\N	\N
10	4	\N	\N	\N
11	3	\N	\N	\N
12	824	\N	\N	\N
13	1	\N	\N	\N
14	4	\N	\N	\N
15	3	\N	\N	\N
16	824	\N	\N	\N
\.


--
-- TOC entry 2991 (class 0 OID 16494)
-- Dependencies: 199
-- Data for Name: subscriber_apns; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subscriber_apns (id, subscriber_id, apn_id, mip6_id) FROM stdin;
1	3	1	\N
2	3	2	\N
3	3	3	\N
4	3	5	\N
5	4	1	\N
6	4	2	\N
7	4	3	\N
8	4	5	\N
9	5	1	\N
10	5	2	\N
11	5	3	\N
12	5	5	\N
13	6	1	\N
14	6	2	\N
15	6	3	\N
16	6	5	\N
\.


--
-- TOC entry 2997 (class 0 OID 16541)
-- Dependencies: 205
-- Data for Name: subscriber_mip6s; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subscriber_mip6s (id, subscriber_id, mip6_id) FROM stdin;
1	3	1
2	3	2
3	3	3
4	3	4
5	4	5
6	4	6
7	4	7
8	4	8
9	5	9
10	5	10
11	5	11
12	5	12
13	6	13
14	6	14
15	6	15
16	6	16
\.


--
-- TOC entry 2988 (class 0 OID 16385)
-- Dependencies: 196
-- Data for Name: subscribers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.subscribers (id, imsi, key, opc, amf, sqn, msisdn, stn_sr, roaming_allowed, schar, max_req_bw_ul, max_req_bw_dl, default_apn, mme_hostname, mme_realm, ue_srvcc_support, odb) FROM stdin;
1	999000000000001	\\x465b5ce8b199b49faa5f0a2ee238a6bc	\\x013d7d16d7ad4fefb61bd95b765c8ceb	\\xb9b9	\\xff9bb4d0b607	5521000000001	5500599999999	t	8	256	256	824	localhost.domain	domain	t	\N
2	999000000000005	\\x465b5ce8b199b49faa5f0a2ee238a6bc	\\x013d7d16d7ad4fefb61bd95b765c8ceb	\\xb9b9	\\xff9bb4d0b607	5521000000005	5500599999999	f	8	100000	100000	1	localhost.mnc000.mcc999.3gppnetwork.org	mnc000.mcc999.3gppnetwork.org	t	ODB-all-APN
3	999000000000006	\\x465b5ce8b199b49faa5f0a2ee238a6bc	\\x013d7d16d7ad4fefb61bd95b765c8ceb	\\xb9b9	\\xff9bb4d0b607	5521000000006	5500599999999	f	8	100000	100000	1	localhost.mnc000.mcc999.3gppnetwork.org	mnc000.mcc999.3gppnetwork.org	t	ODB-HPLMN-APN
4	999000000000007	\\x465b5ce8b199b49faa5f0a2ee238a6bc	\\x013d7d16d7ad4fefb61bd95b765c8ceb	\\xb9b9	\\xff9bb4d0b607	5521000000007	5500599999999	f	8	100000	100000	1	localhost.mnc000.mcc999.3gppnetwork.org	mnc000.mcc999.3gppnetwork.org	t	ODB-VPLMN-APN
\.


--
-- TOC entry 3007 (class 0 OID 0)
-- Dependencies: 200
-- Name: apns_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.apns_id_seq', 6, true);


--
-- TOC entry 3008 (class 0 OID 0)
-- Dependencies: 202
-- Name: mip6s_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mip6s_id_seq', 17, true);


--
-- TOC entry 3009 (class 0 OID 0)
-- Dependencies: 198
-- Name: subscriber_apns_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subscriber_apns_id_seq', 71, true);


--
-- TOC entry 3010 (class 0 OID 0)
-- Dependencies: 204
-- Name: subscriber_mip6s_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subscriber_mip6s_id_seq', 16, true);


--
-- TOC entry 3011 (class 0 OID 0)
-- Dependencies: 201
-- Name: subscribers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.subscribers_id_seq', 5, true);


--
-- TOC entry 2856 (class 2606 OID 16397)
-- Name: apns apns_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.apns
    ADD CONSTRAINT apns_pkey PRIMARY KEY (id);


--
-- TOC entry 2860 (class 2606 OID 16527)
-- Name: mip6s mip6_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mip6s
    ADD CONSTRAINT mip6_pkey PRIMARY KEY (id);


--
-- TOC entry 2858 (class 2606 OID 16499)
-- Name: subscriber_apns profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriber_apns
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);


--
-- TOC entry 2862 (class 2606 OID 16546)
-- Name: subscriber_mip6s subscriber_mip6s_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriber_mip6s
    ADD CONSTRAINT subscriber_mip6s_pkey PRIMARY KEY (id);


--
-- TOC entry 2854 (class 2606 OID 16392)
-- Name: subscribers subscribers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscribers
    ADD CONSTRAINT subscribers_pkey PRIMARY KEY (id);


--
-- TOC entry 2864 (class 2606 OID 16505)
-- Name: subscriber_apns profiles_apn_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriber_apns
    ADD CONSTRAINT profiles_apn_id_fkey FOREIGN KEY (apn_id) REFERENCES public.apns(id);


--
-- TOC entry 2863 (class 2606 OID 16500)
-- Name: subscriber_apns profiles_subscriber_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriber_apns
    ADD CONSTRAINT profiles_subscriber_id_fkey FOREIGN KEY (subscriber_id) REFERENCES public.subscribers(id);


--
-- TOC entry 2866 (class 2606 OID 16552)
-- Name: subscriber_mip6s subscriber_mip6s_mip6_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriber_mip6s
    ADD CONSTRAINT subscriber_mip6s_mip6_id_fkey FOREIGN KEY (mip6_id) REFERENCES public.mip6s(id);


--
-- TOC entry 2865 (class 2606 OID 16547)
-- Name: subscriber_mip6s subscriber_mip6s_subscriber_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriber_mip6s
    ADD CONSTRAINT subscriber_mip6s_subscriber_id_fkey FOREIGN KEY (subscriber_id) REFERENCES public.subscribers(id);


-- Completed on 2021-11-27 22:01:16 UTC

--
-- PostgreSQL database dump complete
--

-- Completed on 2021-11-27 22:01:16 UTC

--
-- PostgreSQL database cluster dump complete
--

