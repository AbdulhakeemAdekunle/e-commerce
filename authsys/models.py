from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


# create a customized user model that inherits from django's abstract user model,
# keeping all its default fields while customizing only the email field.
class User(AbstractUser):
    email = models.EmailField(unique=True)