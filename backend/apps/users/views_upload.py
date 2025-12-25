from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.core.files.storage import default_storage
import os
import uuid


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """
    Upload avatar image for current user.
    Requires 'avatar' file in the request.
    """
    avatar_file = request.FILES.get('avatar')

    if not avatar_file:
        return Response({'error': 'Avatar file is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate file size (e.g., 5MB limit)
    max_file_size = 5 * 1024 * 1024  # 5 MB
    if avatar_file.size > max_file_size:
        return Response({'error': 'Avatar file size cannot exceed 5MB.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate file type
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    file_extension = os.path.splitext(avatar_file.name)[1].lower()
    if file_extension not in allowed_extensions:
        return Response({'error': 'Unsupported image file type. Allowed: JPG, PNG, WebP.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = request.user
        
        # Delete old avatar if exists
        if user.avatar_url:
            try:
                if settings.DEFAULT_FILE_STORAGE == 'django.core.files.storage.FileSystemStorage':
                    relative_path = user.avatar_url.replace(settings.MEDIA_URL, '', 1)
                    if default_storage.exists(relative_path):
                        default_storage.delete(relative_path)
                elif settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto3.S3Boto3Storage':
                    from urllib.parse import urlparse
                    parsed_url = urlparse(user.avatar_url)
                    s3_key = parsed_url.path.lstrip('/')
                    if default_storage.exists(s3_key):
                        default_storage.delete(s3_key)
            except Exception as e:
                print(f"Warning: Failed to delete old avatar: {e}")
        
        # Generate a unique filename
        filename = f"avatars/{user.id}/{uuid.uuid4().hex}{file_extension}"
        
        # Save the file using Django's default storage (local or S3)
        file_path = default_storage.save(filename, avatar_file)
        
        # Get the URL
        avatar_url = default_storage.url(file_path)
        
        # If URL is relative, make it absolute
        if avatar_url.startswith('/'):
            scheme = 'https' if request.is_secure() else 'http'
            host = request.get_host()
            avatar_url = f"{scheme}://{host}{avatar_url}"

        # Update user avatar_url
        user.avatar_url = avatar_url
        user.save()

        return Response({
            'message': 'Avatar uploaded successfully',
            'avatar_url': avatar_url
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Failed to upload avatar: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_avatar(request):
    """
    Delete avatar image for current user.
    """
    try:
        user = request.user
        
        if not user.avatar_url:
            return Response({'error': 'No avatar to delete.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Attempt to delete the file from storage
        try:
            if settings.DEFAULT_FILE_STORAGE == 'django.core.files.storage.FileSystemStorage':
                relative_path = user.avatar_url.replace(settings.MEDIA_URL, '', 1)
                if default_storage.exists(relative_path):
                    default_storage.delete(relative_path)
            elif settings.DEFAULT_FILE_STORAGE == 'storages.backends.s3boto3.S3Boto3Storage':
                from urllib.parse import urlparse
                parsed_url = urlparse(user.avatar_url)
                s3_key = parsed_url.path.lstrip('/')
                if default_storage.exists(s3_key):
                    default_storage.delete(s3_key)
        except Exception as storage_error:
            print(f"Warning: Failed to delete file from storage: {storage_error}")

        # Clear avatar_url from user
        user.avatar_url = None
        user.save()

        return Response({'message': 'Avatar deleted successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Failed to delete avatar: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

