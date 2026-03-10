"""
Señales para eventos
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Evento


@receiver(post_save, sender=Evento)
def desactivar_asignaciones_validadores(sender, instance, **kwargs):
    """
    Cuando un evento se desactiva, desactiva todas las asignaciones de validadores
    """
    if not instance.activo:
        from apps.usuarios.models import ValidadorEvento
        
        # Desactivar todas las asignaciones de este evento
        ValidadorEvento.objects.filter(
            evento=instance,
            activo=True
        ).update(activo=False)
