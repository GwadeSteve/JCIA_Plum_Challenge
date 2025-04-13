import numpy as np
import matplotlib.pyplot as plt
import os
import torch
import timm
import torch
from tqdm import tqdm
import time
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
from torchmetrics.classification import MulticlassStatScores, MulticlassF1Score
import json

class CustomTrainValidation:
    def __init__(self, model_name, train_dataloader, validation_dataloader, classes, device, learning_rate, save_directory, cls_count,
                 run_name, data_name, epochs, project_name, batch_size=32, patience=5, RANDOM_SEED=1242025, SPLIT_RANDOM_SEED=1242025,
                 train_im_paths=None, val_im_paths=None, test_im_paths=None, dataset_path=None):
        self.model_name = model_name
        self.classes = classes
        self.device = device
        self.learning_rate = learning_rate
        self.save_directory = save_directory
        self.batch_size = batch_size
        self.train_dataloader = train_dataloader
        self.validation_dataloader = validation_dataloader
        self.patience = patience
        self.run_name = run_name
        self.epochs = epochs
        self.data_name = data_name
        self.project_name = project_name
        self.train_im_paths = train_im_paths 
        self.val_im_paths = val_im_paths     
        self.test_im_paths = test_im_paths   
        self.dataset_path = dataset_path
        self.RANDOM_SEED = RANDOM_SEED
        self.SPLIT_RANDOM_SEED = SPLIT_RANDOM_SEED
        self.cls_counts = cls_count
        self.run()

    def initialize_model(self):
        self.model = timm.create_model(self.model_name, pretrained=True, num_classes=len(self.classes))

    def initialize_lists(self):
        self.train_losses = []
        self.validation_losses = []
        self.train_accuracies = []
        self.validation_accuracies = []
        self.train_f1_scores = []
        self.validation_f1_scores = []
        self.train_sensitivities = []
        self.validation_sensitivities = []
        self.train_specificities = []
        self.validation_specificities = []
        self.train_times = []
        self.validation_times = []

    def setup_training(self):
        self.best_validation_accuracy = 0.0
        self.improvement_threshold = 0.001
        self.epochs_without_improvement = 0
        self.stop_training = False
        self.train_data_length = len(self.train_dataloader.dataset)
        self.validation_data_length = len(self.validation_dataloader.dataset)
        self.cosine_similarity_labels = {"positive": torch.tensor(1.).unsqueeze(0), "negative": torch.tensor(-1.).unsqueeze(0)}
        self.checkpoint_path = f"{self.save_directory}/best_model.pt"

        self.model.to(self.device).train()
        self.cross_entropy_loss = nn.CrossEntropyLoss()
        self.cosine_embedding_loss = nn.CosineEmbeddingLoss(margin=0.3)
        self.optimizer = optim.Adam(params=self.model.parameters(), lr=self.learning_rate)
        self.scheduler = lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='max', factor=0.1, patience=3, verbose=True) # Changed mode to 'max'
        self.train_f1 = MulticlassF1Score(num_classes=len(self.classes), average='macro').to(self.device)
        self.val_f1 = MulticlassF1Score(num_classes=len(self.classes), average='macro').to(self.device)
        self.train_stats = MulticlassStatScores(num_classes=len(self.classes), average='macro').to(self.device)
        self.val_stats = MulticlassStatScores(num_classes=len(self.classes), average='macro').to(self.device)

    def make_directories(self, path):
        os.makedirs(path, exist_ok=True)

    def get_feature_maps(self, feature_maps):
        pool = nn.AvgPool2d((feature_maps[0].shape[2], feature_maps[0].shape[3]))
        return [torch.reshape(pool(fm), (-1, fm.shape[1])) for fm in feature_maps]

    def get_model_logits(self, images):
        return [self.model.forward_features(im) for im in images]

    def get_model_predictions(self, features):
        return [self.model.forward_head(ft) for ft in features]

    def get_cosine_similarity_loss(self, query_features, positive_features, negative_features):
        positive_loss = self.cosine_embedding_loss(query_features, positive_features, self.cosine_similarity_labels["positive"].to(self.device))
        negative_loss = self.cosine_embedding_loss(query_features, negative_features, self.cosine_similarity_labels["negative"].to(self.device))
        return positive_loss + negative_loss

    def get_cross_entropy_loss(self, query_predictions, positive_predictions, query_labels):
        query_loss = self.cross_entropy_loss(query_predictions, query_labels)
        positive_loss = self.cross_entropy_loss(positive_predictions, query_labels)
        return query_loss + positive_loss

    def calculate_loss_and_predictions(self, query_images, positive_images, negative_images, query_labels):
        query_logits, positive_logits, negative_logits = self.get_model_logits([query_images, positive_images, negative_images])
        query_predictions, positive_predictions = self.get_model_predictions([query_logits, positive_logits])
        query_feature_maps, positive_feature_maps, negative_feature_maps = self.get_feature_maps([query_logits, positive_logits, negative_logits])
        contrastive_loss = self.get_cosine_similarity_loss(query_feature_maps, positive_feature_maps, negative_feature_maps)
        cross_entropy_loss = self.get_cross_entropy_loss(query_predictions, positive_predictions, query_labels)
        total_loss = contrastive_loss + cross_entropy_loss
        return torch.argmax(query_predictions, dim=1), total_loss, query_predictions

    def train_one_epoch(self, epoch):
        self.model.train()
        epoch_loss = 0
        all_predicted_labels = []
        all_ground_truth_labels = []
        start_time = time.time()
        self.train_f1.reset()
        self.train_stats.reset()
        progress_bar = tqdm(self.train_dataloader, desc=f"Epoch {epoch + 1}/{self.epochs} (Train)")
        for batch in progress_bar:
            query_images, positive_images, negative_images, query_labels = self.move_batch_to_device(batch)
            predicted_labels_tensor, loss, query_predictions = self.calculate_loss_and_predictions(query_images, positive_images, negative_images, query_labels)
            epoch_loss += loss.item() * query_labels.size(0)

            predicted_labels_np = predicted_labels_tensor.cpu().numpy()
            ground_truth_labels_np = query_labels.cpu().numpy()
            all_predicted_labels.extend(predicted_labels_np)
            all_ground_truth_labels.extend(ground_truth_labels_np)

            self.train_f1.update(query_predictions, query_labels)
            self.train_stats.update(query_predictions, query_labels)

            accuracy = (predicted_labels_tensor == query_labels).float().mean()
            f1 = self.train_f1.compute()
            tp, fp, tn, fn, _ = self.train_stats.compute()
            specificity = tn / (tn + fp + 1e-10)
            sensitivity = tp / (tp + fn + 1e-10)

            progress_bar.set_postfix({"loss": f"{loss.item():.3f}", "acc": f"{accuracy:.3f}", "f1": f"{f1:.3f}",
                                        "spec": f"{specificity:.3f}", "sens": f"{sensitivity:.3f}"})

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        epoch_time = time.time() - start_time
        train_loss = epoch_loss / len(self.train_dataloader.dataset)
        train_accuracy = (torch.tensor(all_predicted_labels) == torch.tensor(all_ground_truth_labels)).float().mean().item()
        train_f1 = self.train_f1.compute().item()
        tp, fp, tn, fn, _ = self.train_stats.compute()
        train_specificity = tn / (tn + fp + 1e-10)
        train_sensitivity = tp / (tp + fn + 1e-10)

        self.train_losses.append(train_loss)
        self.train_accuracies.append(train_accuracy)
        self.train_f1_scores.append(train_f1)
        self.train_sensitivities.append(train_sensitivity)
        self.train_specificities.append(train_specificity)
        self.train_times.append(epoch_time)

        print("\n******************** TRAIN PROCESS STATS ********************")
        print(f"\n{epoch + 1}-epoch train process is completed!\n")
        print(f"{epoch + 1}-epoch train loss           -> {train_loss:.3f}")
        print(f"{epoch + 1}-epoch train specificity    -> {train_specificity:.3f}")
        print(f"{epoch + 1}-epoch train sensitivity    -> {train_sensitivity:.3f}")
        print(f"{epoch + 1}-epoch train accuracy     -> {train_accuracy:.3f}")
        print(f"{epoch + 1}-epoch train f1-score       -> {train_f1:.3f}")

    def evaluate_one_epoch(self, epoch):
        self.model.eval()
        epoch_loss = 0
        all_predicted_labels = []
        all_ground_truth_labels = []
        start_time = time.time()
        self.val_f1.reset()
        self.val_stats.reset()
        with torch.no_grad():
            progress_bar = tqdm(self.validation_dataloader, desc=f"Epoch {epoch + 1}/{self.epochs} (Validation)")
            for batch in progress_bar:
                query_images, positive_images, negative_images, query_labels = self.move_batch_to_device(batch)
                predicted_labels_tensor, loss, query_predictions = self.calculate_loss_and_predictions(query_images, positive_images, negative_images, query_labels)
                epoch_loss += loss.item() * query_labels.size(0)

                predicted_labels_np = predicted_labels_tensor.cpu().numpy()
                ground_truth_labels_np = query_labels.cpu().numpy()
                all_predicted_labels.extend(predicted_labels_np)
                all_ground_truth_labels.extend(ground_truth_labels_np)

                self.val_f1.update(query_predictions, query_labels)
                self.val_stats.update(query_predictions, query_labels)

                accuracy = (predicted_labels_tensor == query_labels).float().mean()
                f1 = self.val_f1.compute()
                tp, fp, tn, fn, _ = self.val_stats.compute()
                specificity = tn / (tn + fp + 1e-10)
                sensitivity = tp / (tp + fn + 1e-10)

                progress_bar.set_postfix({"loss": f"{loss.item():.3f}", "acc": f"{accuracy:.3f}", "f1": f"{f1:.3f}",
                                            "spec": f"{specificity:.3f}", "sens": f"{sensitivity:.3f}"})

        epoch_time = time.time() - start_time
        validation_loss = epoch_loss / len(self.validation_dataloader.dataset)
        validation_accuracy = (torch.tensor(all_predicted_labels) == torch.tensor(all_ground_truth_labels)).float().mean().item()
        validation_f1 = self.val_f1.compute().item()
        tp, fp, tn, fn, _ = self.val_stats.compute()
        validation_specificity = tn / (tn + fp + 1e-10)
        validation_sensitivity = tp / (tp + fn + 1e-10)

        self.validation_losses.append(validation_loss)
        self.validation_accuracies.append(validation_accuracy)
        self.validation_f1_scores.append(validation_f1)
        self.validation_sensitivities.append(validation_sensitivity)
        self.validation_specificities.append(validation_specificity)
        self.validation_times.append(epoch_time)

        print(f"\n{epoch + 1}-epoch validation process is completed!\n")
        print(f"{epoch + 1}-epoch validation loss       -> {validation_loss:.3f}")
        print(f"{epoch + 1}-epoch validation specificity -> {validation_specificity:.3f}")
        print(f"{epoch + 1}-epoch validation sensitivity -> {validation_sensitivity:.3f}")
        print(f"{epoch + 1}-epoch validation accuracy  -> {validation_accuracy:.3f}")
        print(f"{epoch + 1}-epoch validation f1-score    -> {validation_f1:.3f}")
        print("\n************************************************************~")

        return validation_accuracy 

    def save_best_model(self):
        torch.save(self.model.state_dict(), self.checkpoint_path)
        print("Pretrained weights of the model with highest validation accuracy are successfully saved!")

    def save_model_epoch(self, epoch):
        epoch_checkpoint_path = f"{self.save_directory}/{self.data_name}_{self.run_name}_{self.model_name}_epoch_{epoch + 1}.pt"
        torch.save(self.model.state_dict(), epoch_checkpoint_path)
        print(f"Model weights saved at the end of epoch {epoch + 1}!")

    def summarize_epoch(self, validation_accuracy, epoch):
        if (validation_accuracy > self.best_validation_accuracy + self.improvement_threshold):
            print(f"\nValidation accuracy is increased from {self.best_validation_accuracy:.5f} to {validation_accuracy:.5f}")
            print("Saving the best model with the highest validation accuracy...\n")
            self.best_validation_accuracy = validation_accuracy
            self.save_best_model()
            self.epochs_without_improvement = 0
        else:
            self.epochs_without_improvement += 1
            print(f"\nValidation accuracy is not significantly increased from {self.best_validation_accuracy:.5f}. The current epoch accuracy is {validation_accuracy:.5f}.")
            print(f"Validation accuracy value did not increase for {self.epochs_without_improvement} epochs")
            if self.epochs_without_improvement == self.patience:
                print(f"Stop training since accuracy value did not increase for {self.patience} epochs.")
                self.stop_training = True

        #self.scheduler.step(validation_accuracy) 

    def move_batch_to_device(self, batch):
        return batch["qry_im"].to(self.device), batch["pos_im"].to(self.device), batch["neg_im"].to(self.device), batch["qry_gt"].to(self.device)

    def train_model(self):
        print("Start training...")
        for epoch in range(self.epochs):
            self.train_one_epoch(epoch)
            validation_accuracy = self.evaluate_one_epoch(epoch)
            self.summarize_epoch(validation_accuracy, epoch)
            if self.stop_training:
                break

    def get_training_stats(self):
        return [self.train_losses, self.validation_losses, self.train_accuracies, self.validation_accuracies,
                self.train_f1_scores, self.validation_f1_scores, self.train_specificities, self.validation_specificities,
                self.train_sensitivities, self.validation_sensitivities, self.train_times, self.validation_times]

    def _save_metadata(self):
        total_images = len(self.train_im_paths) + len(self.val_im_paths) + len(self.test_im_paths)
        train_percentage = len(self.train_im_paths) / total_images if total_images > 0 else 0.0
        val_percentage = len(self.val_im_paths) / total_images if total_images > 0 else 0.0
        test_percentage = len(self.test_im_paths) / total_images if total_images > 0 else 0.0

        metadata = {
            "torch_random_seed": self.RANDOM_SEED,
            "split_random_seed": self.SPLIT_RANDOM_SEED,
            "data_splits": {
                "train_percentage": round(train_percentage, 3),
                "validation_percentage": round(val_percentage, 3),
                "test_percentage": round(test_percentage, 3),
            },
            "run_name": self.run_name,
            "model": self.model_name,
            "dataset": self.dataset_path,
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "epochs": self.epochs,
            "patience": self.patience,
            "classes": self.classes,
            "class_counts_train": self.cls_counts 
        }
        metadata_path = os.path.join(self.save_directory, "meta_data.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        print(f"Metadata saved to: {metadata_path}")

    def run(self):
        self.make_directories(self.save_directory)
        self.initialize_lists()
        self.initialize_model()
        self.setup_training()
        self._save_metadata()
        self.train_model()
        
def plot_training_validation_curves(train_validation_instance):
    train_losses = [loss.cpu().numpy() if isinstance(loss, torch.Tensor) else np.array(loss) for loss in train_validation_instance.train_losses]
    validation_losses = [loss.cpu().numpy() if isinstance(loss, torch.Tensor) else np.array(loss) for loss in train_validation_instance.validation_losses]
    train_accuracies = [acc.cpu().numpy() if isinstance(acc, torch.Tensor) else np.array(acc) for acc in train_validation_instance.train_accuracies]
    validation_accuracies = [acc.cpu().numpy() if isinstance(acc, torch.Tensor) else np.array(acc) for acc in train_validation_instance.validation_accuracies]
    train_f1_scores = [f1.cpu().numpy() if isinstance(f1, torch.Tensor) else np.array(f1) for f1 in train_validation_instance.train_f1_scores]
    validation_f1_scores = [f1.cpu().numpy() if isinstance(f1, torch.Tensor) else np.array(f1) for f1 in train_validation_instance.validation_f1_scores]
    train_sensitivities = [sens.cpu().numpy() if isinstance(sens, torch.Tensor) else np.array(sens) for sens in train_validation_instance.train_sensitivities]
    validation_sensitivities = [sens.cpu().numpy() if isinstance(sens, torch.Tensor) else np.array(sens) for sens in train_validation_instance.validation_sensitivities]
    train_specificities = [spec.cpu().numpy() if isinstance(spec, torch.Tensor) else np.array(spec) for spec in train_validation_instance.train_specificities]
    validation_specificities = [spec.cpu().numpy() if isinstance(spec, torch.Tensor) else np.array(spec) for spec in train_validation_instance.validation_specificities]
    epochs = train_validation_instance.epochs
    save_directory = train_validation_instance.save_directory
    run_name = train_validation_instance.run_name

    actual_epochs = len(train_losses)
    epochs_range = range(1, actual_epochs + 1)

    plt.figure(figsize=(18, 12))

    font_size = 14

    plt.subplot(2, 2, 1)
    plt.plot(epochs_range, train_losses, marker='o', linestyle='-', color='dodgerblue', label='Loss')
    plt.title('Training Loss', fontsize=font_size)
    plt.xlabel('Epochs', fontsize=font_size)
    plt.ylabel('Loss', fontsize=font_size)
    plt.legend(loc='best', fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.grid(True)

    plt.subplot(2, 2, 2)
    plt.plot(epochs_range, validation_losses, marker='o', linestyle='--', color='dodgerblue', label='Loss')
    plt.title('Validation Loss', fontsize=font_size)
    plt.xlabel('Epochs', fontsize=font_size)
    plt.ylabel('Loss', fontsize=font_size)
    plt.legend(loc='best', fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.grid(True)

    plt.subplot(2, 2, 3)
    plt.plot(epochs_range, train_accuracies, marker='*', linestyle='-', color='forestgreen', linewidth=3, label='Accuracy')
    plt.plot(epochs_range, train_f1_scores, marker='^', linestyle='--', color='orange', label='F1-Score')
    plt.plot(epochs_range, train_specificities, marker='d', linestyle=':', color='darkviolet', label='Specificity')
    plt.title('Training Metrics', fontsize=font_size)
    plt.xlabel('Epochs', fontsize=font_size)
    plt.ylabel('Metric Value', fontsize=font_size)
    plt.ylim(0, 1.1)
    plt.legend(loc='best', fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.grid(True)

    plt.subplot(2, 2, 4)
    plt.plot(epochs_range, validation_accuracies, marker='*', linestyle='-', color='forestgreen', linewidth=3, label='Accuracy')
    plt.plot(epochs_range, validation_f1_scores, marker='^', linestyle='--', color='orange', label='F1-Score')
    plt.plot(epochs_range, validation_specificities, marker='d', linestyle=':', color='darkviolet', label='Specificity')
    plt.title('Validation Metrics', fontsize=font_size)
    plt.xlabel('Epochs', fontsize=font_size)
    plt.ylabel('Metric Value', fontsize=font_size)
    plt.ylim(0, 1.1)
    plt.legend(loc='best', fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.grid(True)

    plt.tight_layout()
    plot_path = os.path.join(save_directory, f"{run_name}_training_validation_curves.png")
    plt.savefig(plot_path)
    plt.show()
    print(f"Training and validation curves saved to: {plot_path}")