"""
Legal documents views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from apps.core.models_legal import LegalDocument
from apps.core.serializers_legal import LegalDocumentSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_privacy_policy(request):
    """Get active Privacy Policy"""
    language = request.query_params.get('lang', 'en')
    
    try:
        document = LegalDocument.objects.get(
            document_type='privacy_policy',
            is_active=True
        )
        serializer = LegalDocumentSerializer(document)
        return Response(serializer.data)
    except LegalDocument.DoesNotExist:
        return Response({
            'error': 'Privacy Policy not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_terms_of_service(request):
    """Get active Terms of Service"""
    language = request.query_params.get('lang', 'en')
    
    try:
        document = LegalDocument.objects.get(
            document_type='terms_of_service',
            is_active=True
        )
        serializer = LegalDocumentSerializer(document)
        return Response(serializer.data)
    except LegalDocument.DoesNotExist:
        return Response({
            'error': 'Terms of Service not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def manage_legal_documents(request):
    """Admin: List all legal documents or create new one"""
    if request.method == 'GET':
        documents = LegalDocument.objects.all().order_by('-created_at')
        serializer = LegalDocumentSerializer(documents, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = LegalDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def manage_legal_document_detail(request, document_id):
    """Admin: Get, update or delete a specific legal document"""
    try:
        document = LegalDocument.objects.get(id=document_id)
    except LegalDocument.DoesNotExist:
        return Response({
            'error': 'Document not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = LegalDocumentSerializer(document)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = LegalDocumentSerializer(document, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

