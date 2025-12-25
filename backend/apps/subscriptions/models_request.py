"""
Subscription Request Model - for pending subscription payments
"""
import uuid
from datetime import datetime
from mongoengine import Document, fields
from apps.users.models import User
from apps.subscriptions.models import SubscriptionPlan


class SubscriptionRequest(Document):
    """Subscription request waiting for office payment confirmation"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),  # Waiting for payment
        ('approved', 'Approved'),  # Payment confirmed, subscription activated
        ('rejected', 'Rejected'),  # Request rejected
        ('cancelled', 'Cancelled'),  # User cancelled
    ]
    
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # Relation
    user = fields.ReferenceField(User, required=True, reverse_delete_rule=1, dbref=False)
    plan = fields.ReferenceField(SubscriptionPlan, required=True, dbref=False)
    
    # Request details
    period = fields.StringField(choices=PERIOD_CHOICES, required=True)
    amount = fields.FloatField(required=True)  # Expected payment amount
    
    # Status
    status = fields.StringField(choices=STATUS_CHOICES, default='pending')
    
    # Notes
    user_notes = fields.StringField(max_length=500)  # Notes from user
    admin_notes = fields.StringField(max_length=500)  # Notes from admin
    rejection_reason = fields.StringField(max_length=500)  # If rejected
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    approved_at = fields.DateTimeField()
    rejected_at = fields.DateTimeField()
    
    # Admin who processed
    processed_by = fields.ReferenceField(User, dbref=False)
    
    meta = {
        'collection': 'subscription_requests',
        'indexes': [
            'user',
            'status',
            'created_at',
            [('status', 1), ('created_at', -1)],
        ]
    }
    
    def __str__(self):
        return f"Request {self.id} - {self.user.phone} - {self.plan.name.get('en', 'Unknown')} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def approve(self, admin_user, admin_notes=""):
        """Approve request and create subscription"""
        if self.status != 'pending':
            raise ValueError("Only pending requests can be approved")
        
        from apps.subscriptions.models_user import UserSubscription
        from datetime import timedelta
        
        # Get user and plan safely
        mongo_dict = self.to_mongo().to_dict()
        user_id = mongo_dict.get('user')
        plan_id = mongo_dict.get('plan')
        
        if not user_id or not plan_id:
            raise ValueError("Invalid user or plan reference")
        
        user = User.objects(id=user_id).first()
        plan = SubscriptionPlan.objects(id=plan_id).first()
        
        if not user or not plan:
            raise ValueError("User or plan not found")
        
        # Calculate subscription period
        start_date = datetime.utcnow()
        if self.period == 'monthly':
            end_date = start_date + timedelta(days=30)
        else:  # yearly
            end_date = start_date + timedelta(days=365)
        
        # Create user subscription
        subscription = UserSubscription(
            user=user,
            plan=plan,
            start_date=start_date,
            end_date=end_date,
            status='active',
            amount_paid=self.amount,
            payment_method='cash',
        )
        subscription.save()
        
        # Update request status
        self.status = 'approved'
        self.approved_at = datetime.utcnow()
        self.processed_by = admin_user
        self.admin_notes = admin_notes
        self.save()
        
        return subscription
    
    def reject(self, admin_user, reason=""):
        """Reject request"""
        if self.status != 'pending':
            raise ValueError("Only pending requests can be rejected")
        
        self.status = 'rejected'
        self.rejected_at = datetime.utcnow()
        self.processed_by = admin_user
        self.rejection_reason = reason
        self.save()
    
    def cancel(self):
        """User cancels request"""
        if self.status != 'pending':
            raise ValueError("Only pending requests can be cancelled")
        
        self.status = 'cancelled'
        self.save()

