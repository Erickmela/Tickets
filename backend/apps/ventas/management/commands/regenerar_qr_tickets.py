"""
Comando para regenerar QR codes de tickets con encriptación avanzada
Uso: python manage.py regenerar_qr_tickets
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.ventas.models import Ticket
from apps.ventas.services import QRCodeService


class Command(BaseCommand):
    help = 'Regenera los QR codes de tickets existentes con encriptación AES-256 + HMAC'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Regenerar QR de TODOS los tickets (incluso los que ya tienen token encriptado)',
        )
        parser.add_argument(
            '--ticket-id',
            type=int,
            help='Regenerar QR de un ticket específico por ID',
        )
        parser.add_argument(
            '--venta-id',
            type=int,
            help='Regenerar QR de todos los tickets de una venta específica',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('🔒 Iniciando regeneración de QR codes con encriptación avanzada...\n')
        
        # Determinar qué tickets procesar
        if options['ticket_id']:
            tickets = Ticket.objects.filter(id=options['ticket_id'])
            if not tickets.exists():
                self.stdout.write(self.style.ERROR(f'❌ Ticket #{options["ticket_id"]} no encontrado'))
                return
        elif options['venta_id']:
            tickets = Ticket.objects.filter(venta_id=options['venta_id'])
            if not tickets.exists():
                self.stdout.write(self.style.ERROR(f'❌ No se encontraron tickets para la venta #{options["venta_id"]}'))
                return
        elif options['all']:
            tickets = Ticket.objects.all()
        else:
            # Por defecto: solo tickets sin token encriptado
            tickets = Ticket.objects.filter(token_encriptado='')
        
        total = tickets.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('⚠️  No hay tickets para procesar'))
            return
        
        self.stdout.write(f'📊 Se procesarán {total} tickets\n')
        
        confirmacion = input('¿Desea continuar? (s/n): ')
        if confirmacion.lower() != 's':
            self.stdout.write(self.style.WARNING('Operación cancelada'))
            return
        
        exitosos = 0
        fallidos = 0
        
        for ticket in tickets:
            try:
                with transaction.atomic():
                    # Regenerar QR con encriptación
                    qr_file, token_encriptado = QRCodeService.generar_qr(
                        codigo_uuid=ticket.codigo_uuid,
                        ticket_id=ticket.id,
                        usar_encriptacion=True
                    )
                    
                    # Eliminar QR anterior si existe
                    if ticket.qr_image:
                        ticket.qr_image.delete(save=False)
                    
                    # Guardar nuevo QR y token
                    ticket.qr_image.save(f'{ticket.codigo_uuid}.png', qr_file, save=False)
                    ticket.token_encriptado = token_encriptado
                    ticket.save()
                    
                    exitosos += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Ticket #{ticket.id} - {ticket.nombre_titular}')
                    )
            
            except Exception as e:
                fallidos += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ Error en Ticket #{ticket.id}: {str(e)}')
                )
        
        # Resumen
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✅ Exitosos: {exitosos}'))
        if fallidos > 0:
            self.stdout.write(self.style.ERROR(f'❌ Fallidos: {fallidos}'))
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Regeneración completada'))
        self.stdout.write('='*60)
