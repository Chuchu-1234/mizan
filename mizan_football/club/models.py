from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('coach', 'Coach'),
        ('agent', 'Agent'),
        ('player', 'Player'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def is_admin(self):
        return self.role == 'admin'
    
    def is_coach(self):
        return self.role == 'coach'

    def is_agent(self):
        return self.role == 'agent'

    def is_player(self):
        return self.role == 'player'

# Create your models here.
