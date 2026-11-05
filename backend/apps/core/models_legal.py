"""
Legal documents models - Privacy Policy and Terms of Service
"""
import uuid
from datetime import datetime
from mongoengine import Document, fields


class LegalDocument(Document):
    """Model for storing legal documents (Privacy Policy, Terms of Service)"""
    
    DOCUMENT_TYPES = [
        ('privacy_policy', 'Privacy Policy'),
        ('terms_of_service', 'Terms of Service'),
    ]
    
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    document_type = fields.StringField(choices=DOCUMENT_TYPES, required=True, unique=True)
    
    # Content in multiple languages
    title = fields.DictField(required=True)  # {'en': '...', 'ru': '...', 'tk': '...'}
    content = fields.DictField(required=True)  # {'en': '...', 'ru': '...', 'tk': '...'}
    
    # Version tracking
    version = fields.StringField(default='1.0')
    effective_date = fields.DateTimeField(default=datetime.utcnow)
    
    # Status
    is_active = fields.BooleanField(default=True)
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'legal_documents',
        'indexes': [
            'document_type',
            'is_active',
            'created_at',
        ]
    }
    
    def __str__(self):
        return f"{self.get_document_type_display()} v{self.version}"
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

