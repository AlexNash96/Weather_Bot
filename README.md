# WeatherBot
Discord weather bot code repository

## This is the beginning of Alex's discord bot to provide weather updates to users upon request

## Chat commands
Below is a list of the commands that are currently available in WeatherBot

1. !weather <postal_code> / !weather <postal_code> <country_code>
    This command will provide an outoput with weather information for the requested postal code or postal code and country code combination. This report is headed with the name of the city/town that the postal code identifies and includes temperature, humidity, conditions (i.e. cloudy, partly cloudy, sunny, raining, etc), and the air quality index.

    The command can be used with only a postal code when looking up weather for the US, or for international weather, the 2 character country code can also be defined. 

2. !mylocation <postal_code> <country_code>
    This command can be used to define your location to the bot. This is best used in a direct message to the bot to prevent the information from being posted in a Discord server where all users could see.

3. !myweather
    The !myweather command provides a similar weather report to the !weather command, however, in this scenario, it does not show the location that the weather is reported for. This allows users to receive a weather report from the bot in a Discord server without publically displaying their location. 

4. !testsave
    For testing purposes, the !testsave command was implemented to be used during development to ensure the bot stored data correctly. After more updates have been made, and the bot is deployed to a server, this command will only be available in a test version of the bot. 
