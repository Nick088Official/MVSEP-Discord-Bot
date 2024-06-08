   import os
   import discord
   from discord.ext import commands
   from dotenv import load_dotenv
   import requests

   load_dotenv()
   DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
   MVSEP_API_KEY = os.getenv('MVSEP_API_KEY')

   bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())

   @bot.event
   async def on_ready():
       print(f'{bot.user.name} has connected to Discord!')

   @bot.slash_command(name='separate', description='Separate audio using MVSEP')
   async def separate(ctx, url: str):
       await ctx.defer()
       api_url = 'https://mvsep.com/api/separate'
       headers = {'Authorization': f'Bearer {MVSEP_API_KEY}'}
       payload = {'url': url}

       response = requests.post(api_url, headers=headers, json=payload)
       if response.status_code == 200:
           data = response.json()
           await ctx.send(f"Separation complete! Download links:

Vocal: {data['vocal']}
Instrumental: {data['instrumental']}")
       else:
           await ctx.send(f"Error: {response.status_code} - {response.text}")

   bot.run(DISCORD_TOKEN)
