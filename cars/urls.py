"""
URL configuration for cars project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp.views import * 
 

urlpatterns = [
    path('home/', home, name="home"),
    path('cars/', car_list, name="cars"),
    path("car/<int:car_id>/", car_details, name="car_details"),
    path('add_car/', add_car, name="add_car"),
    path('login/', login_user, name='login'),
    path("logout/", logout_user, name="logout"),
    path('register/', register_user, name="register"),
    path('dashboard/', dashboard, name="dashboard"),
    path('account/', account, name='account'),
    path("api/search-cars/", search_cars, name="search_cars_api"),
    path("add-to-favorites/<int:car_id>/", add_to_favorites, name="add_to_favorites"),
    path("place-order/<int:car_id>/", place_order_page, name="place_order_page"),
    path("track-order/", track_order_page, name="track_order_page"),
    path("track-order/<str:track>/", track_order, name="track_order"),
    path("orders/", orders_page, name="orders_page"),
    path("add-review/<int:car_id>/", add_review, name="add_review"),
    path("about/", about_page, name="about"),
    path("contact/", contact_page, name="contact"),
    path("car/<int:car_id>/edit/", edit_car, name="edit_car"),
    path("car/<int:car_id>/delete/", delete_car, name="delete_car"),
    path("favorites/remove/<int:car_id>/", remove_favorite, name="remove_favorite"),
    


   

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



