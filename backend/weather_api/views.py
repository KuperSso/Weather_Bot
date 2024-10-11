from rest_framework import generics
from .models import UserLog
from .serializers import LogSerializer
from django.utils.dateparse import parse_datetime

class LogList(generics.ListAPIView):
    queryset = UserLog.objects.all()
    serializer_class = LogSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if start_date and end_date:
            start_date = parse_datetime(start_date)
            end_date = parse_datetime(end_date)
            queryset = queryset.filter(timestamp__range=(start_date, end_date))

        return queryset

class UserLogList(LogList):
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return super().get_queryset().filter(user_id=user_id)