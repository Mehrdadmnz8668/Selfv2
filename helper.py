from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CallbackQueryHandler, ContextTypes, InlineQueryHandler, MessageHandler, filters
import logging

TOKEN = "0000" # توکن ربات هلپر

# توجه برای اینکه هلپر کار کنه بابد بخش اینلاین مود ربات رو توی بات فادر فعال کنید

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
HELP_TEXTS = {
    "main": """
🤖 <b>پنل مدیریت ربات</b>

🔧 <b>دستورات موجود:</b>

<code>تایم روشن</code>
<code>تایم خاموش</code>
<code>عکس سیو</code> (ریپلای)
<code>سیو @یوزرنیم</code>
<code>وضعیت</code>
<code>لیست فونت</code>
<code>تنظیم فونت عدد</code>
<code>قیمت ارز</code>
<code>اسپم تعداد متن</code>
<code>بولد روشن</code>
<code>بولد خاموش</code>
<code>دشمن</code> (ریپلای)
<code>حذف دشمن</code> (ریپلای)
<code>لیست دشمن</code>
<code>دشمنان</code>
<code>پاک کردن دشمنان</code>
<code>پاسخ افزودن متن|پاسخ</code>
<code>پاسخ حذف متن</code>
<code>پاسخ لیست</code>
<code>فحش افزودن متن</code>
<code>فحش حذف متن</code>

👇 برای مشاهده راهنمای هر بخش، دکمه مربوطه را انتخاب کنید.
""",

    "time": """
⏰ <b>مدیریت تایم</b>

<b>دستورات قابل کپی:</b>
<code>تایم روشن</code>
<code>تایم خاموش</code>

<b>کاربرد:</b>
نمایش زمان کنار نام کاربری
آپدیت خودکار هر دقیقه
فونت‌های مختلف برای زمان

<b>فونت‌های موجود:</b>
𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗 - فونت 1
𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵 - فونت 2  
０１２３４５６７８９ - فونت 3
𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫 - فونت 4
𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡 - فونت 5
0҉1҉2҉3҉4҉5҉6҉7҉8҉9҉ - فونت 6
""",

    "photo": """
📸 <b>ذخیره عکس تایمدار</b>

<b>دستور قابل کپی:</b>
<code>عکس سیو</code> (ریپلای روی عکس)

<b>کاربرد:</b>
ذخیره دستی عکس‌های تایمدار
ذخیره در پوشه saved_photos
ارسال اطلاعات کامل کاربر

<b>نکته:</b>
فقط روی عکس‌های تایمدار کار می‌کند
عکس معمولی قابل ذخیره نیست
""",

    "backup": """
💾 <b>پشتیبان‌گیری</b>

<b>دستور قابل کپی:</b>
<code>سیو @یوزرنیم</code>

<b>مثال:</b>
<code>سیو @username</code>

<b>کاربرد:</b>
ذخیره تاریخچه چت در فایل متنی
ارسال فایل به پیام‌های ذخیره شده
فرمت TXT با اطلاعات کامل
""",

    "status": """
📊 <b>وضعیت سلف</b>

<b>دستور قابل کپی:</b>
<code>وضعیت</code>

<b>کاربرد:</b>
نمایش وضعیت فعلی سلف
نمایش تنظیمات فعال/غیرفعال
نمایش تعداد دشمنان و پاسخ‌های خودکار
لیست دشمنان و پاسخ‌های تنظیم شده
""",

    "font": """
🔤 <b>مدیریت فونت</b>

<b>دستورات قابل کپی:</b>
<code>لیست فونت</code>
<code>تنظیم فونت 1</code> تا <code>تنظیم فونت 6</code>

<b>کاربرد:</b>
تغییر فونت نمایش زمان
پیش‌نمایش فونت‌های مختلف
اعمال فونت روی زمان به صورت زنده
""",

    "price": """
💱 <b>قیمت ارز</b>

<b>دستور قابل کپی:</b>
<code>قیمت ارز</code>

<b>مثال‌ها:</b>
<code>قیمت BTC</code>
<code>قیمت ETH</code>
<code>قیمت TON</code>

<b>کاربرد:</b>
نمایش قیمت لحظه‌ای ارزهای دیجیتال
نمایش قیمت تومانی و دلاری
نمایش تغییرات 24 ساعته
اتصال به API نوبیتکس
""",

    "spam": """
🔁 <b>ارسال اسپم</b>

<b>دستور قابل کپی:</b>
<code>اسپم تعداد متن</code>

<b>مثال‌ها:</b>
<code>اسپم 10 سلام</code>
<code>اسپم 5 تست</code>

<b>کاربرد:</b>
ارسال پیام تکراری
حداکثر 50 پیام در یک دستور
قابلیت ریپلای روی پیام
""",

    "bold": """
🔠 <b>حالت بولد خودکار</b>

<b>دستورات قابل کپی:</b>
<code>بولد روشن</code>
<code>بولد خاموش</code>

<b>کاربرد:</b>
فعال/غیرفعال کردن بولد خودکار
تبدیل خودکار تمام پیام‌ها به بولد
پیام‌ها به صورت **متن** ارسال می‌شوند
فقط برای پیام‌های متنی کاربر
""",

    "enemy": """
👿 <b>مدیریت دشمنان</b>

<b>دستورات قابل کپی:</b>
<code>دشمن</code> (ریپلای روی پیام کاربر)
<code>حذف دشمن</code> (ریپلای روی پیام کاربر)
<code>لیست دشمن</code>
<code>دشمنان</code>
<code>پاک کردن دشمنان</code>

<b>کاربرد:</b>
افزودن کاربر به لیست دشمنان
ارسال خودکار فحش رندوم به دشمنان
مدیریت لیست دشمنان
نمایش اطلاعات کامل دشمنان
حذف دشمن از لیست
""",

    "autoreply": """
🤖 <b>پاسخ خودکار</b>

<b>دستورات قابل کپی:</b>
<code>پاسخ افزودن سلام|سلام چطوری</code>
<code>پاسخ حذف سلام</code>
<code>پاسخ لیست</code>

<b>مثال‌ها:</b>
<code>پاسخ افزودن سلا|سلام عزیزم</code>
<code>پاسخ افزودن چطوری|خوبم ممنون</code>
<code>پاسخ حذف سلا</code>

<b>کاربرد:</b>
تنظیم پاسخ خودکار برای کلمات خاص
پاسخ‌دهی خودکار به کاربران عادی
مدیریت پاسخ‌های خودکار
لیست پاسخ‌های تنظیم شده
""",

    "insult": """
💢 <b>مدیریت فحش‌ها</b>

<b>دستورات قابل کپی:</b>
<code>فحش افزودن متن فحش</code>
<code>فحش حذف متن فحش</code>

<b>مثال‌ها:</b>
<code>فحش افزودن تو احمقی</code>
<code>فحش افزودن برو گمشو</code>
<code>فحش حذف تو احمقی</code>

<b>کاربرد:</b>
افزودن فحش‌های جدید به لیست
حذف فحش‌های موجود
ارسال رندوم فحش به دشمنان
ذخیره در فایل insults.txt
""",
}

def get_main_menu(user_id):
    keyboard = [
        [InlineKeyboardButton("🆔 ایدی", callback_data=f"help_id_{user_id}")],
        [
            InlineKeyboardButton("⏰ تایم", callback_data=f"help_time_{user_id}"),
            InlineKeyboardButton("📸 عکس", callback_data=f"help_photo_{user_id}")
        ],
        [InlineKeyboardButton("💾 پشتیبان", callback_data=f"help_backup_{user_id}")],
        [
            InlineKeyboardButton("📊 وضعیت", callback_data=f"help_status_{user_id}"),
            InlineKeyboardButton("🔤 فونت", callback_data=f"help_font_{user_id}")
        ],
        [InlineKeyboardButton("🔠 بولد", callback_data=f"help_bold_{user_id}")],
        [
            InlineKeyboardButton("💱 قیمت", callback_data=f"help_price_{user_id}"),
            InlineKeyboardButton("🔁 اسپم", callback_data=f"help_spam_{user_id}")
        ],
        [InlineKeyboardButton("👿 دشمنان", callback_data=f"help_enemy_{user_id}")],
        [
            InlineKeyboardButton("🤖 پاسخ خودکار", callback_data=f"help_autoreply_{user_id}"),
            InlineKeyboardButton("💢 فحش", callback_data=f"help_insult_{user_id}")
        ],
        [InlineKeyboardButton("❌ بستن", callback_data=f"help_close_{user_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_button(user_id):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data=f"help_back_{user_id}")]])

def get_reopen_button(user_id):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔄 بازکردن پنل", callback_data=f"help_reopen_{user_id}")]])

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = "<b>سلام به هلپر سلف خوش امدی برای کمک گرفتن میتونی از دکمه های زیر استفاده کنی 👇</b>"
    await update.message.reply_text(text, reply_markup=get_main_menu(user_id), parse_mode='HTML')

async def handle_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip().lower()
    
    if query == "panel":
        user_id = update.inline_query.from_user.id
        
        results = [
            InlineQueryResultArticle(
                id="1",
                title="🎛 پنل مدیریت سلف",
                description="هلپر سلف - تمام دستورات مدیریتی",
                input_message_content=InputTextMessageContent(
                    message_text="<b>سلام به هلپر سلف خوش امدی برای کمک گرفتن میتونی از دکمه های زیر استفاده کنی 👇</b>",
                    parse_mode='HTML'
                ),
                reply_markup=get_main_menu(user_id)
            )
        ]
        await update.inline_query.answer(results, cache_time=300, is_personal=True)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if not data.endswith(f"_{user_id}"):
        await query.answer("دسترسی denied!", show_alert=True)
        return
    
    action = data.split("_")[1]
    
    if action == "close":
        text = "✅ <b>پنل بسته شد</b>\n\n💡 برای باز کردن مجدد:\n<code>@BotUsername panel</code>"
        await query.edit_message_text(text, reply_markup=get_reopen_button(user_id), parse_mode='HTML')
        return
    
    if action == "reopen":
        text = "<b>سلام به هلپر سلف خوش امدی برای کمک گرفتن میتونی از دکمه های زیر استفاده کنی 👇</b>"
        await query.edit_message_text(text, reply_markup=get_main_menu(user_id), parse_mode='HTML')
        return
    
    if action == "back":
        text = "<b>سلام به هلپر سلف خوش امدی برای کمک گرفتن میتونی از دکمه های زیر استفاده کنی 👇</b>"
        await query.edit_message_text(text, reply_markup=get_main_menu(user_id), parse_mode='HTML')
        return
    
    if action in HELP_TEXTS:
        text = HELP_TEXTS[action]
        await query.edit_message_text(text, reply_markup=get_back_button(user_id), parse_mode='HTML')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, show_menu))
    app.add_handler(InlineQueryHandler(handle_inline_query))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_error_handler(error_handler)
    
    print("🤖 ربات هلپر اجرا شد")
    app.run_polling()

if __name__ == "__main__":
    main()