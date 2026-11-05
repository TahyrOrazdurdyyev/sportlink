"""
File upload views for courts
"""
import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from apps.courts.models import Court


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_court_image(request):
    """
    Upload an image for a court
    """
    court_id = request.data.get('court_id')
    image = request.FILES.get('image')
    
    if not court_id:
        return Response({
            'error': 'court_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not image:
        return Response({
            'error': 'image file is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size (max 5MB)
    if image.size > 5 * 1024 * 1024:
        return Response({
            'error': 'File size must be less than 5MB'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
    if image.content_type not in allowed_types:
        return Response({
            'error': 'Only JPEG, PNG, and WebP images are allowed'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get court
    try:
        court = Court.objects.get(id=court_id)
    except Court.DoesNotExist:
        return Response({
            'error': 'Court not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if court already has 10 images
    if len(court.images or []) >= 10:
        return Response({
            'error': 'Maximum 10 images allowed per court'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate unique filename
    ext = os.path.splitext(image.name)[1]
    filename = f'courts/{court_id}/{uuid.uuid4()}{ext}'
    
    # Save file
    try:
        path = default_storage.save(filename, image)
        
        # Get full URL
        if settings.USE_S3:
            # If using S3
            file_url = default_storage.url(path)
        else:
            # Local storage
            file_url = f"{settings.MEDIA_URL}{path}"
            # Make it absolute URL
            if not file_url.startswith('http'):
                file_url = f"{request.build_absolute_uri('/')[:-1]}{file_url}"
        
        # Add to court images
        if not court.images:
            court.images = []
        court.images.append(file_url)
        court.save()
        
        return Response({
            'url': file_url,
            'message': 'Image uploaded successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Failed to upload image: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_court_image(request, court_id, image_index):
    """
    Delete an image from a court
    """
    try:
        court = Court.objects.get(id=court_id)
    except Court.DoesNotExist:
        return Response({
            'error': 'Court not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if not court.images or image_index >= len(court.images):
        return Response({
            'error': 'Image not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get image URL
    image_url = court.images[image_index]
    
    # Remove from list
    court.images.pop(image_index)
    court.save()
    
    # Try to delete file from storage
    try:
        # Extract path from URL
        if settings.MEDIA_URL in image_url:
            path = image_url.split(settings.MEDIA_URL)[-1]
            if default_storage.exists(path):
                default_storage.delete(path)
    except Exception as e:
        print(f"Failed to delete file: {e}")
    
    return Response({
        'message': 'Image deleted successfully'
    }, status=status.HTTP_200_OK)

