from ultralytics import YOLO
from core.models import DiseaseType, PlantType, PestType
import requests
from io import BytesIO
from PIL import Image
import torch
from torch.serialization import add_safe_globals
from torch.nn import Sequential
import tensorflow as tf
import numpy as np

from core.utils import load_disease_detection_model, preprocess_image

add_safe_globals([Sequential])

# Load models
plant_detection_model = YOLO('models/best.pt')
# drought_detection_model = YOLO('models/full_model.pt')
pest_detection_model = tf.keras.models.load_model('models/mobilenetv2_pest_detector.h5')

# Set model parameters
plant_detection_model.overrides['conf'] = 0.25  # NMS confidence threshold
plant_detection_model.overrides['iou'] = 0.45  # NMS IoU threshold
plant_detection_model.overrides['agnostic_nms'] = False  # NMS class-agnostic
plant_detection_model.overrides['max_det'] = 1000  # maximum number of detections per image

# Set drought model parameters
# drought_detection_model.overrides['conf'] = 0.25
# drought_detection_model.overrides['iou'] = 0.45
# drought_detection_model.overrides['agnostic_nms'] = False
# drought_detection_model.overrides['max_det'] = 1000

# Drought level descriptions in Arabic
DROUGHT_DESCRIPTIONS = {
    0: "لا يوجد جفاف - رطوبة التربة مثالية",
    1: "جفاف خفيف - ظروف جافة قليلاً",
    2: "جفاف معتدل - التربة جافة، قد تظهر النباتات علامات الإجهاد",
    3: "جفاف شديد - إجهاد مائي كبير",
    4: "جفاف متطرف - نقص حاد في المياه",
    5: "جفاف استثنائي - ندرة المياه منتشرة"
}

def preprocess_pest_image(image):
    """
    Preprocess image for pest detection model
    
    Args:
        image (PIL.Image): Input image
        
    Returns:
        numpy.ndarray: Preprocessed image
    """
    # Resize image to model's expected size (224x224 for MobileNetV2)
    image = image.resize((224, 224))
    
    # Convert to numpy array and normalize
    img_array = np.array(image)
    img_array = img_array.astype('float32') / 255.0
    
    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array

def detect_plant(image_url):
    """
    Detect plant from image URL using YOLO model
    
    Args:
        image_url (str): URL of the image to analyze
        
    Returns:
        dict: Detection results including plant info and confidence
    """
    try:
        # Download image from URL
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        
        # Run detection
        results = plant_detection_model(image)
        
        # Get the first detection (highest confidence)
        if len(results[0].boxes) > 0:
            # Get class name and confidence
            class_id = int(results[0].boxes.cls[0])
            class_name = results[0].names[class_id]
            confidence = float(results[0].boxes.conf[0])
            
            # Try to find plant in database
            try:
                plant = PlantType.objects.get(name__iexact=class_name)
                return {
                    'success': True,
                    'plantId': plant.id,
                    'name': plant.name,
                    'scientificName': plant.scientific_name,
                    'commonDiseases': plant.common_diseases,
                    'confidence': confidence,
                    'imageUrl': image_url
                }
            except PlantType.DoesNotExist:
                # Plant not found in database
                return {
                    'success': True,
                    'plantId': None,
                    'name': class_name,
                    'scientificName': None,
                    'commonDiseases': [],
                    'confidence': confidence,
                    'imageUrl': image_url
                }
        else:
            # No plant detected
            return {
                'success': False,
                'message': 'No plant detected in the image',
                'imageUrl': image_url
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing image: {str(e)}',
            'imageUrl': image_url
        }

def detect_disease(image_url):
    """
    Detect plant disease from image URL using ResNet model
    
    Args:
        image_url (str): URL of the image to analyze
        plant_id (int, optional): ID of the plant type to narrow down disease detection
        
    Returns:
        dict: Detection results including disease info and confidence
    """
    try:
        # Download image from URL
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        
        # Load and preprocess image
        model = load_disease_detection_model()
        processed_image = preprocess_image(image)
        
        # Run detection
        with torch.no_grad():
            outputs = model(processed_image)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            confidence = float(confidence[0])
            predicted_class = int(predicted[0])
        
        # Get disease information from database
        try:
            disease = DiseaseType.objects.get(name__iexact=predicted_class)
            
            return {
                'success': True,
                'diseaseId': disease.id,
                'name': disease.name,
                'description': disease.description,
                'treatment': disease.treatment,
                'confidence': confidence,
                'imageUrl': image_url
            }
            
        except DiseaseType.DoesNotExist:
            return {
                'success': False,
                'message': 'Disease not found in database',
                'imageUrl': image_url
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing image: {str(e)}',
            'imageUrl': image_url
        }

def detect_pest(image_url):
    """
    Detect plant pests from image URL using MobileNetV2 model
    
    Args:
        image_url (str): URL of the image to analyze
        
    Returns:
        dict: Detection results including pest info and confidence
    """
    try:
        # Download image from URL
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
        
        # Preprocess image
        processed_image = preprocess_pest_image(image)
        
        # Run detection
        predictions = pest_detection_model.predict(processed_image)
        
        # Get the highest confidence prediction
        confidence = float(np.max(predictions[0]))
        predicted_class = int(np.argmax(predictions[0]))
        
        # Get pest information from database
        try:
            pest = PestType.objects.get(id=predicted_class)
            
            return {
                'success': True,
                'pestId': str(pest.id),
                'name': pest.name,
                'description': pest.description,
                'treatment': pest.treatment,
                'severity': pest.severity,
                'confidence': confidence,
                'imageUrl': image_url
            }
            
        except PestType.DoesNotExist:
            return {
                'success': False,
                'message': 'Pest not found in database',
                'imageUrl': image_url
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing image: {str(e)}',
            'imageUrl': image_url
        }

def drought_forecast(climate_data):
    """
    Forecast drought conditions using LSTM model with climate data
    
    Args:
        climate_data (dict): Dictionary containing climate parameters:
            - temperature: List of temperature values over time
            - humidity: List of humidity values over time
            - rainfall: List of rainfall values over time
            - wind_speed: List of wind speed values over time
            - soil_moisture: List of soil moisture values over time
            - evapotranspiration: List of evapotranspiration values over time
            
    Returns:
        dict: Forecast results including drought level and description
    """
    try:
        # Load the LSTM model
        drought_model = tf.keras.models.load_model('models/drought_lstm_model.h5')
        
        # Prepare input data
        # Assuming the model expects a specific sequence length (e.g., 30 days)
        sequence_length = 30
        
        # Create a feature matrix from the climate data
        features = []
        for i in range(min(len(climate_data['temperature']), sequence_length)):
            day_features = [
                climate_data['temperature'][i],
                climate_data['humidity'][i],
                climate_data['rainfall'][i],
                climate_data['wind_speed'][i],
                climate_data['soil_moisture'][i],
                climate_data['evapotranspiration'][i]
            ]
            features.append(day_features)
        
        # Pad or truncate to match sequence length
        if len(features) < sequence_length:
            # Pad with zeros if we have fewer days
            padding = [[0] * 6] * (sequence_length - len(features))
            features = padding + features
        elif len(features) > sequence_length:
            # Take the most recent days
            features = features[-sequence_length:]
        
        # Convert to numpy array and reshape for LSTM input
        features = np.array(features)
        features = np.expand_dims(features, axis=0)  # Add batch dimension
        
        # Run prediction
        prediction = drought_model.predict(features)
        
        # Get drought level (assuming model outputs class probabilities)
        drought_level = int(np.argmax(prediction[0]))
        confidence = float(np.max(prediction[0]))
        
        # Ensure drought level is within valid range
        if drought_level not in DROUGHT_DESCRIPTIONS:
            drought_level = 0  # Default to no drought if level is invalid
        
        return {
            'success': True,
            'droughtLevel': drought_level,
            'description': DROUGHT_DESCRIPTIONS[drought_level],
            'confidence': confidence,
            'forecast': {
                'next_7_days': prediction[0].tolist(),  # Probabilities for each drought level
                'current_level': drought_level,
                'trend': 'increasing' if drought_level > 2 else 'decreasing' if drought_level < 2 else 'stable'
            }
        }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing climate data: {str(e)}'
        }


        
