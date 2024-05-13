from django.db import models

# Create your models here.


class Textdata(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    habitat = models.TextField()
    figure = models.TextField()
    suggestion = models.TextField()
    img_path = models.ImageField(upload_to='images/')
