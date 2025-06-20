# apps/scheduling/management/commands/seed_data.py

import random
from datetime import date, time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction
from faker import Faker

# Importa tus modelos
from apps.academic_setup.models import (
    UnidadAcademica, TipoUnidadAcademica, Carrera, PeriodoAcademico, TiposEspacio,
    EspaciosFisicos, Especialidades, Materias, CarreraMaterias,
    MateriaEspecialidadesRequeridas, Ciclo, Seccion
)
from apps.users.models import Roles, Docentes, DocenteEspecialidades
from apps.scheduling.models import (
    Grupos, BloquesHorariosDefinicion, DisponibilidadDocentes,
    ConfiguracionRestricciones, HorariosAsignados
)

fake = Faker('es_ES')

# --- DATOS COMPLETOS (PLANES DE ESTUDIO, ESPACIOS, ETC.) ---

DATOS_ACADEMICOS = {
    "Escuela Superior La Pontificia": {
        "tipo": "Escuela Profesional",
        "carreras": {
            "CONTABILIDAD Y FINANZAS": {
                "codigo_base": "CF",
                "plan_estudio_codigo": "20241",
                "ciclos": [
                    [("ECF24-001", "Introducción a la Contabilidad", 48, 32), ("ECF24-002", "Matemática para los Negocios", 48, 32), ("ECF24-003", "Introducción al Sistema Tributario", 48, 32), ("ETR24-001", "Intercomunicación Inicial", 48, 32), ("ETR24-002", "Ofimática Inicial", 48, 32)],
                    [("ECF24-004", "Registros y Operaciones Contables", 48, 32), ("ECF24-005", "Matemática Financiera", 48, 32), ("ECF24-006", "Fundamentos de Finanzas", 48, 32), ("ETR24-003", "Intercomunicación Avanzada", 48, 32), ("ETR24-004", "Ofimática Avanzada", 48, 32)],
                    [("ECF24-007", "Contabilidad de Sociedades", 48, 32), ("ECF24-008", "Sistema Tributario", 48, 32), ("ECF24-009", "Regitro de Planillas", 48, 32), ("ECF24-010", "Finanzas Empresariales", 48, 32), ("ETR24-005", "Psicología Organizacional", 32, 32), ("ETR24-010", "Introducción a la Ética", 32, 32)],
                    [("ECF24-011", "Contabilidad de Costos", 48, 32), ("ECF24-012", "Derecho Tributario", 48, 32), ("ECF24-013", "Derecho Comercial", 48, 32), ("ECF24-014", "Declaraciones Juradas Mensuales", 48, 32), ("ETR24-006", "Autorealización Personal", 32, 32), ("ETR24-011", "Ética Profesional", 32, 32)],
                    [("ECF24-015", "Análisis de Reportes Contables", 48, 32), ("ECF24-016", "Contabilidad de MYPES", 48, 32), ("ECF24-017", "Contabilidad Financiera", 48, 32), ("ETR24-007", "Atención al usuario", 48, 32), ("ETR24-012", "Didáctica del Razonamiento", 32, 32), ("ETR24-020", "Experiencia Formativa en Situación Real de Trabajo I", 0, 96)],
                    [("ECF24-018", "Evaluación financiera de proyectos", 48, 32), ("ECF24-019", "Análisis de Reportes Financieros", 48, 32), ("ECF24-020", "Elaboración de Estados Financieros", 48, 32), ("ECF24-021", "Introducción a la Contabilidad Pública", 48, 32), ("ETR24-013", "Analisis de Situaciones Reales", 32, 32), ("ETR24-021", "Experiencia Formativa en Situación Real de Trabajo II", 0, 96)],
                    [("ECF24-022", "Aplicación de las Normas Internacionales de Contabilidad", 48, 32), ("ECF24-023", "Contabilidad Pública", 48, 32), ("ECF24-024", "Auditoría y Control Interno", 48, 32), ("ETR24-008", "Sistema de medición de la atención al usuario", 48, 32), ("ETR24-014", "Introducción a la Innovación", 32, 32), ("ETR24-022", "Experiencia Formativa en Situación Real de Trabajo III", 0, 96)],
                    [("ECF24-025", "Análisis de Riesgos", 48, 32), ("ECF24-026", "Valorización de Empresas", 32, 32), ("ECF24-027", "Auditoría Tributaria", 32, 32), ("ETR24-015", "Innovación en productos y servicios", 32, 32), ("ETR24-023", "Experiencia Formativa en Situación Real de Trabajo IV", 0, 96)],
                    [("ECF24-028", "Portafolio de Inversiones", 16, 32), ("ECF24-029", "Planificación Financiera", 16, 32), ("ECF24-030", "Contabilidad Gerencial", 16, 32), ("ETR24-009", "Plan de Negocios", 48, 32), ("ETR24-019", "Desarrollo Emprendedor", 48, 32), ("ETR24-024", "Experiencia Formativa en Situación Real de Trabajo V", 0, 96)],
                    [("ETR24-016", "Fundamentos de Investigación Aplicada", 48, 32), ("ETR24-017", "Técnicas de Investigación Aplicada", 48, 32), ("ETR24-018", "Seminario de Tesis", 80, 32), ("ETR24-025", "Experiencia Formativa en Situación Real de Trabajo VI", 0, 96)]
                ]
            },
            "ADMINISTRACIÓN DE EMPRESAS": {
                "codigo_base": "AE",
                "plan_estudio_codigo": "20241",
                "ciclos": [
                    [("EAE24-001", "Administración General", 48, 32), ("EAE24-002", "Matemática para los Negocios", 48, 32), ("EAE24-003", "Introducción a la Contabilidad", 48, 32), ("ETR24-001", "Intercomunicación Inicial", 48, 32), ("ETR24-002", "Ofimática Inicial", 48, 32)],
                    [("EAE24-004", "Fundamentos de Marketing", 48, 32), ("EAE24-005", "Matemática Financiera", 48, 32), ("EAE24-006", "Contabilidad General", 48, 32), ("ETR24-003", "Intercomunicación Avanzada", 48, 32), ("ETR24-004", "Ofimática Avanzada", 48, 32)],
                    [("EAE24-007", "Fundamentos de Finanzas", 48, 32), ("EAE24-008", "Investigación de Mercados", 48, 32), ("EAE24-009", "Derecho Empresarial", 48, 32), ("EAE24-010", "Estadística General", 48, 32), ("ETR24-005", "Psicología Organizacional", 32, 32), ("ETR24-010", "Introducción a la Ética", 32, 32)],
                    [("EAE24-011", "Elaboración de Procesos", 48, 32), ("EAE24-012", "Costos y Presupuestos", 48, 32), ("EAE24-013", "Análisis Cuantitativo para los Negocios", 48, 32), ("EAE24-014", "Estadística para los Negocios", 48, 32), ("ETR24-006", "Autorealización Personal", 32, 32), ("ETR24-011", "Ética Profesional", 32, 32)],
                    [("EAE24-015", "Derecho Laboral", 48, 32), ("EAE24-016", "Finanzas Empresariales", 48, 32), ("EAE24-017", "Administración de Operaciones", 48, 32), ("ETR24-007", "Atención al usuario", 48, 32), ("ETR24-012", "Didáctica del Razonamiento", 32, 32), ("ETR24-020", "Experiencia Formativa en Situación Real de Trabajo I", 0, 96)],
                    [("EAE24-018", "Talento Humano", 48, 32), ("EAE24-019", "Comportamiento Humano en las Organizaciones", 48, 32), ("EAE24-020", "Contabilidad Gerencial", 48, 32), ("ETR24-008", "Sistema de medición de la atención al usuario", 48, 32), ("ETR24-013", "Analisis de Situaciones Reales", 32, 32), ("ETR24-021", "Experiencia Formativa en Situación Real de Trabajo II", 0, 96)],
                    [("EAE24-021", "Administración Estratégica", 48, 32), ("EAE24-022", "Evaluación y Gestión de Proyectos", 48, 32), ("EAE24-023", "Cadena de suministro", 48, 32), ("ETR24-014", "Introducción a la Innovación", 32, 32), ("ETR24-019", "Desarrollo Emprendedor", 48, 32), ("ETR24-022", "Experiencia Formativa en Situación Real de Trabajo III", 0, 96)],
                    [("EAE24-024", "Estrategia Comercial", 48, 32), ("EAE24-025", "Micro y Pequeña Empresa", 48, 32), ("ETR24-009", "Plan de Negocios", 48, 32), ("ETR24-015", "Innovación en productos y servicios", 32, 32), ("ETR24-023", "Experiencia Formativa en Situación Real de Trabajo IV", 0, 96)],
                    [("EAE24-026", "Marketing Estratégico", 48, 32), ("EAE24-027", "Administración Pública", 48, 32), ("EAE24-028", "E-business y Transformación Digital en las Empresas", 48, 32), ("ETR24-024", "Experiencia Formativa en Situación Real de Trabajo V", 0, 96)],
                    [("ETR24-016", "Fundamentos de Investigación Aplicada", 48, 32), ("ETR24-017", "Técnicas de Investigación Aplicada", 48, 32), ("ETR24-018", "Seminario de Tesis", 80, 32), ("ETR24-025", "Experiencia Formativa en Situación Real de Trabajo VI", 0, 96)]
                ]
            },
            "INGENIERIA DE SISTEMAS DE INFORMACIÓN": {
                "codigo_base": "II",
                "plan_estudio_codigo": "20241",
                "ciclos": [
                    [("EIS24-001", "Arquitectura Web", 48, 32), ("EIS24-002", "Introducción a la Programación", 48, 32), ("EIS24-003", "Matemática Aplicada", 48, 32), ("ETR24-001", "Intercomunicación Inicial", 48, 32), ("ETR24-002", "Ofimática Inicial", 48, 32)],
                    [("EIS24-004", "Fundamentos de Algoritmia", 48, 32), ("EIS24-005", "Configuración de Aplicaciones", 48, 32), ("EIS24-006", "Introducción al Modelamiento de Procesos", 48, 32), ("ETR24-003", "Intercomunicación Avanzada", 48, 32), ("ETR24-004", "Ofimática Avanzada", 48, 32)],
                    [("EIS24-007", "Fundamentos de Estructura de Datos", 48, 32), ("EIS24-008", "Estadística Aplicada", 48, 32), ("EIS24-009", "Diseño de Sistemas en TI", 48, 32), ("EIS24-010", "Modelado de procesos en TI", 48, 32), ("ETR24-005", "Psicología Organizacional", 32, 32), ("ETR24-010", "Introducción a la Ética", 32, 32)],
                    [("EIS24-011", "Cyberseguridad", 48, 32), ("EIS24-012", "Gestión de Servicios en TI", 48, 32), ("EIS24-013", "Lenguaje de Programación", 48, 32), ("EIS24-014", "Programación orientada a Objetos", 48, 32), ("ETR24-006", "Autorealización Personal", 32, 32), ("ETR24-011", "Ética Profesional", 32, 32)],
                    [("EIS24-015", "Arquitectura de sistemas operativos", 48, 32), ("EIS24-016", "Programación de aplicaciones web", 48, 32), ("EIS24-017", "Sistemas Distribuidos", 48, 32), ("ETR24-007", "Atención al usuario", 48, 32), ("ETR24-012", "Didáctica del Razonamiento", 32, 32), ("ETR24-020", "Experiencia Formativa en Situación Real de Trabajo I", 0, 96)],
                    [("EIS24-018", "Soluciones móviles y cloud", 48, 32), ("EIS24-019", "Modelamiento y análisis de sistemas", 48, 32), ("EIS24-020", "Legislación en sistemas de información", 48, 32), ("ETR24-013", "Analisis de Situaciones Reales", 32, 32), ("ETR24-021", "Experiencia Formativa en Situación Real de Trabajo II", 0, 96)],
                    [("EIS24-021", "Arquitectura de software", 48, 32), ("EIS24-022", "Modelamiento de base de datos", 48, 32), ("EIS24-023", "Validación y pruebas de software", 48, 32), ("ETR24-008", "Sistema de medición de la atención al usuario", 48, 32), ("ETR24-014", "Introducción a la Innovación", 32, 32), ("ETR24-022", "Experiencia Formativa en Situación Real de Trabajo III", 0, 96)],
                    [("EIS24-024", "Auditoría de sistemas", 48, 32), ("EIS24-025", "Analítica con Big Data", 48, 32), ("EIS24-026", "Inteligencia artificial", 48, 32), ("ETR24-015", "Innovación en productos y servicios", 32, 32), ("ETR24-023", "Experiencia Formativa en Situación Real de Trabajo IV", 0, 96)],
                    [("EIS24-027", "Bases de datos", 48, 32), ("EIS24-028", "Proyectos en TI", 48, 32), ("ETR24-009", "Plan de Negocios", 48, 32), ("ETR24-019", "Desarrollo Emprendedor", 48, 32), ("ETR24-024", "Experiencia Formativa en Situación Real de Trabajo V", 0, 96)],
                    [("ETR24-016", "Fundamentos de Investigación Aplicada", 48, 32), ("ETR24-017", "Técnicas de Investigación Aplicada", 48, 32), ("ETR24-018", "Seminario de Tesis", 80, 32), ("ETR24-025", "Experiencia Formativa en Situación Real de Trabajo VI", 0, 96)]
                ]
            }
        }
    },
    "Instituto La Pontificia": {
        "tipo": "Instituto",
        "carreras": {
            "ADMINISTRACIÓN DE EMPRESAS": {
                "codigo_base": "AEI",
                "plan_estudio_codigo": "2024",
                "ciclos": [
                    [("AE23-001", "ADMINISTRACIÓN GENERAL", 5, 0), ("AE23-002", "INTERCOMUNICACIÓN INICIAL", 4, 0), ("AE23-003", "INTRODUCCIÓN A LA CONTABILIDAD", 4, 0), ("AE23-004", "FUNDAMENTOS DE MARKETING", 4, 0), ("AE23-005", "OFIMÁTICA INICIAL", 0, 4), ("AE23-006", "MATEMÁTICA PARA LOS NEGOCIOS I", 5, 0)],
                    [("AE23-007", "INTERCOMUNICACIÓN AVANZADA", 3, 0), ("AE23-008", "CONTABILIDAD FINANCIERA", 2, 2), ("AE23-009", "EXPERIENCIAS FORMATIVAS EN SITUACIONES REALES DE TRABAJO I", 0, 8), ("AE23-010", "OFIMÁTICA AVANZADA", 0, 4), ("AE23-011", "MARKETING ESTRATÉGICO", 5, 0), ("AE23-012", "MATEMÁTICA PARA LOS NEGOCIOS II", 6, 0)],
                    [("AE23-013", "ADMINISTRACIÓN ESTRATÉGICA I", 5, 0), ("AE23-014", "COMPORTAMIENTO HUMANO EN LAS ORGANIZACIONES", 4, 0), ("AE23-015", "AUTOREALIZACIÓN Y ÉTICA", 3, 0), ("AE23-016", "CONTABILIDAD DE COSTOS", 2, 2), ("AE23-017", "SERVICIO Y ATENCIÓN AL CLIENTE", 5, 0), ("AE23-018", "ESTADÍSTICA APLICADA", 3, 2)],
                    [("AE23-019", "ADMINISTRACIÓN DE OPERACIONES", 5, 0), ("AE23-020", "DERECHO EMPRESARIAL", 4, 0), ("AE23-021", "SOSTENIBILIDAD Y RESPONSABILIDAD SOCIAL AMBIENTAL", 3, 0), ("AE23-022", "EXPERIENCIAS FORMATIVAS EN SITUACIONES REALES DE TRABAJO II", 0, 8), ("AE23-023", "FUNDAMENTOS DE FINANZAS", 3, 2), ("AE23-024", "INDUCCIÓN AL MERCADO LABORAL", 3, 2)],
                    [("AE23-025", "DERECHO LABORAL Y TRIBUTARIO", 4, 0), ("AE23-026", "E-BUSINESS Y TRANSFORMACIÓN DIGITAL EN LAS EMPRESAS", 3, 2), ("AE23-027", "INVESTIGACIÓN DE MERCADOS", 3, 3), ("AE23-028", "GESTIÓN DEL TALENTO HUMANO", 4, 0), ("AE23-029", "MACRO Y MICRO ECONOMÍA", 4, 0), ("AE23-030", "LIDERAZGO Y TRABAJO EN EQUIPO", 3, 0)],
                    [("AE23-031", "ADMINISTRACIÓN PÚBLICA", 3, 2), ("AE23-032", "EVALUACIÓN Y GESTIÓN DE PROYECTOS", 3, 2), ("AE23-033", "EXPERIENCIAS FORMATIVAS EN SITUACIONES REALES DE TRABAJO III", 0, 8), ("AE23-034", "INNOVACIÓN Y DESARROLLO DE EMPRENDIMIENTOS PERSONALES", 3, 0), ("AE23-035", "PLAN DE NEGOCIOS", 4, 0), ("AE23-036", "ADQUISICIÓN DE BIENES Y SERVICIOS PÚBLICOS", 4, 0)]
                ]
            },
            "CONTABILIDAD": {
                "codigo_base": "CT",
                "plan_estudio_codigo": "2024",
                "ciclos": [
                    [("CT23-001", "ADMINISTRACIÓN GENERAL", 5, 0), ("CT23-002", "INTERCOMUNICACIÓN INICIAL", 4, 0), ("CT23-003", "FUNDAMENTOS DE MARKETING", 4, 0), ("CT23-004", "OFIMÁTICA INICIAL", 0, 4), ("CT23-005", "INTRODUCCIÓN A LA CONTABILIDAD", 4, 0), ("CT23-006", "MATEMÁTICA PARA LOS NEGOCIOS I", 6, 0)],
                    [("CT23-007", "INTERCOMUNICACIÓN AVANZADA", 3, 0), ("CT23-008", "CONTABILIDAD DE COSTOS", 3, 2), ("CT23-009", "CONTABILIDAD FINANCIERA I", 2, 2), ("CT23-010", "EXPERIENCIAS FORMATIVAS EN SITUACIONES REALES DE TRABAJO I", 0, 8), ("CT23-011", "OFIMÁTICA AVANZADA", 0, 4), ("CT23-012", "MATEMÁTICA PARA LOS NEGOCIOS II", 6, 0)],
                    [("CT23-013", "CONTABILIDAD FINANCIERA II", 4, 2), ("CT23-014", "DERECHO CIVIL Y COMERCIAL", 4, 0), ("CT23-015", "DERECHO TRIBUTARIO", 5, 0), ("CT23-016", "AUTOREALIZACIÓN Y ÉTICA", 3, 0), ("CT23-017", "FUNDAMENTOS DE FINANZAS", 2, 2), ("CT23-018", "MICROECONOMÍA PARA LOS NEGOCIOS", 3, 3)],
                    [("CT23-019", "ANÁLISIS Y REPORTES CONTABLES FINANCIEROS", 4, 0), ("CT23-020", "CONTABILIDAD FINANCIERA III", 4, 2), ("CT23-021", "SOSTENIBILIDAD Y RESPONSABILIDAD SOCIAL AMBIENTAL", 3, 0), ("CT23-022", "EXPERIENCIAS FORMATIVAS EN SITUACIONES REALES DE TRABAJO II", 0, 8), ("CT23-023", "FINANZAS CORPORATIVAS", 4, 2), ("CT23-024", "TRIBUTACIÓN APLICADA I", 4, 0)],
                    [("CT23-025", "AUDITORÍA FINANCIERA", 4, 2), ("CT23-026", "CONTABILIDAD GERENCIAL", 5, 0), ("CT23-027", "DERECHO LABORAL Y TRIBUTARIO", 4, 0), ("CT23-028", "AUDITORÍA Y CONTROL INTERNO", 4, 0), ("CT23-029", "LIDERAZGO Y TRABAJO EN EQUIPO", 3, 0), ("CT23-030", "TRIBUTACIÓN APLICADA II", 6, 0)],
                    [("CT23-031", "ADMINISTRACIÓN PÚBLICA", 3, 2), ("CT23-032", "AUDITORÍA TRIBUTARIA", 4, 0), ("CT23-033", "INNOVACIÓN Y DESARROLLO DE EMPRENDIMIENTOS PERSONALES", 3, 0), ("CT23-034", "CONTABILIDAD GUBERNAMENTAL", 2, 2), ("CT23-035", "EVALUACIÓN Y GESTIÓN DE PROYECTOS", 3, 2), ("CT23-036", "EXPERIENCIAS FORMATIVAS EN SITUACIONES REALES DE TRABAJO III", 0, 8)]
                ]
            },
            "ENFERMERIA TÉCNICA": {
                "codigo_base": "ET",
                "plan_estudio_codigo": "2024",
                "ciclos": [
                    [("ET23-001", "ANATOMÍA Y FISIOLOGÍA", 4, 2), ("ET23-002", "SALUD COMUNITARIA", 4, 2), ("ET23-003", "INTERCOMUNICACIÓN INICIAL", 4, 0), ("ET23-004", "OFIMÁTICA INICIAL", 0, 4), ("ET23-006", "PRIMEROS AUXILIOS", 3, 3)],
                    [("ET23-007", "BIOLOGÍA", 3, 2), ("ET23-008", "INTERCOMUNICACIÓN AVANZADA", 3, 0), ("ET23-009", "ENFERMERÍA BÁSICA I", 4, 3), ("ET23-010", "EXPERIENCIAS FORMATIVAS EN SITUACIONES REALES DE TRABAJO I", 0, 8), ("ET23-011", "TERMINOLOGÍA EN SALUD", 4, 0), ("ET23-012", "OFIMÁTICA AVANZADA", 0, 4)],
                    [("ET23-013", "ADMINISTRACIÓN DE MEDICAMENTOS", 3, 2), ("ET23-014", "AUTOREALIZACIÓN Y ÉTICA", 3, 0), ("ET23-015", "ENFERMERÍA BÁSICA II", 3, 3), ("ET23-016", "EPIDEMIOLOGÍA", 4, 0), ("ET23-017", "BIOSEGURIDAD", 3, 1), ("ET23-018", "FARMACOLOGÍA", 4, 0)],
                    [("ET23-019", "ASISTENCIA EN INMUNIZACIONES", 2, 2), ("ET23-020", "ASISTENCIA EN SALUD MATERNA Y DEL NEONATO", 1, 2), ("ET23-021", "ASISTENCIA QUIRURGICA", 3, 2), ("ET23-022", "SOSTENIBILIDAD Y RESPONSABILIDAD SOCIAL AMBIENTAL", 3, 0), ("ET23-023", "EXPERIENCIAS FORMATIVAS EN SITUACIONES REALES DE TRABAJO II", 0, 8), ("ET23-024", "SALUD PÚBLICA", 4, 0), ("ET23-037", "ASISTENCIA EN NEUMOLOGÍA", 3, 0)],
                    [("ET23-025", "ASISTENCIA EN FISIOTERAPIA Y REHABILITACIÓN", 3, 2), ("ET23-026", "ASISTENCIA EN MEDICINA ALTERNATIVA", 5, 0), ("ET23-027", "ASISTENCIA EN SALUD BUCAL", 4, 0), ("ET23-028", "LIDERAZGO Y TRABAJO EN EQUIPO", 3, 0), ("ET23-029", "SALUD DEL NIÑO Y DEL ADOLESCENTE", 3, 2), ("ET23-030", "SALUD OCUPACIONAL", 2, 2)],
                    [("ET23-031", "ASISTENCIA AL PACIENTE ONCOLOGICO Y CUIDADOS PALIATIVOS", 5, 0), ("ET23-032", "ASISTENCIA EN PROCEDIMIENTOS INVASIVOS Y NO INVASIVOS", 3, 2), ("ET23-033", "ASISTENCIA EN SALUD MENTAL Y PSIQUIATRIA", 5, 0), ("ET23-034", "ASISTENCIA GERIATRICA Y DEL ADULTO MAYOR", 3, 2), ("ET23-035", "EXPERIENCIAS FORMATIVAS EN SITUACIONES REALES DE TRABAJO III", 0, 8), ("ET23-036", "INNOVACIÓN Y DESARROLLO DE EMPRENDIMIENTOS PERSONALES", 3, 0)]
                ]
            }
        }
    }
}
DATOS_ESPACIOS = { "Aula Normal": { "A": {"pisos": 5, "salones_por_piso": 10}, "B": {"pisos": 5, "salones_por_piso": 5}, }, "Sala de Cómputo": { "C": {"pisos": 4, "salones_por_piso": 1}, "D": {"pisos": 4, "salones_por_piso": 2}, } }
ESPECIALIDADES_SUGERIDAS = [ "Contabilidad Financiera", "Tributación", "Finanzas Corporativas", "Administración Estratégica", "Marketing Digital", "Gestión del Talento Humano", "Desarrollo de Software", "Bases de Datos", "Ciberseguridad", "Redes y Comunicaciones", "Anatomía Humana", "Salud Pública", "Farmacología", "Didáctica y Pedagogía", "Ética Profesional", "Investigación Aplicada" ]
NUM_DOCENTES = 80
NUM_USUARIOS_ADMIN = 2
DIAS_SEMANA = [1, 2, 3, 4, 5, 6]
TURNOS_BLOQUES = { 'M': [time(7, 0), time(9, 0), time(9, 0), time(11, 0), time(11,0), time(13,0)], 'T': [time(14, 0), time(16, 0), time(16, 0), time(18, 0), time(18,0), time(20,0)], 'N': [time(19, 0), time(21, 0), time(21,0), time(23,0)] }


class Command(BaseCommand):
    help = 'Genera datos de prueba de alta fidelidad para el sistema de horarios.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("INICIANDO SCRIPT DE POPULACIÓN (ESTRUCTURA GRUPO-MATERIAS MÚLTIPLES)"))
        
        self._limpiar_datos_antiguos()
        self._crear_roles_y_grupos_base()

        tipos_ua = self._crear_tipos_unidades_academicas()
        unidades = self._crear_unidades_academicas(tipos_ua)
        periodos = self._crear_periodos_academicos()
        tipos_espacio = self._crear_tipos_espacio()
        self._crear_espacios_fisicos(tipos_espacio, unidades[0] if unidades else None)
        
        materias_creadas = self._crear_materias_maestra()
        self._crear_estructura_academica_y_grupos(unidades, materias_creadas, periodos)

        especialidades = self._crear_especialidades()
        self._vincular_materias_a_especialidades(materias_creadas, especialidades)
        docentes = self._crear_docentes_y_usuarios(unidades, especialidades)
        bloques = self._crear_bloques_horarios()
        self._crear_disponibilidad_docentes(docentes, periodos, bloques)

        self._crear_usuarios_admin()
        self.stdout.write(self.style.SUCCESS('¡PROCESO DE POPULACIÓN COMPLETADO!'))

    def _limpiar_datos_antiguos(self):
        self.stdout.write("-> Limpiando base de datos anterior...")
        HorariosAsignados.objects.all().delete()
        Grupos.materias.through.objects.all().delete()
        Grupos.objects.all().delete()
        DisponibilidadDocentes.objects.all().delete()
        BloquesHorariosDefinicion.objects.all().delete()
        DocenteEspecialidades.objects.all().delete()
        Docentes.objects.all().delete()
        MateriaEspecialidadesRequeridas.objects.all().delete()
        CarreraMaterias.objects.all().delete()
        Seccion.objects.all().delete()
        Ciclo.objects.all().delete()
        Carrera.objects.all().delete()
        Materias.objects.all().delete()
        Especialidades.objects.all().delete()
        EspaciosFisicos.objects.all().delete()
        TiposEspacio.objects.all().delete()
        PeriodoAcademico.objects.all().delete()
        UnidadAcademica.objects.all().delete()
        TipoUnidadAcademica.objects.all().delete()
        Roles.objects.all().delete()

    def _crear_roles_y_grupos_base(self):
        self.stdout.write("-> Creando Roles y Grupos de Django...")
        Roles.objects.create(nombre_rol='Administrador')
        Roles.objects.create(nombre_rol='Coordinador Académico')
        Roles.objects.create(nombre_rol='Docente')
        Group.objects.get_or_create(name='Admins')
        Group.objects.get_or_create(name='Coordinadores')
        Group.objects.get_or_create(name='Docentes')

    def _crear_tipos_unidades_academicas(self):
        self.stdout.write("-> Creando Tipos de Unidad Académica...")
        tipos = {}
        for _, data in DATOS_ACADEMICOS.items():
            tipo_nombre = data['tipo']
            if tipo_nombre not in tipos:
                tipo, _ = TipoUnidadAcademica.objects.get_or_create(nombre_tipo=tipo_nombre)
                tipos[tipo_nombre] = tipo
        return tipos

    def _crear_unidades_academicas(self, tipos_ua):
        self.stdout.write("-> Creando Unidades Académicas...")
        unidades = []
        for nombre_ua, data in DATOS_ACADEMICOS.items():
            tipo_obj = tipos_ua.get(data['tipo'])
            ua, _ = UnidadAcademica.objects.get_or_create(
                nombre_unidad=nombre_ua,
                defaults={'descripcion': f"Unidad académica: {nombre_ua}", 'tipo_unidad': tipo_obj}
            )
            unidades.append(ua)
        return unidades

    def _crear_periodos_academicos(self):
        self.stdout.write("-> Creando Períodos Académicos...")
        periodos = []
        year = date.today().year
        for i, semestre in enumerate(["I", "II"]):
            nombre = f"{year}-{semestre}"
            start_month = 3 if semestre == "I" else 8
            p, _ = PeriodoAcademico.objects.get_or_create(
                nombre_periodo=nombre,
                defaults={ 'fecha_inicio': date(year, start_month, 1), 'fecha_fin': date(year, start_month + 4, 15), 'activo': (i == 0) }
            )
            periodos.append(p)
        return periodos

    def _crear_tipos_espacio(self):
        self.stdout.write("-> Creando Tipos de Espacio...")
        tipos_espacio = []
        for nombre_tipo in DATOS_ESPACIOS.keys():
            te, _ = TiposEspacio.objects.get_or_create(nombre_tipo_espacio=nombre_tipo)
            tipos_espacio.append(te)
        return tipos_espacio

    def _crear_espacios_fisicos(self, tipos_espacio, unidad_principal):
        self.stdout.write("-> Creando Espacios Físicos (Salones)...")
        if not unidad_principal: return
        for nombre_tipo, pabellones in DATOS_ESPACIOS.items():
            tipo_obj = TiposEspacio.objects.get(nombre_tipo_espacio=nombre_tipo)
            for pabellon_letra, data in pabellones.items():
                for piso_num in range(1, data['pisos'] + 1):
                    piso_real = piso_num + 1 if pabellon_letra in ['C', 'D'] else piso_num
                    for salon_num in range(1, data['salones_por_piso'] + 1):
                        nombre_salon = f"{pabellon_letra}{piso_real}{salon_num:02d}"
                        EspaciosFisicos.objects.get_or_create(
                            nombre_espacio=nombre_salon, unidad=unidad_principal,
                            defaults={ 'tipo_espacio': tipo_obj, 'capacidad': 40 if tipo_obj.nombre_tipo_espacio == "Aula Normal" else 25, 'ubicacion': f"Pabellón {pabellon_letra}, Piso {piso_real}" }
                        )

    def _crear_materias_maestra(self):
        self.stdout.write("-> Creando catálogo maestro de Materias...")
        materias_creadas = {}
        lab_computo = TiposEspacio.objects.filter(nombre_tipo_espacio__icontains="Cómputo").first()
        for _, data_ua in DATOS_ACADEMICOS.items():
            for _, data_carrera in data_ua['carreras'].items():
                for ciclo in data_carrera['ciclos']:
                    for codigo, nombre, h_teo, h_pra in ciclo:
                        if codigo not in materias_creadas:
                            requiere_espacio = lab_computo if any(term in nombre.upper() for term in ["OFIMÁTICA", "PROGRAMACIÓN", "SISTEMAS"]) else None
                            materia, _ = Materias.objects.get_or_create(
                                codigo_materia=codigo,
                                defaults={ 'nombre_materia': nombre.title(), 'horas_academicas_teoricas': h_teo, 'horas_academicas_practicas': h_pra, 'requiere_tipo_espacio_especifico': requiere_espacio }
                            )
                            materias_creadas[codigo] = materia
        return materias_creadas
    
    def _crear_estructura_academica_y_grupos(self, unidades, materias_maestra, periodos):
        self.stdout.write("-> Creando Carreras, Ciclos, Planes y GRUPOS...")
        ua_map = {ua.nombre_unidad: ua for ua in unidades}
        periodo_activo = next((p for p in periodos if p.activo), None)
        if not periodo_activo:
            self.stdout.write(self.style.ERROR("No hay un período académico activo. No se pueden crear grupos."))
            return

        for nombre_ua, data_ua in DATOS_ACADEMICOS.items():
            unidad_obj = ua_map.get(nombre_ua)
            if not unidad_obj: continue

            for nombre_carrera, data_carrera in data_ua['carreras'].items():
                carrera, _ = Carrera.objects.get_or_create(
                    nombre_carrera=f"{nombre_carrera.title()} ({unidad_obj.nombre_unidad.split()[0]})",
                    unidad=unidad_obj,
                    defaults={'codigo_carrera': data_carrera['codigo_base']}
                )

                for i, ciclo_data in enumerate(data_carrera['ciclos']):
                    orden_ciclo = i + 1
                    ciclo, _ = Ciclo.objects.get_or_create(
                        carrera=carrera,
                        orden=orden_ciclo,
                        defaults={'nombre_ciclo': f"Ciclo {orden_ciclo}"}
                    )
                    
                    materias_del_ciclo = []
                    for codigo_materia, _, _, _ in ciclo_data:
                        materia_obj = materias_maestra.get(codigo_materia)
                        if materia_obj:
                            materias_del_ciclo.append(materia_obj)
                            CarreraMaterias.objects.get_or_create(
                                carrera=carrera, materia=materia_obj, ciclo=ciclo
                            )
                    
                    for seccion_nombre in ['A', 'B']:
                        seccion, _ = Seccion.objects.get_or_create(
                            ciclo=ciclo, nombre_seccion=seccion_nombre, defaults={'capacidad': 40}
                        )
                        
                        codigo_grupo = f"G-{carrera.codigo_carrera}-C{orden_ciclo}-{seccion_nombre}"
                        grupo, created = Grupos.objects.get_or_create(
                            codigo_grupo=codigo_grupo,
                            periodo=periodo_activo,
                            defaults={
                                'carrera': carrera,
                                'numero_estudiantes_estimado': seccion.capacidad,
                                'ciclo_semestral': orden_ciclo
                            }
                        )
                        
                        if created and materias_del_ciclo:
                            grupo.materias.add(*materias_del_ciclo)
                            self.stdout.write(f"   -> Creado Grupo '{codigo_grupo}' y asociado con {len(materias_del_ciclo)} materias.")

    def _crear_especialidades(self):
        self.stdout.write("-> Creando Especialidades...")
        especialidades = []
        for nombre in ESPECIALIDADES_SUGERIDAS:
            esp, _ = Especialidades.objects.get_or_create(nombre_especialidad=nombre)
            especialidades.append(esp)
        return especialidades

    def _vincular_materias_a_especialidades(self, materias, especialidades):
        self.stdout.write("-> Vinculando Materias con Especialidades...")
        for materia in materias.values():
            esp_name = random.choice(ESPECIALIDADES_SUGERIDAS)
            esp_obj = next((e for e in especialidades if e.nombre_especialidad == esp_name), None)
            if esp_obj: MateriaEspecialidadesRequeridas.objects.get_or_create(materia=materia, especialidad=esp_obj)

    def _crear_docentes_y_usuarios(self, unidades, especialidades):
        self.stdout.write("-> Creando Docentes y Usuarios...")
        docentes = []
        grupo_docentes = Group.objects.get(name='Docentes')
        for i in range(NUM_DOCENTES):
            nombre, apellido = fake.first_name(), fake.last_name()
            username = f"{nombre[0].lower()}{apellido.lower().replace(' ', '')}{i}"
            email = f"{username}@pontificia.edu.pe"
            user, created = User.objects.get_or_create(username=username, defaults={'first_name': nombre, 'last_name': apellido, 'email': email, 'is_staff': True})
            if created: user.set_password('password123'); user.groups.add(grupo_docentes); user.save()
            doc, _ = Docentes.objects.get_or_create(usuario=user, defaults={'codigo_docente': f"DOC{i+1:04d}", 'nombres': nombre, 'apellidos': apellido, 'email': email, 'dni': fake.numerify(text="########"), 'max_horas_semanales': random.randint(20, 40), 'unidad_principal': random.choice(unidades)})
            especialidades_docente = random.sample(especialidades, k=random.randint(1, 3))
            for esp in especialidades_docente: DocenteEspecialidades.objects.get_or_create(docente=doc, especialidad=esp)
            docentes.append(doc)
        return docentes

    def _crear_bloques_horarios(self):
        self.stdout.write("-> Creando Bloques Horarios...")
        for dia_num in DIAS_SEMANA:
            dia_nombre = dict(BloquesHorariosDefinicion.DIA_SEMANA_CHOICES).get(dia_num)
            for turno_cod, horas in TURNOS_BLOQUES.items():
                for i in range(0, len(horas), 2):
                    h_inicio, h_fin = horas[i], horas[i+1]
                    nombre = f"{dia_nombre[:3]} {h_inicio.strftime('%H:%M')}-{h_fin.strftime('%H:%M')}"
                    BloquesHorariosDefinicion.objects.get_or_create(dia_semana=dia_num, hora_inicio=h_inicio, hora_fin=h_fin, defaults={'nombre_bloque': nombre, 'turno': turno_cod})

    def _crear_disponibilidad_docentes(self, docentes, periodos, bloques):
        self.stdout.write("-> Generando Disponibilidad de Docentes...")
        periodo_activo = next((p for p in periodos if p.activo), None)
        if not periodo_activo: return
        for docente in docentes:
            for bloque in BloquesHorariosDefinicion.objects.all():
                if random.random() < 0.6:
                    DisponibilidadDocentes.objects.create(docente=docente, periodo=periodo_activo, dia_semana=bloque.dia_semana, bloque_horario=bloque, esta_disponible=True, preferencia=random.choice([0, 0, 1]))

    def _crear_usuarios_admin(self):
        self.stdout.write("-> Creando Usuarios Administradores...")
        admin_group = Group.objects.get(name='Admins')
        for i in range(NUM_USUARIOS_ADMIN):
            username = f'admin{i+1}'
            user, created = User.objects.get_or_create(username=username, defaults={'email': f'admin{i+1}@pontificia.edu.pe', 'first_name': 'Admin', 'last_name': f'User {i+1}', 'is_staff': True, 'is_superuser': True})
            if created: user.set_password('adminpass123'); user.save()
            user.groups.add(admin_group)