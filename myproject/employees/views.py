from django.shortcuts import render

# Create your views here.
# employees/views.py
from django.http import JsonResponse
from .es_connection import es

def get_employees(request):
    query_value = request.GET.get('query', '')
    
    resp = es.search(index="employee_db", body={
        "size": 1000,
        "query": {
            "match": {
                "FirstName": {
                    "query": query_value,
                    "fuzziness": "AUTO"
                }
            }
        }
    })
    
    resp_body = resp.body if hasattr(resp, 'body') else resp

    # Return the response body as a JSON response
    return JsonResponse(resp_body, safe=False)

