from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
import json
from .models import Poll, PollOption, PollResponse, PollQuestion

@require_POST
@csrf_protect
def poll_vote(request):
    try:
        data = json.loads(request.body)
        poll_id = data.get('poll_id')
        respondent_name = data.get('respondent_name')
        responses = data.get('responses', [])

        if not all([poll_id, respondent_name, responses]):
            return JsonResponse({
                'success': False,
                'error': 'Informations manquantes'
            })

        poll = Poll.objects.get(id=poll_id)
        
        if poll.is_closed:
            return JsonResponse({
                'success': False,
                'error': 'Ce sondage est fermé'
            })

        # Vérifier si l'utilisateur a déjà voté pour une des questions
        if PollResponse.objects.filter(poll=poll, respondent_name=respondent_name).exists():
            return JsonResponse({
                'success': False,
                'error': 'Vous avez déjà participé à ce sondage'
            })

        # Vérifier les questions obligatoires
        required_questions = poll.questions.filter(is_required=True).values_list('id', flat=True)
        responded_questions = {response['question_id'] for response in responses}
        missing_required = set(required_questions) - responded_questions