from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User 
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .models import Car, MasinaImage, Favorite, Shipment, Order, Review

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q

from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone




@login_required
def add_to_favorites(request, car_id):
    if request.method != "POST":
        return JsonResponse({"error": "invalid method"}, status=400)

    car = get_object_or_404(Car, id=car_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, car=car)

    if created:
        return JsonResponse({"status": "added"})
    else:
        fav.delete()
        return JsonResponse({"status": "removed"})





@login_required
def account(request):
    favorites_qs = Favorite.objects.filter(user=request.user).select_related("car")
    favorites = [f.car for f in favorites_qs]

    orders = Order.objects.filter(User=request.user).select_related("Item", "Shipment")

    return render(request, "account.html", {
        "favorites": favorites,
        "orders": orders,
    })








@login_required
def favorite_list(request):
    cars = Car.objects.filter(favorited_by__user=request.user)
    return render(request, "favorite_list.html", {"cars": cars})






def search_cars(request):
    q = request.GET.get("q", "").strip()
    qs = Car.objects.all()
    if q:
        qs = qs.filter(
            Q(brand__icontains=q) |
            Q(model__icontains=q)
        )
    qs = qs[:10]
    results = [{
        "id": c.id,
        "brand": c.brand,
        "model": c.model,
        "year": c.Year,
        "price": c.price,
        "url": request.build_absolute_uri(c.get_absolute_url())
        if hasattr(c, "get_absolute_url")
        else f"/cars/{c.id}/"
    } for c in qs]
    return JsonResponse({"results": results})



class CustomLoginView(LoginView):
    template_name = 'login.html'

def home(request):
    return render(request, 'home.html')






from decimal import Decimal

def car_list(request):
    cars = Car.objects.all()

    # existing filters
    make = request.GET.get("make")
    body_type = request.GET.get("body_type")
    fuel = request.GET.get("fuel")
    transmission = request.GET.get("transmission")
    max_price = request.GET.get("max_price")
    min_year = request.GET.get("min_year")
    max_km = request.GET.get("max_km")
    search = request.GET.get("search")

    # SEARCH (brand + model)
    if search:
        cars = cars.filter(Name__icontains=search)

    # Marca (extract from Name)
    if make and make != "Oricare":
        cars = cars.filter(Name__icontains=make)

    if body_type and body_type != "Oricare":
        cars = cars.filter(Type__iexact=body_type)

    if fuel and fuel != "Oricare":
        cars = cars.filter(Fuel__iexact=fuel)

    if transmission and transmission != "Oricare":
        cars = cars.filter(Transmission__iexact=transmission)

    if max_price and max_price != "Oricare":
        cars = cars.filter(Price__lte=max_price)

    if min_year and min_year != "Oricare":
        cars = cars.filter(Year__gte=min_year)

    if max_km and max_km != "Oricare":
        cars = cars.filter(Km__lte=max_km)

    return render(request, "car_list.html", {
        "cars": cars,
        "make": make,
        "body_type": body_type,
        "fuel": fuel,
        "transmission": transmission,
        "max_price": max_price,
        "min_year": min_year,
        "max_km": max_km,
        "search": search,
    })






# DETALII MAȘINĂ
def car_details(request, car_id):
    car = get_object_or_404(Car, pk=car_id)

    images = MasinaImage.objects.filter(masina=car)
    similar = Car.objects.filter(Fuel=car.Fuel).exclude(id=car.id)[:8]

    reviews = Review.objects.filter(Car=car).order_by('-CreatedAt')

    return render(request, "car_details.html", {
        "car": car,
        "images": images,
        "similar": similar,
        "reviews": reviews,
    })



# ADAUGĂ MAȘINĂ
@login_required
def add_car(request):
    if request.method == "POST":

        # 1. Creăm mașina
        car = Car.objects.create(
            Name=request.POST["name"],
            Description=request.POST["description"],
            Price=request.POST["price"],
            Type=request.POST["type"],
            Image=request.FILES["image"],
            Year=request.POST["year"],
            Km=request.POST["km"],
            Fuel=request.POST["fuel"],
            Transmission=request.POST["transmission"],
            HorsePower=request.POST["horsepower"],
        )

        # 2. Salvăm pozele secundare
        for f in request.FILES.getlist("poze"):
            MasinaImage.objects.create(
                masina=car,
                imagine=f
            )

        return redirect("cars")

    return render(request, "add_car.html")




@login_required
def edit_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        car.Name = request.POST.get("name")
        car.Description = request.POST.get("description")
        car.Price = request.POST.get("price")
        car.Type = request.POST.get("type")
        car.Year = request.POST.get("year")
        car.Km = request.POST.get("km")
        car.Fuel = request.POST.get("fuel")
        car.Transmission = request.POST.get("transmission")
        car.HorsePower = request.POST.get("horsepower")

        # update imagine principală dacă a fost trimisă
        if request.FILES.get("image"):
            car.Image = request.FILES.get("image")

        car.save()

        # update poze secundare (opțional)
        if request.FILES.getlist("poze"):
            for f in request.FILES.getlist("poze"):
                MasinaImage.objects.create(
                    masina=car,
                    imagine=f
                )

        messages.success(request, "Mașina a fost actualizată cu succes!")
        return redirect("car_details", car_id=car.id)

    return render(request, "edit_car.html", {"car": car})






@login_required
def delete_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        # Șterge poza principală din storage
        if car.Image:
            car.Image.delete(save=False)

        # Șterge pozele secundare
        for img in car.poze.all():
            img.imagine.delete(save=False)
            img.delete()

        # Șterge mașina
        car.delete()

        return redirect("cars")  # redirect spre lista de mașini

    return render(request, "delete_car.html", {"car": car})






from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Email sau parolă incorectă. Mai încearcă o dată.")
            return render(request, "login.html", {"error": "Email sau parolă incorectă. Mai încearcă o dată."})

    return render(request, "login.html")





from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login

User = get_user_model()

def register_user(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password1 = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Parolele nu coincid.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email deja folosit.")
            return redirect("register")

        # username automat = email până la @
        username = email.split("@")[0]

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            FullName=full_name,
            Phone=phone,
        )

        user.save()
        login(request, user)
        return redirect("home")

    return render(request, "register.html")



from django.contrib.auth import logout

def logout_user(request):
    logout(request)
    return redirect("home")



# DASHBOARD (LISTA MAȘINILOR LUI)
@login_required
def dashboard(request):
    cars = Car.objects.all().order_by('-date_added')
    return render(request, 'dashboard.html', {'cars': cars})





def track_order_page(request):
    track = request.GET.get("track")

    shipment = None
    if track:
        try:
            shipment = Shipment.objects.get(TrackNumber=track)
        except Shipment.DoesNotExist:
            return render(request, "track_order.html", {"error": "Cod invalid."})

    return render(request, "track_order.html", {"shipment": shipment})



def track_order(request, track):
    try:
        shipment = Shipment.objects.get(TrackNumber=track)
    except Shipment.DoesNotExist:
        return render(request, "track_order.html", {"error": "Cod invalid."})

    return render(request, "track_order.html", {"shipment": shipment})




from django.utils import timezone
import uuid
from .models import Order, Shipment


@login_required
def place_order_page(request, car_id):
    car = Car.objects.get(id=car_id)

    if request.method == "POST":
        shipment = Shipment.objects.create(
            TrackNumber="TRK-" + str(uuid.uuid4())[:8],
            Carrier="Fan Courier",
            Status="În tranzit",
            EstimatedArrival=timezone.now().date()
        )

        Order.objects.create(
            User=request.user,
            CreatedAt=timezone.now(),
            IBAN=request.POST.get("iban"),
            PaymentDate=request.POST.get("payment_date"),
            Method=request.POST.get("payment_method"),
            Quantity=1,
            Shipment=shipment,
            Item=car
        )

        messages.success(request, "Comanda a fost plasată cu succes!")
        return redirect("orders_page")

    return render(request, "place_order.html", {"car": car})






@login_required
def orders_page(request):
    orders = Order.objects.filter(User=request.user)
    return render(request, "orders.html", {"orders": orders})



from django.shortcuts import get_object_or_404, redirect
from .models import Car, Review
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Car, Review

@login_required
def add_review(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if rating and comment:
            Review.objects.create(
                User=request.user,
                Car=car,
                Rating=rating,
                Comment=comment
            )

    return redirect("car_details", car_id=car.id)



@login_required
def remove_favorite(request, car_id):
    Favorite.objects.filter(user=request.user, car_id=car_id).delete()
    return redirect("account")


from django.core.mail import send_mail
from django.conf import settings

def about_page(request):
    return render(request, "about.html")


def contact_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        full_message = f"De la: {name} ({email})\n\nMesaj:\n{message}"

        send_mail(
            subject=subject,
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )

        return render(request, "contact.html", {"success": True})

    return render(request, "contact.html")






