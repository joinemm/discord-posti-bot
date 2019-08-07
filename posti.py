import discord
from discord.ext import commands
import requests
import arrow
import json


class Posti(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.posti_orange = discord.Color.from_rgb(255, 127, 0)

    @commands.command()
    async def info(self, ctx, seurantakoodi):
        shipment = get_shipment_data(seurantakoodi)

        content = discord.Embed(color=self.posti_orange)
        content.set_author(name="Lähetyksen tiedot",
                           icon_url=self.client.user.avatar_url,
                           url=f"https://www.posti.fi/henkiloasiakkaat/seuranta/#/lahetys/{seurantakoodi}")

        content.description = "```" \
            f"Lähetystunnus     {shipment.get('trackingCode')}\n" \
            f"Kuljetuspalvelu   {shipment.get('product')['name']['fi']}\n" \
            f"Paino             {shipment.get('weight')} Kg\n" \
            f"Tilavuus          {shipment.get('volume')} m3\n" \
            f"Mitat             {shipment.get('width')} x {shipment.get('depth')} x {shipment.get('height')}\n" \
            f"Kohdepostinumero  {shipment.get('destinationPostcode')}," \
            f"{shipment.get('destinationCity')}," \
            f"{shipment.get('destinationCountry')}```"

        await ctx.send(embed=content)

    @commands.command()
    async def events(self, ctx, seurantakoodi):
        shipment = get_shipment_data(seurantakoodi)

        events = shipment.get('events')

        content = discord.Embed(color=self.posti_orange)
        content.set_author(name="Lähetyksen tapahtumat",
                           icon_url=self.client.user.avatar_url,
                           url=f"https://www.posti.fi/henkiloasiakkaat/seuranta/#/lahetys/{seurantakoodi}")

        for event in events:
            description = event.get('description')['fi']
            time = timestamp_parse(event.get('timestamp'))
            location = f"{event.get('locationName')} {event.get('locationCode') or ''}"
            content.add_field(name=description, value=f"`{time}` {location}", inline=False)

        await ctx.send(embed=content)

    @commands.command()
    async def status(self, ctx, seurantakoodi):
        shipment = get_shipment_data(seurantakoodi)

        content = discord.Embed(color=self.posti_orange)
        content.set_author(name=seurantakoodi,
                           icon_url=self.client.user.avatar_url,
                           url=f"https://www.posti.fi/henkiloasiakkaat/seuranta/#/lahetys/{seurantakoodi}")

        phase = shipment.get('phase')
        content.set_thumbnail(url=f'https://www.posti.fi/henkiloasiakkaat/seuranta/assets/images/PARCEL_{phase}.png')

        content.add_field(name="Arvioitu toimitusaika", value=timestamp_parse(shipment.get('estimatedDeliveryTime')))

        recent_event = shipment.get('events')[0]
        content.add_field(name=recent_event.get('description')['fi'], value=recent_event.get('additionalInfo')['fi'])

        await ctx.send(embed=content)


def setup(client):
    client.add_cog(Posti(client))


def get_shipment_data(seurantakoodi):
    url = 'https://www.posti.fi/henkiloasiakkaat/seuranta/api/shipments'
    response = requests.post(url, json={'trackingCodes': [seurantakoodi]}).json()
    print(json.dumps(response, indent=4))
    if response['shipments']:
        return response['shipments'][0]
    else:
        return None


def timestamp_parse(timestamp):
    return arrow.get(timestamp).astimezone(arrow.now('Europe/Helsinki').tzinfo).strftime('%-d.%-m.%Y klo %H:%M')
