from datetime import datetime, timedelta
import pytz

from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import TradeTransactionSerializer
from .services import TradeService
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)


class RecordTradeView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TradeTransactionSerializer

    def post(self, request, *args, **kwargs):
        trade_type = self.kwargs.get('trade_type').upper()
        data = request.data.copy()
        company = data.get('company')
        quantity = data.get('quantity')
        price = data.get('price')
        split_ratio = data.get('split_ratio')

        try:
            trade = TradeService.record_trade(
                user=request.user,
                company=company,
                trade_type=trade_type,
                quantity=quantity,
                price=price,
                split_ratio=split_ratio
            )
            serializer = self.get_serializer(trade)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            logger.error("Error processing trade")
            error_response = {
                "error": str(e)
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Error processing trade")
            error_response = {
                "error": str(e)
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


class StockSummaryView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Query Parameters:
          - time_zone: (Optional)(default: UTC)
          - period: (Optional) "today","this_month", "custom"
          - start_date and end_date: (Required if period=="custom") in YYYY-MM-DD format
          - date: (Optional)
          - company: (Optional) Filter by company name
        """
        try:
            time_zone_str = request.GET.get('time_zone', 'UTC')
            period = request.GET.get('period', None)
            specific_date_str = request.GET.get('date', None)
            company = request.GET.get('company', None)

            tz = pytz.timezone(time_zone_str)

            now = datetime.now(tz)
            start_date = None
            end_date = None
            if specific_date_str:
                specific_date = datetime.strptime(specific_date_str, "%Y-%m-%d")
                specific_date = tz.localize(specific_date)
                start_date = specific_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = specific_date.replace(hour=23, minute=59, second=59, microsecond=999999)

            elif period:
                period = period.lower()
                if period == "today":
                    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
                elif period == "this_month":
                    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    end_date = now
                elif period == "custom":
                    start_date_str = request.GET.get('start_date', None)
                    end_date_str = request.GET.get('end_date', None)
                    if not start_date_str or not end_date_str:
                        return Response({"error": "For custom period, provide both 'start_date' and 'end_date' in YYYY-MM-DD format."}, status=status.HTTP_400_BAD_REQUEST)
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                    start_date = tz.localize(start_date)
                    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                    end_date = tz.localize(end_date)
                    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                else:
                    return Response({"error": f"Unsupported period value: {period}"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                start_date = datetime.min.replace(tzinfo=pytz.UTC)
                end_date = now

            start_date_utc = start_date.astimezone(pytz.UTC)
            end_date_utc = end_date.astimezone(pytz.UTC)

            summary = TradeService.get_stock_summary_range(request.user, start_date_utc, end_date_utc, company)
            return Response(summary, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Error fetching stock summary")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)