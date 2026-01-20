
import os
import json
import numpy as np
import time
import threading
from PIL import Image
import ssl
from pathlib import Path

from src.Framework.Recognition.AbstractRecognizer import AbstractRecognizer

# Fix for MacOS SSL certificate verification error when downloading models
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


# Global imports (lazy loaded to avoid slowing down startup if missing)
torch = None
transforms = None
models = None

class KNNRecognizer(AbstractRecognizer):
    """
    KNN Service for Object Recognition using MobileNetV2.
    """
    def __init__(self, dataset_name="default_dataset"):
        # Since this class is in src/Core/Recognition, parent.parent.parent is src/
        # Adjust path dynamically based on file location
        current_file = Path(__file__).resolve()
        # back/src/Core/Recognition/KNNRecognizer.py
        # root needed: back/
        self.root_dir = current_file.parent.parent.parent.parent
        self.model_dir = self.root_dir / "model"
        self.model_dir.mkdir(exist_ok=True)
        
        self.dataset_name = dataset_name
        self.samples_file = self.model_dir / f"{dataset_name}.json"
        
        self.training_samples = []  # List of {'label': str, 'vector': []}
        self.model = None
        self.transform = None
        
        self.load_samples()
        
        # Preload dependencies and model in background
        print("[KNNRecognizer] Starting background preload...")
        threading.Thread(target=self._ensure_deps, daemon=True).start()
        
    def _ensure_deps(self):
        """Lazy load dependencies."""
        global torch, transforms, models
        if torch is None:
            import torch
            from torchvision import transforms, models
            
        if self.model is None:
            # Load MobileNetV2 (pretrained)
            print("[KNNRecognizer] Loading MobileNetV2...")
            base_model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
            # Remove classifier (last layer) to get features
            self.model = torch.nn.Sequential(*list(base_model.children())[:-1])
            self.model.eval()
            
            self.transform = transforms.Compose([
                transforms.Resize(224),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                     std=[0.229, 0.224, 0.225])
            ])

    def set_dataset(self, name):
        """Switch dataset."""
        self.dataset_name = name
        self.samples_file = self.model_dir / f"{name}.json"
        
        # Ensure file exists if it's new
        if not self.samples_file.exists():
            self.training_samples = []
            self._save_samples()
        else:
            self.load_samples()

    def create_dataset(self, name):
        """Create and switch to new dataset."""
        self.set_dataset(name)

    def list_datasets(self):
        """List available datasets."""
        files = [f.replace(".json", "") for f in os.listdir(self.model_dir) if f.endswith(".json")]
        return files or ["default_dataset"]

    def add_sample(self, image_bytes, label, save=True):
        """Extract features and save sample."""
        self._ensure_deps()
        
        vector = self._extract_vector(image_bytes)
        if vector is not None:
            sample = {
                "label": label,
                "vector": vector.tolist(),  # Convert numpy to list for JSON
                "id": str(time.time())
            }
            self.training_samples.append(sample)
            if save:
                self._save_samples()
            print(f"[KNNRecognizer] Added sample '{label}' to {self.dataset_name} (Total: {len(self.training_samples)})")
            return True
        return False
        
    def save(self):
        """Force save to disk."""
        self._save_samples()

    def predict(self, image_bytes) -> tuple[str, float]:
        """Find nearest neighbor."""
        if not self.training_samples:
            return "Need Training", 0.0
            
        self._ensure_deps()
        
        vector = self._extract_vector(image_bytes)
        if vector is None:
            return "Error", 0.0
            
        # Linear scan for nearest neighbor (simple KNN k=1)
        min_dist = float('inf')
        best_label = "Unknown"
        
        for sample in self.training_samples:
            try:
                sample_vec = np.array(sample['vector'])
                dist = np.linalg.norm(vector - sample_vec)
                
                if dist < min_dist:
                    min_dist = dist
                    best_label = sample['label']
            except:
                continue
                
        return best_label, min_dist

    def delete_label(self, label):
        """Remove all samples of a label."""
        self.training_samples = [s for s in self.training_samples if s['label'] != label]
        self._save_samples()
        print(f"[KNNRecognizer] Deleted label '{label}' from {self.dataset_name}")
        
    def get_counts(self):
        """Return count per label."""
        counts = {}
        for s in self.training_samples:
            l = s['label']
            counts[l] = counts.get(l, 0) + 1
        return counts

    def _extract_vector(self, image_bytes):
        """Run image through MobileNetV2."""
        try:
            import torch
            from io import BytesIO
            
            img = Image.open(BytesIO(image_bytes)).convert('RGB')
            input_tensor = self.transform(img).unsqueeze(0)  # Add batch dim
            
            with torch.no_grad():
                features = self.model(input_tensor)
                # Global Average Pooling (1280, 7, 7) -> (1280)
                features = torch.nn.functional.adaptive_avg_pool2d(features, (1, 1))
                features = torch.flatten(features, 1)
                
            return features[0].numpy()
            
        except Exception as e:
            print(f"[KNNRecognizer] Extraction error: {e}")
            return None

    def _save_samples(self):
        """Save to JSON."""
        with open(self.samples_file, 'w') as f:
            json.dump(self.training_samples, f)

    def load_samples(self):
        """Load from JSON."""
        if os.path.exists(self.samples_file):
            try:
                with open(self.samples_file, 'r') as f:
                    self.training_samples = json.load(f)
                # print(f"[KNNRecognizer] Loaded {len(self.training_samples)} samples from {self.dataset_name}")
            except Exception as e:
                print(f"[KNNRecognizer] Load error: {e}")
        else:
            self.training_samples = []
