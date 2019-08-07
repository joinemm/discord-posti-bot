from discord.ext import commands
import os


TOKEN = os.environ.get('POSTI_TOKEN')
client = commands.Bot(command_prefix='p.', case_insensitive=True)

extensions = ['posti']


@client.event
async def on_ready():
    print("Connected to Discord")

if __name__ == '__main__':
    for extension in extensions:
        try:
            client.load_extension(extension)
            print(f"Loaded {extension}.py")
        except Exception as error:
            print(f"ERROR loading {extension} [{error}]")

    client.run(TOKEN)
