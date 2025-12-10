"""
MongoDB Admin for Users
"""
from django.contrib import admin
from django.http import HttpResponse
import csv
from apps.users.models import User


class UserAdmin:
    """Custom admin for MongoDB User"""
    list_display = ['phone', 'first_name', 'last_name', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_staff', 'gender', 'created_at']
    search_fields = ['phone', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return User.objects.all()
    
    def export_csv(self, request, queryset=None):
        """Export users to CSV"""
        if queryset is None:
            queryset = self.get_queryset()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Phone', 'Email', 'First Name', 'Last Name', 'City', 'Active', 'Created'])
        
        for user in queryset:
            writer.writerow([
                user.phone, user.email, user.first_name, 
                user.last_name, user.city, user.is_active, 
                user.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response


# Register admin (simplified for MongoDB)
user_admin = UserAdmin()