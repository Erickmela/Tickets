"""
Serializer minimalista para select de eventos
Responsabilidad: Retornar solo campos esenciales para dropdowns
"""
from rest_framework import serializers
from apps.eventos.models import Evento
from config.hashid_utils import encode_id


class EventoSelectSerializer(serializers.ModelSerializer):
    """
    Serializer ultra ligero para selects
    Solo retorna: id, encoded_id, nombre
    """
    encoded_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Evento
        fields = ['id', 'encoded_id', 'nombre']
        read_only_fields = ['id']
    
    def get_encoded_id(self, obj):
        """Retornar ID encriptado"""
        return encode_id(obj.id)
