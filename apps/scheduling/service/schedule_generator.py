# apps/scheduling/service/schedule_generator.py
import random
import math
from collections import defaultdict
from django.db import transaction
import logging

from apps.academic_setup.models import PeriodoAcademico, EspaciosFisicos, Materias
from apps.users.models import Docentes
from apps.scheduling.models import (
    Grupos, DisponibilidadDocentes, HorariosAsignados,
    BloquesHorariosDefinicion
)

# --- PARÁMETROS DEL ALGORITMO DE RECOCIDO SIMULADO ---
# Puedes ajustar estos valores para cambiar el comportamiento del generador.
# Aumentar MAX_ITERATIONS mejora la calidad pero tarda más tiempo.
INITIAL_TEMPERATURE = 2000.0
COOLING_RATE = 0.9995  # Un enfriamiento más lento permite una mejor exploración.
MAX_ITERATIONS = 50000 

# --- PENALIZACIONES PARA LA FUNCIÓN DE COSTO (CALIDAD DEL HORARIO) ---
# Estos valores definen la "calidad" de un horario. Mientras más bajo el costo, mejor.
P_DOCENTE_NO_PREFERIDO = 30
P_DOCENTE_NEUTRAL = 5
P_CLASES_CONSECUTIVAS_DOCENTE = -10 # Bonificación
P_HUECO_UNA_HORA_DOCENTE = 20      # Penalización por un hueco de una sesión.
P_HUECO_MAS_HORAS_DOCENTE = 35     # Penalización mayor por huecos largos.
P_CLASES_SEPARADAS_MISMO_DIA_GRUPO = 25 # Penalización por dividir las clases de un grupo en varios días.
P_SESIONES_NO_PROGRAMADAS = 2000   # Penalización muy severa

class ScheduleGeneratorService:
    def __init__(self, periodo: PeriodoAcademico, stdout_ref=None):
        self.periodo = periodo
        self.logger = self._setup_logger(stdout_ref)
        
        # El corazón del generador ahora es la lista de clases a programar
        self.clases_a_programar = [] # Lista de dicts: {'grupo': obj, 'materia': obj}

        self._load_and_cache_data()
        
        self.current_solution = {}  # {(grupo_id, materia_id): [asignacion1, ...]}
        self.best_solution = {}
        self.current_energy = float('inf')
        self.best_energy = float('inf')

        self.docente_slots = set() # {(docente_id, dia, bloque_id)}
        self.espacio_slots = set() # {(espacio_id, dia, bloque_id)}
        self.grupo_slots = set()   # {(grupo_id, dia, bloque_id)}

    def _setup_logger(self, stdout_ref):
        if stdout_ref: return stdout_ref
        logger = logging.getLogger(f"schedule_generator.{self.periodo.id}")
        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            logger.propagate = False
        return logger

    def _load_and_cache_data(self):
        self.logger.info("Cargando y pre-procesando datos para optimización...")
        
        # Cargar todos los grupos y sus materias asociadas
        grupos = Grupos.objects.filter(periodo=self.periodo).prefetch_related(
            'materias__materiaespecialidadesrequeridas_set__especialidad',
            'carrera'
        )
        
        # Crear la lista de "clases" a planificar
        for g in grupos:
            for m in g.materias.all():
                self.clases_a_programar.append({'grupo': g, 'materia': m})
        
        self.docentes = list(Docentes.objects.filter(usuario__is_active=True).prefetch_related('especialidades'))
        self.espacios = list(EspaciosFisicos.objects.select_related('tipo_espacio'))
        self.bloques = list(BloquesHorariosDefinicion.objects.order_by('dia_semana', 'hora_inicio'))

        self.sesiones_requeridas = self._calculate_required_sessions()
        self.docentes_compatibles = self._map_docentes_a_materias()
        self.disponibilidad_docente = self._map_docente_disponibilidad()
        self.espacios_compatibles = self._map_espacios_a_materias()
        self.bloque_indices = {bloque.pk: i for i, bloque in enumerate(self.bloques)}
        self.grupo_map = {g.pk: g for g in grupos} # Mapa para acceso rápido a objetos grupo

        self.logger.info(f"Datos cargados: {len(self.clases_a_programar)} clases a programar, {len(self.docentes)} docentes, {len(self.espacios)} espacios.")

    def _calculate_required_sessions(self):
        reqs = defaultdict(int)
        horas_por_sesion = 2
        for clase in self.clases_a_programar:
            total_horas = clase['materia'].horas_totales
            if total_horas > 0:
                key = (clase['grupo'].pk, clase['materia'].pk)
                reqs[key] = (total_horas + horas_por_sesion - 1) // horas_por_sesion
        return reqs

    def _map_docentes_a_materias(self):
        compatibles = defaultdict(list)
        docente_especialidades = {d.docente_id: set(d.especialidades.values_list('especialidad_id', flat=True)) for d in self.docentes}
        
        all_materias = Materias.objects.prefetch_related('materiaespecialidadesrequeridas_set').all()
        materia_reqs_map = {m.pk: set(m.materiaespecialidadesrequeridas_set.values_list('especialidad_id', flat=True)) for m in all_materias}

        for materia_id, reqs in materia_reqs_map.items():
            for d_id, d_especialidades in docente_especialidades.items():
                if not reqs or (reqs & d_especialidades):
                    compatibles[materia_id].append(d_id)
        return compatibles

    def _map_docente_disponibilidad(self):
        dispo_map = defaultdict(lambda: -999)
        for d in DisponibilidadDocentes.objects.filter(periodo=self.periodo, esta_disponible=True):
            dispo_map[(d.docente_id, d.dia_semana, d.bloque_horario_id)] = d.preferencia
        return dispo_map

    def _map_espacios_a_materias(self):
        compatibles = defaultdict(list)
        for clase in self.clases_a_programar:
            materia, grupo = clase['materia'], clase['grupo']
            req_tipo = materia.requiere_tipo_espacio_especifico
            estudiantes = grupo.numero_estudiantes_estimado or 20
            
            for e in self.espacios:
                if req_tipo and e.tipo_espacio_id != req_tipo.pk:
                    continue
                if e.capacidad >= estudiantes:
                    compatibles[materia.pk].append(e.espacio_id)
        return compatibles

    def _is_slot_available(self, docente_id, espacio_id, grupo_id, dia, bloque_id):
        if (docente_id, dia, bloque_id) in self.docente_slots: return False
        if (espacio_id, dia, bloque_id) in self.espacio_slots: return False
        if (grupo_id, dia, bloque_id) in self.grupo_slots: return False
        return True

    def _add_assignment_to_state(self, asignacion):
        d_id, e_id, g_id, m_id, dia, b_id = asignacion['docente_id'], asignacion['espacio_id'], asignacion['grupo_id'], asignacion['materia_id'], asignacion['dia_semana'], asignacion['bloque_id']
        self.docente_slots.add((d_id, dia, b_id))
        self.espacio_slots.add((e_id, dia, b_id))
        self.grupo_slots.add((g_id, dia, b_id))
        
        key = (g_id, m_id)
        if key not in self.current_solution: self.current_solution[key] = []
        self.current_solution[key].append(asignacion)
    
    def _remove_assignment_from_state(self, asignacion):
        d_id, e_id, g_id, m_id, dia, b_id = asignacion['docente_id'], asignacion['espacio_id'], asignacion['grupo_id'], asignacion['materia_id'], asignacion['dia_semana'], asignacion['bloque_id']
        self.docente_slots.discard((d_id, dia, b_id))
        self.espacio_slots.discard((e_id, dia, b_id))
        self.grupo_slots.discard((g_id, dia, b_id))

        key = (g_id, m_id)
        if key in self.current_solution:
            self.current_solution[key] = [a for a in self.current_solution[key] if a != asignacion]
            if not self.current_solution[key]: del self.current_solution[key]

    def _generate_initial_feasible_solution(self):
        self.logger.info("Generando horario inicial aleatorio pero válido...")
        for clase in self.clases_a_programar:
            grupo, materia = clase['grupo'], clase['materia']
            key = (grupo.pk, materia.pk)
            sesiones_a_programar = self.sesiones_requeridas.get(key, 0)
            
            docentes_posibles = self.docentes_compatibles.get(materia.pk, [])
            espacios_posibles = self.espacios_compatibles.get(materia.pk, [])
            
            if not docentes_posibles or not espacios_posibles:
                self.logger.warning(f"Clase {grupo.codigo_grupo}-{materia.codigo_materia} no tiene docentes o espacios compatibles.")
                continue

            intentos = 0
            while sesiones_a_programar > 0 and intentos < 200:
                intentos += 1
                bloque, docente_id, espacio_id = random.choice(self.bloques), random.choice(docentes_posibles), random.choice(espacios_posibles)
                if self.disponibilidad_docente[(docente_id, bloque.dia_semana, bloque.bloque_def_id)] < -900: continue
                if self._is_slot_available(docente_id, espacio_id, grupo.pk, bloque.dia_semana, bloque.bloque_def_id):
                    asignacion = {"grupo_id": grupo.pk, "materia_id": materia.pk, "docente_id": docente_id, "espacio_id": espacio_id, "dia_semana": bloque.dia_semana, "bloque_id": bloque.bloque_def_id}
                    self._add_assignment_to_state(asignacion)
                    sesiones_a_programar -= 1
        
        self.current_energy = self._calculate_solution_energy(self.current_solution)
        self.best_solution = {k: list(v) for k, v in self.current_solution.items()}
        self.best_energy = self.current_energy
        self.logger.info(f"Horario inicial generado con energía (costo) de: {self.current_energy:.2f}")

    def _calculate_solution_energy(self, solution):
        energy, horarios_por_docente_dia, horarios_por_grupo_dia = 0.0, defaultdict(list), defaultdict(set)
        
        programadas = sum(len(s) for s in solution.values())
        requeridas = sum(self.sesiones_requeridas.values())
        energy += (requeridas - programadas) * P_SESIONES_NO_PROGRAMADAS

        for asignaciones in solution.values():
            for asignacion in asignaciones:
                d_id, g_id, dia, b_id = asignacion['docente_id'], asignacion['grupo_id'], asignacion['dia_semana'], asignacion['bloque_id']
                preferencia = self.disponibilidad_docente.get((d_id, dia, b_id), 0)
                if preferencia < 0: energy += P_DOCENTE_NO_PREFERIDO
                elif preferencia == 0: energy += P_DOCENTE_NEUTRAL
                horarios_por_docente_dia[(d_id, dia)].append(b_id)
                horarios_por_grupo_dia[g_id].add(dia)

        for bloques_ids in horarios_por_docente_dia.values():
            if len(bloques_ids) <= 1: continue
            indices = sorted([self.bloque_indices[b_id] for b_id in bloques_ids])
            for i in range(len(indices) - 1):
                diff = indices[i+1] - indices[i]
                if diff == 1: energy += P_CLASES_CONSECUTIVAS_DOCENTE
                elif diff == 2: energy += P_HUECO_UNA_HORA_DOCENTE
                else: energy += P_HUECO_MAS_HORAS_DOCENTE
        
        for dias in horarios_por_grupo_dia.values():
            if len(dias) > 1: energy += (len(dias) - 1) * P_CLASES_SEPARADAS_MISMO_DIA_GRUPO
        return energy
    
    def _get_neighbor_solution(self):
        if not self.current_solution: return False
        
        key_a_mover = random.choice(list(self.current_solution.keys()))
        if not self.current_solution[key_a_mover]: return False
        
        g_id, m_id = key_a_mover
        asignacion_a_mover = random.choice(self.current_solution[key_a_mover])
        
        docentes_posibles = self.docentes_compatibles.get(m_id, [])
        espacios_posibles = self.espacios_compatibles.get(m_id, [])
        if not docentes_posibles or not espacios_posibles: return False
        
        for _ in range(100):
            nuevo_bloque, nuevo_docente, nuevo_espacio = random.choice(self.bloques), random.choice(docentes_posibles), random.choice(espacios_posibles)
            if self.disponibilidad_docente.get((nuevo_docente, nuevo_bloque.dia_semana, nuevo_bloque.bloque_def_id), -999) < -900: continue
            
            self._remove_assignment_from_state(asignacion_a_mover)
            if self._is_slot_available(nuevo_docente, nuevo_espacio, g_id, nuevo_bloque.dia_semana, nuevo_bloque.bloque_def_id):
                nueva_asignacion = {"grupo_id": g_id, "materia_id": m_id, "docente_id": nuevo_docente, "espacio_id": nuevo_espacio, "dia_semana": nuevo_bloque.dia_semana, "bloque_id": nuevo_bloque.bloque_def_id}
                self._add_assignment_to_state(nueva_asignacion)
                return True
            self._add_assignment_to_state(asignacion_a_mover)
        return False

    def _run_simulated_annealing(self):
        self.logger.info(f"Iniciando Recocido Simulado... T_inicial={INITIAL_TEMPERATURE}, Rate={COOLING_RATE}, Iter={MAX_ITERATIONS}")
        temperature = INITIAL_TEMPERATURE
        for i in range(MAX_ITERATIONS):
            if not self.current_solution:
                self.logger.warning("La solución actual está vacía, deteniendo optimización.")
                break

            original_energy = self.current_energy
            original_solution_copy = {k: list(v) for k, v in self.current_solution.items()}
            original_slots = (self.docente_slots.copy(), self.espacio_slots.copy(), self.grupo_slots.copy())
            
            if not self._get_neighbor_solution(): continue
            
            new_energy = self._calculate_solution_energy(self.current_solution)
            delta_energy = new_energy - original_energy
            
            if delta_energy < 0 or (temperature > 0 and random.random() < math.exp(-delta_energy / temperature)):
                self.current_energy = new_energy
                if self.current_energy < self.best_energy:
                    self.best_energy = self.current_energy
                    self.best_solution = {k: list(v) for k, v in self.current_solution.items()}
            else:
                self.current_solution = original_solution_copy
                self.docente_slots, self.espacio_slots, self.grupo_slots = original_slots
                self.current_energy = original_energy

            temperature *= COOLING_RATE
            if i % 1000 == 0:
                self.logger.info(f"Iteración {i:>5}/{MAX_ITERATIONS} - Temp: {temperature:7.2f} - Energía Actual: {self.current_energy:9.2f} - Mejor Energía: {self.best_energy:9.2f}")

        self.logger.info(f"Optimización finalizada. Mejor energía encontrada: {self.best_energy:.2f}")

    @transaction.atomic
    def _save_solution_to_db(self, solution):
        self.logger.info("Guardando la mejor solución encontrada en la base de datos...")
        HorariosAsignados.objects.filter(periodo=self.periodo).delete()
        
        asignaciones_a_crear = [HorariosAsignados(periodo=self.periodo, grupo_id=asig['grupo_id'], materia_id=asig['materia_id'], docente_id=asig['docente_id'], espacio_id=asig['espacio_id'], dia_semana=asig['dia_semana'], bloque_horario_id=asig['bloque_id'], estado="Programado") for asignaciones in solution.values() for asig in asignaciones]
        
        HorariosAsignados.objects.bulk_create(asignaciones_a_crear)
        self.logger.info(f"Se guardaron {len(asignaciones_a_crear)} asignaciones de horario.")

    def generar_horarios_automaticos(self):
        self.logger.info(f"=== INICIO DEL PROCESO DE GENERACIÓN DE HORARIOS - PERIODO {self.periodo.nombre_periodo} ===")
        
        self._generate_initial_feasible_solution()
        
        if not self.current_solution:
            self.logger.error("No se pudo generar una solución inicial. Abortando.")
            all_clases = [f"G{k[0]}-M{k[1]}" for k in self.sesiones_requeridas.keys()]
            return {"stats": {"error": "No se pudo generar solución inicial"}, "unresolved_classes": all_clases}

        self._run_simulated_annealing()
        self._save_solution_to_db(self.best_solution)

        stats = {"mejor_energia_final": self.best_energy, "sesiones_requeridas": sum(self.sesiones_requeridas.values()), "sesiones_programadas": sum(len(s) for s in self.best_solution.values())}
        
        unresolved_classes = []
        materia_map = {m.pk: m for m in Materias.objects.all()}

        for key, req_sessions in self.sesiones_requeridas.items():
            g_id, m_id = key
            assigned_sessions = len(self.best_solution.get(key, []))
            if assigned_sessions < req_sessions:
                grupo_code = self.grupo_map.get(g_id, f"ID:{g_id}").codigo_grupo
                materia_code = materia_map.get(m_id, f"ID:{m_id}").codigo_materia
                unresolved_classes.append({
                    "grupo": grupo_code,
                    "materia": materia_code,
                    "sesiones_requeridas": req_sessions,
                    "sesiones_asignadas": assigned_sessions
                })
        
        self.logger.info("=== PROCESO DE GENERACIÓN FINALIZADO ===")
        if unresolved_classes: self.logger.warning(f"Clases con sesiones faltantes: {len(unresolved_classes)}")

        return {"stats": stats, "unresolved_classes": unresolved_classes}