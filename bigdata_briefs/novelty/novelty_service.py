from datetime import datetime, timedelta
from typing import Callable

import numpy as np

from bigdata_briefs import logger
from bigdata_briefs.metrics import BulletPointMetrics
from bigdata_briefs.models import BulletPointsUsage
from bigdata_briefs.novelty.embedding_client import EmbeddingClient
from bigdata_briefs.novelty.models import (
    BulletPointEmbedding,
    DiscardedBulletPoint,
    NoveltyDebugInfo,
)
from bigdata_briefs.novelty.storage import EmbeddingStorage
from bigdata_briefs.settings import settings


class NoveltyFilteringService:
    def __init__(
        self,
        embedding_client: EmbeddingClient,
        embedding_storage: EmbeddingStorage,
    ):
        self.embedding_client = embedding_client
        self.storage = embedding_storage

    def filter_by_novelty(
        self,
        texts: list[str],
        entity_id: str,
        *,
        start_date: datetime,
        end_date: datetime,
        current_date: datetime,
        clean_up_func: Callable[[str], str] | None = None,
        collect_debug_info: bool = False,
        entity_name: str | None = None,
    ) -> tuple[list[BulletPointEmbedding], NoveltyDebugInfo | None]:
        new_embeddings = self._compute_embeddings(texts, clean_up_func=clean_up_func)
        logger.debug(f"New embeddings computed for {entity_id}")
        new_bp_embeddings = [
            BulletPointEmbedding(
                date=current_date,
                entity_id=entity_id,
                embedding=embedding,
                original_text=text,
            )
            for embedding, text in zip(new_embeddings, texts)
        ]

        prev_bp_embeddings = self._retrieve_embeddings_from_storage(
            entity_id, start_date=start_date, end_date=end_date
        )
        logger.debug(f"New embeddings retrieved for {entity_id}")

        debug_info = None
        discarded_bullets = []
        
        if prev_bp_embeddings:
            cosine_similarities = self._calculate_similarity_bp_embedding(
                old_bullet_point_embedding=prev_bp_embeddings,
                new_bullet_point_embedding=new_bp_embeddings,
            )
            for idx, bp in enumerate(new_bp_embeddings):
                max_similarity = np.max(cosine_similarities[:, idx])
                if max_similarity > settings.NOVELTY_THRESHOLD:
                    bp.set_novel(False)
                    
                    if collect_debug_info:
                        # Find the most similar old text
                        most_similar_idx = np.argmax(cosine_similarities[:, idx])
                        most_similar_text = prev_bp_embeddings[most_similar_idx].original_text
                        discarded_bullets.append(
                            DiscardedBulletPoint(
                                text=bp.original_text,
                                max_similarity=float(max_similarity),
                                most_similar_text=most_similar_text,
                            )
                        )
        else:
            logger.debug(f"No previous embeddings for {entity_id}")

        self._store_embedding(
            entity_id, current_embedding_dt=current_date, embedding_bp=new_bp_embeddings
        )
        logger.debug(f"New embeddings stored for {entity_id}")

        results = [bp for bp in new_bp_embeddings if bp.is_novel()]
        
        if collect_debug_info:
            debug_info = NoveltyDebugInfo(
                entity_id=entity_id,
                entity_name=entity_name or entity_id,
                generated_texts=texts,
                compared_with=[bp.original_text for bp in prev_bp_embeddings],
                discarded=discarded_bullets,
                kept_texts=[bp.original_text for bp in results],
            )
        
        BulletPointMetrics.track_usage(
            BulletPointsUsage(bullet_points_after_novelty=len(results))
        )
        return results, debug_info

    @staticmethod
    def _calculate_similarity_bp_embedding(
        old_bullet_point_embedding: list[BulletPointEmbedding],
        new_bullet_point_embedding: list[BulletPointEmbedding],
    ):
        old_embedding = np.asarray([bp.embedding for bp in old_bullet_point_embedding])
        new_embedding = np.asarray([bp.embedding for bp in new_bullet_point_embedding])
        return cosine_similarity(old_embedding, new_embedding)

    def _store_embedding(
        self,
        entity_id: str,
        current_embedding_dt: datetime,
        embedding_bp: list[BulletPointEmbedding],
    ):
        recent_stored_bp = self.storage.retrieve(
            entity_id,
            start_date=(
                current_embedding_dt
                - timedelta(hours=settings.NOVELTY_STORAGE_LOOKBACK_HOURS)
            ),
            end_date=current_embedding_dt,
        )
        if recent_stored_bp:
            cosine_similarities = self._calculate_similarity_bp_embedding(
                old_bullet_point_embedding=recent_stored_bp,
                new_bullet_point_embedding=embedding_bp,
            )

            embedding_to_store = []
            for idx, bp in enumerate(embedding_bp):
                if np.all(
                    cosine_similarities[:, idx] < settings.NOVELTY_STORAGE_THRESHOLD
                ):
                    embedding_to_store.append(bp)

        else:
            embedding_to_store = embedding_bp

        if embedding_to_store:
            BulletPointMetrics.track_usage(
                BulletPointsUsage(bullet_points_stored=len(embedding_to_store))
            )
            self.storage.store(embedding_to_store)

    def _retrieve_embeddings_from_storage(
        self, entity_id: str, *, start_date: datetime, end_date: datetime
    ) -> list[BulletPointEmbedding]:
        return self.storage.retrieve(
            entity_id, start_date=start_date, end_date=end_date
        )

    def _compute_embeddings(
        self, texts: list[str], clean_up_func: Callable[[str], str] | None = None
    ) -> list[list[float]]:
        if clean_up_func:
            clean_texts = [clean_up_func(text) for text in texts]
        return self.embedding_client.compute(clean_texts)


def cosine_similarity(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between two matrices X and Y

    Based on the implementation in sklearn.metrics.pairwise.cosine_similarity https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/metrics/pairwise.py#L1691-L1748
    """
    dot_product = np.dot(X, Y.T)

    # Compute the norms of the rows of X and Y
    norm_X = np.linalg.norm(X, axis=1).reshape(-1, 1)  # Shape (X, 1)
    norm_Y = np.linalg.norm(Y, axis=1).reshape(1, -1)  # Reshape as (1, Y)

    # Normalize by dividing the dot product by the outer product of the norms
    return dot_product / (norm_X * norm_Y)
