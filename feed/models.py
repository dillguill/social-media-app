from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Post(models.Model):
    text = models.CharField(max_length=240)
    date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to='posts/', null=True, blank=True)

    def __str__(self):
        return self.text[0:100]