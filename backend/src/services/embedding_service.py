"""Embedding service for generating and managing text embeddings with ChromaDB."""

import logging
from typing import List, Dict, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings

from src.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings and managing vector storage."""
    
    def __init__(self):
        """Initialize the embedding model and ChromaDB client."""
        self._model = None
        self._chroma_client = None
        
    def initialize(self):
        """Initialize the embedding model and ChromaDB client."""
        try:
            # Initialize sentence transformer model
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info("Embedding model loaded successfully")
            
            # Initialize ChromaDB client with persistence
            logger.info(f"Initializing ChromaDB at: {settings.CHROMA_PERSIST_DIR}")
            self._chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            raise
    
    @property
    def model(self) -> SentenceTransformer:
        """Get the embedding model instance."""
        if self._model is None:
            raise RuntimeError("Embedding service not initialized. Call initialize() first.")
        return self._model
    
    @property
    def chroma_client(self) -> chromadb.PersistentClient:
        """Get the ChromaDB client instance."""
        if self._chroma_client is None:
            raise RuntimeError("Embedding service not initialized. Call initialize() first.")
        return self._chroma_client
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            List[float]: Normalized embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).
        
        Args:
            texts: List of input texts
            
        Returns:
            List[List[float]]: List of normalized embedding vectors
        """
        if not texts:
            return []
        
        embeddings = self.model.encode(texts, normalize_embeddings=True, batch_size=32)
        return embeddings.tolist()
    
    def get_collection_name(self, user_id: int) -> str:
        """
        Get the ChromaDB collection name for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            str: Collection name
        """
        return f"{settings.CHROMA_COLLECTION_PREFIX}_user_{user_id}"
    
    def get_or_create_collection(self, user_id: int):
        """
        Get or create a ChromaDB collection for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Collection: ChromaDB collection
        """
        collection_name = self.get_collection_name(user_id)
        
        try:
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"user_id": str(user_id)}
            )
            return collection
        except Exception as e:
            logger.error(f"Failed to get/create collection for user {user_id}: {e}")
            raise
    
    def store_entity_embedding(self, user_id: int, entity_id: int, text: str, metadata: Optional[Dict] = None):
        """
        Generate and store embedding for an entity.
        
        Args:
            user_id: User ID
            entity_id: Entity ID (6-digit)
            text: Text to embed
            metadata: Optional metadata to store with embedding
        """
        if not text or not text.strip():
            logger.warning(f"Empty text for entity {entity_id}, skipping embedding")
            return
        
        try:
            # Generate embedding
            embedding = self.generate_embedding(text)
            
            # Get user's collection
            collection = self.get_or_create_collection(user_id)
            
            # Store in ChromaDB
            collection.add(
                ids=[str(entity_id)],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata or {}]
            )
            
            logger.info(f"Stored embedding for entity {entity_id} in user {user_id}'s collection")
            
        except Exception as e:
            logger.error(f"Failed to store embedding for entity {entity_id}: {e}")
            raise
    
    def update_entity_embedding(self, user_id: int, entity_id: int, text: str, metadata: Optional[Dict] = None):
        """
        Update embedding for an entity.
        
        Args:
            user_id: User ID
            entity_id: Entity ID
            text: Updated text
            metadata: Updated metadata
        """
        if not text or not text.strip():
            logger.warning(f"Empty text for entity {entity_id}, skipping update")
            return
        
        try:
            # Generate new embedding
            embedding = self.generate_embedding(text)
            
            # Get user's collection
            collection = self.get_or_create_collection(user_id)
            
            # Update in ChromaDB
            collection.update(
                ids=[str(entity_id)],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata or {}]
            )
            
            logger.info(f"Updated embedding for entity {entity_id}")
            
        except Exception as e:
            logger.error(f"Failed to update embedding for entity {entity_id}: {e}")
            raise
    
    def delete_entity_embedding(self, user_id: int, entity_id: int):
        """
        Delete embedding for an entity.
        
        Args:
            user_id: User ID
            entity_id: Entity ID
        """
        try:
            collection = self.get_or_create_collection(user_id)
            collection.delete(ids=[str(entity_id)])
            logger.info(f"Deleted embedding for entity {entity_id}")
        except Exception as e:
            logger.error(f"Failed to delete embedding for entity {entity_id}: {e}")
            raise
    
    def search_similar_entities(
        self, 
        user_id: int, 
        query: str, 
        limit: int = 10,
        min_score: float = 0.5
    ) -> List[Tuple[int, float, str]]:
        """
        Search for similar entities using semantic search.
        
        Args:
            user_id: User ID
            query: Search query text
            limit: Maximum number of results
            min_score: Minimum similarity score (0-1)
            
        Returns:
            List[Tuple[int, float, str]]: List of (entity_id, similarity_score, text)
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Get user's collection
            collection = self.get_or_create_collection(user_id)
            
            # Search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            
            # Parse results
            similar_entities = []
            if results['ids'] and results['ids'][0]:
                for i, entity_id_str in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i] if 'distances' in results else 0
                    # Convert distance to similarity score (cosine similarity)
                    # ChromaDB returns squared L2 distance, convert to cosine similarity
                    similarity = 1 - (distance / 2)
                    
                    if similarity >= min_score:
                        entity_id = int(entity_id_str)
                        document = results['documents'][0][i] if 'documents' in results else ""
                        similar_entities.append((entity_id, similarity, document))
            
            logger.info(f"Found {len(similar_entities)} similar entities for user {user_id}")
            return similar_entities
            
        except Exception as e:
            logger.error(f"Failed to search similar entities: {e}")
            raise
    
    def delete_user_collection(self, user_id: int):
        """
        Delete all embeddings for a user.
        
        Args:
            user_id: User ID
        """
        try:
            collection_name = self.get_collection_name(user_id)
            self.chroma_client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to delete collection for user {user_id}: {e}")
            raise


# Global embedding service instance
embedding_service = EmbeddingService()
