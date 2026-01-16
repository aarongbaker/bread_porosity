"""
Simple ML Module for Bread Quality Classification
Allows training on user-labeled images to classify new bread as Good/Problem
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TrainingImage:
    """A labeled training image"""
    path: str
    label: str  # "good" or "problem"
    features: List[float]
    timestamp: str


class SimpleMLClassifier:
    """
    Simple ML classifier for bread quality
    Builds training dataset and classifies new images
    """
    
    def __init__(self, model_dir: str = "./ml_models", verbose: bool = True):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.verbose = verbose
        self.training_data: List[TrainingImage] = []
        self.model_stats = None
        self._load_training_data()
    
    def extract_features(self, image_path: str) -> List[float]:
        """
        Extract simple features from bread image
        
        Args:
            image_path: Path to image
            
        Returns:
            Feature vector (11 features)
        """
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        # Feature 1: Mean brightness
        mean_brightness = np.mean(gray)
        
        # Feature 2: Brightness std dev (uniformity)
        brightness_std = np.std(gray)
        
        # Feature 3: Brightness skewness (distribution shape)
        brightness_flat = gray.flatten()
        brightness_skew = (np.mean((brightness_flat - mean_brightness) ** 3)) / (brightness_std ** 3) if brightness_std > 0 else 0
        
        # Feature 4: Edge detection (crumb structure)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (h * w)
        
        # Feature 5-7: Histogram features (dark/mid/bright pixel ratios)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten() / np.sum(hist)
        dark_ratio = np.sum(hist[:85])  # 0-85 (dark)
        mid_ratio = np.sum(hist[85:170])  # 85-170 (mid)
        bright_ratio = np.sum(hist[170:])  # 170-255 (bright)
        
        # Feature 8: Porosity estimate (hole density)
        threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        holes = cv2.countNonZero(threshold)
        porosity = holes / (h * w)
        
        # Feature 9: Local variance (crumb uniformity)
        local_var = np.std([gray[i:i+10, j:j+10].std() 
                          for i in range(0, h-10, 20) 
                          for j in range(0, w-10, 20)])
        
        # Feature 10: Contrast (using Laplacian)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        contrast = np.std(laplacian)
        
        # Feature 11: Center brightness (higher = better rise)
        center_region = gray[h//4:3*h//4, w//4:3*w//4]
        center_brightness = np.mean(center_region)
        
        features = [
            mean_brightness / 255,  # Normalize to 0-1
            brightness_std / 255,
            brightness_skew,
            edge_density,
            dark_ratio,
            mid_ratio,
            bright_ratio,
            porosity,
            local_var / 255,
            contrast / 255,
            center_brightness / 255
        ]
        
        return features
    
    def add_training_image(self, image_path: str, label: str) -> bool:
        """
        Add labeled image to training dataset
        
        Args:
            image_path: Path to image
            label: "good" or "problem"
            
        Returns:
            True if successful
        """
        if label not in ["good", "problem"]:
            print(f"Invalid label: {label}. Use 'good' or 'problem'")
            return False
        
        features = self.extract_features(image_path)
        if features is None:
            print(f"Could not read image: {image_path}")
            return False
        
        training_img = TrainingImage(
            path=str(image_path),
            label=label,
            features=features,
            timestamp=datetime.now().isoformat()
        )
        
        self.training_data.append(training_img)
        
        if self.verbose:
            print(f"Added training image: {Path(image_path).name} ({label})")
        
        self._save_training_data()
        return True
    
    def train(self) -> Dict[str, Any]:
        """
        Train classifier on current training data
        
        Returns:
            Training statistics
        """
        if len(self.training_data) < 2:
            print("Need at least 2 training images (1 good, 1 problem)")
            return None
        
        good_features = np.array([img.features for img in self.training_data if img.label == "good"])
        problem_features = np.array([img.features for img in self.training_data if img.label == "problem"])
        
        if len(good_features) == 0 or len(problem_features) == 0:
            print("Need at least one 'good' and one 'problem' image")
            return None
        
        # Calculate class statistics
        good_mean = np.mean(good_features, axis=0)
        good_std = np.std(good_features, axis=0)
        problem_mean = np.mean(problem_features, axis=0)
        problem_std = np.std(problem_features, axis=0)
        
        self.model_stats = {
            'good': {
                'mean': good_mean.tolist(),
                'std': good_std.tolist(),
                'count': len(good_features)
            },
            'problem': {
                'mean': problem_mean.tolist(),
                'std': problem_std.tolist(),
                'count': len(problem_features)
            },
            'trained': True,
            'timestamp': datetime.now().isoformat()
        }
        
        self._save_model()
        
        if self.verbose:
            print(f"Model trained: {len(good_features)} good, {len(problem_features)} problem")
        
        return {
            'good_count': len(good_features),
            'problem_count': len(problem_features),
            'total_training_images': len(self.training_data),
            'model_ready': True
        }
    
    def predict(self, image_path: str) -> Dict[str, Any]:
        """
        Classify bread image as good or problem
        
        Args:
            image_path: Path to image
            
        Returns:
            Prediction result
        """
        if self.model_stats is None or not self.model_stats.get('trained'):
            return {'error': 'Model not trained. Add training images and call train()'}
        
        features = self.extract_features(image_path)
        if features is None:
            return {'error': f'Could not read image: {image_path}'}
        
        features = np.array(features)
        
        # Simple Euclidean distance classifier
        good_mean = np.array(self.model_stats['good']['mean'])
        problem_mean = np.array(self.model_stats['problem']['mean'])
        
        dist_to_good = np.linalg.norm(features - good_mean)
        dist_to_problem = np.linalg.norm(features - problem_mean)
        
        # Confidence: inverse of distances
        total_dist = dist_to_good + dist_to_problem
        confidence_good = (1 - dist_to_good / total_dist) * 100 if total_dist > 0 else 50
        confidence_problem = (1 - dist_to_problem / total_dist) * 100 if total_dist > 0 else 50
        
        prediction = "good" if dist_to_good < dist_to_problem else "problem"
        confidence = max(confidence_good, confidence_problem)
        
        result = {
            'image_path': str(image_path),
            'prediction': prediction,
            'confidence': float(confidence),
            'distance_to_good': float(dist_to_good),
            'distance_to_problem': float(dist_to_problem),
            'confidence_good': float(confidence_good),
            'confidence_problem': float(confidence_problem)
        }
        
        if self.verbose:
            print(f"Prediction: {prediction} ({confidence:.0f}% confidence)")
        
        return result
    
    def batch_predict(self, image_dir: str) -> Dict[str, Any]:
        """Predict on batch of images"""
        image_dir = Path(image_dir)
        results = []
        
        for image_file in sorted(image_dir.glob('*.jpg')) + sorted(image_dir.glob('*.png')):
            result = self.predict(str(image_file))
            if 'error' not in result:
                results.append(result)
        
        if not results:
            return {'error': 'No images found'}
        
        good_count = sum(1 for r in results if r['prediction'] == 'good')
        problem_count = sum(1 for r in results if r['prediction'] == 'problem')
        avg_confidence = np.mean([r['confidence'] for r in results])
        
        return {
            'num_images': len(results),
            'good_count': good_count,
            'problem_count': problem_count,
            'pass_rate': (good_count / len(results)) * 100,
            'avg_confidence': float(avg_confidence),
            'results': results
        }
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get status of training data and model"""
        good_count = sum(1 for img in self.training_data if img.label == "good")
        problem_count = sum(1 for img in self.training_data if img.label == "problem")
        
        return {
            'total_training_images': len(self.training_data),
            'good_images': good_count,
            'problem_images': problem_count,
            'model_trained': self.model_stats is not None and self.model_stats.get('trained', False),
            'ready_to_train': len(self.training_data) >= 2 and good_count > 0 and problem_count > 0
        }
    
    def _save_training_data(self):
        """Save training data to file"""
        training_file = self.model_dir / "training_data.json"
        data = [asdict(img) for img in self.training_data]
        with open(training_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_training_data(self):
        """Load training data from file"""
        training_file = self.model_dir / "training_data.json"
        if training_file.exists():
            with open(training_file, 'r') as f:
                data = json.load(f)
                self.training_data = [TrainingImage(**item) for item in data]
    
    def _save_model(self):
        """Save trained model to file"""
        model_file = self.model_dir / "model_stats.json"
        with open(model_file, 'w') as f:
            json.dump(self.model_stats, f, indent=2)
        
        if self.verbose:
            print(f"Model saved to {model_file}")
    
    def _load_model(self):
        """Load trained model from file"""
        model_file = self.model_dir / "model_stats.json"
        if model_file.exists():
            with open(model_file, 'r') as f:
                self.model_stats = json.load(f)


def demo_simple_ml():
    """Demonstrate simple ML classifier"""
    print("Simple ML Classifier for Bread Quality")
    print("=" * 50)
    print("Usage:")
    print("  from ml_simple import SimpleMLClassifier")
    print()
    print("  classifier = SimpleMLClassifier()")
    print()
    print("  # Add training images")
    print("  classifier.add_training_image('good_bread_1.jpg', 'good')")
    print("  classifier.add_training_image('problem_bread_1.jpg', 'problem')")
    print()
    print("  # Train model")
    print("  classifier.train()")
    print()
    print("  # Make predictions")
    print("  result = classifier.predict('new_bread.jpg')")
    print("  print(result['prediction'])  # 'good' or 'problem'")
    print("  print(result['confidence'])  # 0-100")


if __name__ == "__main__":
    demo_simple_ml()
