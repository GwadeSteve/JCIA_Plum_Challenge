import os
from glob import glob
import torch
from PIL import Image
from torchvision import transforms as T
import timm
import numpy as np
import torch.nn.functional as F
import time
import json
import matplotlib.pyplot as plt
import seaborn as sns
import math

sns.set_style("whitegrid")
colors = sns.color_palette("pastel", 3)
plt.rcParams.update({'font.size': 11}) 

plums_dir = "../../Plums"
image_paths = sorted(
    glob(os.path.join(plums_dir, "*.[jJ][pP][gG]")) +
    glob(os.path.join(plums_dir, "*.[pP][nN][gG]")) +
    glob(os.path.join(plums_dir, "*.[jJ][pP][eE][gG]"))
)


models_dir = "../../Models/Trained/CustomRexNet" 
run_directories = sorted(glob(os.path.join(models_dir, "run_*")))

mean, std, size = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225], 224
eval_tfs = T.Compose(
    [
        T.Resize(size=(size, size), antialias=True), 
        T.ToTensor(),
        T.Normalize(mean=mean, std=std)
    ]
)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

print(f"Found {len(image_paths)} images in: {plums_dir}")
print(f"Found {len(run_directories)} runs to evaluate in: {models_dir}")

run_avg_inference_times = {}

if not run_directories:
    print(f"ERROR: No 'run_*' directories found in {models_dir}. Cannot proceed.")
elif not image_paths:
     print(f"ERROR: No images found in {plums_dir}. Cannot proceed.")
else:
    for run_path in run_directories:
        run_name = os.path.basename(run_path)
        model_path = os.path.join(run_path, "best_model.pt")
        metadata_path = os.path.join(run_path, "meta_data.json")
        current_classes_list = None 
        inference_times_current_run = [] 

        if not os.path.exists(model_path):
            print(f"Warning: 'best_model.pt' not found in {run_name}. Skipping this run.")
            continue

        if not os.path.exists(metadata_path):
            print(f"Warning: 'meta_data.json' not found in {run_name}. Skipping this run.")
            continue

        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                current_classes_dict = metadata.get('classes')
                if not current_classes_dict or not isinstance(current_classes_dict, dict):
                    print(f"Warning: 'classes' key not found or not a dictionary in {metadata_path}. Skipping this run.")
                    continue
                num_classes = len(current_classes_dict)
                current_classes_list = [None] * num_classes
                for name, index in current_classes_dict.items():
                    if 0 <= index < num_classes:
                         current_classes_list[index] = name
                    else:
                         raise ValueError(f"Invalid class index {index} for class '{name}' in {metadata_path}")
                if None in current_classes_list:
                     raise ValueError(f"Class indices in {metadata_path} do not form a complete sequence from 0 to N-1.")

        except Exception as e:
            print(f"Error loading or processing metadata from {metadata_path}: {e}. Skipping this run.")
            continue

        print(f"\n--- Evaluating Run: {run_name} ---")

        model = timm.create_model("rexnet_100", pretrained=False, num_classes=len(current_classes_list))
        try:
            model.load_state_dict(torch.load(model_path, map_location=device))
            model.to(device)
            model.eval()
        except Exception as e:
            print(f"Error loading model state_dict for {run_name}: {e}. Skipping this run.")
            continue

        num_images = len(image_paths)
        if num_images > 0:
            pairs_per_row = min(2, num_images)
            num_rows = math.ceil(num_images / pairs_per_row)
            num_cols = pairs_per_row * 2
            fig_width = pairs_per_row * 7 
            fig_height = num_rows * 4.5  
            fig, axes = plt.subplots(num_rows, num_cols, figsize=(fig_width, fig_height), squeeze=False) # squeeze=False keeps axes 2D even if 1 row/col
            axes = axes.flatten()

            with torch.no_grad():
                for i, img_path in enumerate(image_paths):
                    img_name = os.path.basename(img_path)
                    img_ax_idx = i * 2
                    plot_ax_idx = i * 2 + 1

                    if img_ax_idx >= len(axes):
                        print("Warning: Axes index out of bounds.")
                        continue

                    img_ax = axes[img_ax_idx]
                    plot_ax = axes[plot_ax_idx]

                    try:
                        img = Image.open(img_path).convert("RGB")
                        img_transformed = eval_tfs(img).unsqueeze(0).to(device)

                        start_time = time.time()
                        output = model(img_transformed)
                        end_time = time.time()
                        inference_time = end_time - start_time
                        inference_times_current_run.append(inference_time)

                        probabilities = F.softmax(output, dim=1).cpu().numpy()[0]
                        top_indices = np.argsort(probabilities)[::-1][:3]
                        top_probabilities = probabilities[top_indices]
                        top_classes = [current_classes_list[idx] for idx in top_indices]

                        img_ax.imshow(img)
                        predicted_class = top_classes[0]
                        predicted_probability = top_probabilities[0]
                        img_ax.set_title(f"{img_name}\nPred: {predicted_class} ({predicted_probability:.2f})", fontsize=10)
                        img_ax.axis('off')

                        bars = plot_ax.barh(top_classes, top_probabilities, color=colors, height=0.6)
                        plot_ax.set_xlabel("Probability", fontsize=9)
                        plot_ax.set_title(f"Top 3 ({inference_time:.4f}s)", fontsize=10)
                        plot_ax.invert_yaxis()
                        plot_ax.tick_params(axis='both', which='major', labelsize=8)
                        plot_ax.set_xlim(0, 1.05)

                        for bar in bars:
                            width = bar.get_width()
                            plot_ax.text(width + 0.01, bar.get_y() + bar.get_height()/2,
                                         f'{width:.2f}', ha='left', va='center', fontsize=8)

                    except Exception as e:
                        print(f"Error processing image {img_name} for run {run_name}: {e}")
                        img_ax.set_title(f"{img_name}\nError", fontsize=10)
                        img_ax.axis('off')
                        plot_ax.axis('off')

            for j in range(num_images * 2, len(axes)):
                axes[j].axis('off')

            plt.suptitle(f"Predictions for Run: {run_name}", fontsize=14, y=0.99)
            plt.tight_layout(rect=[0, 0.01, 1, 0.96])
            plt.show()

            if inference_times_current_run:
                avg_time = np.mean(inference_times_current_run)
                run_avg_inference_times[run_name] = avg_time
                print(f"Average inference time for run {run_name}: {avg_time:.4f} seconds")
            else:
                 print(f"No valid inference times recorded for run {run_name}.")

        else:
            print(f"No images were processed for run {run_name}.")

print("\n--- Average Inference Time Ranking (Lower is Faster) ---")
if run_avg_inference_times:
    sorted_runs = sorted(run_avg_inference_times.items(), key=lambda item: item[1])
    for rank, (run_name, avg_time) in enumerate(sorted_runs):
        print(f"{rank + 1}. Run: {run_name} - Avg Time: {avg_time:.4f} seconds")
else:
    print("No average inference times were calculated.")

print("\nEvaluation complete.")