from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_message(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').lower()
        
        # Basic response logic - you can enhance this with more sophisticated AI/ML
        responses = {
            'hello': 'Hi! How can I help you with the quiz today?',
            'hi': 'Hello! Need help with something?',
            'help': 'I can help you with:\n- Quiz navigation\n- Understanding questions\n- Technical issues\n- Exam rules\nWhat do you need help with?',
            'rules': 'Here are the main quiz rules:\n1. Answer all questions\n2. Time limit must be followed\n3. No cheating allowed\n4. You can review answers before submission',
            'time': 'The time limit depends on the quiz. Check the timer at the top of your quiz page.',
            'submit': 'To submit your quiz, click the "Submit" button at the bottom of the page after answering all questions.',
            'stuck': 'If you\'re stuck, try:\n1. Reading the question carefully\n2. Eliminating wrong answers\n3. Using any available hints\n4. Managing your time wisely',
            'score': 'Your score will be displayed immediately after submitting the quiz.',
            'review': 'You can review your answers before final submission using the "Review" button.',
            'reset': 'Contact your teacher or administrator if you need to reset your quiz.',
            'technical': 'For technical issues:\n1. Check your internet connection\n2. Try refreshing the page\n3. Clear browser cache\n4. Contact support if issues persist',
        }
        
        # Default response
        response = "I'm here to help! You can ask me about quiz rules, navigation, technical issues, or any other concerns. What would you like to know?"
        
        # Check for keywords in user message
        for key in responses:
            if key in user_message:
                response = responses[key]
                break
                
        return JsonResponse({
            'status': 'success',
            'response': response
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
