import logging
import json

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render

from editor.models import EditorBackup

# @login_required(login_url='/contas/login')
# def editor_user(request):
#     """
#     Serve editor user id
#     """
#     print("in editor_user, username =", request.user.username)
    
#     # Serve the username
#     return JsonResponse({"username": request.user.username})

logger = logging.getLogger(__name__)

def retrieve_backups(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=501)
    try:
        logger.info(request.body.decode("utf-8"))
        data = json.loads(request.body.decode("utf-8"))
        logger.info("data",data)
        backups = EditorBackup.objects.filter(user=request.user,the_type=data['the_type']).order_by("timestamp").values()
        data = list(backups)
        logger.info("data",data)
        return JsonResponse(data, safe=False) 
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError:
        return JsonResponse({'error': 'Missing the_type'}, status=400)

def retrieve_a_backup(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=501)
    try:
        data = json.loads(request.body.decode("utf-8"))
        backup = EditorBackup.objects.filter(user=request.user,the_type=data['the_type'], id=data['id']).only('data').values()
        if not backup:
            return JsonResponse({'error': 'Backup not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError:
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    return JsonResponse(backup[0]['data'], safe=False)


def delete_a_backup(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=501)
    data = json.loads(request.body.decode("utf-8"))
    try:
        EditorBackup.objects.get(user=request.user,the_type=data['the_type'], id=data['id']).delete()
        
    except EditorBackup.DoesNotExist:
        return JsonResponse({'error': 'Backup not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError:
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    except:
        return HttpResponse(status=501)

    return HttpResponse(status=204)
    

def add_a_backup(request):
    print("add_a_backup")
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if not request.user.is_authenticated:
        return HttpResponse(status=501)
    try:
        user_id = request.user.pk
        body_str = request.body.decode("utf-8")
        logger.info(f"body_str is: {body_str}")
        data = json.loads(body_str)
        logger.info(f"data is: {data}")
        logger.info("data", data['the_type'])
        b = EditorBackup()
        b.task_name = data['task_name']
        b.competition_name = data['competition_name']
        b.comment = data['comment']
        b.data = data['data']
        b.user_id = request.user.pk
        b.the_type = data['the_type']
        logger.info("will save")
        b.save()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    return HttpResponse(status=204)

