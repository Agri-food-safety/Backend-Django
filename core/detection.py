from ultralytics import YOLO
from core.models import DiseaseType, PlantType
import requests
from io import BytesIO
from PIL import Image
import torch
from torch.serialization import add_safe_globals
from torch.nn import Sequential

from core.utils import load_disease_detection_model, preprocess_image

add_safe_globals([Sequential])

# Load model
plant_detection_model = YOLO('models/best.pt')

# Set model parameters
plant_detection_model.overrides['conf'] = 0.25  # NMS confidence threshold
plant_detection_model.overrides['iou'] = 0.45  # NMS IoU threshold
plant_detection_model.overrides['agnostic_nms'] = False  # NMS class-agnostic
plant_detection_model.overrides['max_det'] = 1000  # maximum number of detections per image

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
    


        
