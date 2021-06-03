from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=255)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class ForgotPassword(models.Model):

    email = models.EmailField(max_length=150)
    code = models.IntegerField()
    is_used = models.BooleanField(default=False)
    change_code = models.IntegerField(null=True)

    #meta class
    class Meta:
        db_table = "forgot_password"



class Categories(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Tags(models.Model):
    tag = models.CharField(max_length=255)

    def __str__(self):
        return self.tag

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    category = models.ForeignKey(Categories,on_delete=models.CASCADE,null=True)
    tags = models.ManyToManyField(Tags,blank=True)
    image = models.URLField()

    def __str__(self):
        return self.product_name



class BlacklistedAccessTokens(models.Model):
    token = models.TextField()

