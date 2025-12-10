"""
Admin tournament views
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.core.permissions import IsAdminUser
from ..models import Tournament
from ..serializers import TournamentSerializer
from apps.courts.models import Court


class AdminTournamentViewSet(viewsets.ModelViewSet):
    """
    Admin Tournament CRUD
    """
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [IsAdminUser]
    
    def create(self, request):
        """Create tournament"""
        data = request.data.copy()
        court_ids = data.pop('court_ids', [])
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        tournament = serializer.save(created_by=request.user)
        
        # Add courts
        if court_ids:
            courts = Court.objects.filter(id__in=court_ids)
            tournament.courts.set(courts)
        
        # Send push notifications
        from apps.notifications.tasks import send_tournament_created_notification
        send_tournament_created_notification.delay(str(tournament.id))
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

