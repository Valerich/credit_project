# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-25 07:18
from __future__ import unicode_literals

import credit_project.loans.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Borrower',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Создана')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Изменена')),
                ('last_name', models.CharField(max_length=255, verbose_name='Фамилия')),
                ('first_name', models.CharField(max_length=255, verbose_name='Имя')),
                ('middle_name', models.CharField(max_length=255, verbose_name='Отчество')),
                ('birth_date', models.DateField(verbose_name='Дата рождения')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, verbose_name='Номер телефона')),
                ('passport_number', models.CharField(max_length=10, validators=[credit_project.loans.validators.validate_passport_number], verbose_name='Номер паспорта')),
                ('score', models.PositiveSmallIntegerField(verbose_name='Скоринговый балл')),
            ],
            options={
                'verbose_name': 'Анкета клиента',
                'verbose_name_plural': 'Анкеты клиентов',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('kind', models.CharField(choices=[('credit_organization', 'Кредитная организация'), ('partner', 'Партнер')], max_length=20, verbose_name='Тип организации')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Компания',
                'verbose_name_plural': 'Компании',
            },
        ),
        migrations.CreateModel(
            name='CreditRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('new', 'Новая'), ('sent', 'Отправлена'), ('received', 'Получена'), ('approved', 'Одобрено'), ('denied', 'Отказано'), ('issued', 'Выдано')], max_length=20, verbose_name='Статус')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Создана')),
                ('sent_date', models.DateTimeField(blank=True, null=True, verbose_name='Отправлена')),
                ('borrower', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='loans.Borrower', verbose_name='Анкета клиента')),
            ],
            options={
                'verbose_name': 'Заявка в КО',
                'verbose_name_plural': 'Заявки в КО',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Изменено')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('rotation_start', models.DateTimeField(verbose_name='Начало ротации')),
                ('rotation_end', models.DateTimeField(verbose_name='Окончание ротации')),
                ('kind', models.CharField(choices=[('consumer_credit', 'Потребительский кредит'), ('mortgage', 'Ипотека'), ('car_loan', 'Автокредит')], max_length=20, verbose_name='Тип предложения')),
                ('min_score', models.PositiveSmallIntegerField(verbose_name='Минимальный скоринговый балл')),
                ('max_score', models.PositiveSmallIntegerField(verbose_name='Максимальный скоринговый балл')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='loans.Company', verbose_name='Кредитная организация')),
            ],
            options={
                'verbose_name': 'Предложение',
                'verbose_name_plural': 'Предложения',
                'ordering': ('-created',),
            },
        ),
        migrations.AddField(
            model_name='creditrequest',
            name='offer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='loans.Offer', verbose_name='Предложение'),
        ),
        migrations.AddField(
            model_name='borrower',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='loans.Company', verbose_name='Партнер'),
        ),
    ]
