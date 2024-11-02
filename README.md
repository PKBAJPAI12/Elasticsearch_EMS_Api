Certainly! Here’s how you can integrate the new functions into your existing README file, including sections for "Filter by Date of Joining" and "Patch Employee":

```markdown
# Employee Management API

This Django application provides a RESTful API for managing employee data using Elasticsearch as the backend database. The API allows for searching, creating, and filtering employees based on various fields such as name, designation, gender, and age.

## Features
- **Search Employees**: Retrieve a paginated list of employees with optional query-based filtering.
- **Create Employee**: Add new employee records with details such as first name, last name, designation, salary, date of joining, address, gender, age, marital status, and interests.
- **Filter by Designations**: Filter employees based on specific designations.
- **Filter by Gender**: Filter employees based on gender.
- **Filter by Age**: Filter employees based on a specified age range.
- **Filter by Date of Joining**: Retrieve employees who joined within a specified date range.
- **Patch Employee**: Update existing employee records with new data for various fields.

## Installation
### Clone the Repository
```bash
git clone https://github.com/PKBAJPAI12/Elasticsearch_EMS_Api
cd project
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Setup Elasticsearch
Ensure you have an Elasticsearch instance running, and update the connection details in `es_connection.py`.

### Run the Application
```bash
python manage.py runserver
```

## API Endpoints
1. **Get Employees**
   - **Endpoint**: `/employees/`
   - **Method**: `GET`
   - **Query Parameters**:
     - `query`: (optional) Search keyword for the first name.
     - `page`: (optional) Page number, default is 1.
     - `per_page`: (optional) Number of records per page, default is 10.
   - **Response**: JSON with employee data, total count, page, and per-page values.

2. **Create Employee**
   - **Endpoint**: `/employees/create/`
   - **Method**: `POST`
   - **Request Body**:
     - `first_name`: Employee's first name (required).
     - `last_name`: Employee's last name (required).
     - `designation`: Employee's designation.
     - `salary`: Employee's salary.
     - `date_of_joining`: Date when the employee joined.
     - `address`: Employee's address.
     - `gender`: Employee's gender.
     - `age`: Employee's age.
     - `marital_status`: Employee's marital status.
     - `interests`: Employee's interests.
   - **Response**: JSON message indicating success or failure.

3. **Filter by Designations**
   - **Endpoint**: `/employees/filter_by_designations/`
   - **Method**: `POST`
   - **Query Parameters**:
     - `page`: (optional) Page number, default is 1.
     - `per_page`: (optional) Number of records per page, default is 10.
   - **Request Body**:
     - `designations`: List of designations to filter by.
   - **Response**: JSON with filtered employee data.

4. **Filter by Gender**
   - **Endpoint**: `/employees/filter_by_gender/`
   - **Method**: `GET`
   - **Query Parameters**:
     - `page`: (optional) Page number, default is 1.
     - `per_page`: (optional) Number of records per page, default is 10.
     - `gender`: Gender to filter by.
   - **Response**: JSON with filtered employee data or error if no gender is provided.

5. **Filter by Age**
   - **Endpoint**: `/employees/filter_by_age/`
   - **Method**: `GET`
   - **Query Parameters**:
     - `page`: (optional) Page number, default is 1.
     - `per_page`: (optional) Number of records per page, default is 10.
     - `min_age`: Minimum age for the filter.
     - `max_age`: Maximum age for the filter.
   - **Response**: JSON with employees within the specified age range or error if age parameters are missing.

6. **Filter by Date of Joining**
   - **Endpoint**: `/employees/filter_by_date_of_joining/`
   - **Method**: `GET`
   - **Query Parameters**:
     - `page`: (optional) Page number, default is 1.
     - `per_page`: (optional) Number of records per page, default is 100.
     - `start_date`: (required) Start date for the filter (YYYY-MM-DD).
     - `end_date`: (required) End date for the filter (YYYY-MM-DD).
   - **Response**: JSON with employees who joined within the specified date range or error if date parameters are missing.

7. **Patch Employee**
   - **Endpoint**: `/employees/patch/{employee_id}/`
   - **Method**: `PATCH`
   - **Request Body**:
     - JSON object containing fields to update (e.g., designation, salary, first name, last name, date of joining, address, gender, age, marital status, interests).
   - **Response**: JSON message indicating success or failure along with the updated employee data.

## Error Handling
The API includes error responses with appropriate HTTP status codes for invalid requests, missing parameters, and other issues.

## Notes
- **Elasticsearch Configuration**: Ensure that the Elasticsearch server is properly configured and running.
- **Data Validations**: Employee creation validates first and last names; other validations may be added as required.
```

Feel free to adjust any specific wording or formatting to fit your project's style!
