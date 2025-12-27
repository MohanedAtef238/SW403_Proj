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
        """
        Initialize the SelfCheckGPT retrieval system.
        Args:
            chunker (BaseChunker | None, optional): Custom text chunker for document processing.
                If None, uses the chunker specified in settings.CHUNKING_STRATEGY. Defaults to None.
            temp_reducing_factor (float, optional): Factor to reduce the LLM temperature by.
                Subtracted from settings.LLM_TEMPERATURE to control response randomness.
                Defaults to 0.2.
        Raises:
            ValueError: If the embedding model specified in settings is unavailable.
        """
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
    )-> tuple[float, bool]:
        """
            Check if a response contains hallucinations by comparing it with a sampled response.
            
            Uses the SelfCheckGPT approach: generates a new response to the same query and
            computes cosine similarity between embeddings. If similarity is below threshold,
            the initial response is likely hallucinating.
            
            Args:
                query: The original user query.
                inital_response: The initial response to be checked for hallucinations.
                strategy: The chunking strategy to use for query processing.
                k: Number of chunks to retrieve (default: 3).
            
            Returns:
                tuple: A tuple containing:
                    - similarity (float): Cosine similarity score between the sampled and initial responses.
                    - hallucinating (bool): True if hallucination detected (similarity <= 0.5), False otherwise.
            """
        sampled_response, _ = self.query_with_agent(query, strategy, k, temp=self.temp)
        sample_embed, inital_embed = self.embeddings.embed_documents(
            [sampled_response, inital_response]
        )
        similarity = cosine_similarity(sample_embed, inital_embed)
        hallucinating = True if similarity[0] > 0.5 else False
        return similarity, hallucinating
