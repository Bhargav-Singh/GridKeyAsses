import logging

from django.db import transaction
from django.db.models import Sum, F, FloatField

from trades.models import TradeTransaction
logger = logging.getLogger(__name__)


class TradeService:
    @staticmethod
    def record_trade(user, company, trade_type, quantity, price=None, split_ratio=None):
        """
        Record a trade of type BUY, SELL, or SPLIT with validations.
        """
        if trade_type == "BUY":
            quantity = int(quantity)

            if quantity <= 0:
                logger.error("Non-positive quantity provided for BUY trade")
                raise ValueError("Quantity must be greater than 0.")

            # Validate price: must be a float > 0.
            price = float(price)
            if price <= 0:
                logger.error("Non-positive price provided for BUY trade")
                raise ValueError("Price must be greater than 0.")

            try:
                with transaction.atomic():
                    trade = TradeTransaction.objects.create(
                        user=user,
                        company=company,
                        trade_type=trade_type,
                        quantity=quantity,
                        price=price,
                        balance_qty=quantity  # Full quantity is available for selling.
                    )
                    logger.info("BUY trade recorded successfully")
                    return trade
            except Exception as e:
                logger.exception("Error recording BUY trade")
                raise ValueError("An error occurred while recording the BUY trade.")

        elif trade_type == "SELL":
            # Validate quantity: must be an integer > 0.
            quantity = int(quantity)
            if quantity <= 0:
                logger.error("Non-positive quantity provided for SELL trade")
                raise ValueError("Quantity must be greater than 0.")

            # Validate price: must be a float > 0.
            price = float(price)
            if price <= 0:
                logger.error("Non-positive price provided for SELL trade")
                raise ValueError("Price must be greater than 0.")

            try:
                return TradeService.process_sell_trade(user, company, quantity, price)
            except Exception as e:
                logger.exception("Error processing SELL trade")
                raise ValueError("An error occurred while processing the SELL trade.")

        elif trade_type == "SPLIT":
            # Validate that split_ratio is provided and is a float > 1.
            split_ratio = float(split_ratio)
            if split_ratio <= 1:
                logger.error("Invalid split ratio: must be greater than 1")
                raise ValueError("Split ratio must be greater than 1.")

            try:
                return TradeService.process_split_trade(user, company, split_ratio)
            except Exception as e:
                logger.exception("Error processing SPLIT trade")
                raise ValueError("An error occurred while processing the SPLIT trade.")
        else:
            logger.error("Invalid trade type provided")
            raise ValueError("Invalid trade type")

    @staticmethod
    def process_sell_trade(user, company, sell_quantity, sell_price):
        """
        Process a SELL trade using FIFO:
        - Deduct shares from available BUY transactions (ordered by date).
        - If insufficient shares exist, raise an error.
        - Record the SELL transaction.
        """
        remaining_qty = sell_quantity
        buy_trades = TradeTransaction.objects.filter(
            user=user,
            company=company,
            trade_type="BUY",
            balance_qty__gt=0
        ).order_by("date")

        with transaction.atomic():
            for trade in buy_trades:
                if remaining_qty <= 0:
                    break
                if trade.balance_qty >= remaining_qty:
                    trade.balance_qty -= remaining_qty
                    trade.save()
                    remaining_qty = 0
                else:
                    remaining_qty -= trade.balance_qty
                    trade.balance_qty = 0
                    trade.save()
            if remaining_qty > 0:
                logger.error("Not enough shares to sell")
                raise ValueError("Not enough shares to sell")
            sell_trade = TradeTransaction.objects.create(
                user=user,
                company=company,
                trade_type="SELL",
                quantity=sell_quantity,
                price=sell_price,
                balance_qty=0
            )
            logger.info("SELL trade recorded successfully")
        return sell_trade

    @staticmethod
    def process_split_trade(user, company, split_ratio):
        """
        Process a SPLIT trade:
        - Update all existing BUY trades for the user and company:
          * Multiply balance_qty by split_ratio.
          * Divide the price per share by split_ratio.
        - Record a SPLIT transaction for historical purposes.
        """
        with transaction.atomic():
            buy_trades = TradeTransaction.objects.filter(
                user=user,
                company=company,
                trade_type="BUY"
            )
            for trade in buy_trades:
                original_balance = trade.balance_qty
                trade.balance_qty = trade.balance_qty * split_ratio
                if trade.price is not None:
                    trade.price = trade.price / split_ratio
                trade.save()
                logger.info("Updated BUY trade for SPLIT")

            split_trade = TradeTransaction.objects.create(
                user=user,
                company=company,
                trade_type="SPLIT",
                quantity=0,
                split_ratio=split_ratio,
                balance_qty=0
            )
            logger.info("SPLIT trade recorded successfully")
        return split_trade

    @staticmethod
    def calculate_avg_buy_price(user, company, date):
        """
        Calculate the weighted average buy price and total remaining quantity for BUY trades up to the given date.
        Returns a dict with the company name, total_quantity, and avg_buy_price.
        """
        buy_trades = TradeTransaction.objects.filter(
            user=user,
            company=company,
            trade_type="BUY",
            date__lte=date
        )
        total_qty = 0
        total_cost = 0
        for trade in buy_trades:
            remaining = trade.balance_qty
            total_qty += remaining
            total_cost += remaining * trade.price
        avg_buy_price = (total_cost / total_qty) if total_qty > 0 else 0
        return {
            'company': company,
            'total_quantity': total_qty,
            'avg_buy_price': avg_buy_price
        }

    @staticmethod
    def get_stock_summary(user, date, company=None):
        """
        If a company is provided, return summary for that company;
        otherwise, return a list of summaries for each company where the user has BUY trades.
        """
        if company:
            return [TradeService.calculate_avg_buy_price(user, company, date)]
        else:
            companies = TradeTransaction.objects.filter(
                user=user,
                trade_type="BUY"
            ).values_list('company', flat=True).distinct()
            summaries = []
            for comp in companies:
                summary = TradeService.calculate_avg_buy_price(user, comp, date)
                summaries.append(summary)
            return summaries

    @staticmethod
    def get_stock_summary_range(user, start_date, end_date, company=None):
        """
        Returns a summary of BUY trades for the specified user within the date range.
        Filters by company if provided. The summary includes:
         - company name
         - total_quantity: sum of balance_qty from BUY transactions
         - avg_buy_price: weighted average price based on balance_qty and price
        Note: This uses the updated BUY trades (with balance_qty) and only considers trades
              where the trade date is between start_date and end_date.
        """
        filters = {
            'user': user,
            'trade_type': 'BUY',
            'date__gte': start_date,
            'date__lte': end_date,
        }
        if company:
            filters['company'] = company

        trades = TradeTransaction.objects.filter(**filters)
        summary = []
        # If filtering by company, compute for that company only.
        if company:
            total_qty = trades.aggregate(total=Sum('balance_qty'))['total'] or 0
            # Compute total cost as sum(balance_qty * price)
            total_cost = trades.aggregate(
                total_cost=Sum(F('balance_qty') * F('price'), output_field=FloatField())
            )['total_cost'] or 0
            avg_price = (total_cost / total_qty) if total_qty > 0 else 0
            summary.append({
                'company': company,
                'total_quantity': total_qty,
                'avg_buy_price': avg_price
            })
        else:
            # Group by company
            companies = trades.values_list('company', flat=True).distinct()
            for comp in companies:
                comp_trades = trades.filter(company=comp)
                total_qty = comp_trades.aggregate(total=Sum('balance_qty'))['total'] or 0
                total_cost = comp_trades.aggregate(
                    total_cost=Sum(F('balance_qty') * F('price'), output_field=FloatField())
                )['total_cost'] or 0
                avg_price = (total_cost / total_qty) if total_qty > 0 else 0
                summary.append({
                    'company': comp,
                    'total_quantity': total_qty,
                    'avg_buy_price': avg_price
                })
        return summary