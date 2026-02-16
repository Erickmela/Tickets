# Generated manually for encryption upgrade

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='token_encriptado',
            field=models.TextField(blank=True, help_text='Token con UUID encriptado usando AES-256 + HMAC para máxima seguridad', verbose_name='Token Encriptado'),
        ),
    ]
