import torch
import numpy as np
from pathlib import Path
from tqdm import tqdm
import timm
from sklearn.metrics import f1_score
import time

class RunEvaluator:
    def __init__(self, model_dir: str, model_name, class_names, test_dataloader, transform, device):
        self.model_dir = Path(model_dir)
        self.model_name = model_name
        self.class_names = class_names
        self.test_dataloader = test_dataloader
        self.transform = transform
        self.device = device

    def evaluate_run(self, run_path):
        model_path = run_path / "best_model.pt"
        if not model_path.exists():
            print(f"Warning: Model not found in {run_path}")
            return None

        model = timm.create_model(self.model_name, pretrained=False, num_classes=len(self.class_names))
        try:
            model.load_state_dict(torch.load(model_path, map_location=self.device))
        except Exception as e:
            print(f"Error loading model from {model_path}: {e}")
            return None
        model.to(self.device).eval()

        y_true, y_pred, inference_times = [], [], []
        start_time = time.time()
        with torch.no_grad():
            for batch in self.test_dataloader:
                images = batch["qry_im"].to(self.device)
                labels = batch["qry_gt"].numpy()

                start = time.time()
                output = model(images)
                end = time.time()

                preds = torch.argmax(output, dim=1).cpu().numpy()
                y_pred.extend(preds)
                y_true.extend(labels)
                inference_times.extend([end - start] * len(labels))
        end_time = time.time()
        total_inference_time = end_time - start_time
        avg_inference_time = np.mean(inference_times) if inference_times else 0

        accuracy = (np.array(y_true) == np.array(y_pred)).mean()
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

        return {
            "accuracy": accuracy,
            "f1": f1,
            "inference_time": avg_inference_time,
            "total_inference_time": total_inference_time,
            "num_samples": len(y_true)
        }

    def evaluate_all_runs(self):
        run_directories = sorted(
            [d for d in self.model_dir.glob("run_*") if d.is_dir()],
            key=lambda x: x.name  # Sort by run name for consistency
        )

        if not run_directories:
            print(f"No 'run_*' directories found in {self.model_dir}")
            return

        results = {}
        print("Evaluating all runs...")
        for run_path in tqdm(run_directories, desc="Evaluating Runs"):
            run_name = run_path.name
            evaluation_metrics = self.evaluate_run(run_path)
            if evaluation_metrics:
                results[run_name] = evaluation_metrics

        if not results:
            print("No runs were successfully evaluated.")
            return

        self.rank_runs(results)

    def rank_runs(self, results):
        print("\nModel Run Rankings...")

        ranked_by_f1 = sorted(results.items(), key=lambda item: item[1]['f1'], reverse=True)
        print("\nRanked by F1-Score:")
        for i, (run_name, metrics) in enumerate(ranked_by_f1):
            print(f"{i+1}. {run_name}: F1-Score = {metrics['f1']:.4f}")

        ranked_by_accuracy = sorted(results.items(), key=lambda item: item[1]['accuracy'], reverse=True)
        print("\nRanked by Accuracy:")
        for i, (run_name, metrics) in enumerate(ranked_by_accuracy):
            print(f"{i+1}. {run_name}: Accuracy = {metrics['accuracy']:.4f}")

        ranked_by_inference_time = sorted(results.items(), key=lambda item: item[1]['inference_time'])
        print("\nRanked by Average Inference Time (per image):")
        for i, (run_name, metrics) in enumerate(ranked_by_inference_time):
            print(f"{i+1}. {run_name}: Inference Time = {metrics['inference_time']:.4f} s/image")

        ranked_by_total_inference_time = sorted(results.items(), key=lambda item: item[1]['total_inference_time'])
        print("\nRanked by Total Inference Time (for all test samples):")
        for i, (run_name, metrics) in enumerate(ranked_by_total_inference_time):
            print(f"{i+1}. {run_name}: Total Inference Time = {metrics['total_inference_time']:.4f} s (on {metrics['num_samples']} samples)")