"""
Tournament registration views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.tournaments.models import Tournament
from datetime import datetime


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_for_tournament(request, tournament_id):
    """
    Register current user for a tournament
    
    Body:
    - notes: Optional notes from user
    """
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return Response({
            'error': 'Tournament not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if registration is open
    if not tournament.can_register():
        return Response({
            'error': 'Registration is not open for this tournament'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user already registered
    user = request.user
    existing_participant = None
    
    if tournament.participants:
        for participant in tournament.participants:
            if str(participant.user.id) == str(user.id):
                existing_participant = participant
                break
    
    if existing_participant:
        return Response({
            'error': 'You are already registered for this tournament',
            'status': existing_participant.status
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check max participants
    if tournament.is_full():
        return Response({
            'error': 'Tournament is full',
            'message': f'All {tournament.max_participants} spots have been taken. No more registrations available.',
            'max_participants': tournament.max_participants,
            'current_count': tournament.get_participant_count(),
            'available_spots': 0
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Register user
    notes = request.data.get('notes', '')
    
    try:
        tournament.register_participant(user, notes)
        
        return Response({
            'message': 'Successfully registered for tournament',
            'tournament_id': str(tournament.id),
            'tournament_name': tournament.name_i18n,
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': f'Failed to register: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_tournament_registration(request, tournament_id):
    """
    Cancel current user's tournament registration
    """
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return Response({
            'error': 'Tournament not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    
    # Find user's registration
    participant = None
    if tournament.participants:
        for p in tournament.participants:
            if str(p.user.id) == str(user.id):
                participant = p
                break
    
    if not participant:
        return Response({
            'error': 'You are not registered for this tournament'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Remove participant
    tournament.participants = [p for p in tournament.participants if str(p.user.id) != str(user.id)]
    tournament.save()
    
    return Response({
        'message': 'Registration cancelled successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_tournament_registrations(request):
    """
    Get list of tournaments the current user is registered for
    """
    user = request.user
    
    # Find all tournaments where user is a participant
    tournaments = Tournament.objects.all()
    my_tournaments = []
    
    for tournament in tournaments:
        if tournament.participants:
            for participant in tournament.participants:
                if str(participant.user.id) == str(user.id):
                    my_tournaments.append({
                        'id': str(tournament.id),
                        'name': tournament.name_i18n,
                        'description': tournament.description_i18n,
                        'start_date': tournament.start_date.isoformat() if tournament.start_date else None,
                        'end_date': tournament.end_date.isoformat() if tournament.end_date else None,
                        'status': tournament.status,
                        'participant_status': participant.status,
                        'registration_date': participant.registration_date.isoformat() if participant.registration_date else None,
                    })
                    break
    
    return Response({
        'tournaments': my_tournaments
    })

