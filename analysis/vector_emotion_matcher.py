import json
import os
import numpy as np
from typing import Dict, List

class VectorEmotionMatcher:
    def __init__(self, vector_library_path: str = 'assets/emotion_vectors.json'):
        self.library = {}
        self.vector_keys = []
        self.load_library(vector_library_path)

    def load_library(self, path: str):
        print(f"[DEBUG] VectorEmotionMatcher loading from: {os.path.abspath(path)}")
        if os.path.exists(path):
            with open(path, 'r') as f:
                raw_data = json.load(f)
                
            # Collect all unique blendshape names present in the library
            all_keys = set()
            for emotion, traits in raw_data.items():
                if emotion.startswith("_") or not isinstance(traits, dict): 
                    continue
                # Only include keys that don't start with _ (metadata/comments)
                all_keys.update([k for k in traits.keys() if not k.startswith("_")])
            
            self.vector_keys = sorted(list(all_keys))
            print(f"[DEBUG] Vector Keys: {self.vector_keys}")
            
            # Convert library entries into fixed-length vectors
            for emotion, traits in raw_data.items():
                if emotion.startswith("_") or not isinstance(traits, dict):
                    continue
                
                # Force strictly numerical values and ignore strings
                vals = []
                for key in self.vector_keys:
                    val = traits.get(key, 0.0)
                    try:
                        vals.append(float(val))
                    except (ValueError, TypeError):
                        vals.append(0.0)
                
                vec = np.array(vals)
                # Normalize vector to unit length for cosine similarity
                norm = np.linalg.norm(vec)
                self.library[emotion] = vec / norm if norm > 0 else vec
            print(f"[DEBUG] Successfully loaded {len(self.library)} emotions.")

    def match(self, live_blendshapes: Dict[str, float]) -> Dict[str, any]:
        if not self.library:
            return {'emotion': 'neutral', 'confidence': 100.0, 'is_stable': True}

        # Convert live input to fixed-length vector
        live_vec = np.array([live_blendshapes.get(key, 0.0) for key in self.vector_keys])
        live_norm = np.linalg.norm(live_vec)
        
        if live_norm < 0.05: # Very low activity = Neutral
            return {'emotion': 'neutral', 'confidence': 100.0, 'is_stable': True, 'probs': {e: 0.0 for e in self.library}}

        live_vec_norm = live_vec / live_norm
        
        # Calculate Cosine Similarity against all library emotions
        similarities = {}
        for emotion, ref_vec in self.library.items():
            sim = np.dot(live_vec_norm, ref_vec)
            similarities[emotion] = float(max(0, sim)) # Clamp to positive
            
        # Find best match
        best_emotion = max(similarities, key=similarities.get)
        confidence = similarities[best_emotion] * 100.0
        
        return {
            'current_emotion': best_emotion,
            'confidence': confidence,
            'probs': similarities,
            'is_stable': confidence > 65.0,
            'raw_vector': live_vec.tolist()
        }
