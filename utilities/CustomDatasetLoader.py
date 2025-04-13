import os
import random
from PIL import Image
from torch.utils.data import Dataset, DataLoader

class CustomDataset(Dataset):
    def __init__(self, im_paths, transformations=None):
        self.transformations = transformations
        self.im_paths = im_paths
        self.cls_names, self.cls_counts = self._get_class_info()
        self.max_cls_count = max(self.cls_counts.values()) if self.cls_counts else 1 # To avoid division by zero

    def _get_class_info(self):
        cls_names = {}
        cls_counts = {}
        count = 0
        for im_path in self.im_paths:
            cls_name = self._get_cls_name(im_path)
            if cls_name not in cls_names:
                cls_names[cls_name] = count
                count += 1
            if cls_name not in cls_counts:
                cls_counts[cls_name] = 1
            else:
                cls_counts[cls_name] += 1
        return cls_names, cls_counts

    def _get_cls_name(self, path):
        parts = path.split(os.sep)
        return parts[-2]

    def __len__(self):
        return len(self.im_paths)

    def get_pos_neg_im_paths(self, qry_label):
        pos_im_paths = [im_path for im_path in self.im_paths if qry_label == self._get_cls_name(im_path)]
        neg_im_paths = [im_path for im_path in self.im_paths if qry_label != self._get_cls_name(im_path)]

        if not pos_im_paths or not neg_im_paths:
            return None, None

        pos_rand_int = random.randint(a=0, b=len(pos_im_paths) - 1)
        neg_rand_int = random.randint(a=0, b=len(neg_im_paths) - 1)

        return pos_im_paths[pos_rand_int], neg_im_paths[neg_rand_int]

    def __getitem__(self, idx):
        im_path = self.im_paths[idx]
        qry_im = Image.open(im_path).convert("RGB")
        qry_label = self._get_cls_name(im_path)

        pos_im_path, neg_im_path = self.get_pos_neg_im_paths(qry_label=qry_label)

        if pos_im_path is None or neg_im_path is None:
            print(f"Warning: Missing images samples for class {qry_label}. Copying...")
            pos_im = qry_im.copy()
            temp_neg_path = random.choice([p for p in self.im_paths if self._get_cls_name(p) != qry_label])
            neg_im = Image.open(temp_neg_path).convert("RGB")
        else:
            pos_im, neg_im = Image.open(pos_im_path).convert("RGB"), Image.open(neg_im_path).convert("RGB")

        qry_gt = self.cls_names[qry_label]
        neg_gt = self.cls_names[self._get_cls_name(neg_im_path)]

        if self.transformations is not None:
            qry_im_transformed = self.transformations(qry_im)
            pos_im_transformed = self.transformations(pos_im)
            neg_im_transformed = self.transformations(neg_im)
        else:
            qry_im_transformed = qry_im
            pos_im_transformed = pos_im
            neg_im_transformed = neg_im

        # Dynamic augmentation for imbalanced classes
        #augmentation_probability = 0.0
        #if self.cls_counts:
        #    class_count = self.cls_counts.get(qry_label, 1)
        #    augmentation_probability = 1.0 - (class_count / self.max_cls_count)
#
        #if random.random() < augmentation_probability:
        #    augmentations = T.Compose([
        #        T.RandomRotation(degrees=5),
        #        T.ColorJitter(brightness=0.01, contrast=0.01, saturation=0.05, hue=0.01),
        #        T.RandomHorizontalFlip(p=0.25),
        #        T.RandomAffine(degrees=0, translate=(0.05, 0.05), scale=(0.95, 1.05))
        #   ])
        #    qry_im_transformed = augmentations(qry_im_transformed)

        data = {}
        data["qry_im"] = qry_im_transformed
        data["qry_gt"] = qry_gt
        data["pos_im"] = pos_im_transformed
        data["neg_im"] = neg_im_transformed
        data["neg_gt"] = neg_gt

        return data

def get_dls(train_im_paths, val_im_paths, test_im_paths, transformations, bs, ns=4):
    train_ds = CustomDataset(im_paths=train_im_paths, transformations=transformations)
    val_ds = CustomDataset(im_paths=val_im_paths, transformations=transformations)
    test_ds = CustomDataset(im_paths=test_im_paths, transformations=transformations)

    val_ds.cls_names = train_ds.cls_names
    test_ds.cls_names = train_ds.cls_names

    tr_dl = DataLoader(train_ds, batch_size=bs, shuffle=True, num_workers=ns)
    val_dl = DataLoader(val_ds, batch_size=bs, shuffle=False, num_workers=ns)
    ts_dl = DataLoader(test_ds, batch_size=1, shuffle=False, num_workers=ns)

    return tr_dl, val_dl, ts_dl, train_ds.cls_names, train_ds.cls_counts, len(train_ds), len(val_ds), len(test_ds)