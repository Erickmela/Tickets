"""
Servicio de Reconciliación de Carritos
Responsabilidad: Reconciliar carritos duplicados cuando hay un rechazo de pago
"""
import logging
from typing import List
from django.db import transaction

from apps.ventas.models import Carrito, CarritoItem

logger = logging.getLogger(__name__)


class CartReconciliationService:
    """
    Servicio para reconciliar carritos cuando hay un rechazo de pago
    Fusiona carritos duplicados del mismo cliente
    """
    
    def reconcile_for_customer(self, canonical_cart: Carrito) -> None:
        """
        Reconciliar carritos cuando hay un rechazo de pago
        
        Args:
            canonical_cart: Carrito principal (canónico) a mantener
        """
        other_carts = self._find_duplicate_carts(canonical_cart)
        
        if not other_carts.exists():
            logger.info("No hay carritos duplicados para reconciliar")
            return
        
        for other_cart in other_carts:
            self.reconcile_carts(canonical_cart.id, other_cart.id)
        
        logger.info(f"Reconciliación completada para {other_carts.count()} carritos")
    
    def _find_duplicate_carts(self, canonical_cart: Carrito):
        """
        Buscar carritos duplicados del mismo cliente
        
        Args:
            canonical_cart: Carrito canónico
            
        Returns:
            QuerySet de carritos duplicados
        """
        return Carrito.objects.filter(
            cliente=canonical_cart.cliente,
            activo=True
        ).exclude(id=canonical_cart.id)
    
    @transaction.atomic
    def reconcile_carts(self, canonical_id: int, other_id: int) -> None:
        """
        Reconciliar dos carritos
        Mover items únicos del other_id al canonical_id e ignorar duplicados
        
        Args:
            canonical_id: ID del carrito canónico (a mantener)
            other_id: ID del carrito a fusionar
        """
        moved_items = 0
        duplicate_items = 0
        
        other_items = CarritoItem.objects.filter(carrito_id=other_id)
        
        for item in other_items:
            if self._item_exists_in_cart(canonical_id, item.zona_id):
                # Item duplicado, eliminarlo
                item.delete()
                duplicate_items += 1
            else:
                # Item único, moverlo al carrito canónico
                item.carrito_id = canonical_id
                item.save()
                moved_items += 1
        
        # Marcar carrito como inactivo
        Carrito.objects.filter(id=other_id).update(activo=False)
        
        logger.info(
            f"Carritos reconciliados: {moved_items} items movidos, "
            f"{duplicate_items} duplicados eliminados"
        )
    
    def _item_exists_in_cart(self, cart_id: int, zona_id: int) -> bool:
        """
        Verificar si un item existe en el carrito
        
        Args:
            cart_id: ID del carrito
            zona_id: ID de la zona
            
        Returns:
            True si el item ya existe en el carrito
        """
        return CarritoItem.objects.filter(
            carrito_id=cart_id,
            zona_id=zona_id
        ).exists()
