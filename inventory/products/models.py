from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
# Create your models here.
# from rest_framework_simplejwt.tokens import RefreshToken

from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, username, email, phonenumber, password=None):
        if username is None:
            raise TypeError('Users should have a username')
        if email is None:
            raise TypeError('Users should have a Email')
        if phonenumber is None:
            raise TypeError('Users should have a phonenumber')

        user = self.model(username=username, phonenumber=phonenumber, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    firstName = models.CharField(max_length=255, db_column='first_name', null=True, blank=True)
    lastName = models.CharField(max_length=255, db_column='last_name', null=True, blank=True)
    email = models.EmailField(max_length=255, db_column='email', unique=True, null=True, blank=True)
    gender = models.CharField(max_length=255, db_column='gender', null=True, blank=True)
    age = models.IntegerField(max_length=255, db_column='age', null=True, blank=True)
    address = models.CharField(max_length=255, db_column='address', null=True, blank=True)
    created_date = models.DateTimeField(db_column='created_date', default=timezone.now)
    updated_date = models.DateTimeField(db_column='updated_date', default=timezone.now)
   
    USERNAME_FIELD = 'email'
   

    objects = UserManager()

    def __str__(self):
        return self.email

    # def tokens(self):
    #     refresh = RefreshToken.for_user(self)
    #     return {
    #         'refresh': str(refresh),
    #         'access': str(refresh.access_token)
    #     }


class AuthUsers(models.Model):
    firstName = models.CharField(max_length=255, db_column='first_name', null=True, blank=True)
    lastName = models.CharField(max_length=255, db_column='last_name', null=True, blank=True)
    email = models.EmailField(max_length=255, db_column='email', unique=True, null=True, blank=True)
    gender = models.CharField(max_length=255, db_column='gender', null=True, blank=True)
    age = models.IntegerField(max_length=255, db_column='age', null=True, blank=True)
    address = models.CharField(max_length=255, db_column='address', null=True, blank=True)

    # created_date = models.DateTimeField(db_column='created_date', default=timezone.now)
    # updated_date = models.DateTimeField(db_column='updated_date', default=timezone.now)



    #
    def __str__(self):
        return str(self.firstName)
      
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
