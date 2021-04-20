from django.db import models

class Section(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    progress = models.TextField()
    beginner = models.TextField()

class User(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=9)
    image = models.ImageField(upload_to='uploads/%Y/%m/%d')
    role = models.PositiveSmallIntegerField()
    sections = models.ManyToManyField(Section, blank=True)

class Account(models.Model):
    login = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=56)
    salt = models.CharField(max_length=32)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

class Lesson(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.CharField(max_length=200)
    coach = models.ForeignKey(User, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)