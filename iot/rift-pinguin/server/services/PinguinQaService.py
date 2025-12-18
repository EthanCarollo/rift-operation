import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Tuple, Dict, Any
import re
import time
import random

class PinguinQaService:
    """
    Système de Q&A ultra-rapide basé sur la recherche vectorielle (FAISS + Sentence Transformers).
    Transposé depuis le notebook lab/pinguin/1-qa-test.ipynb.
    """
    
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2', db_path: str = "transcription_db.txt"):
        """
        Initialise le service.
        """
        self.model_name = model_name
        self.db_path = db_path
        self.model = None
        self.index = None
        self.segments = []
        self.is_loaded = False
        
    def load_model(self):
        """
        Charge le modèle d'embeddings et restaure l'historique si présent.
        """
        if self.is_loaded:
            return
            
        print(f"📦 Chargement du modèle de Q&A: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        
        # Restauration de la base de données (fichier texte)
        import os
        if os.path.exists(self.db_path):
            print(f"📂 Restauration de la base de données depuis {self.db_path}...")
            with open(self.db_path, "r", encoding="utf-8") as f:
                history = f.read()
                if history.strip():
                    self.index_transcription(history, save_to_db=False)
        
        self.is_loaded = True
        print("✓ Modèle Q&A chargé!")
        
    def prepare_transcription(self, transcription: str, window_size: int = 1) -> List[str]:
        """
        Découpe la transcription en segments avec contexte.
        """
        # Découpe par phrases (points, points d'interrogation ou d'exclamation)
        sentences = re.split(r'[.!?]+', transcription)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        segments = []
        
        # Crée des segments avec fenêtre de contexte
        for i, sentence in enumerate(sentences):
            context = []
            
            # Ajoute les phrases précédentes
            for j in range(max(0, i - window_size), i):
                context.append(sentences[j])
            
            # Phrase actuelle
            context.append(sentence)
            
            # Ajoute les phrases suivantes
            for j in range(i + 1, min(len(sentences), i + window_size + 1)):
                context.append(sentences[j])
            
            segments.append(' '.join(context))
        
        return segments
    
    def index_transcription(self, transcription: str, window_size: int = 1, save_to_db: bool = True):
        """
        Indexe la transcription pour recherche rapide.
        """
        if not transcription.strip():
            print("⚠️ Transcription vide, rien à indexer.")
            return

        print("🔄 Indexation de la transcription...")
        
        # Sauvegarde dans la base de données si demandé
        if save_to_db:
            with open(self.db_path, "a", encoding="utf-8") as f:
                f.write(transcription + "\n")
            
            # Re-charger tout pour l'indexation (si on veut que l'index contienne TOUT)
            with open(self.db_path, "r", encoding="utf-8") as f:
                full_history = f.read()
            self.segments = self.prepare_transcription(full_history, window_size)
        else:
            self.segments = self.prepare_transcription(transcription, window_size)
        
        if not self.segments:
            return

        # Encodage des segments
        embeddings = self.model.encode(
            self.segments, 
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        # Création de l'index FAISS
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product pour similarité cosinus (sur vecteurs normalisés)
        
        # Normalise pour utiliser la similarité cosinus
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        
        print(f"✓ Indexation terminée! ({self.index.ntotal} vecteurs)")
    
    def search(self, question: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Recherche les segments les plus pertinents.
        """
        if self.index is None:
            return []
        
        # Encode la question
        question_embedding = self.model.encode([question], convert_to_numpy=True)
        faiss.normalize_L2(question_embedding)
        
        # Recherche dans l'index
        scores, indices = self.index.search(question_embedding, top_k)
        
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx != -1: # FAISS renvoie -1 si pas assez de résultats
                results.append((self.segments[idx], float(score)))
        
        return results
    
    def answer(self, question: str, min_confidence: float = 0.3) -> Dict[str, Any]:
        """
        Répond à la question de manière naturelle en cherchant dans l'index.
        """
        start_time = time.time()
        
        results = self.search(question, top_k=1)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        if not results:
            return {
                'answer': "Désolé, je n'ai pas encore assez de contenu à analyser.",
                'confidence': 0.0,
                'time_ms': elapsed_ms
            }
        
        best_match, score = results[0]
        
        if score < min_confidence:
            return {
                'answer': "Hmm, je ne suis pas sûr d'avoir cette information. Peux-tu préciser ?",
                'confidence': score,
                'time_ms': elapsed_ms
            }
        
        answer = self._format_answer(best_match, score)
        
        return {
            'answer': answer,
            'confidence': score,
            'time_ms': elapsed_ms,
            'raw_segment': best_match
        }
    
    def _format_answer(self, text: str, confidence: float) -> str:
        """Ajoute un peu de naturel à la réponse"""
        text = text.strip()
        
        if confidence > 0.8:
            prefixes = ["Voilà : ", "Ah oui ! ", "Exactement : ", ""]
        elif confidence > 0.5:
            prefixes = ["D'après ce que j'ai : ", "Il semblerait que : ", ""]
        else:
            prefixes = ["Je pense que : ", "Peut-être que : "]
        
        prefix = random.choice(prefixes)
        return f"{prefix}{text}"
