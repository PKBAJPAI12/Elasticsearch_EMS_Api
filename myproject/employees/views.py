from django.shortcuts import render

# Create your views here.
# employees/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .es_connection import es
import json

def get_employees(request):
    query_value = request.GET.get('query', '')

    if query_value:
        response = es.search(index="employee_db", body={
            "query": {
                "match": {
                    "FirstName": {
                        "query": query_value,
                        "fuzziness": "AUTO"
                    }
                }
            }
        })
    else:
        # If no query is provided, return all employees
        response = es.search(index="employee_db", body={
            "size": 10000,
            "query": {
                "match_all": {}
            }
        })
    
    return JsonResponse(response['hits']['hits'], safe=False)

@csrf_exempt
def create_employee(request):
    try:
        if request.method != 'POST':
            return JsonResponse({"error": "POST request required."}, status=405)

        data = json.loads(request.body)

        if not data.get("first_name") or not data.get("last_name"):
            return JsonResponse({"error": "First Name and Last Name are required."}, status=400)
        
        existing_employee_query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"FirstName": data.get("first_name")}},
                        {"match": {"LastName": data.get("last_name")}},
                        {"match": {"Designation": data.get("designation")}},
                        {"match": {"Salary": data.get("salary")}},
                        {"match": {"DateOfJoining": data.get("date_of_joining")}},
                        {"match": {"Address": data.get("address")}},
                        {"match": {"Gender": data.get("gender")}},
                        {"match": {"Age": data.get("age")}},
                        {"match": {"MaritalStatus": data.get("marital_status")}},
                        {"match": {"Interests": data.get("interests")}}
                    ]
                }
            }
        }
        existresponse = es.search(index="employee_db", body=existing_employee_query)
        print(existresponse['hits']['total']['value'])
        if existresponse['hits']['total']['value'] > 0:
            print(existresponse['hits']['total']['value'])
            existing_employee = existresponse['hits']['hits'][0]['_source']
            print(existing_employee)
            
            return JsonResponse({"message": "Employee already exists with the same details."}, status=400)

        
        employee_data = {
            "FirstName": data.get("first_name"),
            "LastName": data.get("last_name"),
            "Designation": data.get("designation"),
            "Salary": data.get("salary"),
            "DateOfJoining": data.get("date_of_joining"),
            "Address": data.get("address"),
            "Gender": data.get("gender"),
            "Age": data.get("age"),
            "MaritalStatus": data.get("marital_status"),
            "Interests": data.get("interests")
        }

        response = es.index(index="employee_db", body=employee_data)
        
        print(response)
        response_data = str(response)
        
        return JsonResponse({"message": "Employee Created successfully", "data": response_data}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)