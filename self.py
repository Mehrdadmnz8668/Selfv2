from pyrogram import Client, filters
from pyrogram.types import Message
import os, asyncio, aiohttp, random
from datetime import datetime
import pytz
from pyrogram import enums

bot_username = "0000" # ایدی ربات هلپر بدون @
app = Client("self", api_id="0000", api_hash="0000") # اطلاعات اکانت api id, hash

SAVED_PHOTOS_DIR = "saved_photos"
INSULTS_FILE = "insults.txt"
ENEMIES_FILE = "enemies.txt"
BACKUPS_DIR = "backups"

os.makedirs(SAVED_PHOTOS_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

user_time_status = {}
user_original_names = {}
user_fonts = {}
photo_save_active = True
time_updater_started = False
bold_enabled = {}
auto_replies = {}
enemies = set()

FONTS = {
    1: {'0':'𝟎','1':'𝟏','2':'𝟐','3':'𝟑','4':'𝟒','5':'𝟓','6':'𝟔','7':'𝟕','8':'𝟖','9':'𝟗'},
    2: {'0':'𝟬','1':'𝟭','2':'𝟮','3':'𝟯','4':'𝟰','5':'𝟱','6':'𝟲','7':'𝟳','8':'𝟴','9':'𝟵'},
    3: {'0':'０','1':'１','2':'２','3':'３','4':'４','5':'５','6':'６','7':'７','8':'８','9':'９'},
    4: {'0':'𝟢','1':'𝟣','2':'𝟤','3':'𝟥','4':'𝟦','5':'𝟧','6':'𝟨','7':'𝟩','8':'𝟪','9':'𝟫'},
    5: {'0':'𝟘','1':'𝟙','2':'𝟚','3':'𝟛','4':'𝟜','5':'𝟝','6':'𝟞','7':'𝟟','8':'𝟠','9':'𝟡'},
    6: {'0':'0҉','1':'1҉','2':'2҉','3':'3҉','4':'4҉','5':'5҉','6':'6҉','7':'7҉','8':'8҉','9':'9҉'}
}
def get_iran_time() -> str:
    now = datetime.now(pytz.timezone('Asia/Tehran')).strftime("%H:%M")
    font_dict = FONTS.get(user_fonts.get("me", 1), FONTS[1])
    return ''.join([font_dict.get(char, char) for char in now])

def get_iran_datetime() -> str:
    return datetime.now(pytz.timezone('Asia/Tehran')).strftime('%Y-%m-%d %H:%M:%S')

def load_insults() -> list:
    try:
        if os.path.exists(INSULTS_FILE):
            with open(INSULTS_FILE, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines() if line.strip()]
        return []
    except Exception as e:
        print(f"❌ خطا در لود کردن فحش‌ها: {e}")
        return []

def save_insults(insults_list: list) -> bool:
    try:
        with open(INSULTS_FILE, 'w', encoding='utf-8') as f:
            for insult in insults_list:
                f.write(insult + '\n')
        return True
    except Exception as e:
        print(f"❌ خطا در ذخیره فحش‌ها: {e}")
        return False

def load_enemies() -> set:
    try:
        if os.path.exists(ENEMIES_FILE):
            with open(ENEMIES_FILE, 'r', encoding='utf-8') as f:
                return set(int(line.strip()) for line in f.readlines() if line.strip())
        return set()
    except Exception as e:
        print(f"❌ خطا در لود کردن دشمنان: {e}")
        return set()

def save_enemies(enemies_set: set) -> bool:
    try:
        with open(ENEMIES_FILE, 'w', encoding='utf-8') as f:
            for enemy_id in enemies_set:
                f.write(str(enemy_id) + '\n')
        return True
    except Exception as e:
        print(f"❌ خطا در ذخیره دشمنان: {e}")
        return False

def is_enemy(user_id: int) -> bool:
    return user_id in enemies

async def update_name_with_time(user_id: int, client: Client) -> bool:
    if not user_time_status.get(user_id):
        return False
    
    try:
        user = await client.get_users(user_id)
        first_name = user_original_names.get(user_id, user.first_name or "")
        new_name = f"{first_name} {get_iran_time()}"
        await client.update_profile(first_name=new_name)
        return True
    except Exception as e:
        print(f"❌ خطا در آپدیت نام کاربر {user_id}: {e}")
        return False

async def continuous_time_updater(client: Client):
    global time_updater_started
    while True:
        try:
            now = datetime.now(pytz.timezone('Asia/Tehran'))
            seconds_until_next_minute = 60 - now.second
            milliseconds_until_next_minute = (seconds_until_next_minute * 1000) - (now.microsecond // 1000)
           
            await asyncio.sleep(milliseconds_until_next_minute / 1000)
            
            active_users = [uid for uid, status in user_time_status.items() if status]
            for user_id in active_users:
                try:
                    current_time = get_iran_time()
                    original_name = user_original_names.get(user_id, "")
                    new_name = f"{original_name} {current_time}"
                    await client.update_profile(first_name=new_name)
                except Exception as e:
                    print(f"❌ خطا در آپدیت ساعت برای کاربر {user_id}: {e}") 
                    
        except Exception as e:
            print(f"❌ خطا در مدیریت آپدیت زمان: {e}")
            await asyncio.sleep(60)

async def backup_chat(client: Client, chat_id: int, until_message_id: int = None) -> tuple:
    try:
        backup_file = f"{BACKUPS_DIR}/backup_{chat_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        user = await client.get_users(chat_id)
        user_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or f"User_{chat_id}"
        me = await client.get_me()
        message_count = 0

        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + f"\n📱 پشتیبان گیری از تلگرام\n" + "="*60 + f"\n👤 کاربر: {user_name}\n🆔 آیدی: {chat_id}\n📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "="*60 + "\n\n")
            
            async for message in client.get_chat_history(chat_id):
                if until_message_id and message.id >= until_message_id:
                    continue
                message_count += 1
                sender_name = "شما" if message.from_user and message.from_user.id == me.id else f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip() or message.from_user.username or "Unknown"
                if message.from_user and message.from_user.id != me.id:
                    sender_name += f" (ID: {message.from_user.id})"
                
                media_type = ""
                if message.photo: media_type = "📷 عکس"
                elif message.video: media_type = "🎥 ویدیو"
                elif message.document: media_type = "📄 فایل"
                elif message.audio: media_type = "🎵 آudio"
                elif message.voice: media_type = "🎤 ویس"
                elif message.sticker: media_type = "🤡 استیکر"
                
                message_text = message.text or message.caption or ""
                f.write(f"#{message_count}\n👤 ارسال کننده: {sender_name}\n🕐 زمان: {message.date.strftime('%Y-%m-%d %H:%M')}\n")
                if media_type: f.write(f"📎 نوع: {media_type}\n")
                if message_text: f.write(f"💬 متن: {message_text}\n")
                f.write("-"*40 + "\n\n")

        return True, backup_file, message_count, user_name
    except Exception as e:
        return False, str(e), 0, None
@app.on_message(filters.private & ~filters.me)
async def auto_reply_handler(client: Client, message: Message):
    if not message.text:
        return
    
    user_id = message.from_user.id
    message_text = message.text.strip().lower()
    
    if is_enemy(user_id):
        try:
            insults_list = load_insults()
            if insults_list:
                random_insult = random.choice(insults_list)
                await client.send_message(
                    message.chat.id,
                    random_insult,
                    reply_to_message_id=message.id
                )
            return
        except Exception as e:
            print(f"❌ خطا در ارسال فحش به دشمن: {e}")
    
    for trigger, reply in auto_replies.items():
        if trigger.lower() in message_text:
            try:
                await client.send_message(
                    message.chat.id,
                    reply,
                    reply_to_message_id=message.id
                )
                break
            except Exception as e:
                print(f"❌ خطا در ارسال پاسخ خودکار: {e}")

@app.on_message(filters.me & filters.command("عکس", prefixes=""))
async def photo_command(client: Client, message: Message):
    global photo_save_active
    if len(message.command) == 1:
        return await message.edit(f"📸 **وضعیت ذخیره عکس تایمدار:** **{'فعال' if photo_save_active else 'غیرفعال'}**\n\n`عکس روشن` - فعال کردن\n`عکس خاموش` - غیرفعال کردن\n`عکس سیو` - ذخیره عکس تایمدار (با ریپلای)")
    
    action = message.command[1]
    
    if action == "روشن":
        photo_save_active = True
        await message.edit("✅ **ذخیره خودکار عکس تایمدار فعال شد**")
        
    elif action == "خاموش":
        photo_save_active = False
        await message.edit("✅ **ذخیره خودکار عکس تایمدار غیرفعال شد**")
        
    elif action == "سیو":
        if not message.reply_to_message:
            return await message.edit("❌ **لطفا روی یک عکس تایمدار ریپلای کنید**")
        
        replied_message = message.reply_to_message
        if not replied_message.photo:
            return await message.edit("❌ **لطفا روی یک عکس ریپلای کنید**")
        if not hasattr(replied_message.photo, 'ttl_seconds') or not replied_message.photo.ttl_seconds:
            return await message.edit("❌ **این عکس تایمدار نیست**")
        
        try:
            saving_msg = await message.edit("🔄 **در حال ذخیره عکس تایمدار...**")
            
            user = replied_message.from_user
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f"{SAVED_PHOTOS_DIR}/manual_save_{user.id}_{timestamp}.jpg"
            file_path = await replied_message.download(file_name=file_name)
            
            if file_path and os.path.exists(file_path):
                await client.send_photo(
                    "me", 
                    photo=file_path, 
                    caption=(
                        f"عکس ذخیره شد\n"
                        f"👤 کاربر: {user.first_name or 'Unknown'}\n"
                        f"🆔 آیدی: `{user.id}`\n"
                        f"📎 یوزرنیم: @{user.username or 'ندارد'}\n"
                        f"⏱ زمان اصلی: {replied_message.photo.ttl_seconds} ثانیه\n"
                        f"📅 تاریخ ذخیره: {get_iran_datetime()}\n"
                    )
                )
                
                await saving_msg.edit("✅ **عکس تایمدار با موفقیت ذخیره شد**")
            else:
                await saving_msg.edit("❌ **خطا در دانلود عکس**")
                
        except Exception as e:
            error_msg = f"❌ **خطا در ذخیره عکس:**\n`{str(e)}`"
            await message.edit(error_msg)
            print(f"❌ خطا در ذخیره دستی عکس تایمدار: {e}")
    
    else:
        await message.edit("⚠️ **استفاده:**\n`عکس روشن` - فعال کردن\n`عکس خاموش` - غیرفعال کردن\n`عکس سیو` - ذخیره عکس تایمدار (با ریپلای)")

@app.on_message(filters.me & filters.text & ~filters.command(["سیو", "پنل", "ایدی", "تایم", "عکس", "وضعیت", "لیست فونت", "تنظیم فونت", "قیمت", "اسپم", "بولد", "پاسخ", "دشمن", "فحش", "حذف", "لیست دشمن", "دشمنان", "پاک کردن دشمنان"], prefixes=""))
async def auto_bold_messages(client: Client, message: Message):
    user_id = message.from_user.id
    
    if bold_enabled.get(user_id, False):
        original_text = message.text
        
        if not original_text.startswith("**") or not original_text.endswith("**"):
            bold_text = f"**{original_text}**"
            
            try:
                await message.edit_text(bold_text)
            except Exception as e:
                print(f"❌ خطا در بولد کردن پیام: {e}")
@app.on_message(filters.me & filters.command("سیو", prefixes=""))
async def save_command(client: Client, message: Message):
    if len(message.command) < 2: 
        return await message.edit_text("❌ **لطفا یوزرنیم کاربر را وارد کنید**\n\nمثال: `سیو @LuminousPath`")
    
    chat_input = message.command[1].lstrip('@')
    try:
        user = await client.get_users(chat_input)
        chat_id, user_name = user.id, f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or f"User_{user.id}"
    except: 
        return await message.edit_text(f"❌ **کاربر '{chat_input}' پیدا نشد**")
    
    loading_msg = await message.edit_text(f"🔄 **در حال پشتیبان‌گیری از {user_name}...**")
    success, result, message_count, user_name = await backup_chat(client, chat_id, message.id)
    
    if success:
        await loading_msg.edit_text("📤 **در حال آپلود فایل پشتیبان...**")
        await client.send_document(
            "me", 
            document=result, 
            caption=f"✅ **پشتیبان‌گیری کامل شد**\n\n👤 **کاربر:** {user_name}\n🆔 **آیدی:** {chat_id}\n📊 **تعداد پیام‌ها:** {message_count}\n📁 **فرمت:** فایل متنی (TXT)\n📅 **تاریخ:** {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        os.remove(result)
        await loading_msg.delete()
    else: 
        await loading_msg.edit_text(f"❌ **خطا در پشتیبان‌گیری:**\n`{result}`")

@app.on_message(filters.me & filters.command("تایم", prefixes=""))
async def time_command(client: Client, message: Message):
    global time_updater_started  
    if len(message.command) < 2: 
        return await message.edit("⚠️ **استفاده:**\n`تایم روشن` - فعال کردن\n`تایم خاموش` - غیرفعال کردن")
    
    action = message.command[1]
    user_id = message.from_user.id
    
    if action == "روشن":
        user_time_status[user_id] = True
        user_original_names.setdefault(user_id, message.from_user.first_name or "")
        success = await update_name_with_time(user_id, client)
        
        if not time_updater_started:  
            time_updater_started = True  
            asyncio.create_task(continuous_time_updater(client))
        
        await message.edit("✅ تایم کنار نام فعال شد\n⏰ **راس هر دقیقه آپدیت می‌شود**" if success else "❌ خطا در تغییر نام")
        
    elif action == "خاموش":
        user_time_status[user_id] = False
        if user_id in user_original_names:
            try:
                await client.update_profile(first_name=user_original_names[user_id])
                await message.edit("✅ تایم کنار نام غیرفعال شد\nنام شما به حالت اول بازگشت")
            except: 
                await message.edit("❌ خطا در بازگردانی نام")
        else: 
            await message.edit("✅ تایم کنار نام غیرفعال شد")
    else:
        await message.edit("⚠️ **استفاده:**\n`تایم روشن` - فعال کردن\n`تایم خاموش` - غیرفعال کردن")

@app.on_message(filters.me & filters.command("وضعیت", prefixes=""))
async def status_command(client: Client, message: Message):
    user = message.from_user
    replies_list = "\n".join([f"• **{trigger}** → {reply}" for trigger, reply in auto_replies.items()]) or "❌ هیچ پاسخی تنظیم نشده"
    enemies_list = load_enemies()
    enemies_display = "\n".join([f"• `{enemy}`" for enemy in enemies_list]) or "❌ هیچ دشمنی تنظیم نشده"
    insults_list = load_insults()
    insults_count = len(insults_list)
    
    status_text = f"""
🤖 **وضعیت ربات**

👤 کاربر: {user.first_name}
🆔 آیدی: {user.id}

⏰ تایم در نام: **{'فعال' if user_time_status.get(user.id, False) else 'غیرفعال'}**
📸 ذخیره عکس: **{'فعال' if photo_save_active else 'غیرفعال'}**
🔤 فونت زمان: **{user_fonts.get('me', 1)}**
🔠 حالت بولد: **{'فعال' if bold_enabled.get(user.id, False) else 'غیرفعال'}**
🤖 پاسخ‌های خودکار: **{len(auto_replies)}**
🔥 دشمنان: **{len(enemies_list)}**
💢 فحش‌ها: **{insults_count}**

📝 **پاسخ‌های تنظیم شده:**
{replies_list}

👿 **دشمنان:**
{enemies_display}
"""
    await message.edit(status_text)

@app.on_message(filters.me & filters.command("لیست فونت", prefixes=""))
async def font_list_command(client: Client, message: Message):
    sample_time = "12:34"
    fonts_samples = "\n".join([f"**فونت {i}:** {''.join([FONTS[i].get(char, char) for char in sample_time])}" for i in range(1, 7)])
    await message.edit(f"🔤 **لیست فونت‌های زمان**\n\n{fonts_samples}\n\n**استفاده:**\n`تنظیم فونت 1` تا `تنظیم فونت 6`")

@app.on_message(filters.me & filters.command("تنظیم فونت", prefixes=""))
async def set_font_command(client: Client, message: Message):
    if len(message.command) < 2: 
        return await message.edit("⚠️ **استفاده:**\n`تنظیم فونت 1` تا `تنظیم فونت 6`")
    
    try:
        font_num = int(message.command[1])
        if 1 <= font_num <= 6:
            user_fonts["me"] = font_num
            if user_time_status.get(message.from_user.id, False): 
                await update_name_with_time(message.from_user.id, client)
            await message.edit(f"✅ **فونت زمان به شماره {font_num} تغییر کرد**\n\nنمونه: {get_iran_time()}")
        else: 
            await message.edit("❌ **شماره فونت باید بین 1 تا 6 باشد**")
    except ValueError: 
        await message.reply("❌ **لطفا یک عدد وارد کنید**\nمثال: `تنظیم فونت 2`")

@app.on_message(filters.me & filters.command("قیمت", prefixes=""))
async def price_command(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.edit_text("❌ **لطفا نام ارز را وارد کنید**\nمثال: `قیمت ton` یا `قیمت btc`")
            return
        
        coin_input = message.command[1].upper()
        loading_msg = await message.edit_text(f"🔍 **در حال دریافت قیمت {coin_input}...**")
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.fast-creat.ir/nobitex/v2?apikey=8000978149:Vqsu9H08Z6rzAQw@Api_ManagerRoBot") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("ok"):
                        prices = data["result"]
                        
                        if coin_input in prices:
                            coin_data = prices[coin_input]
                            price_text = f"""**💰 قیمت {coin_data['name']} ({coin_input})**

💵 **قیمت تومانی:** `{'{:,}'.format(int(float(coin_data['irr'])))}` تومان
💰 **قیمت دلاری:** `{float(coin_data['usdt']):,.2f}$`
📊 **تغییر 24h:** {'🟢' if float(coin_data['dayChange']) > 0 else '🔴'} `{coin_data['dayChange']}%`

⏰ **آپدیت:** {datetime.now(pytz.timezone('Asia/Tehran')).strftime('%H:%M')}
"""
                            await loading_msg.edit_text(price_text)
                        else:
                            await loading_msg.edit_text(f"❌ **ارز {coin_input} یافت نشد**")
                    else:
                        await loading_msg.edit_text("❌ خطا در دریافت اطلاعات از API")
                else:
                    await loading_msg.edit_text("❌ خطا در اتصال به سرور")
                    
    except Exception as e:
        await message.edit_text(f"❌ خطا: {str(e)}")

@app.on_message(filters.me & filters.command("اسپم", prefixes=""))
async def spam_command(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.edit_text("❌ **فرمت صحیح:**\n`اسپم 10 سلام`\n\nعدد = تعداد پیام\nمتن = پیام مورد نظر")
    
    try:
        count = int(message.command[1])
        if count > 50:
            return await message.edit_text("❌ **حداکثر تعداد مجاز: 50 پیام**")
        
        spam_text = ' '.join(message.command[2:])
        
        if not spam_text:
            return await message.edit_text("❌ **لطفا متن پیام را وارد کنید**")
        
        loading_msg = await message.edit_text(f"🔄 **در حال ارسال {count} پیام...**")
        
        success_count = 0
        for i in range(count):
            try:
                await client.send_message(
                    message.chat.id,
                    f"{spam_text}",
                    reply_to_message_id=message.reply_to_message_id if message.reply_to_message else None
                )
                success_count += 1
                await asyncio.sleep(0.2)
            except Exception as e:
                print(f"خطا در ارسال پیام {i+1}: {e}")
        
        await loading_msg.edit_text(f"✅ **اسپم کامل شد**\n\n📤 **تعداد ارسال شده:** {success_count}/{count}\n💬 **متن:** {spam_text[:50]}{'...' if len(spam_text) > 50 else ''}")
        
    except ValueError:
        await message.edit_text("❌ **لطفا تعداد را به صورت عدد وارد کنید**\nمثال: `اسپم 10 سلام`")
    except Exception as e:
        await message.edit_text(f"❌ **خطا در ارسال اسپم:**\n`{str(e)}`")

@app.on_message(filters.me & filters.command("بولد", prefixes=""))
async def bold_command(client: Client, message: Message):
    if len(message.command) < 2: 
        return await message.edit(f"🔠 **وضعیت حالت بولد:** **{'فعال' if bold_enabled.get(message.from_user.id, False) else 'غیرفعال'}**\n\n`بولد روشن` - فعال کردن بولد خودکار\n`بولد خاموش` - غیرفعال کردن بولد خودکار")
    
    action = message.command[1]
    user_id = message.from_user.id
    
    if action == "روشن":
        bold_enabled[user_id] = True
        await message.edit("✅ **حالت بولد خودکار فعال شد**\n\nاز این پس تمام پیام‌های متنی شما به صورت خودکار بولد خواهند شد.")
    elif action == "خاموش":
        bold_enabled[user_id] = False
        await message.edit("✅ **حالت بولد خودکار غیرفعال شد**\n\nپیام‌های شما دیگر به صورت خودکار بولد نخواهند شد.")
    else:
        await message.edit("⚠️ **استفاده:**\n`بولد روشن` - فعال کردن بولد خودکار\n`بولد خاموش` - غیرفعال کردن بولد خودکار")

@app.on_message(filters.me & filters.command("پاسخ", prefixes=""))
async def auto_reply_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit("⚠️ **استفاده:**\n`پاسخ افزودن سلام|سلام چطوری`\n`پاسخ حذف سلام`\n`پاسخ لیست`")
    
    sub_command = message.command[1]
    
    if sub_command == "افزودن":
        if len(message.command) < 3:
            return await message.edit("❌ **فرمت صحیح:**\n`پاسخ افزودن سلام|سلام چطوری`")
        
        try:
            parts = ' '.join(message.command[2:]).split('|', 1)
            if len(parts) != 2:
                return await message.edit("❌ **فرمت صحیح:**\n`پاسخ افزودن سلام|سلام چطوری`")
            
            trigger, reply = parts[0].strip(), parts[1].strip()
            auto_replies[trigger] = reply
            await message.edit(f"✅ **پاسخ خودکار افزوده شد**\n\n**متن:** {trigger}\n**پاسخ:** {reply}")
        except Exception as e:
            await message.edit(f"❌ **خطا در افزودن پاسخ:**\n`{e}`")
    
    elif sub_command == "حذف":
        if len(message.command) < 3:
            return await message.edit("❌ **لطفا متن پاسخ را وارد کنید**\nمثال: `پاسخ حذف سلام`")
        
        trigger = ' '.join(message.command[2:]).strip()
        if trigger in auto_replies:
            del auto_replies[trigger]
            await message.edit(f"✅ **پاسخ خودکار حذف شد**\n\n**متن:** {trigger}")
        else:
            await message.edit(f"❌ **پاسخ برای متن '{trigger}' یافت نشد**")
    
    elif sub_command == "لیست":
        if not auto_replies:
            await message.edit("❌ **هیچ پاسخی تنظیم نشده**")
        else:
            replies_list = "\n".join([f"• **{trigger}** → {reply}" for trigger, reply in auto_replies.items()])
            await message.edit(f"📝 **لیست پاسخ‌های خودکار**\n\n{replies_list}\n\n**تعداد:** {len(auto_replies)}")
    
    else:
        await message.edit("⚠️ **استفاده:**\n`پاسخ افزودن سلام|سلام چطوری`\n`پاسخ حذف سلام`\n`پاسخ لیست`")

@app.on_message(filters.me & filters.command("دشمن", prefixes=""))
async def enemy_command(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.edit("❌ **لطفا روی پیام کاربر ریپلای کن**")
    
    enemy_user = message.reply_to_message.from_user
    enemy_id = enemy_user.id
    
    if is_enemy(enemy_id):
        await message.edit(f"❌ **این کاربر از قبل دشمن است**\n\n👤 کاربر: {enemy_user.first_name}\n🆔 آیدی: `{enemy_id}`")
    else:
        enemies.add(enemy_id)
        save_enemies(enemies)
        await message.edit(f"**کاربر مورد نظر به لیست دشمن ها اضافه شد 😈**")

@app.on_message(filters.me & filters.command("فحش", prefixes=""))
async def insult_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit("⚠️ **استفاده:**\n`فحش افزودن متن`\n`فحش حذف متن`\n`لیست فحش`")
    
    sub_command = message.command[1]
    
    if sub_command == "افزودن":
        if len(message.command) < 3:
            return await message.edit("❌ **لطفا متن فحش را وارد کنید**\nمثال: `فحش افزودن تو احمقی`")
        
        insult_text = ' '.join(message.command[2:]).strip()
        insults_list = load_insults()
        if insult_text not in insults_list:
            insults_list.append(insult_text)
            if save_insults(insults_list):
                await message.edit(f"✅ **فحش افزوده شد**\n\n💢 متن: {insult_text}")
            else:
                await message.edit("❌ **خطا در ذخیره فحش**")
        else:
            await message.edit(f"❌ **این فحش از قبل وجود دارد**")
    
    elif sub_command == "حذف":
        if len(message.command) < 3:
            return await message.edit("❌ **لطفا متن فحش را وارد کنید**\nمثال: `فحش حذف تو احمقی`")
        
        insult_text = ' '.join(message.command[2:]).strip()
        insults_list = load_insults()
        if insult_text in insults_list:
            insults_list.remove(insult_text)
            if save_insults(insults_list):
                await message.edit(f"✅ **فحش حذف شد**\n\n💢 متن: {insult_text}")
            else:
                await message.edit("❌ **خطا در حذف فحش**")
        else:
            await message.edit(f"❌ **این فحش یافت نشد**")
    
    else:
        await message.edit("⚠️ **استفاده:**\n`فحش افزودن متن`\n`فحش حذف متن`\n`لیست فحش`")

@app.on_message(filters.me & filters.command("حذف", prefixes=""))
async def remove_enemy_command(client: Client, message: Message):
    text = message.text.strip()
    if text == "حذف دشمن":
        if not message.reply_to_message:
            return await message.edit("❌ باید روی پیام دشمن ریپلای کنی")

        user_id = message.reply_to_message.from_user.id

        if user_id in enemies:
            enemies.remove(user_id)
            save_enemies(enemies)
            return await message.edit("✅ کاربر با موفقیت از لیست دشمن حذف شد")
        else:
            return await message.edit("⚠️ این کاربر داخل لیست دشمن نیست")

@app.on_message(filters.me & filters.command("لیست دشمن", prefixes=""))
async def enemy_list_command(client: Client, message: Message):
    if not enemies:
        return await message.edit("❌ **لیست دشمنان خالی است**")
    
    try:
        loading_msg = await message.edit("🔄 **در حال دریافت اطلاعات دشمنان...**")
        
        enemies_list = []
        
        for enemy_id in list(enemies):
            try:
                user = await client.get_users(enemy_id)
                first_name = user.first_name or ""
                last_name = user.last_name or ""
                username = f"@{user.username}" if user.username else "❌ ندارد"
                full_name = f"{first_name} {last_name}".strip()
                
                enemies_list.append({
                    'id': enemy_id,
                    'name': full_name,
                    'username': username
                })
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"❌ خطا در دریافت اطلاعات کاربر {enemy_id}: {e}")
                enemies_list.append({
                    'id': enemy_id,
                    'name': "❌ خطا در دریافت",
                    'username': "❌ خطا در دریافت"
                })
        
        if not enemies_list:
            return await loading_msg.edit("❌ **هیچ دشمنی در لیست وجود ندارد**")
        
        list_text = f"👿 **لیست دشمنان - تعداد: {len(enemies_list)}**\n\n"
        
        for i, enemy in enumerate(enemies_list, 1):
            list_text += f"{i}. **نام:** {enemy['name']}\n"
            list_text += f"   **آیدی:** `{enemy['id']}`\n"
            list_text += f"   **یوزرنیم:** {enemy['username']}\n"
            list_text += "   " + "─" * 30 + "\n"
        
        if len(list_text) > 4000:
            parts = [list_text[i:i+4000] for i in range(0, len(list_text), 4000)]
            for part in parts:
                await client.send_message(message.chat.id, part)
            await loading_msg.delete()
        else:
            await loading_msg.edit(list_text)
            
    except Exception as e:
        await message.edit(f"❌ **خطا در دریافت لیست دشمنان:**\n`{e}`")

@app.on_message(filters.me & filters.command("دشمنان", prefixes=""))
async def enemies_compact_command(client: Client, message: Message):
    if not enemies:
        return await message.edit("❌ **لیست دشمنان خالی است**")
    
    try:
        loading_msg = await message.edit("🔄 **در حال دریافت اطلاعات...**")
        
        compact_text = f"👿 **لیست دشمنان - تعداد: {len(enemies)}**\n\n"
        
        for i, enemy_id in enumerate(list(enemies), 1):
            try:
                user = await client.get_users(enemy_id)
                first_name = user.first_name or ""
                last_name = user.last_name or ""
                username = f"@{user.username}" if user.username else "بدون یوزرنیم"
                full_name = f"{first_name} {last_name}".strip() or "بدون نام"
                
                compact_text += f"{i}. **{full_name}** - {username} - `{enemy_id}`\n"
                
            except Exception as e:
                compact_text += f"{i}. ❌ خطا در دریافت - `{enemy_id}`\n"
        
        await loading_msg.edit(compact_text)
        
    except Exception as e:
        await message.edit(f"❌ **خطا:**\n`{e}`")

@app.on_message(filters.me & filters.command("پاک کردن دشمنان", prefixes=""))
async def clear_enemies_command(client: Client, message: Message):
    if not enemies:
        return await message.edit("❌ **لیست دشمنان از قبل خالی است**")
    
    enemy_count = len(enemies)
    enemies.clear()
    save_enemies(enemies)
    
    await message.edit(f"✅ **تمام دشمنان پاک شدند**\n\n🗑 **تعداد حذف شده:** {enemy_count} نفر")
@app.on_message(filters.me & filters.command("ایدی", prefixes=""))
async def id_command(client: Client, message: Message):
    try:
        if message.reply_to_message:
            user = message.reply_to_message.from_user
            chat = message.chat
            user_info = f"""
👤 <b>اطلاعات کاربر</b>

🆔 <b>آیدی کاربر:</b> <code>{user.id}</code>
👤 <b>نام:</b> {user.first_name or '❌'}
📖 <b>فامیل:</b> {user.last_name or '❌'}
📎 <b>یوزرنیم:</b> @{user.username or 'ندارد'}
🔗 <b>لینک:</b> {f"tg://user?id={user.id}" if user.id else '❌'}

💬 <b>اطلاعات چت</b>
🆔 <b>آیدی چت:</b> <code>{chat.id}</code>
📝 <b>نوع چت:</b> {chat.type}
📛 <b>عنوان چت:</b> {chat.title or '❌'}
            """
            
            if chat.type == "private":
                user_info += f"\n🔒 <b>چت خصوصی با کاربر</b>"
            
            await message.edit_text(user_info, parse_mode=enums.ParseMode.HTML)
            
        else:
            chat = message.chat
            user = message.from_user
            
            chat_info = f"""
💬 <b>اطلاعات چت</b>

🆔 <b>آیدی چت:</b> <code>{chat.id}</code>
📝 <b>نوع چت:</b> {chat.type}
📛 <b>عنوان چت:</b> {chat.title or '❌'}

👤 <b>اطلاعات شما</b>
🆔 <b>آیدی شما:</b> <code>{user.id}</code>
👤 <b>نام:</b> {user.first_name or '❌'}
📖 <b>فامیل:</b> {user.last_name or '❌'}
📎 <b>یوزرنیم:</b> @{user.username or 'ندارد'}
🔗 <b>لینک شما:</b> tg://user?id={user.id}
            """
            
            await message.edit_text(chat_info, parse_mode=enums.ParseMode.HTML)            
    except Exception as e:
        await message.edit_text(f"❌ **خطا در دریافت اطلاعات:**\n`{str(e)}`")
@app.on_message(filters.me & filters.command(["پنل", "panel"], prefixes=""))
async def panel_command(client, message: Message):
        results = await client.get_inline_bot_results(bot_username, "panel")
        
        if results and results.results:
            sent_message = await client.send_inline_bot_result(
                chat_id=message.chat.id,
                query_id=results.query_id,
                result_id=results.results[0].id
            )
            await message.delete()
            
        else:
            await message.reply_text("❌ پنل یافت نشد")
            await asyncio.sleep(3)
            await message.delete()
if __name__ == "__main__":
    print("⏳ چند ثانیه صبر کن بعد لاگین کن")
    app.run()