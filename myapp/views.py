from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User 
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .models import Car, MasinaImage, Favorite 

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q

from django.contrib import messages
from django.shortcuts import redirect



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
    favorites_qs = Favorite.objects.filter(user=request.user).select_related('car')
    cars = [fav.car for fav in favorites_qs]

    return render(request, "account.html", {"favorites": cars})






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


def car_list(request):
    cars = Car.objects.all().order_by("-CreatedAt")

    # --- Search ---
    q = request.GET.get("q")
    if q:
        cars = cars.filter(
            Q(Name__icontains=q) |
            Q(Brand__icontains=q) |
            Q(Model__icontains=q)
        )

    # --- Filtre ---
    brand = request.GET.get("brand")
    if brand:
        cars = cars.filter(Brand=brand)

    fuel = request.GET.get("fuel")
    if fuel:
        cars = cars.filter(Fuel__iexact=fuel)

    max_price = request.GET.get("max_price")
    if max_price:
        cars = cars.filter(Price__lte=max_price)

    min_year = request.GET.get("min_year")
    if min_year:
        cars = cars.filter(Year__gte=min_year)

    max_km = request.GET.get("max_km")
    if max_km:
        cars = cars.filter(Km__lte=max_km)

    # --- Sortare ---
    sort = request.GET.get("sort")
    sort_map = {
        "price_asc": "Price",
        "price_desc": "-Price",
        "year_desc": "-Year",
        "km_asc": "Km",
    }
    if sort in sort_map:
        cars = cars.order_by(sort_map[sort])

    # --- Paginare ---
    paginator = Paginator(cars, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "car_list.html", {
        "cars": page_obj,
        "page_obj": page_obj,
        "brand": brand,
        "fuel": fuel,
        "max_price": max_price,
        "min_year": min_year,
        "max_km": max_km,
        "sort": sort,
        "q": q,
    })



# DETALII MAȘINĂ
def car_details(request, car_id):
    car = get_object_or_404(Car, pk=car_id)

    # similare – aceeași marcă sau combustibil
    similar = Car.objects.filter(
        Q(Fuel=car.Fuel)
    ).exclude(pk=car.pk)[:8]

    images = MasinaImage.objects.filter(masina=car)
    

    return render(request, "car_details.html", {
        "car": car,
        "similar": similar,
        "images": images,
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
def add_to_favorites(request, car_id):
    

    car = get_object_or_404(Car, id=car_id)
    Favorite.objects.get_or_create(user=request.user, car=car)
    return redirect("car_details", car_id=car.id)
    


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
        fullname = request.POST.get("name")
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
            FullName=fullname,
            Phone=phone,
        )

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




