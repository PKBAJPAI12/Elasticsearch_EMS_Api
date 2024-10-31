from django.shortcuts import render

# Create your views here.
# employees/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .es_connection import es
import json

def get_employees(request):
    query_value = request.GET.get('query', '')
    page = request.GET.get('page', 1)  # Default page is 1
    per_page = request.GET.get('per_page', 10)  # Default 10 employees per page
    start = (int(page) - 1) * int(per_page)

    if query_value:
        response = es.search(index="employee_db", body={
            "from": start,
            "size": per_page,
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
            "from": start,
            "size": per_page,
            "query": {
                "match_all": {}
            }
        })
    
    employees = [hit['_source'] for hit in response['hits']['hits']]
    
    return JsonResponse({
        "data": employees,
        "total": response['hits']['total']['value'],
        "page": page,
        "per_page": per_page
    })

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

@csrf_exempt
def filter_by_designations(request):
    if request.method == 'POST':
        try:
            # Get the designations from the query parameters
            page = request.GET.get('page', 1)  # Default page is 1
            per_page = request.GET.get('per_page', 100)  # Default 10 employees per page
            start = (int(page) - 1) * int(per_page)
            data = json.loads(request.body)
            designations = data.get('designations', [])
            print("desg", designations)
            # Validate that the designations list is provided and not empty
            if not designations:
                return JsonResponse({"error": "No designations provided"}, status=400)

            # Create a 'terms' query to match any of the provided designations
            body = {
                "from": start,
                "size": per_page,
                "query": {
                    "terms": {
                        "Designation.keyword": designations  # Filter by array of designations
                    }
                }
            }
            print("body", body)
            # Execute the search query on Elasticsearch
            response = es.search(index="employee_db", body=body)
            print("response", response)
            # Extract the employee data from the response
            employees = [hit["_source"] for hit in response['hits']['hits']]

            # Check if no employees are found
            if not employees:
                return JsonResponse({"message": "No employees found with the provided designations"}, status=404)


            # Return the filtered employee data in the response
            return JsonResponse({
               "data": employees,
               "total": response['hits']['total']['value'],
               "page": page,
               "per_page": per_page
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method. Use GET."}, status=405)

def filter_by_gender(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)  # Default page is 1
        per_page = request.GET.get('per_page', 100)  # Default 10 employees per page
        start = (int(page) - 1) * int(per_page)
        gender = request.GET.get('gender', None)

        if gender is None:
            return JsonResponse({"error": "Gender parameter is required"}, status=400)

        try:
            # Elasticsearch query to filter employees by gender
            body = {
                "from": start,
                "size": per_page,
                "query": {
                    "match": {
                        "Gender": gender
                    }
                }
            }

            # Search for employees by gender
            response = es.search(index="employee_db", body=body)

            # Prepare the result list
            employees = [hit["_source"] for hit in response['hits']['hits']]

            if not employees:
                return JsonResponse({"message": "No employees found for the selected gender"}, status=404)

            return JsonResponse({
               "data": employees,
               "total": response['hits']['total']['value'],
               "page": page,
               "per_page": per_page
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Invalid request method. Use GET."}, status=405)
        
def filter_by_age(request):
    if request.method == 'GET':
        # Get min_age and max_age from request parameters
        page = request.GET.get('page', 1)  # Default page is 1
        per_page = request.GET.get('per_page', 100)  # Default 10 employees per page
        start = (int(page) - 1) * int(per_page)
        min_age = request.GET.get('min_age', None)
        max_age = request.GET.get('max_age', None)

        # Validate that both min_age and max_age are provided
        if min_age is None or max_age is None:
            return JsonResponse({"error": "Both min_age and max_age parameters are required"}, status=400)

        try:
            # Create a range query to filter employees between min_age and max_age
            body = {
                "from": start,
                "size": per_page,
                "query": {
                    "range": {
                        "Age": {
                            "gte": min_age,
                            "lte": max_age
                        }
                    }
                }
            }
            
            # Execute the search query on Elasticsearch
            response = es.search(index="employee_db", body=body)
            # Extract the employee data from the response
            employees = [hit["_source"] for hit in response['hits']['hits']]
            print("employees",employees)
            # Check if no employees are found
            if not employees:
                return JsonResponse({"message": "No employees found in the specified age range"}, status=404)

            # Return the filtered employee data in the response
            return JsonResponse({
               "data": employees,
               "total": response['hits']['total']['value'],
               "page": page,
               "per_page": per_page
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method. Use GET."}, status=405)
