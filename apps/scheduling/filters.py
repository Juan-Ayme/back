# apps/scheduling/filters.py
import django_filters
from .models import Grupos

class GruposFilter(django_filters.FilterSet):
    # Este filtro permite buscar grupos que contengan una materia específica por su ID.
    # Ejemplo de uso en la URL: /api/scheduling/grupos/?materias=15
    materias = django_filters.NumberFilter(field_name='materias', lookup_expr='exact')

    class Meta:
        model = Grupos
        fields = ['carrera', 'periodo', 'ciclo_semestral', 'materias']