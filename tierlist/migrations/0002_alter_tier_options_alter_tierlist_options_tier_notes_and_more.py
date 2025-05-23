# Generated by Django 5.1.5 on 2025-03-10 11:31

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dioses', '0006_alter_ability_ability_type'),
        ('tierlist', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tier',
            options={'ordering': ['tier']},
        ),
        migrations.AlterModelOptions(
            name='tierlist',
            options={'ordering': ['-created_at'], 'verbose_name': 'Tier List', 'verbose_name_plural': 'Tier Lists'},
        ),
        migrations.AddField(
            model_name='tier',
            name='notes',
            field=models.CharField(blank=True, max_length=200, verbose_name='Notas'),
        ),
        migrations.AddField(
            model_name='tierlist',
            name='description',
            field=models.TextField(blank=True, verbose_name='Descripción'),
        ),
        migrations.AddField(
            model_name='tierlist',
            name='is_public',
            field=models.BooleanField(default=True, verbose_name='Público'),
        ),
        migrations.AddField(
            model_name='tierlist',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='tier',
            name='god',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tier_placements', to='dioses.god'),
        ),
        migrations.AlterField(
            model_name='tier',
            name='tier',
            field=models.CharField(choices=[('S', 'S Tier'), ('A', 'A Tier'), ('B', 'B Tier'), ('C', 'C Tier'), ('D', 'D Tier'), ('F', 'F Tier')], max_length=1),
        ),
        migrations.AlterField(
            model_name='tierlist',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='tierlist',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Nombre'),
        ),
        migrations.AlterField(
            model_name='tierlist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tierlists', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='TierListComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Comentario')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tierlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tierlist.tierlist')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
