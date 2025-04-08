import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from ultralyticsplus import YOLO, render_result

def load_model(model_path='./core/AImodels/sat_imaging/Res_18.pth'):
    model = models.resnet18(pretrained=False)
    model.fc = torch.nn.Linear(model.fc.in_features, 8)
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

# load model
plant_detection_model = YOLO('foduucom/plant-leaf-detection-and-classification')

# set model parameters
plant_detection_model.overrides['conf'] = 0.25  # NMS confidence threshold
plant_detection_model.overrides['iou'] = 0.45  # NMS IoU threshold
plant_detection_model.overrides['agnostic_nms'] = False  # NMS class-agnostic
plant_detection_model.overrides['max_det'] = 1000  # maximum number of detections per image



