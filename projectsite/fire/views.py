from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from fire.models import Locations, Incident, FireStation, Firefighters, FireTruck, WeatherConditions
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from datetime import datetime
from .forms import FireStationForm, FireFightersForm, FireTruckForm, IncidentForm, LocationsForm, WeatherConditionsForm
from django.urls import reverse_lazy
from django.contrib import messages
from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Q




class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass

def PieCountbySeverity(request):
    query = '''
        SELECT severity_level, COUNT(*) as count
        FROM fire_incident
        GROUP BY severity_level
        '''
    data = {}
    with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    if rows:
        # Construct the dictionary with severity level as keys and count as values
            data = {severity: count for severity, count in rows}
    else:
             data = {}

    return JsonResponse(data)

def LineCountbyMonth(request):
    current_year = datetime.now().year

    result = {month: 0 for month in range(1, 13)}

    incidents_per_month = Incident.objects.filter(date_time__year=current_year).values_list('date_time', flat=True)

    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    result_with_month_names = {
        month_names[int(month)]: count for month, count in result.items()
    }

    return JsonResponse(result_with_month_names)

def MultilineIncidentTop3Country(request):
    query = '''
    SELECT fl.country, strftime('%m', fi.date_time) AS month, COUNT(fi.id) AS incident_count
    FROM fire_incident fi
    JOIN fire_locations fl ON fi.location_id = fl.id
    WHERE fl.country IN (
        SELECT fl_top.country
        FROM fire_incident fi_top
        JOIN fire_locations fl_top ON fi_top.location_id = fl_top.id
        WHERE strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
        GROUP BY fl_top.country
        ORDER BY COUNT(fi_top.id) DESC
        LIMIT 3
    )
    AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY fl.country, month
    ORDER BY fl.country, month;
    '''
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Initialize a dictionary to store the result
    result = {}
    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))

    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {month: 0 for month in months}

        # Update the incident count for the corresponding month
        result[country][month] = total_incidents

    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        # Placeholder name for missing countries
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}

    # Sort the dictionary by month
    for country in result:
        result[country] = dict(sorted(result[country].items()))

    return JsonResponse(result)

def multipleBarbySeverity(request):
    query = '''
    SELECT fi.severity_level, strftime('%m', fi.date_time) AS month, COUNT(fi.id) AS incident_count
    FROM fire_incident fi
    GROUP BY fi.severity_level, month
    '''
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))

    for row in rows:
        level = str(row[0])  # Ensure the severity level is a string
        month = row[1]
        total_incidents = row[2]

        if level not in result:
            result[level] = {month: 0 for month in months}

        result[level][month] = total_incidents

    # Sort months within each severity level
    for level in result:
        result[level] = dict(sorted(result[level].items()))

    return JsonResponse(result)

def map_station(request):
    fireStations = FireStation.objects.values('name', 'latitude', 'longitude')

    for fs in fireStations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])

    fireStations_list = list(fireStations)

    context = {
        'fireStations': fireStations_list,
    }

    return render(request, 'map_station.html', context)



def map_incident(request):
    # Retrieve incident data from the database
    incidents = Locations.objects.values('name', 'latitude', 'longitude')
    # Convert latitude and longitude to float for proper handling in JavaScript
    for fs in incidents:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])
    # Convert QuerySet to a list
    incident_list = list(incidents)
    
    # Prepare context to pass to the template
    context = {
        'incident': incident_list,
    }
    # Render the template with the incident data
    return render(request, 'map_incidents.html', context)



class FireStationListView(ListView):
    model = FireStation
    context_object_name = 'stations'
    template_name = 'fire_station_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query)
            )
        return qs.order_by('id')
    
class FireStationCreateView(CreateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'fire_station_add.html'
    success_url = reverse_lazy('fire-station')

    def form_valid(self, form):
        name_fireStation = form.instance.name
        messages.success(self.request, f"{name_fireStation} has been added successfully.")
        return super().form_valid(form)



class FireStationUpdateView(UpdateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'fire_station_update.html'
    success_url = reverse_lazy('fire-station')

    def form_valid(self, form):
        fireStation_name = form.instance.name
        messages.success(self.request,f'{fireStation_name} has been Updated.')
        return super().form_valid(form)


class FireStationDeleteView(DeleteView):
    model = FireStation
    template_name = 'fire_station_delete.html'
    success_url = reverse_lazy('fire-station')

    def form_valid(self, form):
        messages.success(self.request, f"Fire Station Deleted successfully.")
        return super().form_valid(form)

class FireFightersListView(ListView):
    model = Firefighters
    context_object_name = 'firefighters'
    template_name = 'fire_fighters_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(rank__icontains=query) |
                Q(experience_level__icontains=query) |
                Q(station__icontains=query)
            )
        return qs.order_by('id')
    
class FireFightersCreateView(CreateView):
    model = Firefighters
    form_class = FireFightersForm
    template_name = 'fire_fighters_add.html'
    success_url = reverse_lazy('fire-fighters')

    def form_valid(self, form):
        name_fireFighter = form.instance.name
        messages.success(self.request, f"{name_fireFighter} has been added successfully.")
        return super().form_valid(form)


    
class FireFightersCreateView(CreateView):
    model = Firefighters
    form_class = FireFightersForm
    template_name = 'fire_station_add.html'
    success_url = reverse_lazy('fire-station')

class FireFightersUpdateView(UpdateView):
    model = Firefighters
    form_class = FireFightersForm
    template_name = 'fire_fighters_update.html'
    success_url = reverse_lazy('fire-fighters')

    def form_valid(self, form):
        fireFighter_name = form.instance.name
        messages.success(self.request,f'{fireFighter_name} has been Updated.')
        return super().form_valid(form)

class FireFightersDeleteView(DeleteView):
    model = Firefighters
    template_name = 'fire_fighters_delete.html'
    success_url = reverse_lazy('fire-fighters')

    def form_valid(self, form):
        messages.success(self.request, f"Fire Fighter Deleted successfully.")
        return super().form_valid(form)

class FireTruckListView(ListView):
    model = FireTruck
    context_object_name = 'fire-truck'
    template_name = 'fire_truck_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
                Q(truck_number__icontains=query) |
                Q(models__icontains=query) |
                Q(capacity__icontains=query) |
                Q(station__icontains=query)
            )
        return qs.order_by('id')

class FireTruckCreateView(CreateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'fire_truck_add.html'
    success_url = reverse_lazy('fire-truck')

    def form_valid(self, form):
        name_fireTruck = form.instance.model
        messages.success(self.request, f"{name_fireTruck} has been added successfully.")
        return super().form_valid(form)

class FireTruckUpdateView(UpdateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'fire_truck_update.html'
    success_url = reverse_lazy('fire-truck')

    def form_valid(self, form):
        name_fireTruck = form.instance.model
        messages.success(self.request,f'{name_fireTruck} has been Updated.')
        return super().form_valid(form)


class FireTruckDeleteView(DeleteView):
    model = FireTruck
    template_name = 'fire_truck_delete.html'
    success_url = reverse_lazy('fire-truck')

    def form_valid(self, form):
        messages.success(self.request, f"Fire Truck Deleted successfully.")
        return super().form_valid(form)

class LocationsListView(ListView):
    model = Locations
    context_object_name = 'locations'
    template_name = 'location_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(latitude__icontains=query) |
                Q(longitude__icontains=query) |
                Q(address__icontains=query)|
                Q(city__icontains=query)|
                Q(country__icontains=query)
            )
        return qs.order_by('id')

class LocationsCreateView(CreateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'location_add.html'
    success_url = reverse_lazy('location')

    def form_valid(self, form):
        name_location = form.instance.name
        messages.success(self.request, f"{name_location} has been added successfully.")
        return super().form_valid(form)


class LocationsUpdateView(UpdateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'location_update.html'
    success_url = reverse_lazy('location')

    def form_valid(self, form):
        name_location = form.instance.name
        messages.success(self.request,f'{name_location} has been Updated.')
        return super().form_valid(form)


class LocationsDeleteView(DeleteView):
    model = Locations
    template_name = 'location_delete.html'
    success_url = reverse_lazy('location')

    def form_valid(self, form):
        messages.success(self.request, f"Location Deleted successfully.")
        return super().form_valid(form)


class IncidentListView(ListView):
    model = Incident
    context_object_name = 'incident'
    template_name = 'incident_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
                Q(location__icontains=query) |
                Q(date_time__icontains=query) |
                Q(severity_level__icontains=query) |
                Q(description__icontains=query)
            )
        return qs.order_by('id')

class IncidentCreateView(CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incident_add.html'
    success_url = reverse_lazy('incident')

    def form_valid(self, form):
        name_location = form.instance.location
        messages.success(self.request, f"{name_location} has been added successfully.")
        return super().form_valid(form)

class IncidentUpdateView(UpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incident_update.html'
    success_url = reverse_lazy('incident')

    def form_valid(self, form):
        name_location = form.instance.location.name
        messages.success(self.request,f'{name_location} has been Updated.')
        return super().form_valid(form)

class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = 'incident_delete.html'
    success_url = reverse_lazy('incident')

    def form_valid(self, form):
        messages.success(self.request, f"Incident Deleted successfully.")
        return super().form_valid(form)

class WeatherConditionsListView(ListView):
    model = WeatherConditions
    context_object_name = 'weather'
    template_name = 'weather_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
                Q(incident__icontains=query) |
                Q(temperature__icontains=query) |
                Q(humidity__icontains=query) |
                Q(wind_speed__icontains=query)|
                Q(weather_description__icontains=query)
            )
        return qs.order_by('id')

class WeatherConditionsCreateView(CreateView):
    model = WeatherConditions
    form_class = WeatherConditionsForm
    template_name = 'weather_add.html'
    success_url = reverse_lazy('weather')

    def form_valid(self, form):
        name_incident = form.instance.incident
        messages.success(self.request, f"{name_incident} has been added successfully.")
        return super().form_valid(form)
    

class WeatherConditionsUpdateView(UpdateView):
    model = WeatherConditions
    form_class = WeatherConditionsForm
    template_name = 'weather_update.html'
    success_url = reverse_lazy('weather')

    def form_valid(self, form):
        name_incident = form.instance.incident
        messages.success(self.request,f'{name_incident} has been Updated.')
        return super().form_valid(form)



class WeatherConditionsDeleteView(DeleteView):
    model = WeatherConditions
    template_name = 'weather_delete.html'
    success_url = reverse_lazy('weather')

    def form_valid(self, form):
        messages.success(self.request, f"Weather Deleted successfully.")
        return super().form_valid(form)

