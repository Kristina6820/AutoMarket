from django.db.models import * 
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    FullName = models.CharField(max_length=50, blank=True, null=True)
    Phone = models.CharField(max_length=50, blank=True, null=True)

    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


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
    Power = IntegerField(null=True, blank=True)
    Tractor = CharField(max_length=20, null=True, blank=True) 


    def get_absolute_url(self):
            from django.urls import reverse
            return reverse('car_details', args=[self.id])

class Favorite(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    car = ForeignKey(Car, on_delete=CASCADE)

    #class Meta:
    #unique_together = ("user", "car")

    def __str__(self):
        return f"{self.user} ❤ {self.car}"




class MasinaImage(Model):
    masina = ForeignKey(Car, on_delete= CASCADE, related_name="poze")
    imagine = ImageField(upload_to="cars/")



   


class Shipment(models.Model):
    TrackNumber = models.CharField(max_length=50, unique=True)
    Carrier = models.CharField(max_length=50, default="Fan Courier")
    Status = models.CharField(max_length=100, default="În tranzit")
    EstimatedArrival = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.TrackNumber} — {self.Status}"

    

class Order(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Item = models.ForeignKey(Car, on_delete=models.CASCADE)
    Shipment = models.ForeignKey(Shipment, on_delete=models.SET_NULL, null=True, blank=True)

    CreatedAt = models.DateTimeField(auto_now_add=True)
    PaymentDate = models.DateField(null=True, blank=True)

    Method = models.CharField(max_length=30, default="Transfer bancar")
    IBAN = models.CharField(max_length=34, blank=True)
    Quantity = models.IntegerField(default=1)

    Status = models.CharField(max_length=50, default="Procesare")

    def __str__(self):
        return f"Comanda #{self.id}"



class Review(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="reviews")

    CreatedAt = models.DateTimeField(auto_now_add=True)
    Rating = models.IntegerField(default=5)
    Comment = models.TextField()

    def __str__(self):
        return f"{self.User.email} — {self.Rating}★"

