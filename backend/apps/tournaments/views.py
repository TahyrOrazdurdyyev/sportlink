"""
Tournament views for MongoDB
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.core.mongoengine_drf import MongoEngineModelViewSet
from apps.tournaments.models import Tournament
from apps.tournaments.serializers import TournamentSerializer


class TournamentViewSet(MongoEngineModelViewSet):
    """
    Tournament ViewSet (accessible for all users)
    """
    permission_classes = [AllowAny]
    serializer_class = TournamentSerializer
    
    def get_queryset(self):
        # Show all tournaments except drafts
        return Tournament.objects.filter(status__ne='draft').order_by('-start_date')


class AdminTournamentViewSet(MongoEngineModelViewSet):
    """
    Admin Tournament CRUD
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TournamentSerializer
    
    def get_queryset(self):
        return Tournament.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        tournament = serializer.save()
        if not tournament.created_by:
            tournament.created_by = self.request.user
            tournament.save()
        return tournament

