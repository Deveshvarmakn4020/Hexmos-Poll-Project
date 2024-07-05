from django.db.models import F
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .models import Choice, Question, Tags
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)

def get_polls():
    return Question.objects.all()

def get_views(request):
    polls = get_polls()
    polls_list = []

    for poll in polls:
        poll_dict = {
            "Question": poll.question_text,
            "QuestionID": poll.id,
            "Tags": [],
            "OptionVote": {},
        }
        for tag in poll.tags.all():
            poll_dict["Tags"].append(tag.tag_name)

        choices = Choice.objects.filter(question_id=poll.id)
        for choice in choices:
            poll_dict["OptionVote"][choice.choice_text] = choice.votes

        polls_list.append(poll_dict)

    return JsonResponse({"msg": "Fetched polls successfully", "data": polls_list, "success": True})

@csrf_exempt
def create_poll(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question_text = data['question_text']
            choices = data['choices']
            tags = data.get('tags', [])

            if not question_text:
                return JsonResponse({"msg": "Question text is required", "success": False}, status=400)

            new_question = Question.objects.create(
                question_text=question_text,
                pub_date=timezone.now()
            )
            
            for choice_text in choices:
                if choice_text:
                    Choice.objects.create(question=new_question, choice_text=choice_text)

            for tag in tags:
                tag_instance, created = Tags.objects.get_or_create(tag_name=tag)
                new_question.tags.add(tag_instance)

            return JsonResponse({"msg": "Poll created successfully", "success": True})
        
        except Exception as e:
            return JsonResponse({'msg': f"An error has occurred: {str(e)}", "success": False}, status=500)

    return JsonResponse({"msg": "Invalid request method", "success": False}, status=405)

def get_filtered_polls(request):
    tags = request.GET.get('tags', '')
    tags_param = tags.split(',')
    print(f"Tags received: {tags_param}")
    
    # Log the polls before filtering
    polls = Question.objects.all()
    print(f"All polls: {polls}")
    
    if tags_param and tags_param[0] != '':
        polls = Question.objects.filter(tags__tag_name__in=tags_param).distinct()
        print(f"Filtered polls: {polls}")
    else:
        polls = Question.objects.all()
        print(f"All polls (no tags): {polls}")
    polls_list = []

    for poll in polls:
        poll_dict = {
            "Question": poll.question_text,
            "QuestionID": poll.id,
            "Tags": [],
            "OptionVote": {},
        }
        for tag in poll.tags.all():
            poll_dict["Tags"].append(tag.tag_name)

        choices = Choice.objects.filter(question_id=poll.id)
        for choice in choices:
            poll_dict["OptionVote"][choice.choice_text] = choice.votes

        polls_list.append(poll_dict)

    return JsonResponse({"msg": "Fetched filtered polls successfully", "data": polls_list, "success": True})

@csrf_exempt
def increment_poll_vote(request, question_id):
    if request.method == 'PUT':
        try: 
            data = json.loads(request.body)
            increment_option = data.get('incrementOption')

            if not increment_option:
                return JsonResponse({"msg": "No option provided.", "success": False}, status=400)

            question = get_object_or_404(Question, id=question_id)
            choice = get_object_or_404(Choice, question=question, choice_text=increment_option)

            choice.votes = F('votes') + 1
            choice.save()
            choice.refresh_from_db()

            return JsonResponse({"msg": "Vote incremented successfully.", "success": True})
        
        except json.JSONDecodeError:
            return JsonResponse({"msg": "Invalid JSON.", "success": False}, status=400)
        except Question.DoesNotExist:
            return JsonResponse({"msg": "Question not found.", "success": False}, status=404)
        except Choice.DoesNotExist:
            return JsonResponse({"msg": "Choice not found.", "success": False}, status=404)
        except Exception as e:
            return JsonResponse({'msg': f"An error has occurred: {str(e)}", "success": False}, status=500)
    else:
        return JsonResponse({"msg": "Invalid request method.", "success": False}, status=405)

def get_poll_detail(request, question_id):
    try:
        question = get_object_or_404(Question, id=question_id)
        poll_dict = {
            "Question": question.question_text,
            "QuestionID": question.id,
            "Tags": [],
            "OptionVote": {},
        }
        for tag in question.tags.all():
            poll_dict["Tags"].append(tag.tag_name)

        choices = Choice.objects.filter(question_id=question.id)
        for choice in choices:
            poll_dict["OptionVote"][choice.choice_text] = choice.votes

        return JsonResponse({"msg": "Fetched polls successfully", "data": poll_dict, "success": True})
    
    except Exception as e:
        return JsonResponse({'msg': f"An error has occurred: {str(e)}", "success": False}, status=500)

def get_tags(request):
    try:
        tags = Tags.objects.values_list('tag_name', flat=True).distinct()
        return JsonResponse({"msg": "Fetched tags successfully", "data": list(tags), "success": True})
    except Exception as e:
        return JsonResponse({'msg': f"An error has occurred: {str(e)}", "success": False}, status=500)

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
