# api/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.db.models import Sum, Q

from django_filters.rest_framework import DjangoFilterBackend

from .models import Pagamento, Categoria, Cliente
from .serializers import PagamentoSerializer, CategoriaSerializer, ClienteSerializer
from .filters import PagamentoFilter

def get_cliente_from_request(request):
    user = request.user
    if user.is_superuser and request.headers.get('X-Cliente-Gerenciado-Id'):
        try:
            cliente_id = int(request.headers.get('X-Cliente-Gerenciado-Id'))
            return Cliente.objects.get(id=cliente_id)
        except (ValueError, Cliente.DoesNotExist):
            return user.perfilusuario.cliente
    return user.perfilusuario.cliente

class CategoriaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CategoriaSerializer

    def get_queryset(self):
        cliente = get_cliente_from_request(self.request)
        return Categoria.objects.filter(cliente=cliente)

    def perform_create(self, serializer):
        cliente = get_cliente_from_request(self.request)
        serializer.save(cliente=cliente)

class PagamentoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PagamentoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PagamentoFilter

    def get_queryset(self):
        cliente = get_cliente_from_request(self.request)
        return Pagamento.objects.filter(cliente=cliente)

    def perform_create(self, serializer):
        cliente = get_cliente_from_request(self.request)
        serializer.save(cliente=cliente)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        agregados = queryset.aggregate(
            total_pago=Sum('valor', filter=Q(status='Pago')),
            # Para o total pendente e atrasado, usamos a propriedade 'status_calculado'
            # Isso é mais complexo com aggregate, então vamos simplificar por agora
            # e calcular no frontend. O importante é o filtro funcionar.
        )
        
        serializer = self.get_serializer(queryset, many=True)
        # Por agora, retornamos apenas a lista. Os totais serão calculados no frontend.
        return Response(serializer.data)


class ClienteAdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cliente.objects.all().order_by('nome_empresa')
    serializer_class = ClienteSerializer
    permission_classes = [IsAdminUser]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_superuser': user.is_superuser,
        'cliente_id': user.perfilusuario.cliente.id if hasattr(user, 'perfilusuario') else None
    }
    return Response(data)