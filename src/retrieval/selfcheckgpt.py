import torch
import torch.nn.functional as F
from langchain_huggingface import HuggingFaceEmbeddings

from src.agents.rag_agent import create_rag_agent, run_agent
from src.api.models import ChunkingStrategy
from src.chunking import get_chunker
from src.chunking.base import BaseChunker
from src.config import settings
from src.retrieval.pipeline import RetrievalPipeline


class SelfCheckGPT:
    def __init__(
        self,
        chunker: BaseChunker | None = None,
        temp_reducing_factor: float = 0.2,
        k: int = 3,
        system_prompt: str | None = None,
    ):
        """
        Initialize the SelfCheckGPT retrieval system.
        Args:
            chunker (BaseChunker | None, optional): Custom text chunker for document processing.
                If None, uses the chunker specified in settings.CHUNKING_STRATEGY. Defaults to None.
            temp_reducing_factor (float, optional): Factor to reduce the LLM temperature by.
                Subtracted from settings.LLM_TEMPERATURE to control response randomness.
                Defaults to 0.2.
            k (int, optional): number of relevent docs to include
            system_prompt (str, optional): System prompt for the agent
        Raises:
            ValueError: If the embedding model specified in settings is unavailable.
        """
        # Initialize embeddings
        self.chunker = chunker or get_chunker(settings.CHUNKING_STRATEGY)
        self.temp = min (1, settings.LLM_TEMPERATURE + temp_reducing_factor)
        self.k = k
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
        self.system_prompt = system_prompt

    def is_hallucinating(self, query: str, inital_response: str) -> tuple[float, bool]:
        """
        Check if a response contains hallucinations by comparing it with a sampled response.

        Uses the SelfCheckGPT approach: generates a new response to the same query and
        computes cosine similarity between embeddings. If similarity is below threshold,
        the initial response is likely hallucinating.

        Args:
            query: The original user query.
            inital_response: The initial response to be checked for hallucinations.

        Returns:
            tuple: A tuple containing:
                - similarity (float): Cosine similarity score between the sampled and initial responses.
                - hallucinating (bool): True if hallucination detected (similarity <= 0.5), False otherwise.
        """
        original_k = settings.RETRIEVAL_K
        settings.RETRIEVAL_K = self.k

        pipeline = RetrievalPipeline(chunker=self.chunker)
        retrieval_tool = pipeline.create_retrieval_tool()

        agent = create_rag_agent(
            tools=[retrieval_tool], temp=self.temp, system_prompt=self.system_prompt
        )

        sampled_response = run_agent(agent, query, stream=False)

        settings.RETRIEVAL_K = original_k

        sample_embed, inital_embed = self.embeddings.embed_documents(
            [sampled_response, inital_response]
        )

        sample_tensor = torch.tensor(sample_embed).unsqueeze(0)
        inital_tensor = torch.tensor(inital_embed).unsqueeze(0)
        similarity = F.cosine_similarity(sample_tensor, inital_tensor).item()

        hallucinating = similarity <= 0.5
        return similarity, hallucinating
