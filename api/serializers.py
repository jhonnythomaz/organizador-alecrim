# api/serializers.py
from rest_framework import serializers
from .models import Pagamento, Categoria, Cliente, User

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nome_empresa']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descricao']

class PagamentoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='status_calculado', read_only=True)
    
    class Meta:
        model = Pagamento
        fields = [
            'id', 'descricao', 'valor', 'data_competencia', 'data_vencimento', 
            'data_pagamento', 'status', 'status_display', 'numero_nota_fiscal', 
            'categoria', 'categoria_nome', 'data_criacao'
        ]