from typing import List, Tuple
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.readers.file import PyMuPDFReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from app.core.config import settings


class Embedder:
    def __init__(self, model_name: str = "nomic-embed-text:v1.5"):
        self.model_name = model_name
        self.embed_model = OllamaEmbedding(
            model_name=model_name, base_url=settings.OLLAMA_URL
        )

    def load_documents(cls, file_path: str) -> List[dict]:
        """
        Load documents from the given file path using PyMuPDFReader.
        """
        reader = PyMuPDFReader()
        return reader.load_data(file_path=file_path)

    def text_splitter(
        self, documents: List[dict], chunk_size: int = 1024, overlap: int = 50
    ) -> Tuple[List[str], List[int]]:
        """
        Split documents into chunks with optional overlap.
        Returns a tuple of text chunks and their document indices.
        """
        splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        split_docs = []
        doc_ids = []

        for doc_id, doc in enumerate(documents):
            chunks = splitter.split_text(doc.text)
            split_docs.extend(chunks)
            doc_ids.extend([doc_id] * len(chunks))

        return split_docs, doc_ids

    def create_text_nodes(
        self,
        text_chunks: List[str],
        documents: List[dict],
        doc_idxs: List[int],
        shared_metadata=None,
    ) -> List[TextNode]:
        """
        Create TextNode objects from text chunks and attach metadata from source documents.
        """
        nodes = []
        for idx, chunk in enumerate(text_chunks):
            metadata = shared_metadata.copy() if shared_metadata else {}
            metadata["chunk_index"] = idx
            node = TextNode(text=chunk, metadata=metadata)
            nodes.append(node)
        return nodes

    def embed_text_nodes(self, nodes: List[TextNode]) -> List[TextNode]:
        """
        Generate and attach embeddings to each TextNode.
        """
        for node in nodes:
            embedding = self.embed_model.get_text_embedding(
                node.get_content()
            )
            node.embedding = embedding
            node.text = node.text.replace("\x00", "") if node.text else node.text
        return nodes

    def embed_query(self, query: str) -> List[float]:
        """
        Generate an embedding vector for a query string.
        """
        return self.embed_model.get_query_embedding(query)
