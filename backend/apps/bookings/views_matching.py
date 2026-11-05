"""
Views for opponent matching
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.bookings.models import Booking
from apps.bookings.matching import OpponentMatch, find_opponent_for_booking
from apps.users.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_booking_matches(request, booking_id):
    """Get all matches for a booking"""
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response(
            {'error': 'Booking not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    matches = OpponentMatch.objects(booking=booking, status='matched')
    
    matches_data = []
    for match in matches:
        opponent = match.opponent
        matches_data.append({
            'match_id': str(match.id),
            'opponent': {
                'id': str(opponent.id),
                'nickname': opponent.nickname,
                'first_name': opponent.first_name,
                'last_name': opponent.last_name,
            },
            'matched_at': match.matched_at.isoformat() if match.matched_at else None,
            'status': match.status,
        })
    
    return Response({
        'booking_id': str(booking.id),
        'matches_count': len(matches_data),
        'opponents_needed': booking.opponents_needed,
        'matches': matches_data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_matches(request):
    """Get all matches where current user is involved (as seeker or opponent)"""
    # Matches where user is the seeker
    seeker_matches = OpponentMatch.objects(seeker=request.user, status='matched')
    
    # Matches where user is the opponent
    opponent_matches = OpponentMatch.objects(opponent=request.user, status='matched')
    
    all_matches = []
    
    # Process seeker matches
    for match in seeker_matches:
        booking = match.booking
        opponent = match.opponent
        all_matches.append({
            'match_id': str(match.id),
            'role': 'seeker',
            'opponent': {
                'id': str(opponent.id),
                'nickname': opponent.nickname,
                'first_name': opponent.first_name,
                'last_name': opponent.last_name,
            },
            'booking': {
                'id': str(booking.id),
                'court_id': str(booking.court.id),
                'court_name': booking.court.name if hasattr(booking.court, 'name') else 'Court',
                'start_time': booking.start_time.isoformat(),
                'end_time': booking.end_time.isoformat(),
                'status': booking.status,
            },
            'matched_at': match.matched_at.isoformat() if match.matched_at else None,
        })
    
    # Process opponent matches
    for match in opponent_matches:
        booking = match.booking
        seeker = match.seeker
        all_matches.append({
            'match_id': str(match.id),
            'role': 'opponent',
            'opponent': {
                'id': str(seeker.id),
                'nickname': seeker.nickname,
                'first_name': seeker.first_name,
                'last_name': seeker.last_name,
            },
            'booking': {
                'id': str(booking.id),
                'court_id': str(booking.court.id),
                'court_name': booking.court.name if hasattr(booking.court, 'name') else 'Court',
                'start_time': booking.start_time.isoformat(),
                'end_time': booking.end_time.isoformat(),
                'status': booking.status,
            },
            'matched_at': match.matched_at.isoformat() if match.matched_at else None,
        })
    
    # Sort by matched_at descending
    all_matches.sort(key=lambda x: x['matched_at'] or '', reverse=True)
    
    return Response({
        'matches_count': len(all_matches),
        'matches': all_matches,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def find_potential_opponents(request):
    """Find potential opponents for a booking"""
    booking_id = request.query_params.get('booking_id')
    
    if not booking_id:
        return Response(
            {'error': 'booking_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response(
            {'error': 'Booking not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not booking.find_opponents:
        return Response(
            {'error': 'This booking is not looking for opponents'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    candidates = find_opponent_for_booking(booking)
    
    candidates_data = []
    for candidate_booking in candidates:
        user = candidate_booking.user
        candidates_data.append({
            'booking_id': str(candidate_booking.id),
            'user': {
                'id': str(user.id),
                'nickname': user.nickname,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'opponents_needed': candidate_booking.opponents_needed,
            'number_of_players': candidate_booking.number_of_players,
        })
    
    return Response({
        'booking_id': str(booking.id),
        'potential_opponents_count': len(candidates_data),
        'potential_opponents': candidates_data,
    })

