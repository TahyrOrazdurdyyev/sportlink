"""
Report/Export views
"""
import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from apps.users.models import User


class UserExportView(APIView):
    """
    Export users to CSV
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        format_type = request.query_params.get('format', 'csv')
        
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="users.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'ID', 'Phone', 'Email', 'First Name', 'Last Name',
                'City', 'Experience Level', 'Rating', 'Created At'
            ])
            
            users = User.objects.all()
            for user in users:
                writer.writerow([
                    str(user.id),
                    user.phone,
                    user.email or '',
                    user.first_name or '',
                    user.last_name or '',
                    user.city or '',
                    user.experience_level,
                    user.rating,
                    user.created_at.isoformat(),
                ])
            
            return response
        
        return HttpResponse('Format not supported', status=400)

