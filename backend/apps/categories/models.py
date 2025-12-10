"""
Category models for MongoDB
"""
import uuid
from datetime import datetime
from mongoengine import Document, fields


class Category(Document):
    """Sports category/type"""
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # Multilingual name and description
    name_i18n = fields.DictField(default=dict)  # {"tk": "Tennis", "ru": "Теннис", "en": "Tennis"}
    description_i18n = fields.DictField(default=dict)  # {"tk": "...", "ru": "...", "en": "..."}
    
    # Parent category for hierarchy
    parent = fields.ReferenceField('self', reverse_delete_rule=1)  # CASCADE
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'categories',
        'indexes': [
            'parent',
            'created_at',
        ]
    }
    
    def __str__(self):
        return self.name_i18n.get('tk', self.name_i18n.get('ru', self.name_i18n.get('en', str(self.id))))
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def get_name(self, language='tk'):
        """Get name in specified language"""
        return self.name_i18n.get(language, self.name_i18n.get('tk', ''))
    
    def get_description(self, language='tk'):
        """Get description in specified language"""
        return self.description_i18n.get(language, self.description_i18n.get('tk', ''))
