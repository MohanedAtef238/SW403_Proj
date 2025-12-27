from langchain_huggingface import HuggingFaceEmbeddings
from torch import cosine_similarity

from src.agents.rag_agent import create_rag_agent
from src.api.models import ChunkingStrategy
from src.chunking import get_chunker
from src.chunking.base import BaseChunker
from src.config import settings
from src.retrieval.pipeline import RetrievalPipeline


class SelfCheckGPT:
    def __init__(
        self, chunker: BaseChunker | None = None, temp_reducing_factor: float = 0.2
    ):
        # Initialize embeddings
        self.chunker = chunker or get_chunker(settings.CHUNKING_STRATEGY)
        self.temp = settings.LLM_TEMPERATURE - temp_reducing_factor

        self.embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
        pipeline = RetrievalPipeline(chunker=chunker)
        retrieval_tool = pipeline.create_retrieval_tool()
        self.agent = create_rag_agent(tools=[retrieval_tool], temp=self.temp)

    def check(
        self,
        query: str,
        inital_response: str,
        strategy: ChunkingStrategy,
        k: int = 3,
    ):
        sampled_response, _ = self.query_with_agent(query, strategy, k, temp=self.temp)
        sample_embed, inital_embed = self.embeddings.embed_documents(
            [sampled_response, inital_response]
        )
        similarity = cosine_similarity(sample_embed, inital_embed)
        hallucinating = True if similarity[0] > 0.5 else False
        return similarity, hallucinating
