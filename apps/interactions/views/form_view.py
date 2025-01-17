from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import CustomForm, FormResponse

@require_http_methods(["POST"])
def handle_form_submission(request):
    """Handle form submission and return JSON response"""
    try:
        form_id = request.POST.get('form_id')
        form = get_object_or_404(CustomForm, id=form_id)
        
        # Create response data
        data = {
            field.label: request.POST.get(field.label.lower())
            for field in form.fields.all()
        }
        
        # Save response
        response = FormResponse.objects.create(
            form=form,
            data=data
        )
        
        # Send email if configured
        if form.send_email:
            response.send_email_notification()
        
        return JsonResponse({
            'status': 'success',
            'message': form.success_message
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=400)