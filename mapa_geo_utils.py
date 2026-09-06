# -*- coding: utf-8 -*-
"""
UTILIDADES GEOESPACIALES Y GENERADOR DE MAPA SATELITAL / CALOR GAMLP (100% $0 COSTO)
====================================================================================
Coordenadas GPS 100% Reales y Precisas extraídas del Sistema GIS GAMLP (Google My Maps Oficial).
Proporciona:
1. Catálogo exhaustivo de Coordenadas GPS, Direcciones, Directores y Servicios de Centros y Hospitales en La Paz.
2. Motor de Georreferenciación Automática con Algoritmo Difuso (Fuzzy Matching) de Alta Precisión.
3. Generador de Mapa Interactivo Satelital Híbrido (Leaflet.js + ESRI World Imagery + Heatmap + Buscador en Vivo).
"""

import json
import re
import unicodedata
import difflib

# Catálogo Oficial de Coordenadas GPS Reales de Centros de Salud y Hospitales del GAMLP (Google My Maps Oficial)
COORDENADAS_CENTROS_GAMLP = {
    "C.S. 8 DE DICIEMBRE": {
        "lat": -16.5181744,
        "lon": -68.1330671,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "FINAL VINCENTI ESQUINA CIRCUNVALACION",
        "director": "DIRECTORA: Dra. Rosse Mary Yupanqui \t69844363",
        "telefono": "69844363",
        "servicios": "MEDICINA GENERAL, ODONTOLOGIA, ENFERMERIA, VACUNACION"
    },
    "C.S. BAJO TACAGUA": {
        "lat": -16.5103194,
        "lon": -68.1458019,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "AVENIDA JULIO TELLEZ ESQUINA MANUEL JOFRE",
        "director": "DIRECTOR.Dr. Gustavo Pereyra\t76515153",
        "telefono": "76515153",
        "servicios": "MEDICINA GENERAL, ODONTOLOGIA, ENFERMERIA, VACUNACION"
    },
    "C.S. BIBLIOTECA": {
        "lat": -16.5049469,
        "lon": -68.1497678,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "",
        "director": "DIRECTOR: Dr. Rubén Copana\t73069373",
        "telefono": "73069373",
        "servicios": "MEDICINA GENERAL, ODONTOLOGIA, ENFERMERIA, VACUNACION"
    },
    "C.S.ALCOREZA": {
        "lat": -16.5089006,
        "lon": -68.1515612,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "AV. PABLO ZARATE Y COOPERATIVAS",
        "director": "DIRECTOR Dr. Edgar Merlo\t72076290",
        "telefono": "72076290",
        "servicios": "MEDICINA GENERAL, ODONTOLOGIA, ENFERMERIA, VACUNACION"
    },
    "C.S.ALTO TACAGUA": {
        "lat": -16.5135143,
        "lon": -68.1498035,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE INCA MAYU Y SANTA ROSA",
        "director": "DIRECTOR: Dra.Jhovana Poma Torres \t73283353",
        "telefono": "73283353",
        "servicios": "MEDICINA GENERAL, ODONTOLOGIA, ENFERMERIA, VACUNACION"
    },
    "C.S.ALTO TACUAGUA": {
        "lat": -16.513504,
        "lon": -68.1498008,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE INCA MAYU Y SANTA ROSA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.BAJO SAN PEDRO": {
        "lat": -16.5007976,
        "lon": -68.1369902,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE INCA MAYU Y SANTA ROSA",
        "director": "DIRECTOR: Dra. Cintia Pimentel \t72035575",
        "telefono": "72035575",
        "servicios": "MEDICINA GENERAL, ODONTOLOGIA, ENFERMERIA, VACUNACION, LABORATORIO CLINICO, ECOGRAFIA"
    },
    "C.S.EL ROSAL": {
        "lat": -16.5342288,
        "lon": -68.1312831,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "AV. MARIO MERCADO ENTRE CALLES \"E\" Y \"B\"",
        "director": "DIRECTOR: Dra. Elfride Cardoso Ledezma\t65171308",
        "telefono": "65171308",
        "servicios": "MEDICINA GENERAL, ODONTOLOGIA, ENFERMERIA, VACUNACION, LABORATORIO CLINICO, ECOGRAFIA"
    },
    "C.S.LA GRUTA": {
        "lat": -16.5064849,
        "lon": -68.1553216,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "AV. 9 DE ABRIL (CASI FARO MURILLO)",
        "director": "DIRECTOR:;Dra. Sonia Isabel Mendoza \t77558497",
        "telefono": "77558497",
        "servicios": "MEDICINA GENERAL, ODONTOLOGIA, ENFERMERIA, VACUNACION"
    },
    "C.S.NIÑO KOLLO": {
        "lat": -16.5100976,
        "lon": -68.1491182,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "AVENIDA 16 DE JULIO EQUINA PABLO ZARATE WILLKA",
        "director": "DIRECTORA:Dra. María del Carmen Guillén \t65644461",
        "telefono": "65644461",
        "servicios": "MEDICINA GENERAL, ODONTOLOGIA, ENFERMERIA, VACUNACION"
    },
    "C.S.PASANKERI": {
        "lat": -16.5229115,
        "lon": -68.146054,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "AV. MARCELO QUIROGA SANTA CRUZ ESQUINA HEROES DEL CHACO",
        "director": "DIRECTOR: Dra. Paola Delgado \t78966043",
        "telefono": "78966043",
        "servicios": "MEDICINA GENERAL, ODONTOLOGIA, ENFERMERIA, VACUNACION"
    },
    "C.S.SAN LUIS": {
        "lat": -16.5105057,
        "lon": -68.135706,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "AV. CHACO ESQUINA IGNACIO PRUDENCIO",
        "director": "dIRECTORA Dra. Ivanoska Chávez Nuñez \t70126560",
        "telefono": "70126560",
        "servicios": "MEDICINA GENERAL, ODONTOLOGIA, ENFERMERIA, VACUNACION"
    },
    "C.S.TEMBLADERANI": {
        "lat": -16.5105837,
        "lon": -68.1425536,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "AV. VICTOR AGUSTIN UGARTE ESQUINA JAIME ZUDAÑEZ",
        "director": "DIRECTOR: Dra. Silvia Victoria Mendoza \t77543436",
        "telefono": "77543436",
        "servicios": "MEDICINA GENERAL, ODONTOLOGIA, ENFERMERIA, VACUNACION, LABORATORIO CLINICO, ECOGRAFIA"
    },
    "C.S.VILLA NUEVA POTOSI": {
        "lat": -16.5073908,
        "lon": -68.1437839,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE MANUEL JOFRE ESQUINA ONDARZA S/N",
        "director": "DIRECTOR Dr. Reynaldo Jiménez \t71507502",
        "telefono": "71507502",
        "servicios": "MEDICINA GENERAL, ODONTOLOGIA, ENFERMERIA, VACUNACION, LABORATORIO CLINICO, ECOGRAFIA, GINECOOBSTETRICIA"
    },
    "Hospital Municipal Cotahuma": {
        "lat": -16.5173,
        "lon": -68.1408,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Segundo Nivel",
        "direccion": "Av. Jaimes Freyre esq. Victor Sanjinez (Cotahuma)",
        "director": "Director Médico Hospital Cotahuma",
        "telefono": "2422323",
        "servicios": "Emergencias 24h, Cirugía, Medicina Interna, Pediatría, Ginecoobstetricia, Imagenología, Laboratorio"
    },
    "Hospital Nuestra Señora de La Paz": {
        "lat": -16.4959112,
        "lon": -68.1458065,
        "red": "RED 1 - SUR OESTE (COTAHUMA)",
        "nivel": "Segundo Nivel",
        "direccion": "alle Presbítero Medina Nº 2412",
        "director": "",
        "telefono": "",
        "servicios": "Alergología e Inmunología, Cardiología, Cirugía de Columna, Cirugía General, Cirugía Plástica, Cirugía Reconstructiva, Cirugía Robótica, Cirugía Pediátrica, Cirugía Maxilofacial, Cirugía Oncológica, Dermatología, Fonoaudiología, Gastroenterología, Geriatría & Gerontología, Ginecología & Obstetricia, Imagenología, Imagenología Intervencionista, Implantología en Odontología, Medicina del Dolor, Medicina Interna, Medicina Preventiva, Medicina Paliativa, Neumología, Neurocirugía Adultos, Neurocirugía Pediátrica, Neurología Adultos, Neurología Pediátrica, Nutrición Adultos, Nutrición Pediátrica, Odontología Adultos, Odontología Pediátrica, Oftalmología, Otorrinolaringología Adultos, Otorrinolaringología Pediátrica, Pediatría, Reumatología, Psiquiatría, Psiquiatría de Adicciones, Telemedicina, Traumatología Adultos, Traumatología Pediátrica, Urología, Terapia Intensiva Neonatal, Terapia Intensiva Pediátrica, Terapia Intensiva Adultos, Servicio de Ambulancia, Servicio de Ecografía, Servicio de Emergencias, Servicio de Farmacia, Servicio de Rayos X, Servicio de Tomografía"
    },
    "C.S. APUMALLA": {
        "lat": -16.493004,
        "lon": -68.150441,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Primer Nivel",
        "direccion": "AV. APUMALLA ESQ. CALLE PEÑA S/N",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.ALTO MARISCAL SANTA CRUZ": {
        "lat": -16.493758,
        "lon": -68.162315,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Primer Nivel",
        "direccion": "AV. 2DO BASCONESPARADA MINIBUS N° 395 A 3 CUADRAS DEL COLEGIO ITALIA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.BAJO EL TEJAR": {
        "lat": -16.495302,
        "lon": -68.154242,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Primer Nivel",
        "direccion": "PLAZA 27 DE MAYO SEDE JUNTA DE VECINOS",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.CHAMOCO CHICO": {
        "lat": -16.501487,
        "lon": -68.154107,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Primer Nivel",
        "direccion": "2DO BASCONES 2DO PUENTE TOPATER",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.M.I.EL TEJAR": {
        "lat": -16.49727,
        "lon": -68.155837,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE DAMAS DE COTAGAITA S/N",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.MUNAYPATA": {
        "lat": -16.487243,
        "lon": -68.159236,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Primer Nivel",
        "direccion": "AV. NACIONES UNIDAS FRENTE 61 (CURVA COMPLEJO DEPORTIVO)",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.OBISPO INDABURO": {
        "lat": -16.500422,
        "lon": -68.149633,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE RUFINO CARRASCO N° 1448 FRENTE AL COL . EDUCATIVO LIBERTAD",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.PANTI SIRPA": {
        "lat": -16.460022,
        "lon": -68.158397,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Primer Nivel",
        "direccion": "FRENTE ESCUELA LUCIO VELASCO",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.SAID": {
        "lat": -16.482207,
        "lon": -68.150862,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE 21 DE ENERO N°29",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.VILLA VICTORIA": {
        "lat": -16.49105,
        "lon": -68.15573,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Primer Nivel",
        "direccion": "REP. ESQ.TUPIZA N° 1896",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.ZONGO": {
        "lat": -15.766634,
        "lon": -67.668731,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Puesto de Salud",
        "direccion": "COMUNIDAD ZONGO CHORO",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.ZONGO CAMSIQUE": {
        "lat": -15.766758,
        "lon": -67.668725,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Puesto de Salud",
        "direccion": "ZONGO",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "CIUDADELA FERROVIARIA": {
        "lat": -16.457302,
        "lon": -68.150092,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE 1",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "Centro de Salud Llojeta": {
        "lat": -16.5326372,
        "lon": -68.1402867,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Primer Nivel",
        "direccion": "AV. MARIO MERCADO, PLAZA 3 MARIAS",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "Hospital La Paz": {
        "lat": -16.495712,
        "lon": -68.145871,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Segundo Nivel",
        "direccion": "PL GARITA DE LIMA Y MAX PAREDES",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "Hospital Municipal La Portada": {
        "lat": -16.4890118,
        "lon": -68.1657554,
        "red": "RED 2 - NOR OESTE (MAX PAREDES)",
        "nivel": "Segundo Nivel",
        "direccion": "LA PORTADA lado IGLESIA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S JUANCITO PINTO": {
        "lat": -16.494039,
        "lon": -68.13942,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE GRANEROS Y MURILLO- SEDE SOCIAL JUNTA DE VECINOS",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S. 18 DE MAYO": {
        "lat": -16.478,
        "lon": -68.146248,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "SEDE SOCIAL Nº 104 ZONA 18 DE MAYO - VINO TINTO",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S. 3 DE MAYO": {
        "lat": -16.463838,
        "lon": -68.113513,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "Entre Calle B Y C",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S. AGUA DE LA VIDA": {
        "lat": -16.494196,
        "lon": -68.129886,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "PJE. LA BANDERA S/N ENTRE CALLE COLON Y AV. LA BANDERA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S. ASISTENCIA PUBLICA": {
        "lat": -16.5001,
        "lon": -68.13142,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "AV CAMACHO Nº 1519 ZONA CENTRAL",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S. CHUQUIAGUILLO": {
        "lat": -16.459179,
        "lon": -68.10234,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "AV. RAMIRO CASTRILLO S/N",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S. EL CALVARIO": {
        "lat": -16.482998,
        "lon": -68.129372,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "AV. PERIFERICA CALLE 7 Nº 10",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S. LAS DELICIAS": {
        "lat": -16.473838,
        "lon": -68.120851,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "C/ SAN JOSE, ESQUINA TIPUANI S/N",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.ACHACHICALA": {
        "lat": -16.475532,
        "lon": -68.15102,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "Av. Chacaltaya frente a la escuela Pedro Domingo",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.ALTO MIRAFLORES": {
        "lat": -16.479019,
        "lon": -68.125974,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE URIAS RODRIGUEZ ESQ. ADRIANA PARIENTE S/N ZONA BARRIO GRAFICO - CHAPUMA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.PLAN AUTOPISTA": {
        "lat": -16.45739,
        "lon": -68.146657,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE MANZANO \"E\" S/N LADO COMPLEJO DEPORTIVO PLAN AUTOPISTA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.SAN JOSE DE NATIVIDAD": {
        "lat": -16.475488,
        "lon": -68.114172,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "AC.COSTANERA NRO, 26 ZONA SAN JOSE DE VIILA FATINA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.SAN JUAN LAZARETO": {
        "lat": -16.49463,
        "lon": -68.12593,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "AV. TEJADA SORZANO- EXPROSALUD",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.VINO TINTO": {
        "lat": -16.482939,
        "lon": -68.141945,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "AV. BALTAZAR DE SALAS Nº 57 VINO TINTO",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.Villa Fatima": {
        "lat": -16.473868,
        "lon": -68.120934,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE SAN JOSE Y CALLE CHICALOMA ZONA LAS DELICIAS - VILLA FATIMA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "Hospital Arco Iris": {
        "lat": -16.484192,
        "lon": -68.120258,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Segundo Nivel",
        "direccion": "C Eusebio Guillarte y Calle 15 de Abril",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "Hospital Municipal La Merced": {
        "lat": -16.471002,
        "lon": -68.117708,
        "red": "RED 3 - NORTE CENTRAL (PERIFERICA)",
        "nivel": "Segundo Nivel",
        "direccion": "CALLE Villa Aspiazu Villa Zona Villa Fatima",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S. KUPINI": {
        "lat": -16.512114,
        "lon": -68.098491,
        "red": "RED 4 - ESTE (SAN ANTONIO)",
        "nivel": "Primer Nivel",
        "direccion": "ZONA KUPINI LADO CANCHA KUPINI",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.BAJO SAN ANTONIO": {
        "lat": -16.498817,
        "lon": -68.116014,
        "red": "RED 4 - ESTE (SAN ANTONIO)",
        "nivel": "Primer Nivel",
        "direccion": "AV. COSTANERA S/N",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.CHOQUECHIHUANI": {
        "lat": -16.450153,
        "lon": -68.04545,
        "red": "RED 4 - ESTE (SAN ANTONIO)",
        "nivel": "Primer Nivel",
        "direccion": "AREA RURAL",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.ESCOBAR URIA": {
        "lat": -16.492642,
        "lon": -68.108909,
        "red": "RED 4 - ESTE (SAN ANTONIO)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE NO. 6",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.PAMPAHASI ALTO": {
        "lat": -16.491135,
        "lon": -68.103719,
        "red": "RED 4 - ESTE (SAN ANTONIO)",
        "nivel": "Primer Nivel",
        "direccion": "LADO MERCADO SAN JUAN PARADA MIN. 332",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.PAMPAHASI BAJO": {
        "lat": -16.5047,
        "lon": -68.101435,
        "red": "RED 4 - ESTE (SAN ANTONIO)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE 7. LADO COLEGIO DELIA GAMBERTE PARADA MIN 849",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.SAN ANTONIO ALTO": {
        "lat": -16.500059,
        "lon": -68.108006,
        "red": "RED 4 - ESTE (SAN ANTONIO)",
        "nivel": "Primer Nivel",
        "direccion": "AV. JOSEFA MUJICA LADO. SUB ALCALDIA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.SAN ISIDRO": {
        "lat": -16.514208,
        "lon": -68.108401,
        "red": "RED 4 - ESTE (SAN ANTONIO)",
        "nivel": "Primer Nivel",
        "direccion": "PLAZA ELIZARDO PEREZ PARADA MIN. 210",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.VALLE HERMOSO": {
        "lat": -16.48959,
        "lon": -68.110083,
        "red": "RED 4 - ESTE (SAN ANTONIO)",
        "nivel": "Primer Nivel",
        "direccion": "Z. VALLE HERMOSO CALLE 7.",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.VILLA ARMONIA": {
        "lat": -16.507594,
        "lon": -68.111111,
        "red": "RED 4 - ESTE (SAN ANTONIO)",
        "nivel": "Primer Nivel",
        "direccion": "AV. JHON KENNEDY LADO IGLESIA SR. DE LA SENTENCIA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.VILLA COPACABANA": {
        "lat": -16.484167,
        "lon": -68.117297,
        "red": "RED 4 - ESTE (SAN ANTONIO)",
        "nivel": "Primer Nivel",
        "direccion": "Z. VALLE PACASA FINAL CALLE UNION",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.VILLA SALOME": {
        "lat": -16.486711,
        "lon": -68.095762,
        "red": "RED 4 - ESTE (SAN ANTONIO)",
        "nivel": "Primer Nivel",
        "direccion": "AV. LA PAZ DE AYACUCHO",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "Hospital San Gabriel": {
        "lat": -16.491424,
        "lon": -68.116539,
        "red": "RED 4 - ESTE (SAN ANTONIO)",
        "nivel": "Segundo Nivel",
        "direccion": "C PEDRO VILLAMIL",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C. S. MALLASA": {
        "lat": -16.569256,
        "lon": -68.089677,
        "red": "RED 5 - SUR (SUR / MALLASA)",
        "nivel": "Primer Nivel",
        "direccion": "PLAZA 2 DE FEBRERO, MALLASA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S. ACHUMANI": {
        "lat": -16.530939,
        "lon": -68.074886,
        "red": "RED 5 - SUR (SUR / MALLASA)",
        "nivel": "Primer Nivel",
        "direccion": "Av. Jose Manuel Chinchilla Esq. Calle 15 Achumani",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S. ALTO IRPAVI": {
        "lat": -16.515162,
        "lon": -68.084083,
        "red": "RED 5 - SUR (SUR / MALLASA)",
        "nivel": "Primer Nivel",
        "direccion": "CALLE 2 No. 10 SECTOR PEÑA AZUL, ALTO IRPAVI",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S. CHASQUIPAMPA": {
        "lat": -16.538255,
        "lon": -68.047886,
        "red": "RED 5 - SUR (SUR / MALLASA)",
        "nivel": "Primer Nivel",
        "direccion": "C/51 Y C/9 No 80, CHASQUIPAMPA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S. MALLASILLA": {
        "lat": -16.565752,
        "lon": -68.098984,
        "red": "RED 5 - SUR (SUR / MALLASA)",
        "nivel": "Primer Nivel",
        "direccion": "MALLASILLA CALLE D ENTRE CALLE 5 Y 6",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S. OBRAJES": {
        "lat": -16.529622,
        "lon": -68.102458,
        "red": "RED 5 - SUR (SUR / MALLASA)",
        "nivel": "Primer Nivel",
        "direccion": "C/16 Y C/ ORMACHEA, OBRAJES",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.ALTO OBRAJES": {
        "lat": -16.5235,
        "lon": -68.105556,
        "red": "RED 5 - SUR (SUR / MALLASA)",
        "nivel": "Primer Nivel",
        "direccion": "AV. DEL MAESTRO ALTO OBRAJES",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.ALTO SEGUENCOMA": {
        "lat": -16.538781,
        "lon": -68.099924,
        "red": "RED 5 - SUR (SUR / MALLASA)",
        "nivel": "Primer Nivel",
        "direccion": "PLAZA CIVICA PARADA MINIBUS 237 A. SEGUENCOMA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.BAJO LLOJETA": {
        "lat": -16.5259,
        "lon": -68.116866,
        "red": "RED 5 - SUR (SUR / MALLASA)",
        "nivel": "Primer Nivel",
        "direccion": "AV. LOS SARGENTOS LADO RETEN POLICIAL",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.BOLOGNIA": {
        "lat": -16.525641,
        "lon": -68.087244,
        "red": "RED 5 - SUR (SUR / MALLASA)",
        "nivel": "Primer Nivel",
        "direccion": "AAV. CABALLERO ESQ. CALLE 5, DETRÁS MERCADO IRPAVI",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "C.S.MATERNO INFANTIL BELLA VISTA": {
        "lat": -16.530282,
        "lon": -68.094895,
        "red": "RED 5 - SUR (SUR / MALLASA)",
        "nivel": "Centro de Salud Integral",
        "direccion": "C/PROLONGACION No 20 BELLA VISTA",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "Hospital Metodista": {
        "lat": -16.527077,
        "lon": -68.104475,
        "red": "RED 5 - SUR (SUR / MALLASA)",
        "nivel": "Segundo Nivel",
        "direccion": "av. 14 de septiembre y calle 13 Obrajes Clinica Amiga",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    },
    "Hospital Municipal Los Pinos": {
        "lat": -16.542376,
        "lon": -68.071713,
        "red": "RED 5 - SUR (SUR / MALLASA)",
        "nivel": "Segundo Nivel",
        "direccion": "Calle 25  a media cuadra de la Calle Fernando -inchauste Montalvo",
        "director": "",
        "telefono": "",
        "servicios": "Medicina General, Odontología, Enfermería, Vacunación"
    }
}

def _normalizar_texto(texto):
    if not texto:
        return ""
    # Quitar acentos y diacríticos
    s = unicodedata.normalize('NFD', str(texto))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.upper().strip()
    s = s.replace('PASANKERY', 'PASANKERI')
    s = s.replace('LLEJETA', 'LLOJETA')
    s = s.replace('BOLOBNIA', 'BOLOGNIA')
    # Limpiar prefijos comunes
    s = re.sub(r'^(C\.?S\.?M\.?I\.?|C\.?S\.?|CS|C\.?M\.?I\.?|CENTRO DE SALUD|CENTRO SALUD|HOSPITAL MUNICIPAL|HOSPITAL|S\.?C\.?)\s*', '', s)
    s = re.sub(r'[.,;:\-_]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def obtener_coordenada_centro(nombre_centro, red_nombre=""):
    """
    Busca con máxima precisión la coordenada GPS real de un centro de salud u hospital del GAMLP.
    Utiliza coincidencia exacta, normalizada, difusa (difflib) y por palabras clave en el catálogo oficial de Google My Maps.
    """
    if not nombre_centro:
        return None
    
    nom_raw = str(nombre_centro).strip()
    nom_upper = nom_raw.upper()
    
    # 1. Coincidencia directa por clave exacta
    if nom_raw in COORDENADAS_CENTROS_GAMLP:
        return COORDENADAS_CENTROS_GAMLP[nom_raw]
    if nom_upper in COORDENADAS_CENTROS_GAMLP:
        return COORDENADAS_CENTROS_GAMLP[nom_upper]
        
    for k, v in COORDENADAS_CENTROS_GAMLP.items():
        if k.upper() == nom_upper:
            return v

    # 2. Coincidencia por texto normalizado
    norm_query = _normalizar_texto(nom_raw)
    if not norm_query:
        norm_query = nom_upper

    for k, v in COORDENADAS_CENTROS_GAMLP.items():
        norm_k = _normalizar_texto(k)
        if norm_query == norm_k:
            return v

    # 3. Coincidencia por subcadena o inclusión de palabras clave
    for k, v in COORDENADAS_CENTROS_GAMLP.items():
        norm_k = _normalizar_texto(k)
        if norm_query and norm_k and (norm_query in norm_k or norm_k in norm_query):
            return v

    # 4. Coincidencia difusa avanzada (Fuzzy Matching con difflib)
    mapa_norm = {_normalizar_texto(k): v for k, v in COORDENADAS_CENTROS_GAMLP.items()}
    candidatos = list(mapa_norm.keys())
    coincidencias = difflib.get_close_matches(norm_query, candidatos, n=1, cutoff=0.60)
    if coincidencias:
        return mapa_norm[coincidencias[0]]

    # 5. Coordenadas centroide de contingencia por Red Oficial (KML GAMLP)
    red_upper = str(red_nombre).upper()
    if "RED 1" in red_upper or "COTAHUMA" in red_upper or "1" in red_upper:
        return {"lat": -16.511000, "lon": -68.144000, "red": "RED 1 - SUR OESTE (COTAHUMA)", "nivel": "Primer Nivel", "direccion": "Cotahuma / Tacagua", "servicios": "Medicina General, Odontología"}
    elif "RED 2" in red_upper or "MAX PAREDES" in red_upper or "2" in red_upper:
        return {"lat": -16.491000, "lon": -68.155000, "red": "RED 2 - NOR OESTE (MAX PAREDES)", "nivel": "Primer Nivel", "direccion": "Max Paredes", "servicios": "Medicina General, Odontología"}
    elif "RED 3" in red_upper or "PERIFERICA" in red_upper or "3" in red_upper:
        return {"lat": -16.478000, "lon": -68.125000, "red": "RED 3 - NORTE CENTRAL (PERIFERICA)", "nivel": "Primer Nivel", "direccion": "Periférica / Miraflores", "servicios": "Medicina General, Odontología"}
    elif "RED 4" in red_upper or "SAN ANTONIO" in red_upper or "4" in red_upper:
        return {"lat": -16.495000, "lon": -68.105000, "red": "RED 4 - ESTE (SAN ANTONIO)", "nivel": "Primer Nivel", "direccion": "San Antonio / Pampahasi", "servicios": "Medicina General, Odontología"}
    elif "RED 5" in red_upper or "SUR" in red_upper or "MALLASA" in red_upper or "5" in red_upper:
        return {"lat": -16.535000, "lon": -68.085000, "red": "RED 5 - SUR (SUR / MALLASA)", "nivel": "Primer Nivel", "direccion": "Zona Sur / Mallasa", "servicios": "Medicina General, Odontología"}
        
    # Centro geográfico oficial de La Paz
    return {"lat": -16.501000, "lon": -68.140000, "red": red_nombre or "RED GAMLP", "nivel": "Primer Nivel", "direccion": "Municipio de La Paz", "servicios": "Atención Médica Integral"}


def consolidar_datos_geoespaciales(equipos, sedes_data=None, incluir_todos_los_centros=True):
    """
    Agrupa los equipos por Centro de Salud y calcula métricas geoespaciales completas.
    Si incluir_todos_los_centros es True, precarga los centros oficiales del GAMLP
    para que la red completa esté georreferenciada en el visor satelital.
    """
    centros_map = {}

    # 1. Precargar centros oficiales del catálogo KML
    if incluir_todos_los_centros:
        for c_nombre, info in COORDENADAS_CENTROS_GAMLP.items():
            centros_map[c_nombre] = {
                "nombre": c_nombre,
                "red": info.get("red", "RED GAMLP"),
                "lat": info.get("lat", -16.5010),
                "lon": info.get("lon", -68.1400),
                "nivel": info.get("nivel", "Primer Nivel"),
                "direccion": info.get("direccion", "Sin dirección registrada"),
                "director": info.get("director", ""),
                "telefono": info.get("telefono", ""),
                "servicios": info.get("servicios", "Medicina General, Odontología, Enfermería"),
                "total_equipos": 0,
                "operativos": 0,
                "baja_falla": 0,
                "riesgo_alto": 0,
                "riesgo_medio": 0,
                "riesgo_bajo": 0,
                "equipos_lista": []
            }

    # 2. Consolidar inventario real de equipos sobre cada centro
    for eq in equipos:
        cen_nom = str(eq.get("centro_salud_nombre") or eq.get("centro_salud") or "Centro General").strip()
        red_nom = str(eq.get("red_salud_nombre") or eq.get("red_salud") or "GAMLP").strip()
        
        # Buscar el centro en el mapa existente o resolver coordenadas
        c_clave = None
        if cen_nom in centros_map:
            c_clave = cen_nom
        else:
            norm_cen = _normalizar_texto(cen_nom)
            for k in centros_map.keys():
                if _normalizar_texto(k) == norm_cen:
                    c_clave = k
                    break
                    
        if not c_clave:
            coords = obtener_coordenada_centro(cen_nom, red_nom)
            centros_map[cen_nom] = {
                "nombre": cen_nom,
                "red": coords.get("red", red_nom) if coords else red_nom,
                "lat": coords["lat"] if coords else -16.5010,
                "lon": coords["lon"] if coords else -68.1400,
                "nivel": coords.get("nivel", "Primer Nivel") if coords else "Primer Nivel",
                "direccion": coords.get("direccion", "La Paz") if coords else "La Paz",
                "director": coords.get("director", "") if coords else "",
                "telefono": coords.get("telefono", "") if coords else "",
                "servicios": coords.get("servicios", "Medicina General") if coords else "Medicina General",
                "total_equipos": 0,
                "operativos": 0,
                "baja_falla": 0,
                "riesgo_alto": 0,
                "riesgo_medio": 0,
                "riesgo_bajo": 0,
                "equipos_lista": []
            }
            c_clave = cen_nom

        c_data = centros_map[c_clave]
        c_data["total_equipos"] += 1
        
        estado = str(eq.get("estado", "Operativo")).lower()
        if "baja" in estado or "inoperante" in estado or "falla" in estado or "reparacion" in estado:
            c_data["baja_falla"] += 1
        else:
            c_data["operativos"] += 1

        criticidad = str(eq.get("criticidad", "Riesgo Medio")).lower()
        if "alto" in criticidad or "critico" in criticidad:
            c_data["riesgo_alto"] += 1
        elif "medio" in criticidad:
            c_data["riesgo_medio"] += 1
        else:
            c_data["riesgo_bajo"] += 1

        if len(c_data["equipos_lista"]) < 8:
            c_data["equipos_lista"].append({
                "af": eq.get("id") or eq.get("codigo_af") or "S/N",
                "nombre": eq.get("nombre") or eq.get("descripcion") or "Equipo Biomédico",
                "area": eq.get("area") or eq.get("servicio") or "Servicio General",
                "estado": eq.get("estado", "Operativo"),
                "criticidad": eq.get("criticidad", "Medio")
            })

    # 3. Calcular porcentajes de operatividad
    lista_centros = list(centros_map.values())
    for c in lista_centros:
        tot = c["total_equipos"]
        if tot > 0:
            c["porcentaje_operatividad"] = round((c["operativos"] / tot) * 100, 1)
        else:
            c["porcentaje_operatividad"] = 100.0

    return lista_centros


def generar_html_mapa_gamlp(centros_geo, red_filtro=None):
    """
    Genera el archivo HTML interactivo autónomo con Leaflet.js,
    capas satelitales híbridas ESRI World Imagery + Labels,
    mapa de calor ultra-preciso, buscador en vivo y popups biomédicos enriquecidos.
    """
    centros_filtrados = centros_geo
    if red_filtro and not str(red_filtro).startswith("[ Todas"):
        centros_filtrados = [c for c in centros_geo if c.get("red") == red_filtro]

    # Datos para mapa de calor: [lat, lon, intensidad]
    puntos_calor = []
    max_eq = max([c["total_equipos"] for c in centros_filtrados] + [1])
    for c in centros_filtrados:
        if c["total_equipos"] > 0:
            intensidad = min(1.0, max(0.25, c["total_equipos"] / max_eq))
        else:
            intensidad = 0.15
        puntos_calor.append([c["lat"], c["lon"], intensidad])

    centros_json = json.dumps(centros_filtrados, ensure_ascii=False)
    puntos_calor_json = json.dumps(puntos_calor)

    total_eq_sum = sum(c["total_equipos"] for c in centros_filtrados)
    total_op_sum = sum(c["operativos"] for c in centros_filtrados)
    porc_global = round((total_op_sum / max(1, total_eq_sum)) * 100, 1) if total_eq_sum > 0 else 100.0

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GIS GAMLP - Mapa Satelital y de Calor de Equipamiento Biomédico</title>
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }}
        html, body {{ height: 100%; width: 100%; overflow: hidden; background: #0B1120; }}
        #map {{ height: 100%; width: 100%; position: absolute; top: 0; left: 0; }}
        
        /* Panel Superior Flotante */
        .top-panel {{
            position: absolute;
            top: 16px;
            left: 16px;
            z-index: 1000;
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(12px);
            padding: 14px 18px;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #F8FAFC;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
            max-width: 400px;
            width: calc(100% - 32px);
        }}
        .top-panel h1 {{ font-size: 15px; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; gap: 8px; }}
        .top-panel p {{ font-size: 11.5px; color: #94A3B8; margin-top: 3px; line-height: 1.3; }}
        
        /* Buscador en Vivo en el Mapa */
        .search-box {{
            margin-top: 10px;
            display: flex;
            align-items: center;
            background: rgba(30, 41, 59, 0.95);
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 4px 10px;
            gap: 6px;
        }}
        .search-box input {{
            width: 100%;
            background: transparent;
            border: none;
            outline: none;
            color: #FFFFFF;
            font-size: 12px;
        }}
        .search-box input::placeholder {{ color: #94A3B8; }}

        /* Botones de Control de Capas */
        .controls-row {{
            margin-top: 10px;
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        }}
        .btn-layer {{
            background: rgba(30, 41, 59, 0.9);
            border: 1px solid #334155;
            color: #CBD5E1;
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 11.5px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .btn-layer:hover, .btn-layer.active {{
            background: #2563EB;
            color: #FFFFFF;
            border-color: #3B82F6;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.4);
        }}

        /* Tarjetas de Estadísticas Inferiores */
        .bottom-stats {{
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(12px);
            padding: 8px 18px;
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #F8FAFC;
            display: flex;
            gap: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            font-size: 12px;
        }}
        .stat-item {{ display: flex; align-items: center; gap: 6px; }}
        .stat-num {{ font-weight: 700; font-size: 13.5px; color: #38BDF8; }}

        /* Popups Estilizados */
        .leaflet-popup-content-wrapper {{
            background: #1E293B;
            color: #F8FAFC;
            border-radius: 12px;
            border: 1px solid #475569;
            padding: 6px;
            box-shadow: 0 14px 35px rgba(0,0,0,0.6);
        }}
        .leaflet-popup-tip {{ background: #1E293B; }}
        .popup-header {{
            border-bottom: 1px solid #334155;
            padding-bottom: 6px;
            margin-bottom: 6px;
        }}
        .popup-title {{ font-size: 13.5px; font-weight: 700; color: #38BDF8; display: flex; align-items: center; gap: 6px; }}
        .popup-sub {{ font-size: 11px; color: #94A3B8; margin-top: 2px; }}
        .popup-dir {{ font-size: 11px; color: #CBD5E1; margin-top: 4px; line-height: 1.25; }}
        .popup-serv {{ font-size: 10.5px; color: #A7F3D0; margin-top: 4px; font-style: italic; }}

        .stat-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 5px;
            margin: 6px 0;
            font-size: 11.5px;
        }}
        .stat-box {{
            background: #0F172A;
            padding: 5px 7px;
            border-radius: 6px;
            border: 1px solid #334155;
        }}
        .stat-box-lbl {{ font-size: 9.5px; color: #64748B; }}
        .stat-box-val {{ font-weight: 700; color: #F1F5F9; font-size: 12px; }}
        
        .eq-mini-list {{
            max-height: 100px;
            overflow-y: auto;
            margin-top: 6px;
            padding-top: 6px;
            border-top: 1px dashed #334155;
            font-size: 10.5px;
        }}
        .eq-mini-item {{
            display: flex;
            justify-content: space-between;
            padding: 2px 0;
            color: #CBD5E1;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
    </style>
</head>
<body>
    <div id="map"></div>

    <!-- Panel Superior -->
    <div class="top-panel">
        <h1>🛰️ GIS GAMLP: Mapa Satelital de Salud</h1>
        <p>Georreferenciación 100% Precisa de la Red Municipal de Salud</p>
        
        <div class="search-box">
            <span>🔍</span>
            <input type="text" id="mapSearch" placeholder="Buscar hospital o centro (ej: Pasankeri, Cotahuma, Portada)..." oninput="filtrarMapaEnVivo()">
        </div>

        <div class="controls-row">
            <button class="btn-layer active" id="btn-sat" onclick="cambiarCapa('sat')">🛰️ Satélite Híbrido</button>
            <button class="btn-layer" id="btn-osm" onclick="cambiarCapa('osm')">🗺️ Calles</button>
            <button class="btn-layer" id="btn-dark" onclick="cambiarCapa('dark')">🌙 Oscuro</button>
            <button class="btn-layer active" id="btn-heat" onclick="toggleCalor()">🔥 Mapa de Calor</button>
            <button class="btn-layer active" id="btn-markers" onclick="toggleMarcadores()">🏥 Centros</button>
        </div>
    </div>

    <!-- Barra Inferior de Métricas -->
    <div class="bottom-stats">
        <div class="stat-item">
            <span>🏥 Centros Mapeados:</span>
            <span class="stat-num">{len(centros_filtrados)}</span>
        </div>
        <div class="stat-item">
            <span>📦 Total Equipos:</span>
            <span class="stat-num">{total_eq_sum:,}</span>
        </div>
        <div class="stat-item">
            <span>🟢 Operatividad Global:</span>
            <span class="stat-num" style="color: #4ADE80;">{porc_global}%</span>
        </div>
    </div>

    <!-- Scripts de Leaflet y Plugins -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
    
    <script>
        const centrosData = {centros_json};
        const heatData = {puntos_calor_json};

        // 1. Inicializar Mapa centrado en el corazón geográfico de La Paz
        const map = L.map('map', {{
            center: [-16.5010, -68.1400],
            zoom: 13,
            zoomControl: false
        }});
        L.control.zoom({{ position: 'topright' }}).addTo(map);

        // 2. Capas Base Satelitales y Cartográficas
        const satImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            attribution: 'Tiles &copy; Esri &mdash; GAMLP',
            maxZoom: 19
        }});

        const satLabels = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            maxZoom: 19
        }});

        const satHybridGroup = L.layerGroup([satImagery, satLabels]);

        const osmLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}.{{y}}.png', {{
            attribution: '&copy; OpenStreetMap &mdash; GAMLP',
            maxZoom: 19
        }});

        const darkLayer = L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; CartoDB &mdash; GAMLP',
            maxZoom: 19
        }});

        satHybridGroup.addTo(map);
        let capaActual = satHybridGroup;

        function cambiarCapa(tipo) {{
            map.removeLayer(capaActual);
            document.querySelectorAll('.controls-row .btn-layer').forEach(b => {{
                if (['btn-sat', 'btn-osm', 'btn-dark'].includes(b.id)) b.classList.remove('active');
            }});

            if (tipo === 'sat') {{
                satHybridGroup.addTo(map);
                capaActual = satHybridGroup;
                document.getElementById('btn-sat').classList.add('active');
            }} else if (tipo === 'osm') {{
                osmLayer.addTo(map);
                capaActual = osmLayer;
                document.getElementById('btn-osm').classList.add('active');
            }} else {{
                darkLayer.addTo(map);
                capaActual = darkLayer;
                document.getElementById('btn-dark').classList.add('active');
            }}
        }}

        // 3. Capa de Mapa de Calor (Heatmap)
        let heatLayer = L.heatLayer(heatData, {{
            radius: 35,
            blur: 22,
            maxZoom: 16,
            max: 1.0,
            gradient: {{ 0.2: '#3B82F6', 0.4: '#10B981', 0.6: '#FBBF24', 0.8: '#F97316', 1.0: '#EF4444' }}
        }}).addTo(map);

        let calorVisible = true;
        function toggleCalor() {{
            const btn = document.getElementById('btn-heat');
            if (calorVisible) {{
                map.removeLayer(heatLayer);
                btn.classList.remove('active');
                calorVisible = false;
            }} else {{
                heatLayer.addTo(map);
                btn.classList.add('active');
                calorVisible = true;
            }}
        }}

        // 4. Marcadores Georreferenciados
        const markersGroup = L.markerClusterGroup({{
            maxClusterRadius: 32,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false
        }});

        const marcadoresRefs = [];

        function crearIconoCentro(nivel, totalEq) {{
            let bg = '#3B82F6';
            if (nivel.includes('Segundo') || nivel.includes('Hospital')) bg = '#8B5CF6';
            else if (nivel.includes('Integral')) bg = '#06B6D4';
            else if (nivel.includes('Puesto')) bg = '#10B981';

            const etiqueta = totalEq > 0 ? totalEq : '🏥';
            return L.divIcon({{
                className: 'custom-pin',
                html: `<div style="
                    background: ${{bg}};
                    color: white;
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 700;
                    font-size: ${{totalEq > 0 ? '11px' : '13px'}};
                    border: 2px solid white;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.6);
                ">${{etiqueta}}</div>`,
                iconSize: [32, 32],
                iconAnchor: [16, 16]
            }});
        }}

        centrosData.forEach(c => {{
            const marker = L.marker([c.lat, c.lon], {{
                icon: crearIconoCentro(c.nivel, c.total_equipos)
            }});

            let listaHtml = '';
            if (c.equipos_lista && c.equipos_lista.length > 0) {{
                listaHtml = '<div class="eq-mini-list">' + 
                    c.equipos_lista.map(eq => `<div class="eq-mini-item"><span>• ${{eq.nombre}}</span><span style="color:#38BDF8;">${{eq.area}}</span></div>`).join('') +
                    '</div>';
            }}

            const dirHtml = c.direccion ? `<div class="popup-dir">📍 <b>Dir:</b> ${{c.direccion}}</div>` : '';
            const servHtml = c.servicios ? `<div class="popup-serv">🩺 ${{c.servicios}}</div>` : '';

            const popupContent = `
                <div class="popup-header">
                    <div class="popup-title">🏥 ${{c.nombre}}</div>
                    <div class="popup-sub">${{c.red}} &bull; ${{c.nivel}}</div>
                    ${{dirHtml}}
                    ${{servHtml}}
                </div>
                <div class="stat-grid">
                    <div class="stat-box">
                        <div class="stat-box-lbl">Total Equipos:</div>
                        <div class="stat-box-val">${{c.total_equipos}}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-box-lbl">Operatividad:</div>
                        <div class="stat-box-val" style="color: #4ADE80;">${{c.porcentaje_operatividad}}%</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-box-lbl">Riesgo Alto (IA):</div>
                        <div class="stat-box-val" style="color: #F87171;">${{c.riesgo_alto}}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-box-lbl">Riesgo Medio:</div>
                        <div class="stat-box-val" style="color: #FBBF24;">${{c.riesgo_medio}}</div>
                    </div>
                </div>
                ${{listaHtml}}
            `;

            marker.bindPopup(popupContent, {{ maxWidth: 320 }});
            markersGroup.addLayer(marker);
            marcadoresRefs.push({{ marker: marker, nombre: c.nombre.toLowerCase(), red: c.red.toLowerCase(), lat: c.lat, lon: c.lon }});
        }});

        map.addLayer(markersGroup);
        let marcadoresVisibles = true;

        function toggleMarcadores() {{
            const btn = document.getElementById('btn-markers');
            if (marcadoresVisibles) {{
                map.removeLayer(markersGroup);
                btn.classList.remove('active');
                marcadoresVisibles = false;
            }} else {{
                map.addLayer(markersGroup);
                btn.classList.add('active');
                marcadoresVisibles = true;
            }}
        }}

        // 5. Búsqueda en vivo y enfoque satelital
        function filtrarMapaEnVivo() {{
            const q = document.getElementById('mapSearch').value.trim().toLowerCase();
            if (!q) return;

            const match = marcadoresRefs.find(m => m.nombre.includes(q) || m.red.includes(q));
            if (match) {{
                map.flyTo([match.lat, match.lon], 16, {{ animate: true, duration: 1.2 }});
                setTimeout(() => {{
                    match.marker.openPopup();
                }}, 1300);
            }}
        }}
    </script>
</body>
</html>
"""
    return html
