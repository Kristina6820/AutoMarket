from django.db.models import * 
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.




class Brand(Model):
    Name = CharField(max_length=50)


class Type(Model):   
    Name = CharField(max_length=50)


class Car(Model):  
    Name = CharField(max_length=50)         
    Description = TextField()
    Price = DecimalField(max_digits=10, decimal_places=3)
    Type = CharField(max_length=50)
    Image = ImageField(upload_to="cars/")       
    Reviews = ForeignKey('Review', on_delete=DO_NOTHING, null=True, blank=True)
    CreatedAt = DateTimeField(auto_now_add=True)
    Year = IntegerField(default=20, null=True,blank=True)
    Km = IntegerField(default=20, null=True, blank=True)         
    Fuel = CharField(max_length=20, default="Diesel")  
    Transmission = CharField(max_length=20, default="Manuala")  
    HorsePower = IntegerField(default=90)   
    Power = IntegerField(default=20, null=True, blank=True)
    Tractor = CharField(max_length=20, null=True, blank=True) 


def get_absolute_url(self):
        from django.urls import reverse
        return reverse('car_details', args=[self.id])

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "car")

    def __str__(self):
        return f"{self.user} ❤ {self.car}"




class MasinaImage(Model):
    masina = ForeignKey(Car, on_delete= CASCADE, related_name="poze")
    imagine = ImageField(upload_to="cars/")


class User(AbstractUser):
    FullName = models.CharField(max_length=50, blank=True, null=True)
    Phone = models.CharField(max_length=50, blank=True, null=True)

    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
   


class Shipment(Model):
    TrackNumber = CharField(max_length=50)
    Product = CharField(max_length=100)
    

class Order(Model):
    User = ForeignKey(User, on_delete= DO_NOTHING)
    CreatedAt = DateTimeField()
    IBAN = CharField(max_length=34)
    PaymentDate = DateField()
    Method = CharField(max_length=20)
    Quantity = IntegerField()
    Shipment = ForeignKey(Shipment, on_delete= DO_NOTHING)
    Item = ForeignKey(Car, on_delete= DO_NOTHING)


class Review(Model):
    User = ForeignKey(User, on_delete= DO_NOTHING)
    CreatedAt = DateTimeField()
    Rating = IntegerField()
    Comment = TextField()
