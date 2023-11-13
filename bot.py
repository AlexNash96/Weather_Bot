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
# bot stuffs
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
bot = commands.Bot(command_prefix='!')
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?lat="
BASE_GEO_URL = "http://api.openweathermap.org/geo/1.0/zip?"
API_KEY = os.getenv('API_KEY')


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


@bot.command(pass_context = True)
async def weather(weather, zip_code, country_code='us'):
    # updating the URL
    # geo_url = f'''{BASE_GEO_URL}zip={zip_code},{country_code}&appid={API_KEY}'''
    # response = requests.get(geo_url)
    # location = response.json()
    # convert lat and lon to string
    # lat = str(location['lat'])
    # lon = str(location['lon'])

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
        # getting temperature
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


@bot.command(pass_context = True)
async def myweather(myweather):
    '''
    if os.path.exists(f"./{str(myweather.author)}.pickle"):
        with open(f"{str(myweather.author)}.pickle", "rb") as input_file:
            user_dict = cPickle.load(input_file)
'''
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


@bot.command(pass_context = True)
async def mylocation(mylocation, zip_code, country_code):
    coords = geo_code(zip_code, country_code)
    user = str(mylocation.author)
    user_dict = {"username": user, "lat": coords[0], "lon": coords[1]}
    fieldnames = ['username','lat','lon']
    #with open(f"{str(mylocation.author)}.pickle", "wb") as output_file:
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
    # may be best to build database to store user data instead of pickle files


@bot.command(pass_context = True)
async def testsave(testsave):
    #with open(f"{str(testsave.author)}.pickle", "rb") as input_file:
    with open(os.path.join(os.getcwd(), "User_locations.csv"),"r+",encoding='UTF8',newline='') as input_file:
        csv_rows = csv.DictReader(input_file)
        for line in csv_rows:
                if testsave.author.name in line['username']:
                    user_dict = {
                        "user": line['username'],
                        "lat": line['lat'],
                        "lon": line['lon']
                    }

        #user_dict = cPickle.load(input_file)

    await testsave.author.send(f"your location is saved as user = {user_dict['user']}\nlat = {user_dict['lat']}\nlon = {user_dict['lon']}")
'''
@bot.command(pass_context = True)
async def f10(f10, zip_code, country_code):
    # command for forecast?

@bot.command(pass_context = True)
async def radar(radar, zip_code, country_code):
    # command for radar?
'''

bot.run(TOKEN)


# base URL

'''
print(f"Please enter the postal code for the city you would like weather data for")
ZIP_CODE = input()
print(f"Please enter the two digit country code for the city you are looking for")
COUNTRY_CODE = input()
print(f"Select weather Description: \nFull, Temp, Precipitation")
REPORT_TYPE = input()
REPORT_TYPE = REPORT_TYPE.lower()



# print(f"{response.json()}")


def weather():

        if REPORT_TYPE == "full":
            """
            print(f"{name:-^30}")
            print(f"Temperature: {temperature}")
            print(f"Humidity: {humidity}")
            print(f"Pressure: {pressure}")
            print(f"Weather Report: {report[0]['description']}")
            """
            # fix formatting of the tabs when putting string on second line
            return f"""{name:-^30} \nTemperature: {temperature} \nHumidity: {humidity} \n
                Pressure: {pressure} \nWeather Report: {report[0]['description']}"""
        elif REPORT_TYPE == "temp":
            return f"{name:-^30} \nTemperature: {temperature}"
        elif REPORT_TYPE == "precipitation":
            return f"{name:-^30} \nWeather Report: {report[0]['description']}"
    else:
        # showing the error message
        print(f"Error in the HTTP request: {response.status_code}")


a = weather()
print(a)
'''