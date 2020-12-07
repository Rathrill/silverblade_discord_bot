import configparser

config = configparser.RawConfigParser()
config.read('config/config.properties')

DISCORD_APPLICATION_CHANNEL = config.get('Discord', 'applications.channel')
DISCORD_GUILD = config.get('Discord', 'guild')
DISCORD_OFFICER_CHANNEL = config.get('Discord', 'officer.channel')

GAME_GUILD = config.get('Game', 'guild')
GAME_REALM = config.get('Game', 'realm')
GAME_REGION = config.get('Game', 'region')
