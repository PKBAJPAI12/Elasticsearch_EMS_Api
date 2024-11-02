from django.shortcuts import render

# Create your views here.
# employees/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .es_connection import es
from datetime import datetime
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
def patch_employee(request, employee_id):
    if request.method == 'PATCH':
        try:
            # Parse the request body
            data = json.loads(request.body)

            if not employee_id:
                return JsonResponse({"error": "Employee ID is required"}, status=400)

            # Check if the employee exists
            employee_exists = es.exists(index="employee_db", id=employee_id)

            if not employee_exists:
                return JsonResponse({"error": "Employee not found"}, status=404)

            # Prepare the updated data dynamically
            updated_fields = {}
            if "designation" in data:
                updated_fields["Designation"] = data.get("designation")
            if "salary" in data:
                updated_fields["Salary"] = data.get("salary")
            if "first_name" in data:
                updated_fields["FirstName"] = data.get("first_name")
            if "last_name" in data:
                updated_fields["LastName"] = data.get("last_name")
            if "date_of_joining" in data:
                updated_fields["DateOfJoining"] = data.get("date_of_joining")
            if "address" in data:
                updated_fields["Address"] = data.get("address")
            if "gender" in data:
                updated_fields["Gender"] = data.get("gender")
            if "age" in data:
                updated_fields["Age"] = data.get("age")
            if "marital_status" in data:
                updated_fields["MaritalStatus"] = data.get("marital_status")
            if "interests" in data:
                updated_fields["Interests"] = data.get("interests")

            # Only include fields that are passed in the request
            if updated_fields:
                update_body = {
                    "doc": updated_fields
                }
                print("update_body", update_body)
            else:
                return JsonResponse({"error": "No fields to update"}, status=400)

            # Update the employee record in Elasticsearch
            response = es.update(index="employee_db", id=employee_id, body=update_body)
            print("response", response)

            updated_doc = es.get(index="employee_db", id=employee_id)

            return JsonResponse({
                "message": "Employee updated successfully",
                "data": updated_doc["_source"]
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method. Use PATCH."}, status=405)

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

def filter_by_date_of_joining(request):
    if request.method == 'GET':
        
        page = request.GET.get('page', 1) 
        per_page = request.GET.get('per_page', 100) 
        start = (int(page) - 1) * int(per_page)
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)

        
        if not start_date or not end_date:
            return JsonResponse({"error": "Both start_date and end_date parameters are required"}, status=400)

        try:

            start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d')

            body = {
                "from": start,
                "size": per_page,
                "query": {
                    "range": {
                        "DateOfJoining": {
                            "gte": start_date,
                            "lte": end_date
                        }
                    }
                },
                "sort": [
                    {
                        "DateOfJoining": {
                            "order": "asc"
                        }
                    }
                ]
            }

            
            response = es.search(index="employee_db", body=body)

          
            employees = [hit["_source"] for hit in response['hits']['hits']]

            
            if not employees:
                return JsonResponse({"message": "No employees found within the specified date range"}, status=404)

            
            return JsonResponse({
               "data": employees,
               "total": response['hits']['total']['value'],
               "page": page,
               "per_page": per_page
            }, status=200)

        except ValueError:
            return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD for start_date and end_date."}, status=400)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Invalid request method. Use GET."}, status=405)
    
def get_aggregations(request):
    
    query = {
        "size": 0,
        "aggs": {
            "Designation": {
                "terms": {
                    "field": "Designation.keyword",
                    "size": 25
                }
            },
            "Gender": {
                "terms": {
                    "field": "Gender.keyword",
                    "size": 25
                }
            },
            "MaritalStatus": {
                "terms": {
                    "field": "MaritalStatus.keyword",
                    "size": 25
                }
            }
        }
    }
    print("q", query)

    response = es.search(index='employee_db', body=query)

    aggregations = response.get('aggregations', {})
    print("des",aggregations["Designation"]["buckets"])


    return JsonResponse({
               "Designations": aggregations["Designation"]["buckets"],
               "Genders": aggregations["Gender"]["buckets"],
               "MaritalStatus": aggregations["MaritalStatus"]["buckets"],
            }, status=200)