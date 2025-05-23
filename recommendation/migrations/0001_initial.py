# Generated by Django 5.1.7 on 2025-04-12 15:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('books', '0013_alter_book_description'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Hozzáadás dátuma')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlisted', to='books.book', verbose_name='Könyv')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_item', to=settings.AUTH_USER_MODEL, verbose_name='Felhasználó')),
            ],
            options={
                'verbose_name': 'Kívánságlista Elem',
                'verbose_name_plural': 'Kívánságlista Elemek',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'book')},
            },
        ),
    ]
