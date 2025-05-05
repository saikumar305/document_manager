from llama_index.core import VectorStoreIndex
from llama_index.embeddings.ollama import OllamaEmbedding

from llama_index.core.schema import NodeWithScore
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.vector_stores import VectorStoreQuery, MetadataFilters



from typing import List, Optional


from llama_index.core import QueryBundle
from llama_index.core.retrievers import BaseRetriever
from typing import Any, List


class VectorDBRetriever(BaseRetriever):
    """Retriever over a postgres vector store."""

    def __init__(
        self,
        vector_store: PGVectorStore,
        embed_model: OllamaEmbedding,
        query_mode: str = "default",
        similarity_top_k: int = 5,
        filters: Optional[MetadataFilters] = None,
    ) -> None:
        """Init params."""
        self._vector_store = vector_store
        self._embed_model = embed_model
        self._query_mode = query_mode
        self._similarity_top_k = similarity_top_k
        self._filters = filters
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve."""

        query_embedding = self._embed_model.get_query_embedding(query_bundle.query_str)
        vector_store_query = VectorStoreQuery(
            query_embedding=query_embedding,
            similarity_top_k=self._similarity_top_k,
            mode=self._query_mode,
            filters=self._filters,
        )
        query_result = self._vector_store.query(vector_store_query)

        nodes_with_scores = []
        for index, node in enumerate(query_result.nodes):
            score: Optional[float] = None
            if query_result.similarities is not None:
                score = query_result.similarities[index]
            nodes_with_scores.append(NodeWithScore(node=node, score=score))

        return nodes_with_scores


from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever


from llama_index.core.llms import LLM


class Retriever:
    def __init__(
        self,
        vector_store: PGVectorStore,
        top_k: int = 5,
        embed_model: OllamaEmbedding = None,
        llm: LLM = None,
        response_mode: str = "compact",
    ):
        """
        :param response_mode: One of 'refine', 'compact', 'tree_summarize', etc.
        """
        from llama_index.core import Settings

        if embed_model:
            Settings.embed_model = embed_model
        if llm:
            Settings.llm = llm

        self.vector_store = vector_store
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store, storage_context=self.storage_context
        )

        self.retriever = self.index.as_retriever(similarity_top_k=top_k)
        self.response_synthesizer = get_response_synthesizer()

        self.query_engine = RetrieverQueryEngine(
            retriever=self.retriever, response_synthesizer=self.response_synthesizer
        )

    def retrieve(self, query: str) -> List[NodeWithScore]:
        return self.retriever.retrieve(query)

    def query_with_context(self, query: str) -> str:
        response = self.query_engine.query(query)
        return str(response)
