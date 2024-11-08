import requests
from supabase import create_client
from datetime import datetime
import json
import time

# Configuration
WEATHER_API_KEY = "YOUR_WEATHER_API_KEY" 
HUGGINGFACE_API_KEY = "YOUR_HUGGINGFACE_API_KEY"
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"

def get_weather_data(city):
    """Get current weather data for a city"""
    url = f"http://api.weatherapi.com/v1/current.json"
    params = {
        'key': WEATHER_API_KEY,
        'q': city,
        'aqi': 'no'
    }
    response = requests.get(url, params=params)
    return response.json()

def analyze_with_ai(weather_data):
    """Get AI analysis of weather conditions"""
    try:
        API_URL = "https://api-inference.huggingface.co/models/gpt2"
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        temp_c = weather_data['current']['temp_c']
        condition = weather_data['current']['condition']['text']
        humidity = weather_data['current']['humidity']
        wind_kph = weather_data['current']['wind_kph']
        
        prompt = f"Describe this weather condition in exactly 30 words: Temperature is {temp_c}°C with {condition}, humidity at {humidity}% and wind speed of {wind_kph} km/h."
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 50,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()
        
        # Handle different response formats
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', 'Weather analysis not available')
        elif isinstance(result, dict):
            return result.get('generated_text', 'Weather analysis not available')
        else:
            return f"Current weather: {condition}, {temp_c}°C, {humidity}% humidity, wind {wind_kph} km/h"
            
    except Exception as e:
        # Fallback response if AI analysis fails
        return f"Current weather: {condition}, {temp_c}°C, {humidity}% humidity, wind {wind_kph} km/h"

def store_in_database(weather_data, ai_analysis):
    """Store weather data and AI analysis in Supabase"""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    data = {
        'timestamp': datetime.now().isoformat(),
        'location': weather_data['location']['name'],
        'country': weather_data['location']['country'],
        'weather_data': json.dumps({
            'temperature': weather_data['current']['temp_c'],
            'condition': weather_data['current']['condition']['text'],
            'humidity': weather_data['current']['humidity'],
            'wind_kph': weather_data['current']['wind_kph']
        }),
        'ai_analysis': ai_analysis
    }
    
    supabase.table('weather_analysis').insert(data).execute()

def process_city(city):
    """Process weather data for a city"""
    try:
        print(f"\nProcessing weather data for {city}...")
        
        # Step 1: Get weather data
        weather_data = get_weather_data(city)
        
        # Step 2: Get AI analysis
        ai_analysis = analyze_with_ai(weather_data)
        print(f"AI Analysis: {ai_analysis}")
        
        # Step 3: Store in database
        store_in_database(weather_data, ai_analysis)
        
        return True
    except Exception as e:
        print(f"Error processing {city}: {str(e)}")
        return False

if __name__ == "__main__":
    cities = ["London", "New York", "Tokyo", "Sydney", "Paris"]
    
    print("Starting weather analysis...")
    successful_cities = 0
    
    for city in cities:
        if process_city(city):
            successful_cities += 1
        time.sleep(2)  # Small delay between cities
    
    print(f"\n✅ Done! Successfully processed {successful_cities} out of {len(cities)} cities.")
    print("Check Supabase for the analyzed weather data.")