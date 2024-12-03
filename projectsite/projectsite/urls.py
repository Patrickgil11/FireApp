from django.contrib import admin
from django.urls import path

from fire.views import HomePageView, ChartView, PieCountbySeverity, WeatherConditionsDeleteView, WeatherConditionsUpdateView, WeatherConditionsCreateView, WeatherConditionsListView, IncidentDeleteView, IncidentUpdateView, LocationsDeleteView, LocationsUpdateView, LocationsCreateView, LocationsListView, IncidentCreateView,  IncidentListView,  FireTruckDeleteView, FireTruckUpdateView, FireTruckCreateView, FireTruckListView, FireFightersDeleteView, FireFightersUpdateView, FireFightersCreateView, FireFightersListView, FireStationDeleteView, LineCountbyMonth, FireStationUpdateView, MultilineIncidentTop3Country, multipleBarbySeverity, FireStationListView, FireStationCreateView
from fire import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard-chart'),
    path('chart/', PieCountbySeverity, name='chart'),
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('multiBarChart/', multipleBarbySeverity, name='chart'),
    path('stations', views.map_station, name='map-station'),
    path('firestations/', FireStationListView.as_view(), name='fire-station'),
    path('firestations/add/', FireStationCreateView.as_view(), name='fire-station-add'),
    path('firestations/<pk>/', FireStationUpdateView.as_view(), name='fire-station-update'),
    path('firestations/<pk>/delete/', FireStationDeleteView.as_view(), name='fire-station-delete'),
    path('firefightersstations/', FireFightersListView.as_view(), name='fire-fighters'),
    path('firefightersstations/add/', FireFightersCreateView.as_view(), name='fire-fighters-add'),
    path('firefightersstations/<pk>/', FireFightersUpdateView.as_view(), name='fire-fighters-update'),
    path('firefightersstations/<pk>/delete/', FireFightersDeleteView.as_view(), name='fire-fighters-delete'),
    path('firetruck/', FireTruckListView.as_view(), name='fire-truck'),
    path('firetruck/add/', FireTruckCreateView.as_view(), name='fire-truck-add'),
    path('firetruck/<pk>/', FireTruckUpdateView.as_view(), name='fire-truck-update'),
    path('firetruck/<pk>/delete/', FireTruckDeleteView.as_view(), name='fire-truck-delete'),
    path('location/', LocationsListView.as_view(), name='location'),
    path('location/add/', LocationsCreateView.as_view(), name='location-add'),
    path('location/<pk>/', LocationsUpdateView.as_view(), name='location-update'),
    path('location/<pk>/delete/', LocationsDeleteView.as_view(), name='location-delete'),
    path('incident/', IncidentListView.as_view(), name='incident'),
    path('incident/add/', IncidentCreateView.as_view(), name='incident-add'),
    path('incident/<pk>/', IncidentUpdateView.as_view(), name='incident-update'),
    path('incident/<pk>/delete/', IncidentDeleteView.as_view(), name='incident-delete'),
    path('weather/', WeatherConditionsListView.as_view(), name='weather'),
    path('weather/add/', WeatherConditionsCreateView.as_view(), name='weather-add'),
    path('weather/<pk>/', WeatherConditionsUpdateView.as_view(), name='weather-update'),
    path('weather/<pk>/delete/', WeatherConditionsDeleteView.as_view(), name='weather-delete'),
    
]

