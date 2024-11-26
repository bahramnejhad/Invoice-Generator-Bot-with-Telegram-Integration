
# Invoice Generator Bot with Telegram Integration

This project is a Telegram bot that allows users to generate sales invoices by interacting with the bot. It collects user details, such as their phone number and store information, then allows them to add items to an invoice. Once the items are added, the bot generates a PDF invoice and sends it to the user.

### Features
- **User Data Management**: Stores user data such as phone number, store name, and seller name in a JSON file.
- **Invoice Generation**: Allows users to add items and generate a sales invoice in PDF format.
- **Telegram Integration**: Full integration with Telegram to interact with users and receive their inputs.
- **Arabic Support**: The invoice is generated with Arabic text and right-to-left support, using the `arabic_reshaper` and `bidi` libraries.

### Requirements
- Python 3.x
- `fpdf` for generating PDF invoices.
- `telegram` and `telegram.ext` for Telegram bot functionality.
- `arabic_reshaper` and `bidi` for Arabic text support.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/telegram-invoice-bot.git
   cd telegram-invoice-bot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Telegram bot:
   - Create a new bot via [BotFather](https://core.telegram.org/bots#botfather) and get your bot token.
   - Replace the placeholder token in the script with your actual bot token:
     ```python
     application = Application.builder().token("YOUR-BOT-TOKEN-HERE").build()
     ```

4. Run the bot:
   ```bash
   python bot.py
   ```

### Usage
1. Start the bot by sending `/start` to it.
2. Share your phone number and input your store information.
3. Add items to the invoice by entering product name, quantity, and price.
4. Request the invoice by clicking on the "Generate Invoice" option, and the bot will send you a PDF invoice.

### Notes
- The bot stores user data in a JSON file (`user_data.json`), which includes their phone number, store name, and invoice items.
- Ensure that the required fonts (`Vazir.ttf` and `Vazir-Bold.ttf`) are available in your project directory for Arabic text support.

