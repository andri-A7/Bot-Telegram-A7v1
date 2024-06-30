# handlers/command_handlers.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from database.DbContext import db

async def get_username(bot, user_id):
    user = await bot.get_chat(user_id)
    user_name = user.username if user.username else f"{user.first_name} {user.last_name}".strip()
    return user_name

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_name = await get_username(context.bot, user_id)
    referrer_id = context.args[0] if context.args else None

    if referrer_id and referrer_id != user_id:
        referrer_name = await get_username(context.bot, referrer_id)
        if db.update_referral(referrer_id, user_id, user_name, referrer_name):
            await update.message.reply_text("Anda telah berhasil menggunakan link referral "+user_name)
            leaderboard()
        else:
            await update.message.reply_text('Referral gagal, Anda sudah menggunakan referral sebelumnya.')
    elif referrer_id == user_id:
        await update.message.reply_text('Anda tidak dapat mereferensikan diri sendiri.')

    welcome_message = (
        f"Selamat datang di A7 Bot!\n\n"
        f"Bot ini membantu Anda untuk mengelola airdrop dengan mudah.\n\n"
        f"Untuk melihat airdrop yang tersedia, gunakan perintah /view.\n"
        f"Jika Anda adalah admin, Anda dapat menambahkan, mengedit, atau menghapus airdrop.\n\n"
        f"Event Referral: Ajak teman Anda menggunakan bot ini dengan memberikan link referral Anda! "
        f"Pengguna dengan referral terbanyak akan mendapatkan hadiah $100. "
        f"Gunakan link berikut untuk mereferensikan teman Anda: "
        f"https://t.me/iniA7_bot?start={user_id}"
    )
    await update.message.reply_text(welcome_message)

async def referral(update: Update, context: CallbackContext) -> None:
    try:
        referrer_id = int(update.message.text.split()[1]) if len(update.message.text.split()) > 1 else None
        referred_id = update.message.from_user.id
        user_name = await get_username(context.bot, referred_id)

        if referrer_id and referred_id and referrer_id != referred_id:
            referrer_name = await get_username(context.bot, referrer_id)
            if db.update_referral(referrer_id, referred_id, user_name, referrer_name):
                await update.message.reply_text('Referral berhasil dicatat. Terima kasih!')
            else:
                await update.message.reply_text('Referral gagal, Anda sudah menggunakan referral sebelumnya.')
        else:
            await update.message.reply_text('Referral gagal. ID referensi tidak valid atau Anda tidak bisa mereferensikan diri sendiri.')
    except Exception as e:
        await update.message.reply_text('Terjadi kesalahan saat mencatat referral.')
async def view_airdrops(update: Update, context: CallbackContext) -> None:
    airdrops = db.get_airdrops()
    if not airdrops:
        await update.message.reply_text('Tidak ada airdrop yang tersedia.')
    else:
        keyboard = [[InlineKeyboardButton(ad[1], url=ad[2])] for ad in airdrops]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Airdrop yang tersedia:', reply_markup=reply_markup)

async def add_airdrop_handler(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != int(context.bot_data['ADMIN_ID']):
        await update.message.reply_text('Anda tidak memiliki otorisasi untuk menambahkan airdrop.')
        return
    context.user_data['adding'] = True
    await update.message.reply_text('Kirimkan nama dan link airdrop untuk ditambahkan dalam format "Nama; Link".')

async def edit_airdrop_handler(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != int(context.bot_data['ADMIN_ID']):
        await update.message.reply_text('Anda tidak memiliki otorisasi untuk mengedit airdrop.')
        return
    airdrops = db.get_airdrops()
    if not airdrops:
        await update.message.reply_text('Tidak ada airdrop yang tersedia untuk diedit.')
        return
    context.user_data['editing'] = True
    keyboard = [[InlineKeyboardButton(ad[1], callback_data=f'edit_{ad[0]}')] for ad in airdrops]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Pilih airdrop untuk diedit:', reply_markup=reply_markup)

async def delete_airdrop_handler(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != int(context.bot_data['ADMIN_ID']):
        await update.message.reply_text('Anda tidak memiliki otorisasi untuk menghapus airdrop.')
        return
    airdrops = db.get_airdrops()
    if not airdrops:
        await update.message.reply_text('Tidak ada airdrop yang tersedia untuk dihapus.')
        return
    context.user_data['deleting'] = True
    keyboard = [[InlineKeyboardButton(ad[1], callback_data=f'delete_{ad[0]}')] for ad in airdrops]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Pilih airdrop untuk dihapus:', reply_markup=reply_markup)

# handlers/command_handlers.py
async def leaderboard(update: Update, context: CallbackContext) -> None:
    leaderboard_data = db.get_leaderboard()
    if not leaderboard_data:
        await update.message.reply_text('Belum ada referral yang tercatat.')
    else:
        leaderboard_message = "Leaderboard Referral:\n\n"
        for rank, (user_name, referrals) in enumerate(leaderboard_data, start=1):
            leaderboard_message += f"{rank}. {user_name}: {referrals} referral(s)\n"
        await update.message.reply_text(leaderboard_message)
