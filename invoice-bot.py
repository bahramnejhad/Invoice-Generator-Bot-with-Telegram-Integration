from fpdf import FPDF
import os
import json
from telegram import ReplyKeyboardMarkup, KeyboardButton, Contact
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging
import arabic_reshaper
from bidi.algorithm import get_display

# تنظیمات اولیه
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# مسیر فایل JSON برای ذخیره‌سازی اطلاعات
USER_DATA_FILE = 'user_data.json'

# تابع ذخیره‌سازی اطلاعات کاربر
def save_user_data(user_id, data):
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as file:
            user_data = json.load(file)
    else:
        user_data = {}

    user_data[str(user_id)] = data
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(user_data, file, ensure_ascii=False, indent=4)

# تابع دریافت اطلاعات کاربر
def get_user_data(user_id):
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as file:
            user_data = json.load(file)
            return user_data.get(str(user_id), {})
    return {}

# کلاس ایجاد فاکتور
class InvoicePDF(FPDF):
    def header(self):
        if os.path.exists('Vazir.ttf'):
            self.add_font('Vazir', 'B', 'Vazir-Bold.ttf', uni=True)
            self.add_font('Vazir', '', 'Vazir.ttf', uni=True)
            self.set_font('Vazir', '', 14)
        else:
            self.set_font('Arial', '', 14)
            logger.warning("فایل فونت یافت نشد، از Arial استفاده می‌شود.")
        # عنوان فاکتور
        header_text = get_display(arabic_reshaper.reshape('فاکتور فروش'))
        self.cell(0, 10, header_text, 0, 1, 'C')
        self.ln(10)

        # اطلاعات فروشنده و خریدار
        user_data = get_user_data(self.user_id)
        store_name = user_data.get('store_name', 'نام فروشگاه تعریف نشده')
        seller_name = user_data.get('seller_name', 'نام فروشنده تعریف نشده')
        self.set_font('Vazir' if os.path.exists('Vazir.ttf') else 'Arial', '', 12)
        self.cell(95, 10, get_display(arabic_reshaper.reshape(f'تاریخ: 1402/03/13')), 1, 0, 'R')
        self.cell(95, 10, get_display(arabic_reshaper.reshape('شماره فاکتور: 0238')), 1, 1, 'R')
        self.cell(95, 10, get_display(arabic_reshaper.reshape(f'توسط: {seller_name}')), 1, 0, 'R')
        self.cell(95, 10, get_display(arabic_reshaper.reshape(f'فروشگاه: {store_name}')), 1, 1, 'R')
        self.ln(10)

    def footer(self):
        self.set_y(-30)
        self.set_font('Vazir' if os.path.exists('Vazir.ttf') else 'Arial', '', 12)
        footer_text = get_display(arabic_reshaper.reshape('مبلغ به حروف: سه میلیون و چهارصد و چهل و دو هزار ریال'))
        self.cell(0, 10, footer_text, 0, 1, 'C')
        self.ln(5)
        self.cell(95, 10, get_display(arabic_reshaper.reshape('امضاء فروشنده')), 0, 0, 'L')
        self.cell(95, 10, get_display(arabic_reshaper.reshape('امضاء خریدار')), 0, 1, 'R')

    def invoice_body(self, items):
        # Table Header
        self.set_font('Vazir' if os.path.exists('Vazir.ttf') else 'Arial', '', 12)
        self.cell(40, 10, get_display(arabic_reshaper.reshape('قیمت کل (ریال)')), 1, 0, 'C')
        self.cell(40, 10, get_display(arabic_reshaper.reshape('قیمت واحد (ریال)')), 1, 0, 'C')
        self.cell(20, 10, get_display(arabic_reshaper.reshape('تعداد')), 1, 0, 'C')
        self.cell(60, 10, get_display(arabic_reshaper.reshape('شرح کالا یا خدمات')), 1, 0, 'C')
        self.cell(10, 10, get_display(arabic_reshaper.reshape('ردیف')), 1, 1, 'C')

        # Table Body
        self.set_font('Vazir' if os.path.exists('Vazir.ttf') else 'Arial', '', 12)
        total_price = 0
        for idx, item in enumerate(items, start=1):
            name, quantity, unit_price = item
            total = quantity * unit_price
            total_price += total
            idx_text = str(idx)
            name_text = get_display(arabic_reshaper.reshape(name))
            quantity_text = str(quantity)
            unit_price_text = get_display(arabic_reshaper.reshape(f'{unit_price:,}'))
            total_text = get_display(arabic_reshaper.reshape(f'{total:,}'))
            self.cell(40, 10, total_text, 1, 0, 'C')
            self.cell(40, 10, unit_price_text, 1, 0, 'C')
            self.cell(20, 10, quantity_text, 1, 0, 'C')
            self.cell(60, 10, name_text, 1, 0, 'C')
            self.cell(10, 10, idx_text, 1, 1, 'C')

        # Total Price
        total_price_text = get_display(arabic_reshaper.reshape(f'{total_price:,} ریال'))
        self.cell(40, 10, total_price_text, 1, 0, 'C')
        self.cell(130, 10, get_display(arabic_reshaper.reshape('جمع کل')), 1, 1, 'R')

# تابع ایجاد فاکتور
def generate_invoice_pdf(file_path, items, user_id):
    pdf = InvoicePDF()
    pdf.user_id = user_id
    pdf.add_page()
    pdf.invoice_body(items)
    pdf.output(file_path)

# تابع مدیریت بات تلگرام
async def start(update, context):
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    if 'phone_number' in user_data:
        # اگر شماره تلفن قبلا ذخیره شده بود، مستقیما منوی افزودن آیتم و صدور فاکتور را نمایش دهد
        keyboard = [[KeyboardButton("افزودن آیتم"), KeyboardButton("صدور فاکتور")]]
        reply_markup = ReplyKeyboardMarkup(keyboard)
        await update.message.reply_text('سلام! لطفاً انتخاب کنید:', reply_markup=reply_markup)
    else:
        # اگر شماره تلفن ذخیره نشده بود، درخواست اشتراک‌گذاری شماره تلفن را ارسال کند
        contact_keyboard = KeyboardButton(text="اشتراک‌گذاری شماره تلفن", request_contact=True)
        reply_markup = ReplyKeyboardMarkup([[contact_keyboard]], one_time_keyboard=True)
        await update.message.reply_text('لطفاً شماره تلفن خود را به اشتراک بگذارید:', reply_markup=reply_markup)

async def contact_handler(update, context):
    contact: Contact = update.effective_message.contact
    user_id = update.effective_user.id
    phone_number = contact.phone_number
    user_data = get_user_data(user_id)
    user_data['phone_number'] = phone_number
    user_data['state'] = 'awaiting_store_info'
    save_user_data(user_id, user_data)
    await update.message.reply_text('شماره تلفن شما ذخیره شد. لطفاً نام فروشگاه و نام فروشنده را به شکل زیر وارد کنید:\n\nفروشگاه: نام فروشگاه - فروشنده: نام فروشنده')

async def handle_store_info(update, context):
    user_id = update.effective_user.id
    user_data = get_user_data(user_id)
    if user_data.get('state') == 'awaiting_store_info':
        try:
            store_info = update.message.text.split('-')
            store_name = store_info[0].split(':')[1].strip()
            seller_name = store_info[1].split(':')[1].strip()
            user_data['store_name'] = store_name
            user_data['seller_name'] = seller_name
            user_data['state'] = 'ready'
            save_user_data(user_id, user_data)
            await update.message.reply_text('اطلاعات فروشگاه شما ذخیره شد.')
            # نمایش منوی افزودن آیتم و صدور فاکتور پس از ذخیره اطلاعات فروشگاه
            keyboard = [[KeyboardButton("افزودن آیتم"), KeyboardButton("صدور فاکتور")]]
            reply_markup = ReplyKeyboardMarkup(keyboard)
            await update.message.reply_text('لطفاً انتخاب کنید:', reply_markup=reply_markup)
        except (IndexError, ValueError):
            await update.message.reply_text('فرمت وارد شده صحیح نیست. لطفاً به شکل صحیح وارد کنید:\n\nفروشگاه: نام فروشگاه - فروشنده: نام فروشنده')
    else:
        await handle_add_item(update, context)

async def handle_add_item(update, context):
    if update.message.text == "صدور فاکتور":
        await generate_invoice(update, context)
        return
    try:
        item_text = update.message.text.split('-')
        name_quantity = item_text[0].strip()
        name, quantity = name_quantity.split(':')
        name = name.strip()
        quantity = int(quantity.strip())
        unit_price = int(item_text[1].strip())
        if 'items' not in context.user_data:
            context.user_data['items'] = []
        context.user_data['items'].append((name, quantity, unit_price))
        await update.message.reply_text(f'محصول {name} با تعداد {quantity} و قیمت واحد {unit_price} تومان به فاکتور اضافه شد.')
    except (IndexError, ValueError):
        await update.message.reply_text("فرمت وارد شده صحیح نیست. لطفاً به شکل صحیح وارد کنید: نازل: تعداد-قیمت واحد")

async def generate_invoice(update, context):
    user_id = update.effective_user.id
    items = context.user_data.get('items', [])
    if not items:
        await update.message.reply_text("هیچ آیتمی برای صدور فاکتور وجود ندارد.")
        return
    file_path = 'invoice.pdf'
    generate_invoice_pdf(file_path, items, user_id)
    await update.message.reply_document(document=open(file_path, 'rb'))

# تابع اصلی
def main():
    # توکن بات خود را اینجا وارد کنید
    application = Application.builder().token("YourToken").build()

    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_store_info))
    application.add_handler(MessageHandler(filters.Regex('^افزودن آیتم$'), handle_add_item))
    application.add_handler(MessageHandler(filters.Regex('^صدور فاکتور$'), generate_invoice))

    # شروع بات
    application.run_polling()

if __name__ == '__main__':
    main()
