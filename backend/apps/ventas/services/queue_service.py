"""
Servicio de Cola Virtual
Responsabilidad: Gestionar sala de espera para eventos de alta demanda
"""
import redis
from django.conf import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Configurar conexión Redis
# En desarrollo usa Redis local, en producción usa variable de entorno
try:
    redis_client = redis.Redis(
        host=getattr(settings, 'REDIS_HOST', 'localhost'),
        port=getattr(settings, 'REDIS_PORT', 6379),
        db=getattr(settings, 'REDIS_DB', 0),
        decode_responses=True,
        socket_connect_timeout=5
    )
    # Verificar conexión
    redis_client.ping()
    logger.info("✅ Conexión a Redis establecida")
except (redis.ConnectionError, AttributeError) as e:
    logger.warning(f"⚠️ Redis no disponible: {e}. Cola virtual desactivada.")
    redis_client = None


class VirtualQueueService:
    """
    Gestiona cola virtual para proteger el servidor en eventos de alta demanda
    
    Ejemplo de uso:
    - Evento normal: 50 usuarios → Sin cola
    - Evento popular: 500 usuarios → Cola activada, 300 usuarios activos a la vez
    """
    
    # Configuración ajustable
    MAX_CONCURRENT_USERS = 300  # Máximo comprando simultáneamente
    QUEUE_TIMEOUT = 900  # 15 minutos en cola antes de expirar
    ACTIVE_SESSION_TIMEOUT = 600  # 10 minutos para completar compra
    
    @staticmethod
    def is_redis_available():
        """Verificar si Redis está disponible"""
        if redis_client is None:
            return False
        try:
            redis_client.ping()
            return True
        except redis.ConnectionError:
            return False
    
    @staticmethod
    def is_high_demand_event(evento_slug):
        """
        Determinar si un evento tiene alta demanda
        Activa la cola si hay más de MAX_CONCURRENT_USERS comprando
        """
        if not VirtualQueueService.is_redis_available():
            return False
            
        active_key = f"queue:evento:{evento_slug}:active_users"
        active_users = redis_client.scard(active_key)
        return active_users >= VirtualQueueService.MAX_CONCURRENT_USERS
    
    @staticmethod
    def join_queue(user_id, evento_slug):
        """
        Usuario se une a la cola virtual
        Retorna posición en la cola y tiempo estimado de espera
        """
        if not VirtualQueueService.is_redis_available():
            # Si Redis no está disponible, permitir acceso directo
            return {'status': 'active', 'redis_unavailable': True}
        
        # Verificar si ya está activo (puede comprar)
        if VirtualQueueService.is_user_active(user_id, evento_slug):
            return {'status': 'active', 'position': 0}
        
        # Agregar a la cola con timestamp
        queue_key = f"queue:evento:{evento_slug}"
        timestamp = datetime.now().timestamp()
        redis_client.zadd(queue_key, {str(user_id): timestamp})
        
        # Establecer expiración de la cola (limpieza automática)
        redis_client.expire(queue_key, VirtualQueueService.QUEUE_TIMEOUT)
        
        # Obtener posición en la cola (0-indexed, sumar 1)
        position = redis_client.zrank(queue_key, str(user_id))
        if position is None:
            position = 0
        else:
            position += 1
        
        # Calcular tiempo estimado (2 segundos por persona)
        estimated_wait = position * 2
        
        return {
            'status': 'waiting',
            'position': position,
            'estimated_wait': estimated_wait,
            'total_in_queue': redis_client.zcard(queue_key)
        }
    
    @staticmethod
    def activate_user(user_id, evento_slug):
        """
        Activar usuario para que pueda comprar (sale de la cola)
        """
        if not VirtualQueueService.is_redis_available():
            return True
            
        queue_key = f"queue:evento:{evento_slug}"
        active_key = f"queue:evento:{evento_slug}:active_users"
        
        # Remover de la cola
        redis_client.zrem(queue_key, str(user_id))
        
        # Agregar a usuarios activos con expiración
        redis_client.sadd(active_key, str(user_id))
        redis_client.expire(active_key, VirtualQueueService.ACTIVE_SESSION_TIMEOUT)
        
        logger.info(f"Usuario {user_id} activado para evento {evento_slug}")
        return True
    
    @staticmethod
    def is_user_active(user_id, evento_slug):
        """
        Verificar si el usuario está activo (puede comprar)
        """
        if not VirtualQueueService.is_redis_available():
            return True  # Permitir si Redis no está disponible
            
        active_key = f"queue:evento:{evento_slug}:active_users"
        return redis_client.sismember(active_key, str(user_id))
    
    @staticmethod
    def get_queue_position(user_id, evento_slug):
        """
        Obtener posición actual del usuario en la cola
        """
        if not VirtualQueueService.is_redis_available():
            return {'status': 'active', 'redis_unavailable': True}
            
        # Verificar si está activo
        if VirtualQueueService.is_user_active(user_id, evento_slug):
            return {'status': 'active', 'position': 0}
        
        # Verificar si está en cola
        queue_key = f"queue:evento:{evento_slug}"
        position = redis_client.zrank(queue_key, str(user_id))
        
        if position is None:
            # No está en la cola, debe unirse
            return {'status': 'not_in_queue'}
        
        position += 1  # Convertir de 0-indexed a 1-indexed
        estimated_wait = position * 2
        
        return {
            'status': 'waiting',
            'position': position,
            'estimated_wait': estimated_wait,
            'total_in_queue': redis_client.zcard(queue_key)
        }
    
    @staticmethod
    def process_queue(evento_slug):
        """
        Procesar cola: activar usuarios hasta el límite
        Este método se puede llamar periódicamente o cuando un usuario termina
        """
        if not VirtualQueueService.is_redis_available():
            return 0
            
        queue_key = f"queue:evento:{evento_slug}"
        active_key = f"queue:evento:{evento_slug}:active_users"
        
        # Obtener usuarios activos actuales
        current_active = redis_client.scard(active_key)
        slots_available = VirtualQueueService.MAX_CONCURRENT_USERS - current_active
        
        if slots_available > 0:
            # Obtener los primeros N usuarios de la cola
            next_users = redis_client.zrange(queue_key, 0, slots_available - 1)
            
            for user_id in next_users:
                VirtualQueueService.activate_user(user_id, evento_slug)
            
            logger.info(f"Activados {len(next_users)} usuarios para {evento_slug}")
            return len(next_users)
        
        return 0
    
    @staticmethod
    def bypass_queue_for_staff(user):
        """
        ADMIN, VALIDADOR y VENDEDOR saltean la cola
        """
        if not hasattr(user, 'rol'):
            return False
        return user.rol in ['ADMIN', 'VALIDADOR', 'VENDEDOR']
    
    @staticmethod
    def deactivate_user(user_id, evento_slug):
        """
        Remover usuario de activos (cuando termina o abandona la compra)
        Automáticamente procesa la cola para activar al siguiente
        """
        if not VirtualQueueService.is_redis_available():
            return
            
        active_key = f"queue:evento:{evento_slug}:active_users"
        redis_client.srem(active_key, str(user_id))
        
        # Procesar cola para activar al siguiente
        VirtualQueueService.process_queue(evento_slug)
    
    @staticmethod
    def clear_queue(evento_slug):
        """
        Limpiar toda la cola de un evento (útil para testing o mantenimiento)
        """
        if not VirtualQueueService.is_redis_available():
            return
            
        queue_key = f"queue:evento:{evento_slug}"
        active_key = f"queue:evento:{evento_slug}:active_users"
        
        redis_client.delete(queue_key)
        redis_client.delete(active_key)
        logger.info(f"Cola limpiada para evento {evento_slug}")
    
    @staticmethod
    def get_queue_stats(evento_slug):
        """
        Obtener estadísticas de la cola (para admin/monitoreo)
        """
        if not VirtualQueueService.is_redis_available():
            return {'redis_available': False}
            
        queue_key = f"queue:evento:{evento_slug}"
        active_key = f"queue:evento:{evento_slug}:active_users"
        
        return {
            'redis_available': True,
            'users_in_queue': redis_client.zcard(queue_key),
            'active_users': redis_client.scard(active_key),
            'max_concurrent': VirtualQueueService.MAX_CONCURRENT_USERS,
            'slots_available': VirtualQueueService.MAX_CONCURRENT_USERS - redis_client.scard(active_key),
            'is_high_demand': VirtualQueueService.is_high_demand_event(evento_slug)
        }
