from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, MessageHandler, Filters
from database.repositories import PaymentRepository, SubscriptionRepository
from services import bharatpe_service, paytm_service
from config import settings, payment_config
from utils.helpers import format_currency
import re

class PaymentHandlers:
    def __init__(self, db):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.subscription_repo = SubscriptionRepository(db)

    async def request_payment(self, update: Update, context: CallbackContext):
        user = update.effective_user
        keyboard = [
            [InlineKeyboardButton("BharatPe UPI", callback_data='payment_bharatpe')],
            [InlineKeyboardButton("PayTM", callback_data='payment_paytm')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Please select a payment method for your subscription:",
            reply_markup=reply_markup
        )

    async def handle_payment_method(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()
        
        payment_method = query.data.split('_')[1]
        context.user_data['payment_method'] = payment_method
        
        plans_keyboard = []
        for plan_name, plan_data in settings.SUBSCRIPTION_PLANS.items():
            plans_keyboard.append([
                InlineKeyboardButton(
                    f"{plan_name.capitalize()} - {format_currency(plan_data['price'])}",
                    callback_data=f'plan_{plan_name}'
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(plans_keyboard)
        await query.edit_message_text(
            text="Please select a subscription plan:",
            reply_markup=reply_markup
        )

    async def handle_plan_selection(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()
        
        plan_name = query.data.split('_')[1]
        plan_data = settings.SUBSCRIPTION_PLANS[plan_name]
        context.user_data['selected_plan'] = {
            'name': plan_name,
            'duration': plan_data['duration_days'],
            'price': plan_data['price']
        }
        
        payment_method = context.user_data['payment_method']
        
        if payment_method == 'bharatpe':
            await self._handle_bharatpe_payment(update, context)
        elif payment_method == 'paytm':
            await self._handle_paytm_payment(update, context)

    async def _handle_bharatpe_payment(self, update: Update, context: CallbackContext):
        query = update.callback_query
        plan = context.user_data['selected_plan']
        
        await query.edit_message_text(
            text=f"Please send payment of {format_currency(plan['price'])} to our BharatPe UPI ID:\n\n"
                 f"`{payment_config.BHARATPE_UPI_ID}`\n\n"
                 "After payment, please share the UTR number you received.",
            parse_mode='Markdown'
        )
        
        return 'WAITING_FOR_UTR'

    async def handle_utr(self, update: Update, context: CallbackContext):
        utr = update.message.text.strip()
        if not re.match(r'^\d{12}$', utr):
            await update.message.reply_text("Invalid UTR format. Please enter a 12-digit UTR number.")
            return 'WAITING_FOR_UTR'
        
        plan = context.user_data['selected_plan']
        is_verified = await bharatpe_service.verify_utr(utr, plan['price'])
        
        if is_verified:
            await self._complete_subscription(update, context, utr)
            return -1  # End conversation
        else:
            await update.message.reply_text(
                "Payment verification failed. Please check the UTR number or try again later."
            )
            return 'WAITING_FOR_UTR'

    async def _complete_subscription(self, update: Update, context: CallbackContext, transaction_id: str):
        user = update.effective_user
        plan = context.user_data['selected_plan']
        payment_method = context.user_data['payment_method']
        
        # Create subscription record
        subscription = self.subscription_repo.create_subscription(
            user_id=user.id,
            plan_id=plan['name'],
            duration_days=plan['duration']
        )
        
        # Create payment record
        self.payment_repo.create_payment(
            subscription_id=subscription.id,
            amount=plan['price'],
            payment_method=payment_method,
            transaction_id=transaction_id
        )
        
        await update.message.reply_text(
            "Payment verified! Your subscription is now active. "
            f"You have been added to the premium group for {plan['duration']} days."
  )
