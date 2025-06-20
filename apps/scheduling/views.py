# apps/scheduling/views.py

from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
import logging

from .models import Grupos, BloquesHorariosDefinicion, DisponibilidadDocentes, HorariosAsignados, ConfiguracionRestricciones
from apps.academic_setup.models import PeriodoAcademico

from .serializers import (
    GruposSerializer, BloquesHorariosDefinicionSerializer, DisponibilidadDocentesSerializer,
    HorariosAsignadosSerializer, ConfiguracionRestriccionesSerializer
)
# Importar el servicio
from .service.schedule_generator import ScheduleGeneratorService

logger = logging.getLogger(__name__)


class GruposViewSet(viewsets.ModelViewSet):
    # Usamos prefetch_related para la relación ManyToMany 'materias'
    queryset = Grupos.objects.prefetch_related('materias').select_related('carrera', 'periodo', 'docente_asignado_directamente').all()
    
    serializer_class = GruposSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]

    # Se quita el campo 'materia' y se reemplaza por 'materias'
    filterset_fields = ['periodo', 'carrera', 'ciclo_semestral', 'materias']


class BloquesHorariosDefinicionViewSet(viewsets.ModelViewSet):
    queryset = BloquesHorariosDefinicion.objects.all()
    serializer_class = BloquesHorariosDefinicionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['turno', 'dia_semana']


class DisponibilidadDocentesViewSet(viewsets.ModelViewSet):
    queryset = DisponibilidadDocentes.objects.select_related('docente', 'periodo', 'bloque_horario').all()
    serializer_class = DisponibilidadDocentesSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['docente', 'periodo', 'dia_semana', 'esta_disponible']

    @action(detail=False, methods=['post'], url_path='cargar-disponibilidad-excel')
    def cargar_disponibilidad_excel(self, request):
        return Response({"message": "Funcionalidad de carga Excel pendiente de implementación."}, status=status.HTTP_501_NOT_IMPLEMENTED)


class HorariosAsignadosViewSet(viewsets.ModelViewSet):
    # La relación con materia ahora es directa, no a través de grupo.
    queryset = HorariosAsignados.objects.select_related(
        'grupo', 'materia', 'docente', 'espacio', 'periodo', 'bloque_horario'
    ).all()

    serializer_class = HorariosAsignadosSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    
    # Se quita 'grupo__materia' y se usa 'materia' directamente.
    filterset_fields = ['periodo', 'docente', 'espacio', 'grupo', 'materia', 'grupo__carrera', 'dia_semana']


class ConfiguracionRestriccionesViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionRestricciones.objects.select_related('periodo_aplicable').all()
    serializer_class = ConfiguracionRestriccionesSerializer
    permission_classes = [AllowAny]


class GeneracionHorarioView(viewsets.ViewSet):
    permission_classes = [AllowAny] 

    @action(detail=False, methods=['post'], url_path='generar-horario-automatico')
    def generar_horario(self, request):
        periodo_id = request.data.get('periodo_id')
        if not periodo_id:
            return Response({"error": "Se requiere el ID del período académico."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = get_object_or_404(PeriodoAcademico, pk=periodo_id)
            logger.info(f"Iniciando generación para periodo_id: {periodo_id}")

            generator_service = ScheduleGeneratorService(periodo=periodo, stdout_ref=logger)
            resultado = generator_service.generar_horarios_automaticos()
            
            logger.info(f"Generación para periodo_id: {periodo_id} completada. Stats: {resultado.get('stats')}")
            return Response({
                "message": f"Proceso de generación de horarios para {periodo.nombre_periodo} completado.",
                "stats": resultado.get('stats', {}),
                "unresolved_classes": resultado.get('unresolved_classes', [])
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error catastrófico en generación de horario para periodo_id {periodo_id}: {str(e)}", exc_info=True)
            return Response({"error": f"Ocurrió un error crítico durante la generación: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='exportar-horarios-excel')
    def exportar_horarios(self, request):
        return Response({"message": "Funcionalidad de exportación a Excel pendiente de implementación."}, status=status.HTTP_501_NOT_IMPLEMENTED)