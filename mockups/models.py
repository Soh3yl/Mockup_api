from django.db import models
from django.contrib.auth.models import User

class Mockup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mockups')
    text = models.CharField(max_length=255)
    font = models.CharField(max_length=50, default='arial')
    text_color = models.CharField(max_length=20, default='#000000')
    shirt_color = models.CharField(max_length=20, default='white')
    image = models.ImageField(upload_to='mockups/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.text[:20]}"
