import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Tuple, Dict, Any
import re
import time
import random
import os

class PinguinQaService:
    """
    Système de Q&A ultra-rapide basé sur la recherche vectorielle (FAISS + Sentence Transformers).
    Transposé depuis le notebook lab/pinguin/1-qa-test.ipynb.
    """
    
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2', db_path: str = "transcription_db.txt", audio_map_path: str = "audio_map.json"):
        """
        Initialise le service.
        """
        self.model_name = model_name
        self.db_path = db_path
        self.audio_map_path = audio_map_path
        self.model = None
        self.index = None
        self.segments = []
        self.audio_map = {}
        self.is_loaded = False
        
    def load_model(self):
        """
        Charge le modèle d'embeddings et restaure l'historique si présent.
        """
        if self.is_loaded:
            return
            
        print(f"📦 Chargement du modèle de Q&A: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        
        # Chargement de la table de correspondance audio
        import json
        if os.path.exists(self.audio_map_path):
            print(f"🎵 Chargement de la map audio depuis {self.audio_map_path}...")
            with open(self.audio_map_path, "r", encoding="utf-8") as f:
                raw_map = json.load(f)
                # On garde les segments originaux pour l'indexation (pour avoir les majuscules/ponctuation dans la réponse)
                self.segments = list(raw_map.keys())
                # Normalisation des clés pour faciliter la correspondance lors du lookup final si besoin
                self.audio_map = {self.normalize_text(k): v for k, v in raw_map.items()}
            
            # Indexation immédiate des clés
            if self.segments:
                self._build_index()
        
        self.is_loaded = True
        print(f"✓ Modèle Q&A chargé avec {len(self.segments)} clés!")
    
    def normalize_text(self, text: str) -> str:
        """
        Normalise le texte pour la recherche (minuscules, sans ponctuation).
        """
        text = text.lower().strip()
        text = re.sub(r'[.!?,\d]', '', text)
        return text.strip()
    
    def find_exact_match(self, question: str) -> Tuple[str, str] | None:
        """
        Recherche une correspondance avec les stratégies suivantes (par ordre de priorité):
        1. Correspondance exacte après normalisation
        2. Correspondance à 90%+ (fuzzy matching)
        3. Fin de phrase correspondant exactement à une phrase indexée
        
        Utile quand le STT ne met pas de ponctuation ou délire un peu.
        
        Returns:
            Tuple (segment_original, audio_file) si trouvé, None sinon.
        """
        from difflib import SequenceMatcher
        
        normalized_question = self.normalize_text(question)
        
        best_match = None
        best_ratio = 0.0
        
        for original_segment in self.segments:
            normalized_segment = self.normalize_text(original_segment)
            
            # 1. Correspondance exacte
            if normalized_segment == normalized_question:
                print(f"✅ [EXACT] '{question}' == '{original_segment}'")
                return self._get_audio_for_segment(original_segment)
            
            # 2. Correspondance à 90%+ (fuzzy)
            ratio = SequenceMatcher(None, normalized_question, normalized_segment).ratio()
            if ratio >= 0.90 and ratio > best_ratio:
                best_ratio = ratio
                best_match = original_segment
            
            # 3. Fin de phrase correspondant exactement
            # Ex: "blabla blabla C'est quoi la lettre" -> match "C'est quoi la lettre ?"
            if normalized_question.endswith(normalized_segment):
                print(f"✅ [SUFFIX] '{question}' ends with '{original_segment}'")
                return self._get_audio_for_segment(original_segment)
        
        # Retourne le meilleur match fuzzy si trouvé
        if best_match and best_ratio >= 0.90:
            print(f"✅ [FUZZY {best_ratio:.0%}] '{question}' ≈ '{best_match}'")
            return self._get_audio_for_segment(best_match)
        
        return None
    
    def _get_audio_for_segment(self, original_segment: str) -> Tuple[str, str]:
        """
        Récupère le fichier audio associé à un segment.
        """
        norm_key = self.normalize_text(original_segment)
        audio_entry = self.audio_map.get(norm_key)
        
        audio_file = None
        if audio_entry:
            if isinstance(audio_entry, list) and audio_entry:
                audio_file = random.choice(audio_entry)
            elif isinstance(audio_entry, str):
                audio_file = audio_entry
        
        return (original_segment, audio_file)
        
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
    
    def _build_index(self):
        """
        Construit l'index FAISS à partir de self.segments.
        """
        if not self.segments:
            return

        print(f"🔄 Indexation de {len(self.segments)} clés...")
        
        # Encodage des segments
        embeddings = self.model.encode(
            self.segments, 
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        # Création de l'index FAISS
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        
        # Normalise pour utiliser la similarité cosinus
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        
        print("✓ Indexation terminée!")

    def index_transcription(self, transcription: str, window_size: int = 0, save_to_db: bool = True):
        """
        DEPRECATED: L'indexation se fait désormais via audio_map.json.
        """
        pass
    
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
        
        # --- [FAST PATH] Vérification de correspondance exacte (sans ponctuation) ---
        # Utile quand le STT ne met pas de ponctuation mais dit exactement la bonne phrase.
        exact_match = self.find_exact_match(question)
        if exact_match:
            original_segment, audio_file = exact_match
            elapsed_ms = (time.time() - start_time) * 1000
            print(f"✅ [EXACT MATCH] '{question}' → '{original_segment}'")
            
            # Vérification de l'existence du fichier sur le disque
            if audio_file:
                audio_path = os.path.join("audio", audio_file)
                if not os.path.exists(audio_path):
                    print(f"⚠️ Fichier audio introuvable sur le disque : {audio_path}")
                    audio_file = None
            
            return {
                'answer': self._format_answer(original_segment, 1.0),
                'confidence': 1.0,
                'time_ms': elapsed_ms,
                'raw_segment': original_segment,
                'audio_file': audio_file
            }
        # -------------------------------------------------------------------------------
        
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
        
        # --- [AMÉLIORATION] Vérification des mots-clés (Noms) ---
        # Si la question contient des mots spécifiques (en majuscules ou clés),
        # on vérifie si le segment choisi les contient bien.
        words_in_question = [w.strip("?,!").lower() for w in question.split() if len(w) > 2]
        
        # On recherche d'autres résultats si le premier ne contient pas un nom important
        important_keywords = [w for w in question.split() if w[0].isupper() and len(w) > 1]
        
        if important_keywords:
            results_top3 = self.search(question, top_k=5)
            for seg, sc in results_top3:
                if any(name.lower() in seg.lower() for name in important_keywords):
                    best_match = seg
                    score = sc
                    break
        # -------------------------------------------------------
        
        answer = self._format_answer(best_match, score)
        
        # Recherche du fichier audio associé (clé normalisée)
        norm_match = self.normalize_text(best_match)
        print(f"🔍 [DEBUG] Normalized match key: '{norm_match}'")
        
        audio_entry = self.audio_map.get(norm_match)
        if not audio_entry:
            print(f"⚠️ [DEBUG] No audio entry found for '{norm_match}'. Available keys: {list(self.audio_map.keys())[:3]}...")

        audio_file = None
        
        if audio_entry:
            if isinstance(audio_entry, list) and audio_entry:
                audio_file = random.choice(audio_entry)
            elif isinstance(audio_entry, str):
                audio_file = audio_entry
        
        # Vérification de l'existence du fichier sur le disque
        if audio_file:
            audio_path = os.path.join("audio", audio_file)
            if not os.path.exists(audio_path):
                print(f"⚠️ Fichier audio introuvable sur le disque : {audio_path}")
                audio_file = None
        
        return {
            'answer': answer,
            'confidence': score,
            'time_ms': elapsed_ms,
            'raw_segment': best_match,
            'audio_file': audio_file
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
