# Generated by Django 3.2.6 on 2022-02-17 20:44

import application.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('archive', '0001_initial'),
        ('parts', '0001_initial'),
        ('process', '0001_initial'),
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('app_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('app_no', models.CharField(default=application.models.create_appno, max_length=20, unique=True, verbose_name='申请单号')),
                ('description', models.CharField(max_length=256, verbose_name='申请说明')),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=application.models.upload_to, verbose_name='申请文件')),
                ('bom', models.FileField(blank=True, max_length=255, null=True, upload_to=application.models.upload_to, verbose_name='申请文件清单')),
                ('username', models.CharField(max_length=18, verbose_name='申请人')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='申请时间')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='archive.product', verbose_name='产品名称')),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='process.process', verbose_name='审批流程')),
            ],
            options={
                'verbose_name': '图纸申请单',
                'verbose_name_plural': '图纸申请单',
            },
        ),
        migrations.CreateModel(
            name='ApplicationBom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sn', models.CharField(max_length=60, null=True, verbose_name='序号')),
                ('code', models.CharField(max_length=60, null=True, verbose_name='编码')),
                ('draw', models.CharField(max_length=50, null=True, verbose_name='图号')),
                ('name', models.CharField(max_length=50, null=True, verbose_name='名称')),
                ('is_download', models.IntegerField(default=0, verbose_name='下载')),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='application.application', verbose_name='申请单号')),
                ('file', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='files.ssfile', verbose_name='图纸')),
                ('part', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='parts.partcode', verbose_name='物料')),
            ],
            options={
                'verbose_name': '图纸申请明细',
                'verbose_name_plural': '图纸申请明细',
            },
        ),
    ]
