from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Escola

@require_http_methods(["GET"])
def consulta(request, inep_code):
    """
    Returns school data as JSON for the given INEP code.
    
    Args:
        request: Django request object
        inep_code: School code (co_entidade)
    
    Returns:
        JsonResponse with school data or error message
    """
    try:
        escola = Escola.objects.get(co_entidade=inep_code)
        
        data = {
            'co_entidade': escola.co_entidade,
            'no_entidade': escola.no_entidade,
            'no_municipio': escola.no_municipio,
            'sg_uf': escola.sg_uf,
            'tp_dependencia': escola.tp_dependencia,
            'ds_endereco': escola.ds_endereco,
            'nu_endereco': escola.nu_endereco,
            'ds_complemento': escola.ds_complemento,
            'no_bairro': escola.no_bairro,
            'co_cep': escola.co_cep,
            'nu_ddd': escola.nu_ddd,
            'nu_telefone': escola.nu_telefone,
            # Include computed fields
            'telefone_completo': escola.get_telefone_completo(),
        }
        
        return JsonResponse(data)
        
    except Escola.DoesNotExist:
        return JsonResponse(
            {'erro': f'Escola com código {inep_code} não encontrada'}
        )
