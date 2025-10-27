#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime
import pandas as pd

# Free OpenWeatherMap API (1000 calls/day)
API_KEY = "d8e984a220ab8069b7f0dad712885409"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather_data(city, state, game_date):
    """Get weather data for a specific city and date"""
    try:
        # Format city name for API
        city_formatted = f"{city},{state},US"
        
        # Make API request
        params = {
            'q': city_formatted,
            'appid': API_KEY,
            'units': 'imperial'
        }
        
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if response.status_code == 200:
            # Extract weather data
            temp = data['main']['temp']
            wind_speed = data['wind']['speed']
            humidity = data['main']['humidity']
            weather_desc = data['weather'][0]['description']
            
            return {
                'temp': temp,
                'wind': wind_speed,
                'humidity': humidity,
                'weather': weather_desc
            }
        else:
            print(f"Weather API error for {city}: {data}")
            return None
            
    except Exception as e:
        print(f"Error getting weather for {city}: {e}")
        return None

def get_stadium_weather(stadium_name, game_date):
    """Get weather data for NFL stadiums"""
    # NFL stadium locations
    stadium_locations = {
        'Soldier Field': ('Chicago', 'IL'),
        'Lambeau Field': ('Green Bay', 'WI'),
        'Arrowhead Stadium': ('Kansas City', 'MO'),
        'M&T Bank Stadium': ('Baltimore', 'MD'),
        'FirstEnergy Stadium': ('Cleveland', 'OH'),
        'Paycor Stadium': ('Cincinnati', 'OH'),
        'Acrisure Stadium': ('Pittsburgh', 'PA'),
        'New Era Field': ('Buffalo', 'NY'),
        'MetLife Stadium': ('East Rutherford', 'NJ'),
        'Lincoln Financial Field': ('Philadelphia', 'PA'),
        'FedExField': ('Landover', 'MD'),
        'Hard Rock Stadium': ('Miami', 'FL'),
        'Raymond James Stadium': ('Tampa', 'FL'),
        'Bank of America Stadium': ('Charlotte', 'NC'),
        'Mercedes-Benz Stadium': ('Atlanta', 'GA'),
        'Mercedes-Benz Superdome': ('New Orleans', 'LA'),
        'AT&T Stadium': ('Arlington', 'TX'),
        'NRG Stadium': ('Houston', 'TX'),
        'TIAA Bank Stadium': ('Jacksonville', 'FL'),
        'Lumen Field': ('Seattle', 'WA'),
        'SoFi Stadium': ('Inglewood', 'CA'),
        'State Farm Stadium': ('Glendale', 'AZ'),
        'Allegiant Stadium': ('Las Vegas', 'NV'),
        'Empower Field at Mile High': ('Denver', 'CO'),
        'Levi\'s Stadium': ('Santa Clara', 'CA'),
        'U.S. Bank Stadium': ('Minneapolis', 'MN'),
        'Ford Field': ('Detroit', 'MI'),
        'Lucas Oil Stadium': ('Indianapolis', 'IN'),
        'Nissan Stadium': ('Nashville', 'TN'),
        'Gillette Stadium': ('Foxborough', 'MA')
    }
    
    if stadium_name in stadium_locations:
        city, state = stadium_locations[stadium_name]
        return get_weather_data(city, state, game_date)
    else:
        print(f"Stadium location not found: {stadium_name}")
        return None

def update_weather_data():
    """Update weather data for upcoming games"""
    print("🌤️ Updating weather data for upcoming games...")
    
    # This would integrate with your existing data loading
    # For now, this is the framework
    
    # Example usage:
    weather_data = get_stadium_weather('Soldier Field', '2025-10-23')
    if weather_data:
        print(f"Weather at Soldier Field: {weather_data}")
    
    return weather_data

if __name__ == "__main__":
    # Test the weather API
    test_weather = update_weather_data()
    print(f"Test result: {test_weather}")
