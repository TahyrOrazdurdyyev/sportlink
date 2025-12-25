"""
Opponent Matching - Partner Search System
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.users.models import User
from apps.subscriptions.permissions import require_feature
from datetime import datetime


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@require_feature('opponent_matching')
def find_opponents(request):
    """
    Find opponents matching user's skill level and preferences
    
    Query params:
    - experience_level: int (1-7, optional - defaults to current user's level ±1)
    - category_id: ObjectId (optional - filter by sport category)
    - city: str (optional - filter by location)
    - limit: int (default 20)
    """
    current_user = request.user
    
    # Get query parameters
    experience_level = request.query_params.get('experience_level')
    category_id = request.query_params.get('category_id')
    city = request.query_params.get('city', current_user.city)
    limit = int(request.query_params.get('limit', 20))
    
    # Build query
    query = {
        'is_active': True,
        'is_banned': False,
        'id__ne': current_user.id,  # Exclude current user
    }
    
    # Filter by city
    if city:
        query['city'] = city
    
    # Filter by experience level (±1 from user's level)
    if experience_level:
        target_level = int(experience_level)
    else:
        target_level = current_user.experience_level or 3
    
    # Find users within ±1 skill level
    query['experience_level__gte'] = max(1, target_level - 1)
    query['experience_level__lte'] = min(7, target_level + 1)
    
    # Find matching users
    users = User.objects(**query).order_by('-rating')[:limit]
    
    # Serialize results
    results = []
    for user in users:
        # Calculate compatibility score (0-100)
        compatibility = calculate_compatibility(current_user, user)
        
        results.append({
            'id': str(user.id),
            'first_name': user.first_name,
            'last_name': user.last_name,
            'avatar_url': user.avatar_url,
            'experience_level': user.experience_level,
            'rating': float(user.rating) if user.rating else 0.0,
            'city': user.city,
            'categories': [
                {
                    'id': str(cat.category_id),
                    'name': cat.name
                } for cat in (user.categories or [])
            ],
            'compatibility_score': compatibility,
            'last_active': user.last_active_at.isoformat() if user.last_active_at else None,
        })
    
    return Response({
        'count': len(results),
        'results': results,
        'filters': {
            'experience_level': target_level,
            'city': city,
            'category_id': category_id,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@require_feature('opponent_matching')
def send_match_invitation(request):
    """
    Send match invitation to another user
    
    Body:
    - opponent_id: UUID
    - court_id: UUID (optional)
    - proposed_time: datetime (optional)
    - message: str (optional)
    """
    current_user = request.user
    opponent_id = request.data.get('opponent_id')
    
    if not opponent_id:
        return Response({
            'error': 'opponent_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        opponent = User.objects.get(id=opponent_id)
    except User.DoesNotExist:
        return Response({
            'error': 'Opponent not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if opponent has active subscription with opponent_matching feature
    # TODO: Add subscription check here
    
    # Create match invitation (using notifications system)
    from apps.notifications.fcm_utils import send_push_notification
    
    message = request.data.get('message', f'{current_user.get_full_name()} invites you to play')
    
    # Send push notification if opponent has FCM token
    if opponent.fcm_token:
        send_push_notification(
            token=opponent.fcm_token,
            title='Match Invitation',
            body=message,
            data={
                'type': 'match_invitation',
                'sender_id': str(current_user.id),
                'sender_name': current_user.get_full_name(),
            }
        )
    
    return Response({
        'success': True,
        'message': 'Match invitation sent successfully',
        'opponent': {
            'id': str(opponent.id),
            'name': opponent.get_full_name(),
        }
    })


def calculate_compatibility(user1, user2):
    """
    Calculate compatibility score between two users (0-100)
    
    Factors:
    - Experience level similarity (40 points)
    - Common sports/categories (30 points)
    - Location proximity (20 points)
    - Rating similarity (10 points)
    """
    score = 0
    
    # Experience level similarity (40 points)
    if user1.experience_level and user2.experience_level:
        level_diff = abs(user1.experience_level - user2.experience_level)
        score += max(0, 40 - (level_diff * 13))  # -13 points per level difference
    
    # Common categories (30 points)
    if user1.categories and user2.categories:
        user1_cats = set(str(cat.category_id) for cat in user1.categories)
        user2_cats = set(str(cat.category_id) for cat in user2.categories)
        common = len(user1_cats.intersection(user2_cats))
        score += min(30, common * 10)  # 10 points per common category
    
    # Same city (20 points)
    if user1.city and user2.city and user1.city == user2.city:
        score += 20
    
    # Rating similarity (10 points)
    if user1.rating and user2.rating:
        rating_diff = abs(user1.rating - user2.rating)
        score += max(0, 10 - rating_diff)  # -1 point per rating difference
    
    return min(100, max(0, int(score)))

