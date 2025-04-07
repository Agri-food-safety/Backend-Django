# AgriScan Backend API

## Project Overview
AgriScan is a Django REST framework backend for a plant disease and pest detection system. It provides:
- User authentication and profile management
- Plant, disease, and pest type catalog
- Report submission and management
- Alert system for agricultural threats
- Image-based detection endpoints (plant, disease, pest, drought)

## API Documentation

### Authentication

#### Register User
- **Endpoint**: `POST /auth/register/`
- **Request**:
  ```json
  {
    "phone": "+1234567890",
    "password": "securepassword123",
    "fullName": "John Doe",
    "role": "farmer",
    "city": "Lagos",
    "state": "Lagos",
    "gpsLat": 6.5244,
    "gpsLng": 3.3792
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "User registered successfully",
    "data": {
      "userId": "550e8400-e29b-41d4-a716-446655440000",
      "fullName": "John Doe",
      "role": "farmer",
      "access_token": "eyJhbGciOi...",
      "refresh_token": "eyJhbGciOi..."
    }
  }
  ```

#### User Login
- **Endpoint**: `POST /auth/login/`
- **Request**:
  ```json
  {
    "phone": "+1234567890",
    "password": "securepassword123"
  }
  ```
- **Response**: Same as registration response

#### Refresh Token
- **Endpoint**: `POST /auth/token/refresh/`
- **Request**:
  ```json
  {
    "refresh": "eyJhbGciOi..."
  }
  ```
- **Response**:
  ```json
  {
    "access": "eyJhbGciOi..."
  }
  ```

#### User Profile
- **Endpoint**: `GET /auth/profile/`
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "userId": "550e8400-e29b-41d4-a716-446655440000",
      "phone": "+1234567890",
      "fullName": "John Doe",
      "role": "farmer",
      "city": "Lagos",
      "state": "Lagos",
      "gpsLat": 6.5244,
      "gpsLng": 3.3792,
      "createdAt": "2025-04-07T18:25:43Z",
      "lastActive": "2025-04-07T19:15:22Z"
    }
  }
  ```

### Detection Services

#### Plant Detection
- **Endpoint**: `POST /detect/plant/`
- **Request**:
  ```json
  {
    "imageUrl": "https://example.com/plant.jpg"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "plantId": "550e8400-e29b-41d4-a716-446655440000",
      "confidence": 0.95,
      "imageUrl": "https://example.com/plant.jpg"
    }
  }
  ```

#### Disease Detection
- **Endpoint**: `POST /detect/disease/`
- **Request**: Same as plant detection
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "diseaseId": "550e8400-e29b-41d4-a716-446655440010",
      "name": "Early Blight",
      "description": "A fungal disease...",
      "treatment": "Remove infected leaves...",
      "severity": "medium",
      "confidence": 0.92,
      "imageUrl": "https://example.com/plant.jpg"
    }
  }
  ```

#### Pest Detection
- **Endpoint**: `POST /detect/pest/`
- **Request**: Same as plant detection
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "pestId": "550e8400-e29b-41d4-a716-446655440020",
      "name": "Aphids",
      "description": "Small, soft-bodied insects...",
      "treatment": "Use insecticidal soap...",
      "severity": "medium",
      "confidence": 0.89,
      "imageUrl": "https://example.com/plant.jpg"
    }
  }
  ```

#### Drought Detection
- **Endpoint**: `POST /detect/drought/`
- **Request**: Same as plant detection
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "droughtLevel": 3,
      "description": "Severe drought - Significant water stress",
      "confidence": 0.91,
      "imageUrl": "https://example.com/plant.jpg"
    }
  }
  ```

### Data Management

#### Reports
- **Create Report**: `POST /reports/`
  - **Request**:
    ```json
    {
      "gpsLat": 6.5244,
      "gpsLng": 3.3792,
      "city": "Lagos",
      "state": "Lagos",
      "imageUrl": "https://example.com/report.jpg",
      "plantType": {"plantId": "550e8400-e29b-41d4-a716-446655440000"},
      "disease": {"diseaseId": "550e8400-e29b-41d4-a716-446655440010"},
      "pest": {"pestId": "550e8400-e29b-41d4-a716-446655440020"},
      "drought": {"droughtLevel": 3}
    }
    ```
  - **Response**:
    ```json
    {
      "success": true,
      "data": {
        "reportId": "550e8400-e29b-41d4-a716-446655440100",
        "status": "submitted",
        "gpsLat": 6.5244,
        "gpsLng": 3.3792,
        "city": "Lagos",
        "state": "Lagos",
        "imageUrl": "https://example.com/report.jpg",
        "plant_detection": {"plantId": "550e8400-e29b-41d4-a716-446655440000"},
        "disease_detection": {"diseaseId": "550e8400-e29b-41d4-a716-446655440010"},
        "pest_detection": {"pestId": "550e8400-e29b-41d4-a716-446655440020"},
        "drought_detection": {"droughtLevel": 3},
        "timestamp": "2025-04-07T19:20:15Z"
      }
    }
    ```

#### Alerts
- **Create Alert**: `POST /alerts/`
  - **Request**:
    ```json
    {
      "title": "Drought Warning",
      "description": "Severe drought expected in Lagos region",
      "severity": "danger",
      "target_state": "Lagos",
      "expires_at": "2025-04-14T00:00:00Z"
    }
    ```
  - **Response**:
    ```json
    {
      "success": true,
      "data": {
        "id": "550e8400-e29b-41d4-a716-446655440200",
        "title": "Drought Warning",
        "description": "Severe drought expected in Lagos region",
        "severity": "danger",
        "target_state": "Lagos",
        "created_at": "2025-04-07T19:25:00Z",
        "expires_at": "2025-04-14T00:00:00Z"
      }
    }
    ```

## Architecture Documentation

### Models
- **User**: Custom user model with phone-based authentication
- **PlantType**: Catalog of plant types with scientific names
- **DiseaseType**: Plant diseases with descriptions and treatments
- **PestType**: Plant pests with descriptions and treatments
- **Report**: User-submitted reports with detection results
- **Alert**: System-generated agricultural alerts

### Key Features
- JWT authentication
- Role-based access control (Farmers/Inspectors)
- GPS location tracking
- Image-based detection services
- Comprehensive reporting system

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis (optional for caching)

### Installation
1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your database credentials:
   ```
   DB_NAME=agriscan
   DB_USER=postgres
   DB_PASSWORD=yourpassword
   DB_HOST=localhost
   DB_PORT=5432
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## API Response Format
All API responses follow this structure:
```json
{
  "success": boolean,
  "message": "description",
  "data": {
    // endpoint-specific data
  }
}
```

## Testing
Run the test suite with:
```bash
python manage.py test
```

## Deployment
For production deployment:
1. Set `DEBUG=False` in settings.py
2. Configure proper ALLOWED_HOSTS
3. Set up a production database
4. Use a production WSGI server (Gunicorn + Nginx recommended)
