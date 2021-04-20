# Generated by Django 3.1.2 on 2020-11-19 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('title_description', models.CharField(max_length=165)),
                ('description', models.TextField()),
                ('title_progress', models.CharField(max_length=165)),
                ('progress', models.TextField()),
                ('title_beginner', models.CharField(max_length=165)),
                ('beginner', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('surname', models.CharField(max_length=50)),
                ('middle_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=9)),
                ('image', models.ImageField(upload_to='uploads/%Y/%m/%d')),
                ('role', models.PositiveSmallIntegerField()),
                ('sections', models.ManyToManyField(blank=True, to='mainapp.Section')),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('login', models.CharField(max_length=20, unique=True)),
                ('password', models.CharField(max_length=56)),
                ('salt', models.CharField(max_length=32)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='mainapp.user')),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('description', models.CharField(max_length=200)),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.user')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.section')),
            ],
        ),
    ]