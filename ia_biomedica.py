# -*- coding: utf-8 -*-
"""
MÓDULO DE INTELIGENCIA ARTIFICIAL Y DIAGNÓSTICO BIOMÉDICO GAMLP (100% OFFLINE / LOCAL)
======================================================================================
Proporciona:
1. Motor de Inferencia y Diagnóstico Experto de Fallas Biomédicas.
2. Análisis Predictivo de Degradación y Vida Útil Restante (RUL - Remaining Useful Life).
3. Presupuestador Predictivo de Repuestos y Accesorios por Red / Centro.
4. Recomendaciones de Seguridad Eléctrica y Normativa Clínica (IEC 60601 / IEC 62353).
"""

import re
import math
from datetime import datetime, date

# =============================================================================
# BASE DE CONOCIMIENTO EXPERTO DE FALLAS BIOMÉDICAS Y PROTOCOLOS DE SOLUCIÓN
# =============================================================================
BASE_CONOCIMIENTO_FALLAS = [
    # ------------------ AUTOCLAVES Y ESTERILIZADORES ------------------
    {
        "tipo_equipo": "Autoclave / Esterilizador",
        "keywords": ["autoclave", "esterilizador", "presion", "vapor", "temperatura", "camara", "e01", "e02", "e03", "puerta", "resistencia", "vacio", "valvula"],
        "sintomas": [
            "No alcanza la temperatura de esterilización (121°C / 134°C)",
            "Fuga de vapor por el empaque de la puerta",
            "Error de presión insuficiente o exceso de presión (E01 / E02 / E03)",
            "El agua no drena o no genera vacío en la fase de secado",
            "Resistencia calefactora no calienta o dispara el disyuntor"
        ],
        "diagnosticos": [
            {
                "problema": "Falla en el Sistema de Calefacción o Termostato de Seguridad",
                "causas": [
                    "Resistencia eléctrica tubular abierta, calcificada o en cortocircuito.",
                    "Termocupla / sensor PT100 descalibrado o con cableado sulfatado.",
                    "Relé de estado sólido (SSR) o contactor principal trabado.",
                    "Nivel de agua desmineralizada insuficiente en la cámara."
                ],
                "procedimiento": [
                    "1. Desconectar la alimentación eléctrica y purgar completamente la presión residual.",
                    "2. Medir con multímetro la resistencia de la resistencia calefactora (debe marcar entre 15 y 45 Ohms según potencia).",
                    "3. Verificar continuidad del sensor de temperatura PT100 (~108 Ohms a 20°C).",
                    "4. Inspeccionar la placa de control y probar el accionamiento del relé/SSR con multímetro en VDC.",
                    "5. Limpiar el sensor de nivel de agua y descalcificar los conductos internos con solución desincrustante suave."
                ],
                "repuestos": ["Resistencia calefactora 220V/2000W-3000W", "Sensor de temperatura PT100", "Relé de estado sólido SSR 40A", "Sensor de nivel de agua"],
                "herramientas": ["Multímetro digital", "Manómetro patrón de presión", "Termómetro patrón / Termocupla calibrada", "Juego de llaves aisladas"],
                "norma_seguridad": "Verificar prueba hidrostática periódica y resistencia de aislamiento (> 2 MOhm) según IEC 62353."
            },
            {
                "problema": "Pérdida de Presión y Fuga por Empaque de Puerta o Válvula de Alivio",
                "causas": [
                    "Empaque de silicona de la compuerta reseco, fisurado o desalineado.",
                    "Válvula solenoide de purga atascada por depósitos de cal/óxido.",
                    "Válvula de seguridad calibrada disparando a presión prematura (< 2.2 bar)."
                ],
                "procedimiento": [
                    "1. Limpiar el marco de cierre y aplicar lubricante de grado médico / silicona neutra al empaque.",
                    "2. Reemplazar el empaque de silicona si presenta endurecimiento o deformación.",
                    "3. Desmontar la electroválvula de purga, limpiar el émbolo y probar bobina a 220VAC.",
                    "4. Probar la válvula de seguridad y verificar que no gotee antes del límite de seguridad."
                ],
                "repuestos": ["Empaque de silicona para puerta de autoclave", "Electroválvula de vapor 2 vías 220V", "Válvula de seguridad de 2.5 bar"],
                "herramientas": ["Juego de llaves Allen y fijas", "Grasa de silicona de grado médico", "Limpiador dieléctrico"],
                "norma_seguridad": "No manipular la válvula de seguridad mientras el equipo contenga presión o temperatura."
            }
        ]
    },

    # ------------------ MONITORES DE SIGNOS VITALES ------------------
    {
        "tipo_equipo": "Monitor de Signos Vitales / Multiparámetro",
        "keywords": ["monitor", "signos vitales", "multiparametro", "spo2", "nibp", "presion arterial", "ecg", "pantalla", "bateria", "e04", "ruido", "derivacion"],
        "sintomas": [
            "Fallo en lectura de SpO2 / Mensaje 'Sensor Desconectado' o curva pletismográfica plana",
            "Error en PNI / NIBP: 'Fuga neumática' o no infla el brazalete",
            "Ruido excesivo o interferencia en la traza electrocardiográfica (ECG)",
            "El equipo se apaga al desconectar de la red eléctrica (Batería agotada)",
            "Pantalla táctil descalibrada o sin retroiluminación"
        ],
        "diagnosticos": [
            {
                "problema": "Fallo en Módulo Neumático PNI (Presión No Invasiva) o Manguera",
                "causas": [
                    "Brazalete o manguera de extensión perforada o con conector rápido fracturado.",
                    "Microbomba de aire con desgaste en diafragma o pérdida de compresión.",
                    "Válvula de escape rápido trabada en posición abierta."
                ],
                "procedimiento": [
                    "1. Inspeccionar el brazalete con manómetro de calibración para descartar microfugas.",
                    "2. Revisar los conectores rápidos neumáticos tipo Luer / Bayoneta.",
                    "3. Acceder al modo de servicio y ejecutar la prueba de fuga neumática (Leak Test < 5 mmHg/min).",
                    "4. Si la bomba no alcanza 250 mmHg en 10 seg, reemplazar microbomba neumática de 12VDC."
                ],
                "repuestos": ["Brazalete de PNI adulto/pediátrico de 2 vías", "Manguera de extensión PNI", "Microbomba de inflado 12V PNI", "Válvula de desinflado PNI"],
                "herramientas": ["Simulador / Manómetro patrón NIBP", "Jeringa de calibración 500cc", "Multímetro"],
                "norma_seguridad": "Calibrar transductor de presión con simulador patrón cada 6 meses."
            },
            {
                "problema": "Interferencia en ECG o Falla en Sensor de Oximetría SpO2",
                "causas": [
                    "Cable troncal de ECG con hilos internos fracturados o terminales sulfatados.",
                    "Falta de conexión equipotencial a tierra en la toma eléctrica del hospital.",
                    "Diodos emisor IR o fotodetector del sensor SpO2 rotos por tirones mecánicos."
                ],
                "procedimiento": [
                    "1. Conectar simulador de paciente multiparamétrico al cable de ECG y verificar traza en DII.",
                    "2. Medir continuidad pin a pin en el cable troncal y latiguillos de 3/5 puntas.",
                    "3. Verificar que la resistencia de puesta a tierra del tomacorriente sea < 2 Ohms.",
                    "4. Probar sensor de SpO2 en simulador de oximetría; verificar emisión de luz roja/infrarroja."
                ],
                "repuestos": ["Sensor SpO2 tipo clip adulto / universal", "Cable troncal ECG 5 latiguillos (Snap)", "Batería de respaldo Li-ion / Plomo-Ácido 12V 2.3Ah"],
                "herramientas": ["Simulador de paciente multiparamétrico", "Comprobador de tomas con tierra"],
                "norma_seguridad": "Verificar corriente de fuga en paciente (< 10 uA tipo CF) según IEC 60601-1."
            }
        ]
    },

    # ------------------ DESFIBRILADORES / CARDIOVERSORES ------------------
    {
        "tipo_equipo": "Desfibrilador / Monitor Cardioversor",
        "keywords": ["desfibrilador", "cardioversor", "choque", "descarga", "joules", "paletas", "bifasico", "sincronismo", "marcapasos", "carga"],
        "sintomas": [
            "No carga la energía seleccionada (Joules) o tiempo de carga excesivo (> 15 segundos)",
            "Fallo en autotest matutino / Alarma de fallo en capacitor de descarga",
            "Descarga no entregada a través de las paletas externas",
            "Fallo en el módulo de marcapasos externo o sincronismo"
        ],
        "diagnosticos": [
            {
                "problema": "Falla en Circuito de Alto Voltaje, Relé de Descarga o Capacitor",
                "causas": [
                    "Batería interna con capacidad degradada (< 50% de almacenamiento de corriente).",
                    "Capacitor de alta tensión con fugas o resistencia serie equivalente (ESR) alta.",
                    "Microinterruptores de los botones de descarga de las paletas dañados.",
                    "Relé de alto voltaje de seguridad con contactos carbonizados."
                ],
                "procedimiento": [
                    "1. ¡PRECAUCIÓN DE ALTO VOLTAJE! Descargar el capacitor antes de tocar el circuito interno.",
                    "2. Probar la batería bajo carga; si cae a menos de 10V durante la carga de energía, reemplazarla.",
                    "3. Medir la entrega real de energía conectando las paletas a un Analizador de Desfibriladores patrón.",
                    "4. Verificar que la energía entregada esté dentro del ±15% de la energía programada (ej. 200J).",
                    "5. Probar continuidad de los cables y gatillos de las paletas de descarga."
                ],
                "repuestos": ["Batería recargable para desfibrilador 12V/14.8V", "Cable de paletas externas", "Papel termosensible para registrador", "Electrodos multifunción desechables"],
                "herramientas": ["Analizador de desfibriladores y marcapasos", "Voltímetro de alto voltaje aislado", "Descargador de seguridad"],
                "norma_seguridad": "Obligatorio realizar prueba de energía entregada y seguridad eléctrica IEC 60601-2-4 anualmente."
            }
        ]
    },

    # ------------------ SILLÓN ODONTOLÓGICO / UNIDAD DENTAL ------------------
    {
        "tipo_equipo": "Sillón Odontológico / Unidad Dental",
        "keywords": ["dental", "sillon", "turbina", "pieza de mano", "micromotor", "compresor", "escupidera", "pedal", "lampara dental", "agua", "aire"],
        "sintomas": [
            "Pieza de mano / turbina no gira o tiene pérdida de potencia y torque",
            "Fuga de agua o aire constante en la manguera borden / midwest",
            "Los actuadores del sillón (subida/bajada/respaldo) no responden desde el pedal o botonera",
            "Lámpara de luz dental no enciende o parpadea",
            "Suctor de saliva o eyector quirúrgico sin vacío"
        ],
        "diagnosticos": [
            {
                "problema": "Fuga Neumática / Obstrucción en Válvulas Distribuidoras o Mangueras",
                "causas": [
                    "Manguera borden de 2/4 vías fisurada o acoples con empaques tóricos (O-rings) gastados.",
                    "Bloque de electroválvulas neumáticas con residuos de agua del compresor sin filtrar.",
                    "Válvula de pie (pedal neumático) con resortes o diafragma roto."
                ],
                "procedimiento": [
                    "1. Verificar la presión de entrada de aire del compresor (debe estar entre 5.5 y 6.5 bar).",
                    "2. Revisar el regulador de presión de la unidad y purgar el filtro de condensado.",
                    "3. Reemplazar los O-rings de los terminales de turbina y micromotor.",
                    "4. Desmontar el pedal reostato y lubricar el émbolo con spray de silicona pura."
                ],
                "repuestos": ["Manguera borden de 2 vías / 4 vías", "Kit de O-rings para acoples dentales", "Válvula neumática para pedal", "Filtro purificador de aire/agua"],
                "herramientas": ["Manómetro para manguera borden", "Juego de llaves fijas 8-17mm", "Extractor de mangueras"],
                "norma_seguridad": "Purgar y desinfectar el tanque del compresor semanalmente para evitar humedad en las piezas rotatorias."
            },
            {
                "problema": "Fallo en Motores Actuadores o Placa Electrónica del Sillón",
                "causas": [
                    "Finales de carrera (microswitches) de seguridad atascados o descalibrados.",
                    "Transformador de 24VAC o fusible principal fundido por sobretensión.",
                    "Condensador de arranque de los motores lineales degradado."
                ],
                "procedimiento": [
                    "1. Medir voltaje de salida del transformador principal (24VAC / 12VDC).",
                    "2. Verificar que los microswitches de seguridad en la base y respaldo tengan continuidad.",
                    "3. Probar los relés de subida y bajada en la placa principal.",
                    "4. Aplicar grasa de litio a los husillos sinfín de elevación."
                ],
                "repuestos": ["Microswitch de final de carrera", "Transformador 220V/24VAC 100VA", "Bombillo LED/Halógeno 12V 50W para lámpara", "Relé de potencia 24VDC"],
                "herramientas": ["Multímetro", "Grasa de litio blanca", "Destornilladores aislados"],
                "norma_seguridad": "Comprobar el sistema anticolisión de la base antes de entregar el equipo al odontólogo."
            }
        ]
    },

    # ------------------ BOMBAS DE INFUSIÓN ------------------
    {
        "tipo_equipo": "Bomba de Infusión / Perfusor",
        "keywords": ["bomba", "infusion", "perfusor", "goteo", "oclusion", "aire en linea", "flujo", "volumen", "jeringa", "peristaltica"],
        "sintomas": [
            "Alarma recurrente de 'Oclusión Aguas Abajo' o 'Aguas Arriba'",
            "Alarma de 'Burbuja de Aire en Línea' falsa o no detecta aire real",
            "Error de flujo / Volumen infundido no concuerda con lo programado",
            "Mecanismo de dedos peristálticos trabado o ruidoso"
        ],
        "diagnosticos": [
            {
                "problema": "Descalibración en Sensores de Presión / Sensor Ultrasónico de Aire",
                "causas": [
                    "Sensor de burbujas ultrasónico con cristal sucio por salpicadura de soluciones glucosadas.",
                    "Transductor piezoeléctrico de oclusión descalibrado o con cable flex agrietado.",
                    "Guía de infusión no compatible o no ajustada correctamente en el canal."
                ],
                "procedimiento": [
                    "1. Limpiar cuidadosamente la ranura del sensor ultrasónico con hisopo humedecido en alcohol isopropílico.",
                    "2. Entrar al menú de calibración técnica de la bomba.",
                    "3. Realizar prueba de flujo gravimétrico con balanza de precisión y cronómetro (margen de error < ±5%).",
                    "4. Probar la alarma de oclusión con manómetro de línea (debe disparar entre 8 y 12 psi según nivel)."
                ],
                "repuestos": ["Sensor de aire ultrasónico", "Sensor de presión de oclusión", "Batería recargable Ni-MH / Li-Ion", "Sensor de gotas óptico"],
                "herramientas": ["Analizador de bombas de infusión / Balanza de precisión", "Manómetro de línea para perfusión", "Alcohol isopropílico"],
                "norma_seguridad": "Verificar precisión de volumen cada 6 meses según protocolo de la OMS."
            }
        ]
    },

    # ------------------ RAYOS X Y RADIOLOGÍA ------------------
    {
        "tipo_equipo": "Equipo de Rayos X (Fijo / Rodable / Dental)",
        "keywords": ["rayos x", "radiologia", "tubo", "kv", "ma", "mas", "colimador", "disparo", "calentamiento", "filamento", "bucky", "plomo"],
        "sintomas": [
            "No emite radiación al presionar el pulsador de disparo de 2 tiempos",
            "Error de filamento abierto o sobrecorriente en ánodo (Overcurrent)",
            "Lámpara del colimador no enciende o el temporizador no la apaga",
            "Sobrecalentamiento del tubo térmico de rayos X (Thermal Overload)"
        ],
        "diagnosticos": [
            {
                "problema": "Fallo en Circuito de Disparo, Contactores de Alta Tensión o Filamento",
                "causas": [
                    "Pulsador de mano con cable espiralado roto en la primera o segunda fase (Prep/Expose).",
                    "Circuito de precalentamiento de filamento (Filament Driver) dañado.",
                    "Falta de aceite dieléctrico refrigerante en la calota del tubo.",
                    "Interlock de seguridad de puerta de la sala de rayos X abierto."
                ],
                "procedimiento": [
                    "1. Verificar el estado del interruptor de seguridad de la puerta plomada.",
                    "2. Medir continuidad de los cables del pulsador manual en ambas posiciones.",
                    "3. Medir la resistencia del filamento grueso y fino en el conector de alta tensión.",
                    "4. Inspeccionar el colimador manual y cambiar el bombillo halógeno de 24V 150W si está quemado.",
                    "5. Verificar calibración de kVp y mAs con multímetro de rayos X no invasivo."
                ],
                "repuestos": ["Pulsador de disparo de 2 tiempos", "Bombillo para colimador 24V/150W", "Contactor de potencia 3 polos 220V", "Cable de alta tensión"],
                "herramientas": ["Detector de radiación / Dosímetro de seguridad", "Multímetro de alta precisión", "Lentes y mandil plomado"],
                "norma_seguridad": "USO OBLIGATORIO DE DOSÍMETRO Y PROTECCIÓN RADIOLÓGICA durante cualquier prueba de emisión."
            }
        ]
    },

    # ------------------ ELECTROCARDIÓGRAFO (ECG) ------------------
    {
        "tipo_equipo": "Electrocardiógrafo (ECG)",
        "keywords": ["electrocardiografo", "ecg", "ekg", "derivaciones", "traza", "papel", "cabezal", "impresora", "ruido 50hz", "ruido 60hz"],
        "sintomas": [
            "Línea de base inestable o interferencia de 50Hz/60Hz en todas las derivaciones",
            "La impresora térmica arrastra el papel pero no imprime o imprime líneas en blanco",
            "Derivación específica plana (ej: V1 a V6 o DI)",
            "El equipo no detecta los electrodos de extremidades"
        ],
        "diagnosticos": [
            {
                "problema": "Filtro de Tierra Inadecuado o Falla en Cabezal Térmico",
                "causas": [
                    "Cable de paciente con latiguillo roto internamente.",
                    "Cabezal térmico sucio con polvo de papel o con píxeles quemados.",
                    "Mala conductividad por falta de gel conductor en los electrodos.",
                    "Tierra deficiente en la red eléctrica de la sala."
                ],
                "procedimiento": [
                    "1. Limpiar el cabezal térmico con hisopo de algodón y alcohol isopropílico al 99%.",
                    "2. Medir continuidad en los 10 latiguillos del cable de paciente con multímetro.",
                    "3. Conectar el simulador de ECG patrón para comprobar la respuesta en frecuencia.",
                    "4. Activar el filtro de línea de 50/60Hz y filtro muscular (EMG 35Hz) en la configuración del equipo."
                ],
                "repuestos": ["Cable de paciente 10 puntas banana/broche", "Set de perillas precordiales y pinzas de extremidades", "Papel térmico milimetrado", "Cabezal térmico de impresión"],
                "herramientas": ["Simulador de ECG de 12 derivaciones", "Multímetro digital", "Alcohol isopropílico"],
                "norma_seguridad": "Verificar aislamiento galvánico de entrada del paciente (< 10 uA de fuga)."
            }
        ]
    },

    # ------------------ INCUBADORAS Y CUNAS TÉRMICAS ------------------
    {
        "tipo_equipo": "Incubadora Neonatal / Cuna Radiante",
        "keywords": ["incubadora", "cuna", "neonatal", "bebe", "piel", "temperatura piel", "aire", "humedad", "oxigeno", "alarma temperatura"],
        "sintomas": [
            "Alarma de desviación de temperatura de piel o aire (> 0.5°C)",
            "Ventilador de circulación de aire trabado o con vibración anormal",
            "Calefactor no enciende o calienta sin control (Hi-Temp)",
            "Falla en el sensor de servocontrol de temperatura de piel"
        ],
        "diagnosticos": [
            {
                "problema": "Descalibración en Sensor de Piel / Motor Fan de Circulación",
                "causas": [
                    "Sensor de piel (Skin Probe) golpeado o con termistor descalibrado.",
                    "Motor blower de circulación de aire con bujes gastados o pelusa acumulada.",
                    "Termostato de seguridad de corte de emergencia disparado."
                ],
                "procedimiento": [
                    "1. Contrastar la lectura de temperatura de la incubadora con un termómetro patrón de precisión.",
                    "2. Probar el sensor de piel en baño térmico a 36.0°C y 37.0°C (debe medir con error < 0.1°C).",
                    "3. Desmontar la turbina de aire, retirar pelusas y verificar que gire libremente a 1500 RPM.",
                    "4. Comprobar que la alarma acústica y visual de sobretemperatura a 38.5°C funcione con 100% de eficacia."
                ],
                "repuestos": ["Sensor de temperatura de piel reutilizable/desechable", "Motor de circulación de aire 24VDC/220VAC", "Filtro de aire bacteriológico de entrada", "Resistencia de calefacción blindada"],
                "herramientas": ["Termómetro patrón de precisión (±0.05°C)", "Anemómetro para flujo de aire", "Calibrador de seguridad"],
                "norma_seguridad": "CRÍTICO: Toda incubadora debe ser probada con termómetro patrón certificado antes de ingresar a neonatología."
            }
        ]
    },

    # ------------------ CENTRÍFUGAS DE LABORATORIO ------------------
    {
        "tipo_equipo": "Centrífuga de Laboratorio",
        "keywords": ["centrifuga", "rotor", "tubos", "rpm", "tacometro", "escobillas", "carbon", "desbalance", "tapa", "freno"],
        "sintomas": [
            "Vibración excesiva al subir de velocidad / Alarma de Desbalance (Imbalance)",
            "El motor no gira o echa chispas y olor a quemado por la base",
            "La tapa no desbloquea al terminar el ciclo de centrifugado",
            "Velocidad real (RPM) no coincide con el display digital"
        ],
        "diagnosticos": [
            {
                "problema": "Desgaste de Carbones / Desbalance de Rotor o Falla en Sensor Hall",
                "causas": [
                    "Escobillas de carbón del motor universal totalmente gastadas (< 5mm).",
                    "Sensor óptico o magnético de tacómetro (RPM) sucio o fuera de posición.",
                    "Amortiguadores de goma del motor vencidos o deformados.",
                    "Microswitch de bloqueo de tapa electromagnético desalineado."
                ],
                "procedimiento": [
                    "1. Desconectar la centrífuga y verificar el largo de los carbones; reemplazarlos si miden menos de 6mm.",
                    "2. Limpiar el colector de cobre del motor con lija muy fina (grano 1000).",
                    "3. Medir la velocidad real con tacómetro óptico láser contrastando con el valor programado.",
                    "4. Verificar el solenoide de traba de seguridad de la tapa para que no abra mientras el rotor gire."
                ],
                "repuestos": ["Juego de carbones para motor de centrífuga", "Sensor tacómetro de RPM", "Solenoide de bloqueo de tapa", "Soportes / amortiguadores de goma"],
                "herramientas": ["Tacómetro láser óptico", "Lija fina para colectores", "Juego de destornilladores"],
                "norma_seguridad": "Prohibido anular el sensor de tapa abierta para evitar accidentes graves en laboratorio."
            }
        ]
    },

    # ------------------ CONCENTRADORES Y GENERADORES DE OXÍGENO ------------------
    {
        "tipo_equipo": "Concentrador de Oxígeno",
        "keywords": ["concentrador", "oxigeno", "pureza", "tamiz", "compresor", "flujometro", "zeolita", "filtro", "alarma oxigeno", "baja pureza"],
        "sintomas": [
            "Alarma de 'Baja Pureza de Oxígeno' (< 85% O2 a 5 L/min)",
            "Flujo de salida bajo o nulo con flujómetro abierto al máximo",
            "Sonido de escape de aire continuo y no conmuta el ciclo de tamices PSA",
            "Compresor se sobrecalienta y se apaga por protección térmica"
        ],
        "diagnosticos": [
            {
                "problema": "Saturación de Columnas de Zeolita o Válvula de Conmutación Trabada",
                "causas": [
                    "Filtro de aire de entrada totalmente tupido de polvo ambiental.",
                    "Columnas de tamiz molecular (Zeolita) degradadas por humedad ambiental alta.",
                    "Válvula solenoide de distribución de 4 vías trabada por carbonilla.",
                    "Copas de teflón del compresor sin aceite gastadas con pérdida de presión (< 25 psi)."
                ],
                "procedimiento": [
                    "1. Medir la concentración de O2 con un Analizador de Oxígeno Ultrasónico (debe ser > 90% a 5 LPM).",
                    "2. Reemplazar el filtro de esponja de entrada y el filtro HEPA antibacteriano de salida.",
                    "3. Medir la presión de salida del compresor con manómetro en la entrada del bloque de válvulas.",
                    "4. Si la presión es normal pero la pureza sigue baja (< 82%), sustituir o regenerar las columnas de zeolita."
                ],
                "repuestos": ["Juego de columnas de tamiz molecular / Zeolita", "Filtro HEPA para concentrador", "Filtro de entrada de aire", "Válvula solenoide distribuidora"],
                "herramientas": ["Analizador de concentración de oxígeno", "Manómetro 0-60 PSI", "Flujómetro patrón"],
                "norma_seguridad": "Mantener alejado de fuentes de ignición o lubricantes inflamables."
            }
        ]
    }
]

# =============================================================================
# MOTOR DE INFERENCIA Y DIAGNÓSTICO BIOMÉDICO (ALGORITMO LOCAL $0)
# =============================================================================

def diagnosticar_falla_ia(texto_busqueda, tipo_equipo_sel=None):
    """
    Analiza síntomas, códigos de error o descripción del problema ingresados por el técnico
    y devuelve el diagnóstico más probable, pasos de reparación y repuestos sugeridos.
    """
    if not texto_busqueda:
        return {
            "encontrado": False,
            "mensaje": "Por favor ingrese una descripción de la falla, síntoma o código de error."
        }

    texto_normalizado = texto_busqueda.lower()
    palabras_usuario = set(re.findall(r'\b\w+\b', texto_normalizado))
    
    mejores_coincidencias = []

    for categoria in BASE_CONOCIMIENTO_FALLAS:
        # Calcular afinidad por tipo de equipo
        score_tipo = 0
        if tipo_equipo_sel and tipo_equipo_sel != "Todos":
            if tipo_equipo_sel.lower() in categoria["tipo_equipo"].lower():
                score_tipo = 5

        # Calcular coincidencia de palabras clave
        keywords_categoria = set(categoria["keywords"])
        coincidencias_kw = palabras_usuario.intersection(keywords_categoria)
        score_kw = len(coincidencias_kw) * 3

        # Calcular coincidencia en síntomas
        score_sintomas = 0
        for sintoma in categoria["sintomas"]:
            palabras_sintoma = set(re.findall(r'\b\w+\b', sintoma.lower()))
            coincidencias_sint = palabras_usuario.intersection(palabras_sintoma)
            if len(coincidencias_sint) > score_sintomas:
                score_sintomas = len(coincidencias_sint) * 2

        score_total = score_tipo + score_kw + score_sintomas

        if score_total > 0:
            for diag in categoria["diagnosticos"]:
                mejores_coincidencias.append({
                    "score": score_total,
                    "tipo_equipo": categoria["tipo_equipo"],
                    "problema": diag["problema"],
                    "causas": diag["causas"],
                    "procedimiento": diag["procedimiento"],
                    "repuestos": diag["repuestos"],
                    "herramientas": diag["herramientas"],
                    "norma_seguridad": diag["norma_seguridad"],
                    "sintomas_similares": categoria["sintomas"]
                })

    # Ordenar por mayor coincidencia
    mejores_coincidencias.sort(key=lambda x: x["score"], reverse=True)

    if mejores_coincidencias:
        mejor = mejores_coincidencias[0]
        return {
            "encontrado": True,
            "confianza": min(95, 60 + mejor["score"] * 4),
            "tipo_equipo": mejor["tipo_equipo"],
            "problema": mejor["problema"],
            "causas": mejor["causas"],
            "procedimiento": mejor["procedimiento"],
            "repuestos": mejor["repuestos"],
            "herramientas": mejor["herramientas"],
            "norma_seguridad": mejor["norma_seguridad"],
            "sintomas_similares": mejor["sintomas_similares"],
            "otras_opciones": mejores_coincidencias[1:4]
        }
    else:
        # Sugerencia general inteligente cuando no hay match exacto
        return {
            "encontrado": False,
            "mensaje": f"No se encontró un patrón exacto para '{texto_busqueda}'. Recomendamos verificar alimentación eléctrica, fusibles de protección, inspección visual de cables y ejecutar autodiagnóstico del fabricante.",
            "recomendacion_general": [
                "1. Verificar que el voltaje de línea esté en 220V ± 10% y que la toma cuente con tierra física.",
                "2. Revisar el fusible principal de entrada (ubicado cerca del conector IEC de poder).",
                "3. Inspeccionar el cableado interno en busca de componentes quemados o capacitores inflados.",
                "4. Consultar el manual de servicio del fabricante para verificar el significado de códigos de error específicos."
            ]
        }


# =============================================================================
# MOTOR PREDICTIVO DE CONFIABILIDAD Y DEGRADACIÓN (CURVAS WEIBULL / RUL)
# =============================================================================

def calcular_riesgo_predictivo_equipo(equipo, historial_intervenciones=None):
    """
    Calcula el Score de Riesgo de Fallo (0% a 100%), la probabilidad de avería en 30/60 días
    y el RUL (Vida Útil Restante Estimada) basándose en parámetros de ingeniería clínica.
    """
    if not equipo:
        return None

    # 1. Antigüedad del equipo
    anio_fab = equipo.get("anio_fab")
    hoy_anio = datetime.now().year
    edad_anios = 5
    if anio_fab:
        try:
            val_anio = int(str(anio_fab).strip())
            if 1970 <= val_anio <= hoy_anio:
                edad_anios = hoy_anio - val_anio
        except:
            edad_anios = 5

    vida_util_esperada = 10 # Promedio estándar hospitalario OMS
    vu_str = str(equipo.get("vida_util", "")).lower()
    if "año" in vu_str or "ano" in vu_str:
        nums = re.findall(r'\d+', vu_str)
        if nums:
            vida_util_esperada = int(nums[0])

    fraccion_edad = min(2.0, edad_anios / max(1, vida_util_esperada))

    # 2. Factor de Criticidad
    criticidad = str(equipo.get("criticidad", "Riesgo Medio")).lower()
    if "alto" in criticidad:
        factor_criticidad = 1.4
    elif "medio" in criticidad:
        factor_criticidad = 1.0
    else:
        factor_criticidad = 0.7

    # 3. Factor de Tecnologías involucradas (Más tecnologías = mayor probabilidad de fallo)
    tecnologias_activas = 0
    for campo in ["t_elec", "t_elco", "t_mec", "t_hid", "t_neu", "t_vap"]:
        if equipo.get(campo) in ("X", "x", True, 1, "1"):
            tecnologias_activas += 1
    factor_tech = 1.0 + (tecnologias_activas * 0.08)

    # 4. Historial de fallas correctivas previas
    num_correctivos = 0
    if historial_intervenciones:
        id_eq = str(equipo.get("id", "")).strip().lower()
        for inter in historial_intervenciones:
            if str(inter.get("id_equipo", "")).strip().lower() == id_eq:
                if "correctiv" in str(inter.get("tipo", "")).lower():
                    num_correctivos += 1

    factor_historial = 1.0 + (min(5, num_correctivos) * 0.12)

    # 5. Estado actual
    estado_actual = str(equipo.get("estado", "Operativo")).lower()
    if "baja" in estado_actual or "inoperante" in estado_actual:
        probabilidad_fallo = 99.0
        dias_estimados_fallo = 0
        estado_predictivo = "🔴 Fuera de Servicio / Requiere Baja"
    else:
        # Modelo de Degradación Exponencial (Weibull simplificado)
        lambda_t = 0.15 * fraccion_edad * factor_criticidad * factor_tech * factor_historial
        probabilidad_30d = (1.0 - math.exp(-lambda_t * 0.5)) * 100.0
        probabilidad_60d = (1.0 - math.exp(-lambda_t * 1.0)) * 100.0
        probabilidad_fallo = round(min(98.0, max(5.0, probabilidad_60d)), 1)

        # Estimación de días hasta el siguiente mantenimiento / fallo
        if probabilidad_fallo > 75:
            dias_estimados_fallo = max(7, int(30 * (1 - (probabilidad_fallo / 100))))
            estado_predictivo = "🔴 Alto Riesgo de Avería Próxima"
        elif probabilidad_fallo > 45:
            dias_estimados_fallo = max(25, int(90 * (1 - (probabilidad_fallo / 100))))
            estado_predictivo = "🟡 Mantenimiento Preventivo Recomendado"
        else:
            dias_estimados_fallo = max(90, int(180 * (1 - (probabilidad_fallo / 100))))
            estado_predictivo = "🟢 Estado Operativo Confiable"

    # RUL (Remaining Useful Life en Años)
    rul_anios = max(0.0, round(vida_util_esperada - edad_anios, 1))

    return {
        "equipo_id": equipo.get("id"),
        "nombre": equipo.get("nombre"),
        "marca": equipo.get("marca"),
        "modelo": equipo.get("modelo"),
        "centro": equipo.get("centro_salud_nombre"),
        "red": equipo.get("red_salud_nombre"),
        "edad_anios": edad_anios,
        "vida_util_esperada": vida_util_esperada,
        "rul_anios": rul_anios,
        "probabilidad_fallo_60d": probabilidad_fallo,
        "dias_estimados_fallo": dias_estimados_fallo,
        "estado_predictivo": estado_predictivo,
        "num_correctivos_previos": num_correctivos,
        "recomendacion": (
            "Priorizar inspección de seguridad eléctrica y calibración preventiva urgente."
            if probabilidad_fallo > 75 else
            "Programar mantenimiento preventivo estándar en el cronograma trimestral."
            if probabilidad_fallo > 45 else
            "Equipo en condiciones óptimas. Mantener rutina de limpieza y verificación de rutina."
        )
    }


# =============================================================================
# PRESUPUESTADOR PREDICTIVO DE REPUESTOS POR RED / CENTRO
# =============================================================================

def generar_pronostico_repuestos_ia(equipos, repuestos_stock, red_filtro=None):
    """
    Analiza el parque de equipamiento de cada Red o Centro y calcula la demanda
    estimada de repuestos críticos para los próximos 6 meses.
    """
    equipos_filtrados = equipos
    if red_filtro and not str(red_filtro).startswith("[ Todas"):
        equipos_filtrados = [e for e in equipos if e.get("red_salud_nombre") == red_filtro]

    conteo_tipos = {}
    for eq in equipos_filtrados:
        nom = str(eq.get("nombre", "")).strip().lower()
        conteo_tipos[nom] = conteo_tipos.get(nom, 0) + 1

    pronostico = []
    
    # Reglas de tasa de recambio estándar por tipo de equipo
    TASAS_RECAMBIO = [
        {"tipo_match": "monitor", "repuesto": "Sensor SpO2 Reutilizable", "tasa_anual": 0.40, "costo_aprox": 350.0},
        {"tipo_match": "monitor", "repuesto": "Brazalete NIBP Adulto con Manguera", "tasa_anual": 0.35, "costo_aprox": 180.0},
        {"tipo_match": "monitor", "repuesto": "Batería Li-ion 12V 2.3Ah", "tasa_anual": 0.25, "costo_aprox": 280.0},
        {"tipo_match": "autoclave", "repuesto": "Empaque de Silicona para Puerta", "tasa_anual": 0.80, "costo_aprox": 220.0},
        {"tipo_match": "autoclave", "repuesto": "Resistencia Calefactora Tubular 2000W", "tasa_anual": 0.30, "costo_aprox": 450.0},
        {"tipo_match": "autoclave", "repuesto": "Electroválvula de Purga de Vapor 220V", "tasa_anual": 0.25, "costo_aprox": 320.0},
        {"tipo_match": "dental", "repuesto": "Manguera Borden 2 Vías con Terminal", "tasa_anual": 0.50, "costo_aprox": 160.0},
        {"tipo_match": "dental", "repuesto": "Kit de O-Rings y Empaques Neumáticos", "tasa_anual": 1.20, "costo_aprox": 45.0},
        {"tipo_match": "desfibrilador", "repuesto": "Electrodos Multifunción Desechables", "tasa_anual": 1.50, "costo_aprox": 190.0},
        {"tipo_match": "desfibrilador", "repuesto": "Batería de Respaldo Alta Capacidad", "tasa_anual": 0.30, "costo_aprox": 650.0},
        {"tipo_match": "electrocardiografo", "repuesto": "Cable de Paciente ECG 10 Puntas", "tasa_anual": 0.30, "costo_aprox": 420.0},
        {"tipo_match": "electrocardiografo", "repuesto": "Set de Perillas y Pinzas de Extremidad", "tasa_anual": 0.40, "costo_aprox": 120.0},
        {"tipo_match": "centrifuga", "repuesto": "Juego de Escobillas de Carbón Motor", "tasa_anual": 0.60, "costo_aprox": 85.0},
        {"tipo_match": "oxigeno", "repuesto": "Juego de Filtros HEPA / Entrada Aire", "tasa_anual": 1.00, "costo_aprox": 150.0},
    ]

    for tasa in TASAS_RECAMBIO:
        # Contar cuántos equipos coinciden con el tipo
        equipos_compatibles = sum(qty for nom, qty in conteo_tipos.items() if tasa["tipo_match"] in nom)
        if equipos_compatibles > 0:
            demanda_semestral = max(1, math.ceil(equipos_compatibles * (tasa["tasa_anual"] / 2.0)))
            costo_total_est = demanda_semestral * tasa["costo_aprox"]
            
            # Verificar stock actual disponible
            stock_actual = 0
            for rep in repuestos_stock:
                if tasa["repuesto"].lower() in str(rep.get("nombre_repuesto", "")).lower():
                    try:
                        stock_actual += int(rep.get("cantidad", 0))
                    except:
                        pass

            deficit = max(0, demanda_semestral - stock_actual)

            pronostico.append({
                "repuesto": tasa["repuesto"],
                "equipos_instalados": equipos_compatibles,
                "demanda_estimada_6m": demanda_semestral,
                "stock_disponible": stock_actual,
                "sugerencia_compra": deficit,
                "costo_unitario": tasa["costo_aprox"],
                "costo_total_estimado": deficit * tasa["costo_aprox"],
                "prioridad": "🔴 ALTA (Sin Stock)" if deficit > 0 and stock_actual == 0 else ("🟡 MEDIA" if deficit > 0 else "🟢 CUBIERTO")
            })

    # Ordenar por prioridad y costo
    pronostico.sort(key=lambda x: (0 if "ALTA" in x["prioridad"] else (1 if "MEDIA" in x["prioridad"] else 2), -x["costo_total_estimado"]))
    return pronostico
