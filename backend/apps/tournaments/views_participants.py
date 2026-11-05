"""
Tournament participants views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.tournaments.models import Tournament


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tournament_participants(request, tournament_id):
    """
    Get list of participants for a tournament (admin only)
    """
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return Response({
            'error': 'Tournament not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    participants = []
    
    if tournament.participants:
        from apps.users.models import User
        from uuid import UUID
        
        for participant in tournament.participants:
            try:
                # Get user ID from participant
                # participant.user might be a DBRef, UUID, or User object
                user_ref = participant.to_mongo().to_dict().get('user')
                
                # Convert to UUID if needed
                if isinstance(user_ref, str):
                    user_id = UUID(user_ref)
                elif hasattr(user_ref, 'id'):
                    user_id = user_ref.id
                else:
                    user_id = user_ref
                
                # Load user directly
                user = User.objects.get(id=user_id)
                
                participants.append({
                    'id': str(user.id),
                    'phone': user.phone,
                    'nickname': user.nickname,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'status': participant.status,
                    'registration_date': participant.registration_date.isoformat() if participant.registration_date else None,
                    'payment_status': participant.payment_status,
                    'notes': participant.notes,
                })
            except Exception as e:
                # Skip participants with invalid user references
                continue
    
    return Response({
        'tournament_id': str(tournament.id),
        'tournament_name': tournament.name_i18n,
        'max_participants': tournament.max_participants,
        'current_count': tournament.get_participant_count(),
        'is_full': tournament.is_full(),
        'participants': participants,
        'total_registered': len(participants),
    })

