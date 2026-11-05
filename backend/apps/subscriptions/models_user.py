"""
User Subscription Model
"""
import uuid
from datetime import datetime
from mongoengine import Document, fields
from apps.users.models import User
from apps.subscriptions.models import SubscriptionPlan


class UserSubscription(Document):
    """User's active subscription"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # Relation
    user = fields.ReferenceField(User, required=True, reverse_delete_rule=1, dbref=False)
    plan = fields.ReferenceField(SubscriptionPlan, required=True, dbref=False)
    
    # Period
    start_date = fields.DateTimeField(required=True, default=datetime.utcnow)
    end_date = fields.DateTimeField(required=True)
    
    # Status
    status = fields.StringField(choices=STATUS_CHOICES, default='active')
    is_auto_renew = fields.BooleanField(default=False)
    
    # Payment
    amount_paid = fields.FloatField(required=True)
    payment_method = fields.StringField(max_length=50)
    transaction_id = fields.StringField(max_length=255)
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    cancelled_at = fields.DateTimeField()
    
    meta = {
        'collection': 'user_subscriptions',
        'indexes': [
            'user',
            'status',
            'end_date',
            [('user', 1), ('status', 1)],
        ]
    }
    
    def __str__(self):
        # Get plan ID from MongoDB directly
        sub_dict = self.to_mongo().to_dict()
        plan_id = sub_dict.get('plan')
        
        plan_name = 'Unknown'
        if plan_id:
            plan = SubscriptionPlan.objects(id=plan_id).first()
            if plan:
                plan_name = plan.name.get('en', 'Unknown')
        
        return f"{self.user} - {plan_name} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != 'active':
            return False
        
        now = datetime.utcnow()
        return self.start_date <= now <= self.end_date
    
    def has_feature(self, feature_key):
        """Check if user has access to specific feature"""
        if not self.is_active():
            return False
        
        # Get plan ID from MongoDB directly to avoid dereferencing issues
        sub_dict = self.to_mongo().to_dict()
        plan_id = sub_dict.get('plan')
        
        if not plan_id:
            return False
        
        # Load plan by ID
        plan = SubscriptionPlan.objects(id=plan_id).first()
        if not plan:
            return False
        
        return plan.features.get(feature_key, False)
    
    def cancel(self):
        """Cancel subscription"""
        self.status = 'cancelled'
        self.cancelled_at = datetime.utcnow()
        self.is_auto_renew = False
        self.save()
    
    def expire(self):
        """Mark subscription as expired"""
        self.status = 'expired'
        self.save()

