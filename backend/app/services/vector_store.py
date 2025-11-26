"""
Vector Store Service using FAISS for similarity search.
Stores document embeddings and enables RAG pipeline.
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss

from backend.app.utils.logger import init_logger
from backend.app.services.document_parser import DocumentChunk
from backend.app.services.bedrock_client import get_bedrock_client

# Initialize logger
logger = init_logger()


class VectorStore:
    """FAISS-based vector store for document embeddings"""

    def __init__(
        self,
        store_path: str,
        collection_name: str = "qa_documents",
        embedding_dimension: int = 1024
    ):
        """
        Initialize vector store

        Args:
            store_path: Path to store vector database files
            collection_name: Name of the collection
            embedding_dimension: Dimension of embedding vectors
        """
        self.store_path = Path(store_path)
        self.collection_name = collection_name
        self.embedding_dimension = embedding_dimension

        # Create store directory
        self.store_path.mkdir(parents=True, exist_ok=True)

        # File paths
        self.index_file = self.store_path / f"{collection_name}_index.faiss"
        self.metadata_file = self.store_path / f"{collection_name}_metadata.pkl"
        self.config_file = self.store_path / f"{collection_name}_config.json"

        # Initialize FAISS index
        self.index: Optional[faiss.IndexFlatL2] = None
        self.metadata: List[Dict[str, Any]] = []

        # Get Bedrock client
        self.bedrock_client = get_bedrock_client()

        # Load existing index if available
        self._load_or_create_index()

        logger.info(
            "VectorStore initialized",
            extra={
                "store_path": str(self.store_path),
                "collection_name": collection_name,
                "embedding_dimension": embedding_dimension,
                "documents": len(self.metadata)
            }
        )

    def _load_or_create_index(self):
        """Load existing index or create new one"""
        if self.index_file.exists() and self.metadata_file.exists():
            logger.info(f"Loading existing vector store from {self.store_path}")
            self._load_index()
        else:
            logger.info("Creating new vector store")
            self._create_index()

    def _create_index(self):
        """Create new FAISS index"""
        logger.debug("Creating new FAISS index")

        # Create L2 distance index (cosine similarity via normalization)
        self.index = faiss.IndexFlatL2(self.embedding_dimension)
        self.metadata = []

        logger.debug("New FAISS index created")

    def _load_index(self):
        """Load existing FAISS index and metadata"""
        logger.debug("Loading FAISS index from disk")

        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_file))

            # Load metadata
            with open(self.metadata_file, 'rb') as f:
                self.metadata = pickle.load(f)

            logger.info(
                "Vector store loaded successfully",
                extra={
                    "documents": len(self.metadata),
                    "index_size": self.index.ntotal
                }
            )

        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            logger.info("Creating new index instead")
            self._create_index()

    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        logger.debug("Saving FAISS index to disk")

        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_file))

            # Save metadata
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)

            # Save config
            config = {
                "collection_name": self.collection_name,
                "embedding_dimension": self.embedding_dimension,
                "num_documents": len(self.metadata)
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

            logger.debug("Vector store saved successfully")

        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            raise

    def add_documents(
        self,
        chunks: List[DocumentChunk],
        batch_size: int = 10
    ) -> int:
        """
        Add document chunks to vector store

        Args:
            chunks: List of DocumentChunk objects
            batch_size: Batch size for embedding generation

        Returns:
            Number of documents added
        """
        logger.info(f"Adding {len(chunks)} documents to vector store")

        logger.log_function_call(
            "add_documents",
            args={"num_chunks": len(chunks), "batch_size": batch_size},
            status="started"
        )

        try:
            if not chunks:
                logger.warning("No chunks provided")
                return 0

            # Extract texts
            texts = [chunk.text for chunk in chunks]

            # Generate embeddings in batches
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                logger.debug(f"Generating embeddings for batch {i // batch_size + 1}")

                embeddings = self.bedrock_client.generate_embeddings(
                    batch_texts,
                    input_type="search_document"
                )

                all_embeddings.extend(embeddings)

            # Convert to numpy array
            embeddings_array = np.array(all_embeddings, dtype='float32')

            # Normalize vectors for cosine similarity (optional but recommended)
            faiss.normalize_L2(embeddings_array)

            # Add to FAISS index
            self.index.add(embeddings_array)

            # Add metadata
            for chunk in chunks:
                self.metadata.append(chunk.to_dict())

            # Save to disk
            self._save_index()

            logger.log_vector_db_operation(
                operation="add_documents",
                collection=self.collection_name,
                documents=len(chunks),
                status="success"
            )

            logger.log_function_call(
                "add_documents",
                args={"num_chunks": len(chunks)},
                status="completed"
            )

            return len(chunks)

        except Exception as e:
            logger.log_function_call(
                "add_documents",
                args={"num_chunks": len(chunks)},
                status="failed"
            )
            logger.exception("Error adding documents to vector store")
            raise

    def search(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of matching documents with scores
        """
        logger.info(f"Searching vector store with query: {query[:100]}...")

        logger.log_function_call(
            "search",
            args={"query_length": len(query), "top_k": top_k},
            status="started"
        )

        try:
            if self.index.ntotal == 0:
                logger.warning("Vector store is empty")
                return []

            # Generate query embedding
            query_embedding = self.bedrock_client.generate_query_embedding(query)

            # Convert to numpy array and reshape
            query_vector = np.array([query_embedding], dtype='float32')

            # Normalize for cosine similarity
            faiss.normalize_L2(query_vector)

            # Search
            distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))

            # Prepare results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < len(self.metadata):
                    result = self.metadata[idx].copy()
                    result['score'] = float(dist)
                    result['similarity'] = 1 / (1 + float(dist))  # Convert distance to similarity
                    results.append(result)

            logger.info(
                f"Search completed, found {len(results)} results",
                extra={"top_score": results[0]['score'] if results else None}
            )

            logger.log_function_call(
                "search",
                args={"query_length": len(query), "results": len(results)},
                status="completed"
            )

            return results

        except Exception as e:
            logger.log_function_call(
                "search",
                status="failed"
            )
            logger.exception("Error searching vector store")
            raise

    def clear(self):
        """Clear all documents from vector store"""
        logger.warning("Clearing vector store")

        try:
            self._create_index()
            self._save_index()

            logger.log_vector_db_operation(
                operation="clear",
                collection=self.collection_name,
                status="success"
            )

        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            "collection_name": self.collection_name,
            "num_documents": len(self.metadata),
            "index_size": self.index.ntotal if self.index else 0,
            "embedding_dimension": self.embedding_dimension,
            "store_path": str(self.store_path)
        }

    def build_knowledge_base(
        self,
        file_paths: List[str],
        clear_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Build knowledge base from multiple files

        Args:
            file_paths: List of file paths to process
            clear_existing: Whether to clear existing data

        Returns:
            Statistics about the build process
        """
        logger.info(
            f"Building knowledge base from {len(file_paths)} files",
            extra={"clear_existing": clear_existing}
        )

        logger.log_function_call(
            "build_knowledge_base",
            args={"num_files": len(file_paths), "clear_existing": clear_existing},
            status="started"
        )

        try:
            # Clear existing if requested
            if clear_existing:
                logger.info("Clearing existing knowledge base")
                self.clear()

            # Parse documents
            from backend.app.services.document_parser import get_document_parser

            parser = get_document_parser()
            chunks = parser.parse_multiple_files(file_paths)

            if not chunks:
                logger.warning("No chunks extracted from files")
                return {
                    "success": False,
                    "message": "No content extracted from files",
                    "files_processed": 0,
                    "chunks_created": 0
                }

            # Add to vector store
            num_added = self.add_documents(chunks)

            stats = {
                "success": True,
                "message": "Knowledge base built successfully",
                "files_processed": len(file_paths),
                "chunks_created": len(chunks),
                "documents_added": num_added,
                **self.get_stats()
            }

            logger.info(
                "Knowledge base built successfully",
                extra=stats
            )

            logger.log_function_call(
                "build_knowledge_base",
                args={"files": len(file_paths), "chunks": len(chunks)},
                status="completed"
            )

            return stats

        except Exception as e:
            logger.log_function_call(
                "build_knowledge_base",
                status="failed"
            )
            logger.exception("Error building knowledge base")
            raise


# Global instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """Get or create global vector store instance"""
    global _vector_store
    if _vector_store is None:
        from backend.config import settings

        _vector_store = VectorStore(
            store_path=settings.vector_db_path,
            collection_name=settings.vector_db_collection_name,
            embedding_dimension=settings.embedding_dimensions
        )
    return _vector_store
