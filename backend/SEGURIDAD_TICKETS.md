# Sistema de Encriptación Avanzada para Tickets

## 🔒 Características de Seguridad Implementadas

### Nivel 1: Seguridad Básica (Anterior)
- ✅ UUID4 único e imposible de adivinar
- ✅ Códigos QR únicos por ticket

### Nivel 2: Seguridad Avanzada (Nueva - AES-256 + HMAC)
- ✅ **Encriptación AES-256-CBC**: Estándar militar para proteger el UUID
- ✅ **HMAC-SHA256**: Detecta cualquier manipulación del QR
- ✅ **IV Aleatorio**: Previene patrones repetidos
- ✅ **Timestamp**: Detecta tickets expirados o clonados
- ✅ **Anti-Replay**: Verifica que el token sea el original
- ✅ **Metadata Segura**: Incluye ID del ticket, fecha de emisión y expiración

## 🛡️ ¿Por qué es "Recontra Seguro"?

### 1. El UUID nunca aparece en texto plano en el QR
Antes: `QR → "a1b2c3d4-e5f6-7890-abcd-ef1234567890"`
Ahora: `QR → "dmZLMnhRWjNhc2RmZ2hqa2xwb2l1..." (encriptado)`

### 2. Imposible de falsificar
- Incluso si alguien intercepta el QR, no puede modificarlo
- El HMAC detecta cualquier cambio de 1 bit
- Sin las claves secretas del servidor, no se puede generar un QR válido

### 3. Anti-clonación mejorada
- Cada ticket tiene un token único encriptado
- El sistema verifica que el token escaneado sea exactamente el almacenado
- Si alguien copia el QR, se detecta como "TOKEN CLONADO"

### 4. Expiración automática
- Los tokens tienen fecha de expiración (default: 1 año)
- Después de esa fecha, el QR deja de funcionar

## 📦 Instalación

### Paso 1: Instalar la nueva dependencia

```bash
cd backend
pip install -r requirements.txt
```

Esto instalará `cryptography==42.0.8`

### Paso 2: Generar claves secretas para producción

**IMPORTANTE**: Las claves por defecto son solo para desarrollo. Para producción, genera claves únicas:

```bash
# Generar clave de encriptación
python -c "import secrets; print('TICKET_ENCRYPTION_KEY=' + secrets.token_hex(32))"

# Generar clave HMAC
python -c "import secrets; print('TICKET_HMAC_KEY=' + secrets.token_hex(32))"
```

### Paso 3: Configurar variables de entorno

Crea o edita el archivo `.env` en `backend/`:

```env
# Claves de encriptación (MANTENER SECRETAS)
TICKET_ENCRYPTION_KEY=tu_clave_generada_aqui_64_caracteres_hex
TICKET_HMAC_KEY=tu_otra_clave_generada_aqui_64_caracteres_hex
```

⚠️ **CRÍTICO**: 
- Nunca compartas estas claves
- No las subas a Git
- Usa claves diferentes en desarrollo y producción
- Si se pierden las claves, los QR antiguos no podrán leerse

### Paso 4: Aplicar migraciones

```bash
python manage.py migrate
```

## 🔄 Compatibilidad con Tickets Antiguos

El sistema mantiene **compatibilidad completa** con tickets existentes:

- **Tickets nuevos**: Usan encriptación AES-256 + HMAC
- **Tickets antiguos**: Siguen funcionando con UUID plano
- **Migración gradual**: Los tickets se actualizan automáticamente

## 🧪 Prueba de Seguridad

### Probar encriptación/desencriptación:

```python
# En Django shell
python manage.py shell

from config.encryption import ticket_encryption
import uuid

# Generar un UUID de prueba
test_uuid = uuid.uuid4()

# Encriptar
token = ticket_encryption.encrypt_ticket_data(test_uuid, ticket_id=123)
print(f"Token encriptado: {token}")

# Desencriptar
payload = ticket_encryption.decrypt_ticket_data(token)
print(f"UUID recuperado: {payload['uuid']}")
print(f"Fecha emisión: {payload['issued_at']}")
print(f"Fecha expiración: {payload['expires_at']}")
```

### Probar manipulación (debe fallar):

```python
# Intentar modificar el token
token_manipulado = token[:-5] + "XXXXX"
try:
    ticket_encryption.decrypt_ticket_data(token_manipulado)
except ValueError as e:
    print(f"✅ Manipulación detectada: {e}")
```

## 📊 Formato del Token Encriptado

```
[IV: 16 bytes][Datos Encriptados: variable][HMAC: 32 bytes]
                        ↓
              Base64URL Encoding
                        ↓
              Token final para QR
```

### Estructura del payload (antes de encriptar):
```json
{
  "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "id": 123,
  "issued_at": "2026-02-15T10:30:00",
  "expires_at": "2027-02-15T10:30:00",
  "version": "2"
}
```

## 🚀 Uso en Producción

### Al crear una venta:
```python
# En services.py - Ya implementado
qr_file, token_encriptado = QRCodeService.generar_qr(
    codigo_uuid=ticket.codigo_uuid,
    ticket_id=ticket.id,
    usar_encriptacion=True  # ← Activa encriptación
)
```

### Al validar un ticket:
```python
# El endpoint /api/validaciones/validar/ detecta automáticamente
# si el QR es encriptado o UUID plano
POST /api/validaciones/validar/
{
  "codigo_uuid": "TOKEN_ENCRIPTADO_O_UUID"
}
```

## 🔍 Ventajas vs Otras Soluciones

| Característica | UUID Solo | JWT | AES-256 + HMAC (Nuestra) |
|----------------|-----------|-----|---------------------------|
| UUID protegido | ❌ | ⚠️ | ✅ |
| Detección manipulación | ❌ | ✅ | ✅ |
| Expiración | ❌ | ✅ | ✅ |
| Metadata segura | ❌ | ⚠️ | ✅ |
| No requiere librería externa | ✅ | ❌ | ❌ |
| Estándar militar | ❌ | ❌ | ✅ |
| Tamaño QR | Pequeño | Medio | Medio |

## 📝 Logs de Seguridad

El sistema registra:
- Método usado: `ENCRIPTADO_AES256` o `UUID_PLANO`
- Intentos de clonación
- Tokens manipulados
- Validaciones exitosas

## 🆘 Solución de Problemas

### Error: "TICKET_ENCRYPTION_KEY no está configurada"
**Solución**: Agrega las claves en `settings.py` o `.env`

### Error: "Token inválido: HMAC inválido"
**Causa**: El QR fue modificado o las claves cambiaron
**Solución**: El QR es falso, denegar acceso

### Error: "Token expirado"
**Causa**: El QR tiene más de 1 año (o el tiempo configurado)
**Solución**: Contactar al cliente para reemisión

### Tickets antiguos no funcionan
**Verificar**: El sistema debe aceptar UUID plano (fallback)
**Revisar**: Logs del servidor para ver el error exacto

## 🔐 Mejores Prácticas

1. **Rotar claves cada 6-12 meses** (requiere reemitir tickets)
2. **Monitorear intentos de clonación** en logs
3. **Auditar validaciones sospechosas** (múltiples intentos fallidos)
4. **Backup de claves** en lugar seguro (no Git)
5. **Usar HTTPS** siempre en producción

## 📚 Referencias

- [AES Specification (FIPS-197)](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf)
- [HMAC RFC 2104](https://datatracker.ietf.org/doc/html/rfc2104)
- [Cryptography Library](https://cryptography.io/)
