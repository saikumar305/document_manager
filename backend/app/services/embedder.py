from llama_index.embeddings.ollama import OllamaEmbedding
from typing import List, Optional

from llama_index.readers.file import PyMuPDFReader
from llama_index.core.node_parser import SentenceSplitter


def load_documents(file_path : str) -> List[dict]:
    """
    Load documents from a file path.
    """
    reader = PyMuPDFReader()
    documents = reader.load_data(file_path=file_path)
    return documents

def text_splitter(documents : List[dict], chunk_size: int = 1024, overlap= 50) -> List[str]:
    """
    Split documents into smaller chunks.
    """
    splitter = SentenceSplitter(chunk_size=chunk_size, overlap=overlap)
    split_docs = []
    doc_ids = []
    for doc_id, doc in enumerate(documents):
        cur_text_chunks = splitter.split_text(doc.text)
        split_docs.extend(cur_text_chunks)
        doc_ids.extend([doc_id] * len(cur_text_chunks))
    return split_docs , doc_ids

def create_text_nodes(text_chunks: List[str], documents: List[dict], doc_idxs: List[int]) -> List[dict]:
    from llama_index.core.schema import TextNode

    nodes = []
    for idx, text_chunk in enumerate(text_chunks):
        node = TextNode(
            text=text_chunk,
        )
        src_doc = documents[doc_idxs[idx]]
        node.metadata = src_doc.metadata
        nodes.append(node)

    return nodes

def embed_text_nodes(nodes: List[dict], embed_model) -> List[dict]:
    for node in nodes:
        node_embedding = embed_model.get_text_embedding(
            node.get_content(metadata_mode="all")
        )
        node.embedding = node_embedding

    return nodes

def embed_query(query: str, embed_model: OllamaEmbedding) -> List[float]:
    return embed_model.get_query_embedding(query)


