import torch
from PIL import Image
from io import BytesIO
import json
import os
import timm
from torchvision import transforms as T
import numpy as np
import torch.nn.functional as F
import time
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "best_model.pt")
DEFAULT_METADATA_PATH = os.path.join(os.path.dirname(__file__), "..", "meta_data.json")

MODEL_PATH = os.environ.get("PLUMVISION_MODEL_PATH", DEFAULT_MODEL_PATH)
METADATA_PATH = os.environ.get("PLUMVISION_METADATA_PATH", DEFAULT_METADATA_PATH)

superclass_mapping_json = os.environ.get("SUPERCLASS_MAPPING_JSON")
SUPERCLASS_MAPPING = {}

if superclass_mapping_json:
    try:
        SUPERCLASS_MAPPING = json.loads(superclass_mapping_json)
    except json.JSONDecodeError:
        print("Warning: Could not decode SUPERCLASS_MAPPING_JSON environment variable. Using default superclass mapping.")
        SUPERCLASS_MAPPING = {
            "unaffected": "Good",
            "unripe": "Unripe",
            "spotted": "Defective",
            "rotten": "Defective",
            "bruised": "Defective",
            "cracked": "Defective",
        }
else:
    SUPERCLASS_MAPPING = {
        "unaffected": "Good",
        "unripe": "Unripe",
        "spotted": "Defective",
        "rotten": "Defective",
        "bruised": "Defective",
        "cracked": "Defective",
    }

IMAGE_SIZE = int(os.environ.get("IMAGE_SIZE", 224))
NORM_MEAN_STR = os.environ.get("NORM_MEAN", "0.485,0.456,0.406")
NORM_STD_STR = os.environ.get("NORM_STD", "0.229,0.224,0.225")

NORM_MEAN = [float(x) for x in NORM_MEAN_STR.split(',')]
NORM_STD = [float(x) for x in NORM_STD_STR.split(',')]

class PlumPredictor:
    def __init__(self):
        #print(f"Using model path: {MODEL_PATH}")
        #print(f"Using metadata path: {METADATA_PATH}")
        if superclass_mapping_json:
            print("Superclass mapping loaded from environment variable.")
        else:
            print("Superclass mapping loaded from default.")
        #print(f"Using image size: {IMAGE_SIZE}")
        #print(f"Using normalization mean: {NORM_MEAN}")
        #print(f"Using normalization std: {NORM_STD}")

        self.metadata = self._load_metadata()  
        self.model = self._load_model()
        self.class_names = self._get_class_names()
        self.transform = self._get_transforms()

        if self.model is not None and self.metadata is not None:
            print("Predictor ready")
        else:
            if self.model is None:
                print(f"Error: Model not loaded from {MODEL_PATH}")
            if self.metadata is None:
                print(f"Error: Metadata not loaded from {METADATA_PATH}")

    def _load_model(self):
        try:
            if self.metadata and 'model' in self.metadata and 'classes' in self.metadata:
                model_name = self.metadata['model']
                num_classes = len(self.metadata['classes'])
                model = timm.create_model(model_name, pretrained=False, num_classes=num_classes)
                model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
                model.eval()
                return model
            else:
                print("Error: Model information or classes not found in metadata.")
                return None
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def _load_metadata(self):
        try:
            with open(METADATA_PATH, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error loading metadata: {e}")
            return None

    def _get_class_names(self):
        if self.metadata and 'classes' in self.metadata:
            classes_dict = self.metadata['classes']
            num_classes = len(classes_dict)
            class_names_list = [None] * num_classes
            for name, index in classes_dict.items():
                if 0 <= index < num_classes:
                    class_names_list[index] = name
                else:
                    print(f"Warning: Invalid class index {index} for class '{name}'.")
            return [name for name in class_names_list if name is not None]
        else:
            return [f'class_{i}' for i in range(6)]

    def _get_transforms(self):
        mean, std, size = NORM_MEAN, NORM_STD, IMAGE_SIZE
        return T.Compose([
            T.Resize(size=(size, size), antialias=True),
            T.ToTensor(),
            T.Normalize(mean=mean, std=std)
        ])

    def predict_image(self, image_content: bytes, image_name: str):
        if self.model is None:
            return {"error": "Model not loaded"}

        try:
            start_time = time.time()
            img = Image.open(BytesIO(image_content)).convert('RGB')
            img_transformed = self.transform(img).unsqueeze(0)
            img_transformed = img_transformed.to(next(self.model.parameters()).device)

            with torch.no_grad():
                output = self.model(img_transformed)
                probabilities = F.softmax(output, dim=1).cpu().numpy()[0]
                top_indices = np.argsort(probabilities)[::-1][:3]
                top_probabilities = probabilities[top_indices].tolist()
                top_classes = [self.class_names[i] for i in top_indices]

            end_time = time.time()
            inference_time = end_time - start_time

            top_predictions = []
            for i in range(len(top_classes)):
                top_predictions.append({
                    "class": top_classes[i],
                    "probability": f"{top_probabilities[i]:.4f}"
                })

            superclass_mapping_result = {}
            for prediction in top_predictions:
                class_name = prediction['class']
                superclass_mapping_result[class_name] = SUPERCLASS_MAPPING.get(class_name, "Unknown")

            return {
                "image_name": image_name,
                "prediction": top_predictions,
                "superclass_mapping": superclass_mapping_result,
                "inference_time": f"{inference_time:.4f}"
            }

        except Exception as e:
            return {"error": f"Error during prediction: {e}"}

predictor = PlumPredictor()