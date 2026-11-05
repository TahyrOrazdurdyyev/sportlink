"""
Match views
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MatchResult
from .serializers import MatchResultSerializer


class MatchResultViewSet(viewsets.ModelViewSet):
    """
    Match Result ViewSet
    """
    serializer_class = MatchResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        booking_id = self.request.query_params.get('booking_id')
        if booking_id:
            return MatchResult.objects.filter(booking_id=booking_id)
        return MatchResult.objects.filter(recorded_by=self.request.user)
    
    def create(self, request):
        """Create match result"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(recorded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

