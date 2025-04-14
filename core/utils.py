import torch
import torchvision.models as models
import torchvision.transforms as transforms
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import json
import os

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def load_model(model_path, num_classes):
    model = models.resnet18(pretrained=False)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model


import requests


def predict_image(image_url, model, idx_to_class):
    # Download image from the internet
    response = requests.get(image_url)
    response.raise_for_status()  # Ensure the request was successful

    from io import BytesIO
    
    image = Image.open(BytesIO(response.content)).convert("RGB")
    image_tensor = transform(image).unsqueeze(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    image_tensor = image_tensor.to(device)

    with torch.no_grad():
        # Get the raw model outputs
        outputs = model(image_tensor)
        
        # Apply softmax to get probabilities
        probabilities = nn.functional.softmax(outputs, dim=1)
        
        # Get the highest probability and its index
        confidence, prediction = torch.max(probabilities, dim=1)
        
        # Convert to Python values
        confidence_value = confidence.item()
        class_idx = prediction.item()
        
        # Get all probabilities as numpy array (optional)
        all_probabilities = probabilities.cpu().numpy()[0]

    class_name = idx_to_class[class_idx]

    return class_name, confidence_value




def load_disease_detection_model(model_path='models/plant_disease_model.pth'):
    model = models.resnet18(pretrained=False)
    model.fc = torch.nn.Linear(model.fc.in_features, 19)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model


def preprocess_image(image):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])
    return transform(image).unsqueeze(0)