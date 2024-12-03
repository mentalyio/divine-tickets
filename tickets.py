import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix=",", intents=intents)

# Define the hex color as a discord.Color
custom_color = discord.Color.from_rgb(193, 248, 255)

# Ticket Panel Command
@bot.command()
async def ticketpanel(ctx):
    # Ensure the command can only be used by authorized personnel
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You don't have permission to use this command.")
        return

    channel_id = 1312830613803237376  # Replace with the ticket panel channel ID
    channel = bot.get_channel(channel_id)

    # Create an embed
    embed = discord.Embed(
        title="<:divine:1312873678655983708> Ticket Panel",
        description=(
            "<:WhiteStar:1313154757069897768> **Buy Slot**: Open to buy a slot\n"
            "\n"
            "<:WhiteStar:1313154757069897768> **Report**: Open to report a slot owner\n"
            "\n"
            "<:WhiteStar:1313154757069897768> **Support**: Open for support\n"
            "\n"
            "<:checkmark:1312865699219243110> Don't spam ping\n"
            "<:checkmark:1312865699219243110> No answer = ban\n"
            "<:checkmark:1312865699219243110> Don't disrespect staff\n"
        ),
        color=custom_color
    )
    embed.set_footer(text="")

    # Create a dropdown
    class TicketDropdown(Select):
        def __init__(self):
            options = [
                discord.SelectOption(
                    label="Buy Slot",
                    description="Open to buy a slot",
                    emoji="<:WhiteStar:1313154757069897768>"  # Custom emoji for Buy Slot
                ),
                discord.SelectOption(
                    label="Report",
                    description="Open to report a slot owner",
                    emoji="<:WhiteStar:1313154757069897768>"  # Custom emoji for Report
                ),
                discord.SelectOption(
                    label="Support",
                    description="Open for support",
                    emoji="<:WhiteStar:1313154757069897768>"  # Custom emoji for Support
                ),
            ]
            super().__init__(placeholder="Choose an option", options=options)

        async def callback(self, interaction: discord.Interaction):
            # Define category IDs
            category_ids = {
                "Buy Slot": 1313155376899686420,
                "Report": 1313155389193191424,
                "Support": 1313155401210138644
            }

            selected_option = self.values[0]  # Get selected option
            category_id = category_ids[selected_option]  # Find the category ID
            category = interaction.guild.get_channel(category_id)  # Get the category

            if selected_option == "Buy Slot":
                # Request further details for the "Buy Slot" option
                await interaction.response.send_message("You selected Buy Slot. Please fill in the details.")

                # Trigger the modal for the user to input the details
                modal = BuySlotModal()
                await interaction.response.send_modal(modal)

            elif category:
                # Create a private channel for the user in the specified category
                ticket_channel = await interaction.guild.create_text_channel(
                    name=f"{selected_option.lower().replace(' ', '-')}-{interaction.user.name}",
                    category=category,
                    overwrites={
                        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    }
                )
                # Notify the user
                await interaction.response.send_message(
                    f"Ticket created in {ticket_channel.mention}!", ephemeral=True
                )
                # Send a welcome message in the ticket channel
                await ticket_channel.send(
                    content=f"Hello {interaction.user.mention}, thank you for opening a ticket. Our team will assist you shortly."
                )
            else:
                await interaction.response.send_message(
                    "Failed to create a ticket. Please contact an administrator.", ephemeral=True
                )

    # Create a view for the dropdown
    class TicketView(View):
        def __init__(self):
            super().__init__()
            self.add_item(TicketDropdown())

    # Send the embed with the dropdown menu to the specified channel
    await channel.send(embed=embed, view=TicketView())

# Modal for the Buy Slot
class BuySlotModal(Modal):
    def __init__(self):
        super().__init__(title="Buy Slot - Details")

        self.duration = TextInput(
            label="Duration (Week/Month/Lifetime)",
            placeholder="e.g., Week",
            required=True,
            max_length=50
        )
        self.category = TextInput(
            label="Category (e.g., cat1, cat2)",
            placeholder="e.g., cat1",
            required=True,
            max_length=50
        )
        self.payment = TextInput(
            label="Payment Method (BTC, LTC, ETH, PayPal)",
            placeholder="e.g., BTC",
            required=True,
            max_length=50
        )

        self.add_item(self.duration)
        self.add_item(self.category)
        self.add_item(self.payment)

    async def callback(self, interaction: discord.Interaction):
        # Get the user's inputs from the modal
        duration = self.duration.value
        category = self.category.value
        payment = self.payment.value

        # Confirm the slot details to the user
        await interaction.response.send_message(
            f"Thank you! Your slot details are:\n"
            f"**Duration**: {duration}\n"
            f"**Category**: {category}\n"
            f"**Payment**: {payment}\n"
            f"Your request is being processed.",
            ephemeral=True
        )

# Command to close a ticket
@bot.command()
async def ticketclose(ctx):
    if ctx.channel.category:  # Check if the channel belongs to a category
        await ctx.send("This ticket will be closed immediately.")
        await ctx.channel.delete()  # Delete the channel immediately
    else:
        await ctx.send("This command can only be used in a ticket channel.")

# Command to add a user to a ticket
@bot.command()
async def ticketadd(ctx, member: discord.Member):
    if ctx.channel.category:
        # Update permissions to allow the mentioned user to view and send messages in the ticket channel
        await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
        await ctx.send(f"{member.mention} has been added to the ticket.")
    else:
        await ctx.send("This command can only be used in a ticket channel.")

# Run the bot
bot.run("MTMxMzE2MzYwOTQ5MjI5MTYyNQ.GeSkbq.DbarBftri4DktfZimqa9G_4dFd3-x-Nq5isNAY")
