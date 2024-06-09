import os
import discord
from discord.ext import tasks, commands
from discord import app_commands
import requests

DISCORD_BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
MVSEP_API_KEY = os.environ['MVSEP_API_KEY']

# Initialize Discord bot
bot = discord.Client(command_prefix="!", intents=discord.Intents.default())
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
  await tree.sync()
  print(f'{bot.user.name} has connected to Discord!')

@tree.command(name="separate", description="Separate uploaded audio into its components")
async def separate(interaction: discord.Interaction, audio_file: discord.Attachment):
    await interaction.response.defer()
    try:
        # Download the file
        file_path = f"mvsep/{audio_file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        await audio_file.save(file_path)

        # Sending the file to MVSEP API
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                data = {
                    'api_token': MVSEP_API_KEY,
                    'sep_type': '35',
                    'add_opt1': '5', 
                    'audiofile': f
                }
                async with session.post("https://mvsep.com/api/separation/create", headers={'Authorization': f'Bearer {MVSEP_API_KEY}'}, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        job_hash = result['data']['hash']

                        # Wait for the job to finish
                        while True:
                            await asyncio.sleep(5)  # Check every 5 seconds
                            async with session.get(f'https://mvsep.com/api/separation/get?hash={job_hash}') as status_response:
                                if status_response.status == 200:
                                    status_result = await status_response.json()
                                    if status_result['status'] == 'done':
                                        separated_files = status_result['data']['files']
                                        urls = [file['url'] for file in separated_files]
                                        await interaction.followup.send(f"Audio separated successfully! Download them here:\n" + "\n".join(urls))
                                        break
                                    elif status_result['status'] == 'failed':
                                        await interaction.followup.send(f"Audio separation failed: {status_result['data']['message']}")
                                        break
                                else:
                                    await interaction.followup.send(f"Failed to check status. Status code: {status_response.status}")
                                    break

                    else:
                        await interaction.followup.send(f"Failed to separate audio. Status code: {response.status}")
        
        # Clean up the downloaded file
        os.remove(file_path)
    except aiohttp.ClientConnectorError as e:
        await interaction.followup.send(f"Error connecting to the MVSEP API: {e}")
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")

bot.run(DISCORD_BOT_TOKEN)
