# Generated by Django 4.0.2 on 2022-02-25 20:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=18, verbose_name='审批流程名')),
                ('step', models.IntegerField(verbose_name='节点序号')),
                ('step_name', models.CharField(max_length=18, verbose_name='节点名称')),
                ('username', models.CharField(blank=True, max_length=18, null=True, verbose_name='审批人')),
            ],
            options={
                'verbose_name': '审批流程',
                'verbose_name_plural': '审批流程',
            },
        ),
        migrations.CreateModel(
            name='ProcessLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(max_length=32, verbose_name='表单ID')),
                ('type', models.CharField(max_length=18, verbose_name='表单类型')),
                ('step', models.IntegerField(verbose_name='节点序号')),
                ('step_name', models.CharField(max_length=18, verbose_name='节点名称')),
                ('username', models.CharField(max_length=18, verbose_name='审批人')),
                ('result', models.IntegerField(default=1, verbose_name='审核结果')),
                ('remark', models.CharField(blank=True, max_length=64, null=True, verbose_name='审核备注')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='审核时间')),
            ],
            options={
                'verbose_name': '审批记录表',
                'verbose_name_plural': '审批记录表',
            },
        ),
    ]
