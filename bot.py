import logging
import requests
import os
import discord
import pickle as cPickle
import os.path
import json
import csv
from dotenv import load_dotenv
from discord.ext import commands

# discord logger
logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)  # change "WARNING" to "DEBUG" for verbose logs
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
# variables used for bot authentication and base URLs
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
bot = commands.Bot(command_prefix='!')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?lat="
BASE_GEO_URL = "http://api.openweathermap.org/geo/1.0/zip?"
API_KEY = os.getenv('API_KEY')

# The geo_code funciton is used to translate postal code location data to coordinates
# The weather API requires coordinates to identify the location of the requested weather report
def geo_code(zip_code, country_code):
    base_geo_url = "http://api.openweathermap.org/geo/1.0/zip?"
    geo_url = f'{base_geo_url}zip={zip_code},{country_code}&appid={API_KEY}'
    response = requests.get(geo_url)
    location = response.json()
    # convert lat and lon to string
    lat = str(location['lat'])
    lon = str(location['lon'])
    return lat, lon


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=''))


'''
The !weather command is accepts a postal code and a country code which is
sent to the geo_code function then used to get weather and air quality data
for the specified location.
'''
@bot.command(pass_context = True)
async def weather(weather, zip_code, country_code='us'):

    coords = geo_code(zip_code, country_code)
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={coords[0]}&lon={coords[1]}&appid={API_KEY}'
    air = f'https://api.openweathermap.org/data/2.5/air_pollution?lat={coords[0]}&lon={coords[1]}&appid={API_KEY}'

    # HTTP request
    response = requests.get(url)
    air_response = requests.get(air)
    # checking the status code of the request
    if response.status_code == 200 and air_response.status_code == 200:
        # getting data in the json format
        data = response.json()
        air_data = air_response.json()
        # getting the main dict block
        main = data['main']
        # getting temperature: temp is converted from Kelvin to Farenheit
        temperature = int((main['temp'] - 273.15) * 9/5 + 32)
        # getting the humidity
        humidity = main['humidity']
        # getting the city name
        name = data['name']
        # get air pollution
        air_main = air_data['list'][0]['main']['aqi']
        # weather report
        report = data['weather']
        output = f"{name:-^30}\nTemperature: {temperature}\nHumidity: {humidity}\nWeather Report: {report[0]['description']}\nAir Quality: {air_main}"
        await weather.send(output)
        # await weather.author.send(output)



'''
The !myweather command is used to get a users weather data after they have saved
their location data with the bot. The coordinates are stored to avoid unnecessary
calls to the geocoding API.

The location and user data is currently stored in a CSV
'''
@bot.command(pass_context = True)
async def myweather(myweather):
    #TO DO: update function to store in DB instead of CSV
    with open(os.path.join(os.getcwd(), "User_locations.csv"),"r+",encoding='UTF8',newline='') as input_file:
        csv_rows = csv.DictReader(input_file)
        for line in csv_rows:
                if myweather.author.name in line['username']:
                    user_dict = {
                        "user": line['username'],
                        "lat": line['lat'],
                        "lon": line['lon']
                    }
                    url = f"https://api.openweathermap.org/data/2.5/weather?lat={user_dict['lat']}&lon={user_dict['lon']}&appid={API_KEY}"
                    air = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={user_dict['lat']}&lon={user_dict['lon']}&appid={API_KEY}"

                    # HTTP request
                    response = requests.get(url)
                    air_response = requests.get(air)
                    # checking the status code of the request
                    if response.status_code == 200 and air_response.status_code == 200:
                        # getting data in the json format
                        data = response.json()
                        air_data = air_response.json()
                        # getting the main dict block
                        main = data['main']
                        # getting temperature
                        temperature = int((main['temp'] - 273.15) * 9 / 5 + 32)
                        # getting the humidity
                        humidity = main['humidity']
                        # get air pollution
                        air_list = air_data['list']
                        air_main = air_list[0]['main']['aqi']
                        # weather report
                        report = data['weather']
                        output = f"Temperature: {temperature}\nHumidity: {humidity}\nWeather Report: {report[0]['description']}\nAir Quality: {air_main}"
                        await myweather.send(output)
                        # await weather.author.send(output)
                    # lookup existing location data
                    # message if no data
                    # output weather WITHOUT location name if data exists
                else:
                    await myweather.author.send(f"I do not have your location data, please send me a message with !mylocation zip_code country_code")


'''
The !mylocation command is used for users to save their user and location data
to the bot. This command is best used in a direct message to avoid posting location 
data publicly.

The mylocation command will send the location data to the geo_code function to get
coordinates which will be stored in CSV.
'''
@bot.command(pass_context = True)
async def mylocation(mylocation, zip_code, country_code):
    '''TO DO: add temperature unit as preference so users can choose to report temperature
       in farenheit or celsius'''
    coords = geo_code(zip_code, country_code)
    user = str(mylocation.author)
    user_dict = {"username": user, "lat": coords[0], "lon": coords[1]}
    fieldnames = ['username','lat','lon']
    with open(os.path.join(os.getcwd(), "User_locations.csv"),"r+",encoding='UTF8',newline='') as input_file:
        csv_rows = csv.DictReader(input_file)
        for line in csv_rows:
                if mylocation.author.name in line['username']:
                     await mylocation.author.send(f"I have already saved your location, please use the !myweather command to get your weather information.")
                else:
                    input_file.seek(0, os.SEEK_END)
                    writer = csv.DictWriter(input_file, fieldnames=fieldnames)
                    writer.writerow(user_dict)
                    #cPickle.dump(user_dict, output_file)
                    await mylocation.author.send(f"your location is saved as user = {mylocation.author} lat = {coords[0]} and lon = {coords[1]}")
    

'''
The !testsave command is used for testing purposes to ensure user data is saved
successfully. The command simply looks for saved user data and sends a message
with the username and saved coordinates.
'''
@bot.command(pass_context = True)
async def testsave(testsave):
    with open(os.path.join(os.getcwd(), "User_locations.csv"),"r+",encoding='UTF8',newline='') as input_file:
        csv_rows = csv.DictReader(input_file)
        for line in csv_rows:
                if testsave.author.name in line['username']:
                    user_dict = {
                        "user": line['username'],
                        "lat": line['lat'],
                        "lon": line['lon']
                    }

    await testsave.author.send(f"your location is saved as user = {user_dict['user']}\nlat = {user_dict['lat']}\nlon = {user_dict['lon']}")
'''
@bot.command(pass_context = True)
async def f10(f10, zip_code, country_code):
    # command for 10-day forecast

@bot.command(pass_context = True)
async def radar(radar, zip_code, country_code):
    # command for radar
'''

bot.run(TOKEN)
