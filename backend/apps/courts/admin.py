"""
MongoDB Admin for Courts
"""
from django.contrib import admin
from django.http import HttpResponse
import csv
from apps.courts.models import Court


class CourtAdmin:
    """Custom admin for MongoDB Court"""
    list_display = ['get_name', 'type', 'address', 'is_active', 'created_at']
    list_filter = ['type', 'is_active', 'created_at']
    search_fields = ['address']
    ordering = ['-created_at']
    
    def get_name(self, obj):
        return obj.get_name()
    get_name.short_description = 'Name'
    
    def get_queryset(self):
        return Court.objects.all()
    
    def export_csv(self, request, queryset=None):
        """Export courts to CSV"""
        if queryset is None:
            queryset = self.get_queryset()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="courts.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Type', 'Address', 'Active', 'Created'])
        
        for court in queryset:
            writer.writerow([
                court.get_name(), court.type, court.address,
                court.is_active, court.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        return response


# Register admin
court_admin = CourtAdmin()