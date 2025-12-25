"""
User serializers for MongoDB
"""
from rest_framework import serializers
from apps.core.mongoengine_drf import MongoEngineModelSerializer
from apps.users.models import User, UserCategory
from apps.categories.models import Category


class UserCategorySerializer(serializers.Serializer):
    """Serializer for user's favorite sport with experience level"""
    category_id = serializers.UUIDField()
    experience_level = serializers.IntegerField(min_value=1, max_value=10, default=1)
    
    # Read-only fields for convenience
    category_name = serializers.SerializerMethodField(read_only=True)
    
    def get_category_name(self, obj):
        """Get category name from category_id"""
        try:
            from apps.categories.models import Category
            category = Category.objects.get(id=obj.category_id)
            return category.name_i18n
        except Category.DoesNotExist:
            return None


class UserSerializer(MongoEngineModelSerializer):
    """Full user serializer"""
    favorite_sports = UserCategorySerializer(many=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'phone', 'nickname', 'email', 'first_name', 'last_name', 'birth_date',
            'age', 'gender', 'city', 'location', 'favorite_sports', 'experience_level',
            'preferred_ball', 'goals', 'rating', 'avatar_url', 'is_active',
            'created_at', 'updated_at', 'last_active_at'
        ]
        read_only_fields = ['id', 'rating', 'created_at', 'updated_at']


class UserPublicSerializer(MongoEngineModelSerializer):
    """Public user profile serializer (limited fields)"""
    
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'city', 'experience_level',
            'rating', 'avatar_url', 'last_active_at'
        ]


class UserCreateSerializer(MongoEngineModelSerializer):
    """Serializer for user creation"""
    
    class Meta:
        model = User
        fields = [
            'phone', 'email', 'first_name', 'last_name', 'birth_date',
            'gender', 'city', 'firebase_uid'
        ]
    
    def create(self, validated_data):
        """Create user with Firebase UID"""
        user = User(**validated_data)
        user.save()
        return user


class UserUpdateSerializer(MongoEngineModelSerializer):
    """Serializer for updating user profile"""
    location = serializers.ListField(
        child=serializers.FloatField(),
        required=False,
        allow_null=True
    )
    favorite_sports = UserCategorySerializer(many=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'birth_date', 'age', 'gender',
            'city', 'location', 'favorite_sports', 'experience_level',
            'preferred_ball', 'goals', 'avatar_url'
        ]
    
    def update(self, instance, validated_data):
        """Update user with location and favorite_sports handling"""
        # Handle location (convert from [lng, lat] to GeoJSON Point)
        location = validated_data.pop('location', None)
        if location is not None and len(location) == 2:
            validated_data['location'] = {
                'type': 'Point',
                'coordinates': [float(location[0]), float(location[1])]
            }
        
        # Handle favorite_sports (convert from dict to UserCategory objects)
        favorite_sports_data = validated_data.pop('favorite_sports', None)
        if favorite_sports_data is not None:
            from apps.users.models import UserCategory
            favorite_sports_objects = []
            for sport_data in favorite_sports_data:
                user_category = UserCategory(
                    category_id=sport_data['category_id'],
                    experience_level=sport_data.get('experience_level', 1)
                )
                favorite_sports_objects.append(user_category)
            validated_data['favorite_sports'] = favorite_sports_objects
        
        return super().update(instance, validated_data)


class AdminUserSerializer(MongoEngineModelSerializer):
    """Admin user serializer with all fields"""
    id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'phone', 'nickname', 'email', 'first_name', 'last_name',
            'is_active', 'is_banned', 'is_staff', 'is_superuser',
            'created_at', 'updated_at', 'last_active_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Fix booleans and add subscription info"""
        from apps.subscriptions.models_user import UserSubscription
        from apps.subscriptions.models import SubscriptionPlan
        from datetime import datetime
        from uuid import UUID
        
        ret = super().to_representation(instance)
        ret['is_active'] = bool(instance.is_active)
        ret['is_banned'] = bool(instance.is_banned)
        ret['is_staff'] = bool(instance.is_staff)
        ret['is_superuser'] = bool(instance.is_superuser)
        
        # Add subscription info
        print(f"\nDEBUG: to_representation for user {instance.phone}")
        try:
            # Get active subscription that is not cancelled or expired
            subscription = UserSubscription.objects(
                user=instance, 
                status='active',
                end_date__gte=datetime.utcnow()
            ).order_by('-created_at').first()
            
            print(f"DEBUG: Found subscription: {subscription is not None}")
            
            if subscription:
                # Get plan_id from subscription document
                sub_dict = subscription.to_mongo().to_dict()
                plan_ref = sub_dict.get('plan')
                print(f"DEBUG: Plan ref: {plan_ref} (type: {type(plan_ref)})")
                
                # Convert to UUID
                if isinstance(plan_ref, str):
                    plan_id = UUID(plan_ref)
                elif isinstance(plan_ref, UUID):
                    plan_id = plan_ref
                else:
                    plan_id = plan_ref
                
                print(f"DEBUG: Plan ID: {plan_id}")
                
                # Load plan
                plan = SubscriptionPlan.objects(id=plan_id).first()
                print(f"DEBUG: Loaded plan: {plan is not None}")
                
                if plan:
                    ret['subscription_plan'] = plan.name
                    ret['subscription_end_date'] = subscription.end_date.isoformat() if subscription.end_date else None
                    ret['subscription_status'] = subscription.status
                    print(f"✅ Added subscription info for {instance.phone}: {plan.name}")
                else:
                    ret['subscription_plan'] = None
                    ret['subscription_end_date'] = None
                    ret['subscription_status'] = None
                    print(f"❌ Plan not found")
            else:
                ret['subscription_plan'] = None
                ret['subscription_end_date'] = None
                ret['subscription_status'] = None
                print(f"No subscription found for {instance.phone}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            ret['subscription_plan'] = None
            ret['subscription_end_date'] = None
            ret['subscription_status'] = None
        
        return ret
