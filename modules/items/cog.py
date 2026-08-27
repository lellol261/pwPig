import nextcord
from nextcord.ext import commands
import sqlite3

database = sqlite3.connect('items.db')
cursor = database.cursor()
database.execute('''CREATE TABLE IF NOT EXISTS item(item STRING, quantity INT, purchased INT, price INT, suggested INT, sold INT, profit INT)''')

class db(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Initial Add item
    @nextcord.slash_command(description="Add an item to the database")
    async def add(self, interaction: nextcord.Interaction, item: str, quantity: int):
        item = item.lower()
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_item_unique ON item(item)")
        try:
            cursor.execute("INSERT INTO item VALUES (?,?,0,0,0,0,0)", (item, quantity))
            database.commit()
            await interaction.response.send_message("Item added to database!", ephemeral=True)
        except nextcord.Forbidden:
            pass
        except database.IntegrityError:
            await interaction.response.send_message("That item already exists in the database!", ephemeral=True)


    # Completely delete item
    @nextcord.slash_command(description="Delete item")
    async def delete(self, interaction: nextcord.Interaction, item: str):
        item = item.lower()
        query = "DELETE FROM item WHERE item = ?"
        cursor.execute(query, (item,))
        database.commit()
        if cursor.rowcount == 0:
            await interaction.response.send_message("That item doesn't exist in the database!", ephemeral=True)
        else:
            await interaction.response.send_message("Item removed from database!", ephemeral=True)

# Update quantity
    @nextcord.slash_command(description="Update quantity")
    async def update(self, interaction: nextcord.Interaction, item: str, quantity: int):
        item = item.lower()
        query = "UPDATE item SET quantity = quantity + ? WHERE item = ?"
        cursor.execute(query, (quantity, item))
        if quantity <= 0:
            await interaction.response.send_message("Quantity must be a positive number!", ephemeral=True)
            return
        database.commit()
        if cursor.rowcount == 0:
            await interaction.response.send_message("That item doesn't exist in the database!", ephemeral=True)
        else:
            await interaction.response.send_message("Quantity updated!", ephemeral=True)
# Purchase command
    @nextcord.slash_command(description="Purchasing an item")
    async def purchase(self, interaction: nextcord.Interaction, item: str, purchased: int, price: int):
        item = item.lower()

        cursor.execute("SELECT purchased, price FROM item WHERE item = ?", (item,))
        row = cursor.fetchone()
        if row is None:
            await interaction.response.send_message("That item doesn't exist in the database!", ephemeral=True)
            return

        old_purchased, old_price = row

        new_purchased = old_purchased + purchased
        new_price = old_price + (price * purchased)

        if new_purchased == 0:
            suggested = 0
        else:
            suggested = (new_price / new_purchased) * 1.25

        cursor.execute(
            "UPDATE item SET purchased = ?, price = ?, suggested = ?, quantity = quantity + ? WHERE item = ?",
            (new_purchased, new_price, suggested, purchased, item),
        )
        database.commit()

        await interaction.response.send_message(
            f"Purchase recorded! Purchased: {new_purchased}, Quantity: +{purchased}, Price total: {new_price}, Suggested: {suggested:.2f}",
        )
# Selling an item
    @nextcord.slash_command(description="Selling an item")
    async def sold(self, interaction: nextcord.Interaction, item: str, sold: int, profit: int):
        item = item.lower()

        cursor.execute("SELECT quantity FROM item WHERE item = ?", (item,))
        row = cursor.fetchone()
        if row is None:
            await interaction.response.send_message("That item doesn't exist in the database!", ephemeral=True)
            return

        current_quantity = row[0]
        if sold > current_quantity:
            await interaction.response.send_message(
                f"Not enough in stock! You have {current_quantity} of {item}.", ephemeral=True
            )
            return

        cursor.execute(
            "UPDATE item SET sold = sold + ?, quantity = quantity - ?, profit = profit + ? WHERE item = ?",
            (sold, sold, profit, item),
        )
        database.commit()

        await interaction.response.send_message(
            f"Sale recorded! Sold: {sold}, New quantity: {current_quantity - sold}, Profit added: {profit}",

        )
# Search for an item
    @nextcord.slash_command(description="Search for an item")
    async def search(self, interaction: nextcord.Interaction, item: str):
        item = item.lower()

        cursor.execute("SELECT quantity, suggested FROM item WHERE item = ?", (item,))
        row = cursor.fetchone()
        if row is None:
            await interaction.response.send_message("That item doesn't exist in the database!", ephemeral=True)
            return

        quantity, suggested = row

        await interaction.response.send_message(
            f"**{item}**\nQuantity in stock: {quantity}\n~Price: ${suggested:,.2f}",

        )
# Displays the money stats for 1 item
    @nextcord.slash_command(description="Displays the money stats for 1 item")
    async def singleproft(self, interaction: nextcord.Interaction, item: str):
        item = item.lower()

        cursor.execute("SELECT price, profit FROM item WHERE item = ?", (item,))
        row = cursor.fetchone()
        if row is None:
            await interaction.response.send_message("That item doesn't exist in the database!", ephemeral=True)
            return

        price, profit = row
        difference = profit - price

        await interaction.response.send_message(
            f"**{item}**\nSpent: ${price:,.2f}\nMade: ${profit:,.2f}\nProfit: ${difference:,.2f}",

        )
    # Total money stats
    @nextcord.slash_command(description="Display total money stats")
    async def money(self, interaction: nextcord.Interaction):
        cursor.execute("SELECT SUM(price), SUM(profit) FROM item")
        row = cursor.fetchone()

        total_price = row[0] or 0
        total_profit = row[1] or 0
        difference = total_profit - total_price

        await interaction.response.send_message(
            f"**Overall Totals**\nSpent: ${total_price:,.2f}\nMade: ${total_profit:,.2f}\nProfit: ${difference:,.2f}",

        )
def setup(bot):
    bot.add_cog(db(bot))