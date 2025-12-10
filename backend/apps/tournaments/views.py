"""
Tournament views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from .models import Tournament, TournamentParticipant
from .serializers import TournamentSerializer, TournamentParticipantSerializer


class TournamentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Tournament ViewSet (read-only for users)
    """
    queryset = Tournament.objects.filter(registration_open=True).order_by('-start_date')
    serializer_class = TournamentSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request, pk=None):
        """Register for tournament"""
        tournament = self.get_object()
        
        if not tournament.registration_open:
            return Response(
                {'error': 'Registration is closed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already registered
        existing = TournamentParticipant.objects.filter(
            tournament=tournament,
            user=request.user
        ).first()
        
        if existing:
            return Response(
                {'error': 'Already registered'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Check max participants
        participant_count = tournament.participants.filter(
            status__in=['accepted', 'paid']
        ).count()
        
        if participant_count >= tournament.max_participants:
            tournament.registration_open = False
            tournament.save()
            return Response(
                {'error': 'Tournament is full'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Register
        participant = TournamentParticipant.objects.create(
            tournament=tournament,
            user=request.user,
            status='applied'
        )
        
        # Check if full now
        participant_count = tournament.participants.filter(
            status__in=['accepted', 'paid']
        ).count()
        if participant_count >= tournament.max_participants:
            tournament.registration_open = False
            tournament.save()
        
        # Send notification
        from apps.notifications.tasks import send_tournament_registration_confirmation
        send_tournament_registration_confirmation.delay(str(participant.id))
        
        return Response(
            TournamentParticipantSerializer(participant).data,
            status=status.HTTP_201_CREATED
        )

