"""
Tournament image upload views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.core.files.storage import default_storage
from apps.tournaments.models import Tournament
import os
import uuid


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_tournament_image(request, tournament_id):
    """
    Upload tournament image
    Requires 'image' file in the request
    """
    print(f"\n{'='*80}")
    print(f"UPLOAD TOURNAMENT IMAGE - tournament_id: {tournament_id}")
    print(f"FILES: {request.FILES}")
    print(f"DATA: {request.data}")
    print(f"{'='*80}\n")
    
    try:
        tournament = Tournament.objects.get(id=tournament_id)
        print(f"Tournament found: {tournament.name_i18n}")
    except Tournament.DoesNotExist:
        print(f"Tournament not found: {tournament_id}")
        return Response({'error': 'Tournament not found'}, status=status.HTTP_404_NOT_FOUND)
    
    image_file = request.FILES.get('image')
    
    if not image_file:
        print(f"No image file in request. FILES keys: {list(request.FILES.keys())}")
        return Response({'error': 'Image file is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size (e.g., 10MB limit)
    max_file_size = 10 * 1024 * 1024  # 10 MB
    if image_file.size > max_file_size:
        return Response({'error': 'Image file size cannot exceed 10MB'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file type
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    file_extension = os.path.splitext(image_file.name)[1].lower()
    if file_extension not in allowed_extensions:
        return Response({'error': 'Unsupported image file type. Allowed: JPG, PNG, WebP'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Delete old image if exists
        if tournament.image_url:
            print(f"Deleting old image: {tournament.image_url}")
            try:
                if settings.DEFAULT_FILE_STORAGE == 'django.core.files.storage.FileSystemStorage':
                    relative_path = tournament.image_url.replace(settings.MEDIA_URL, '', 1)
                    if default_storage.exists(relative_path):
                        default_storage.delete(relative_path)
                elif settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto3.S3Boto3Storage':
                    from urllib.parse import urlparse
                    parsed_url = urlparse(tournament.image_url)
                    s3_key = parsed_url.path.lstrip('/')
                    if default_storage.exists(s3_key):
                        default_storage.delete(s3_key)
            except Exception as storage_error:
                print(f"Warning: Failed to delete old tournament image: {storage_error}")
        
        # Generate unique filename
        filename = f"tournaments/{tournament_id}/{uuid.uuid4().hex}{file_extension}"
        print(f"Saving file as: {filename}")
        
        # Save the file
        file_path = default_storage.save(filename, image_file)
        print(f"File saved at: {file_path}")
        
        # Get the URL
        image_url = default_storage.url(file_path)
        print(f"Image URL: {image_url}")
        
        # If URL is relative, make it absolute
        if image_url.startswith('/'):
            # Build absolute URL
            scheme = 'https' if request.is_secure() else 'http'
            host = request.get_host()
            image_url = f"{scheme}://{host}{image_url}"
            print(f"Absolute Image URL: {image_url}")
        
        # Update tournament
        tournament.image_url = image_url
        tournament.save()
        print(f"Tournament updated with image_url")
        
        return Response({
            'message': 'Tournament image uploaded successfully',
            'image_url': image_url
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        print(f"ERROR uploading image: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': f'Failed to upload image: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_tournament_image(request, tournament_id):
    """
    Delete tournament image
    """
    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return Response({'error': 'Tournament not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not tournament.image_url:
        return Response({'error': 'No image to delete'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Delete file from storage
        try:
            if settings.DEFAULT_FILE_STORAGE == 'django.core.files.storage.FileSystemStorage':
                relative_path = tournament.image_url.replace(settings.MEDIA_URL, '', 1)
                if default_storage.exists(relative_path):
                    default_storage.delete(relative_path)
            elif settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto3.S3Boto3Storage':
                from urllib.parse import urlparse
                parsed_url = urlparse(tournament.image_url)
                s3_key = parsed_url.path.lstrip('/')
                if default_storage.exists(s3_key):
                    default_storage.delete(s3_key)
        except Exception as storage_error:
            print(f"Warning: Failed to delete file from storage: {storage_error}")
        
        # Clear image_url
        tournament.image_url = None
        tournament.save()
        
        return Response({'message': 'Tournament image deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    except Exception as e:
        return Response({'error': f'Failed to delete image: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

