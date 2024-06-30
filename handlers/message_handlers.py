# handlers/message_handlers.py
from telegram import Update
from telegram.ext import CallbackContext
from database.DbContext import db
import logging

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('adding'):
        name, link = update.message.text.split(';')
        db.add_airdrop(name.strip(), link.strip())
        context.user_data['adding'] = False
        await update.message.reply_text('Airdrop berhasil ditambahkan.')
    elif context.user_data.get('editing'):
        id = context.user_data['edit_id']
        name, link = update.message.text.split(';')
        db.edit_airdrop(id, name.strip(), link.strip())
        context.user_data['editing'] = False
        await update.message.reply_text('Airdrop berhasil diedit.')

async def referral(update: Update, context: CallbackContext) -> None:
    try:
        referrer_id = int(update.message.text.split()[1]) if len(update.message.text.split()) > 1 else None
        referred_id = update.message.from_user.id

        if referrer_id and referred_id:
            db.update_referral(referrer_id, referred_id)
            logger.info(f"Referral berhasil dicatat: {referrer_id} mereferensikan {referred_id}")
            await update.message.reply_text('Referral berhasil dicatat. Terima kasih!')
        else:
            logger.warning(f"Referral gagal: referrer_id atau referred_id tidak valid. referrer_id: {referrer_id}, referred_id: {referred_id}")
            await update.message.reply_text('Referral gagal. ID referensi tidak valid.')
    except Exception as e:
        logger.error(f"Error dalam pencatatan referral: {str(e)}")
        await update.message.reply_text('Terjadi kesalahan saat mencatat referral.')

async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')
    action = data[0]
    id = int(data[1])

    if action == 'edit':
        context.user_data['edit_id'] = id
        await query.message.reply_text('Kirimkan nama dan link airdrop baru dalam format "Nama; Link":')
    elif action == 'delete':
        db.delete_airdrop(id)
        await query.message.reply_text('Airdrop berhasil dihapus.')
