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
- `POST /auth/register/`: Register a new user
- `POST /auth/login/`: Authenticate and get JWT tokens
- `POST /auth/token/refresh/`: Refresh access token
- `GET /auth/profile/`: Get current user profile

### Detection Services
- `POST /detect/plant/`: Detect plant type from image
- `POST /detect/disease/`: Detect plant diseases from image
- `POST /detect/pest/`: Detect plant pests from image
- `POST /detect/drought/`: Detect drought conditions from image

### Data Management
- `/users/`: User CRUD operations
- `/plant-types/`: Plant type catalog
- `/disease-types/`: Disease type catalog
- `/pest-types/`: Pest type catalog
- `/reports/`: Report submission and management
- `/alerts/`: Agricultural alert system

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
