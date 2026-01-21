from django.contrib.auth.decorators import login_required
from django.views.static import serve
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.models import User

import os

# Create your views here.

@login_required(login_url='/contas/login')
def serve_editor(request, path='index.html'):
    """
    Serve editor static files only to authenticated users
    """
    document_root = os.path.join(settings.STATIC_ROOT, 'editor')
    
    # Security: prevent directory traversal attacks
    if '..' in path or path.startswith('/'):
        raise Http404("Invalid path")
    
    # Serve the file
    return serve(request, path, document_root=document_root)

