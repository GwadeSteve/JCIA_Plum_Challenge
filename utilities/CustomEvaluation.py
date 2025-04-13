import os
import torch
import random
import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from torchvision import transforms
from torch.utils.data import DataLoader
from pathlib import Path
from PIL import Image
import timm
from tqdm import tqdm
from torchvision import transforms as T
import json

class EvaluationReport:
    def __init__(self, model_name, model_dir: str, class_names, test_dataloader, transform, device, run_to_evaluate=None):
        self.model_dir = Path(model_dir)
        self.class_names = class_names
        self.test_dataloader = test_dataloader
        self.transform = transform
        self.device = device
        self.run_to_evaluate = run_to_evaluate
        self.model_name = model_name
        self.model_file_path = None
        self.model = self.load_model()

    def get_model_path(self, model_name="best_model.pt"):
        if self.run_to_evaluate:
            run_path = self.model_dir / self.run_to_evaluate
            if not run_path.is_dir():
                raise FileNotFoundError(f"Run '{self.run_to_evaluate}' not found in {self.model_dir}")
            model_path = run_path / model_name
            if not model_path.exists():
                raise FileNotFoundError(f"Model {model_name} not found in {run_path}")
            print(f"Evaluating run : {self.run_to_evaluate}")
            return model_path
        else:
            runs = sorted(
                [d for d in self.model_dir.glob("run_*") if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            if not runs:
                raise FileNotFoundError(f"No folder run_* found in {self.model_dir}")

            latest_run = runs[0]
            model_path = latest_run / model_name

            if not model_path.exists():
                raise FileNotFoundError(f"Model {model_name} not found in {latest_run}")

            print(f"Last run found : {latest_run.name}")
            return model_path

    def load_model(self):
        path = self.get_model_path()
        self.model_file_path = str(path) # Store the model file path
        model = timm.create_model(self.model_name, pretrained=False, num_classes=len(self.class_names))
        model.load_state_dict(torch.load(path, map_location=self.device))
        return model.to(self.device).eval()

    def load_metadata(self):
        if self.run_to_evaluate:
            run_path = self.model_dir / self.run_to_evaluate
        else:
            runs = sorted(
                [d for d in self.model_dir.glob("run_*") if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            if not runs:
                print(f"Warning: No run directories found in {self.model_dir}. Cannot load metadata.")
                return {}
            run_path = runs[0]

        metadata_path = run_path / "meta_data.json"
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            return metadata
        except FileNotFoundError:
            print(f"Warning: Metadata file not found in {run_path}. Cannot load metadata.")
            return {}
        except json.JSONDecodeError:
            print(f"Warning: Could not decode metadata JSON in {run_path}. Cannot load metadata.")
            return {}

    def save_metadata(self, metadata):
        if self.run_to_evaluate:
            run_path = self.model_dir / self.run_to_evaluate
        else:
            runs = sorted(
                [d for d in self.model_dir.glob("run_*") if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            if not runs:
                print(f"Warning: No run directories found to save metadata.")
                return

            run_path = runs[0]

        metadata_path = run_path / "meta_data.json"
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=4)
            print(f"Evaluation metrics saved to metadata: {metadata_path}")
        except IOError:
            print(f"Error: Could not save metadata to {metadata_path}.")

    def evaluate(self):
        metadata = self.load_metadata()
        if metadata and "data_splits" in metadata:
            print("\nData Split Percentages:")
            print(f"  Train: {metadata['data_splits'].get('train_percentage', 'N/A')}")
            print(f"  Validation: {metadata['data_splits'].get('validation_percentage', 'N/A')}")
            print(f"  Test: {metadata['data_splits'].get('test_percentage', 'N/A')}")
            print("----------------------")

        y_true, y_pred, inference_times = [], [], []

        for batch in tqdm(self.test_dataloader, desc="Evaluating"):
            images = batch["qry_im"].to(self.device)
            labels = batch["qry_gt"].numpy()

            start = time.time()
            with torch.no_grad():
                output = self.model(images)
            end = time.time()

            preds = torch.argmax(output, dim=1).cpu().numpy()
            y_pred.extend(preds)
            y_true.extend(labels)
            inference_times.extend([end - start] * len(labels))

        report = self.generate_report(y_true, y_pred, inference_times)

        if metadata:
            metadata["evaluation_metrics"] = report
            self.save_metadata(metadata)

        return report

    def generate_report(self, y_true, y_pred, inference_times):
        cm = confusion_matrix(y_true, y_pred)
        TN = np.diag(cm).sum() - np.trace(cm)
        FP = cm.sum(axis=0) - np.diag(cm)
        FN = cm.sum(axis=1) - np.diag(cm)
        TP = np.diag(cm)

        accuracy = (np.array(y_true) == np.array(y_pred)).mean()
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        sensitivity = (TP / (TP + FN + 1e-10)).mean()
        specificity = (TN / (TN + FP + 1e-10)).mean()
        avg_inference_time = np.mean(inference_times)
        model_size = sum(p.numel() for p in self.model.parameters() if p.requires_grad)

        model_file_size_bytes = os.path.getsize(self.model_file_path)
        model_file_size_mb = model_file_size_bytes / (1024 * 1024)

        print("Classification Report :\n")
        print(classification_report(y_true, y_pred, target_names=self.class_names, zero_division=0))

        print("\nGlobal Stats :")
        print(f"Accuracy          : {accuracy:.4f}")
        print(f"F1-score          : {f1:.4f}")
        print(f"Sensitivity       : {sensitivity:.4f}")
        print(f"Specificity       : {specificity:.4f}")
        print(f"Inference time    : {avg_inference_time:.4f}s/image")
        print(f"Model size        : {model_size:,} parameters")
        print(f"Model file size   : {model_file_size_mb:.2f} MB")

        return {
            "accuracy": accuracy,
            "f1": f1,
            "sensitivity": sensitivity,
            "specificity": specificity,
            "avg_inference_time": avg_inference_time,
            "model_size": model_size,
            "model_file_size_mb": round(model_file_size_mb, 2) # Round to 2 decimal places
        }

    def visualize_predictions(self, n=9):
        plt.figure(figsize=(12, 8))
        indices = random.sample(range(len(self.test_dataloader.dataset)), n)
        sampled_data = [self.test_dataloader.dataset[i] for i in indices]

        self.model.eval()
        with torch.no_grad():
            for i, data in enumerate(sampled_data):
                image_tensor = data["qry_im"]
                true_label = data["qry_gt"]
                image = image_tensor.unsqueeze(0).to(self.device)
                output = self.model(image)
                probabilities = torch.softmax(output, dim=1)
                pred_index = torch.argmax(output, dim=1).item()
                confidence = probabilities[0, pred_index].item() * 100
                pred = pred_index

                mean = [0.485, 0.456, 0.406]
                std = [0.229, 0.224, 0.225]
                img_copy = image_tensor.clone().detach().cpu()
                for t, m, s in zip(img_copy, mean, std):
                    t.mul_(s).add_(m)

                pil_img = transforms.ToPILImage()(img_copy)

                plt.subplot(3, 3, i + 1)
                plt.imshow(pil_img)
                plt.axis("off")
                color = "green" if pred == true_label else "red"

                confidence_str = f"({confidence:.2f}%)"

                if isinstance(self.class_names, dict):
                    reverse_mapping = {v: k for k, v in self.class_names.items()}
                    true_label_name = reverse_mapping.get(true_label, str(true_label))
                    predicted_label_name = reverse_mapping.get(pred, str(pred))
                    plt.title(f"True: {true_label_name}\nPredicted: {predicted_label_name} {confidence_str}", color=color)
                elif isinstance(self.class_names, list):
                    true_label_name = self.class_names[true_label]
                    predicted_label_name = self.class_names[pred]
                    plt.title(f"True: {true_label_name}\nPredicted->Conf: {predicted_label_name}{confidence_str}", color=color)
                else:
                    plt.title(f"True: {true_label}\nPredicted: {pred} {confidence_str}", color=color)

        plt.tight_layout()
        plt.show()