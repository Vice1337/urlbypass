import discord
from discord.ext import commands
import aiohttp
import json

# made by vice
DISCORD_TOKEN = "token"
API_KEY = "your api key here"
UPLOAD_URL = "https://api.fivemanage.com/api/image"
TARGET_CHANNEL_ID = "channel id"

# bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.channel.id != TARGET_CHANNEL_ID:
        return

    if message.author.bot:
        return

    if not message.attachments: 
        return

    attachment = message.attachments[0]
    if not attachment.content_type.startswith("image"):
        await message.channel.send("Sadece görseller destekleniyor.")
        return

    uploader_name = message.author.name
    uploader_id = message.author.id

    embed = discord.Embed(
        title="__Accessing API...__",
        description="```Writing metadata...```"
    )
    loading_msg = await message.channel.send(embed=embed)

    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as img_response:
            image_data = await img_response.read()

        form_data = aiohttp.FormData()
        form_data.add_field("file", image_data, filename=attachment.filename)
        form_data.add_field("metadata", json.dumps({
            "uploader": {"userId": uploader_id, "name": uploader_name}
        }))

        headers = {"Authorization": API_KEY}
        async with session.post(UPLOAD_URL, data=form_data, headers=headers) as api_response:
            if api_response.status == 200:
                response_data = await api_response.json()

                embed = discord.Embed(
                    title="*Image uploaded*",
                    description=f"**Bypassed URL**```{response_data['url']}```"
                )
                embed.set_image(url=response_data['url'])
                embed.set_footer(text=f"Uploaded by: {uploader_name}")

                await loading_msg.delete()
                await message.channel.send(embed=embed)
                await message.delete()

            else:
                error_text = await api_response.text()
                await message.channel.send(f"Error: {error_text}")

bot.run(DISCORD_TOKEN)
