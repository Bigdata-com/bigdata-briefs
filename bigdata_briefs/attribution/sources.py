from bigdata_briefs import logger
from bigdata_briefs.attribution.models import ReportSourcesReverseMap
from bigdata_briefs.models import (
    AnalysisResponse,
    QAPairs,
    ReportSources,
    SourceChunkReference,
    TopicCollection,
    TopicMetadata,
)


def create_sources_for_report(
    qa_pairs: QAPairs,
) -> tuple[ReportSources, ReportSourcesReverseMap]:
    """
    Create a mapping of document IDs to reference IDs and metadata, including chunks.

    To improve LLM performance when choosing the right source, we create a new reference ID for each
    document and chunk combination. This way instead of having to generate a long Document ID and chunk ID,
    it creates a single short ID, that can be replaced by the correct source with the reverse map.
    """
    report_sources = {}
    reverse_map = {}
    ref_counter = 1

    for pair in qa_pairs.pairs:
        for result in pair.answer:
            if not result.document_id:
                continue

            for chunk in result.chunks:
                doc_reference = SourceChunkReference(
                    ref_id=ref_counter,
                    document_id=result.document_id,
                    chunk_id=chunk.chunk,
                    headline=result.headline,
                    source_key=result.source_key,
                    source_name=result.source_name,
                    source_rank=result.source_rank,
                    ts=result.ts,
                    document_scope=result.document_scope,
                    language=result.language,
                    url=result.url,
                    text=chunk.text,
                    highlights=chunk.highlights,
                )

                key = f"{result.document_id}-{chunk.chunk}"
                report_sources[key] = doc_reference

                reverse_map[ref_counter] = key

                ref_counter += 1

    return ReportSources(root=report_sources), ReportSourcesReverseMap(root=reverse_map)


def replace_references_in_topic_metadata(
    input_metadata: TopicMetadata,
    reverse_map: ReportSourcesReverseMap,
    entity,
) -> TopicMetadata:
    """
    Replace reference IDs in the source_attribution of a TopicMetadata object
    with their original document IDs and chunk numbers.
    """
    updated_source_attribution = []

    for ref_id in input_metadata.source_citation:
        if source_id := reverse_map.get(int(ref_id)):
            updated_source_attribution.append(source_id)
        else:
            logger.warning(
                f"Reference ID {ref_id} not found in reverse map {reverse_map} for {entity}."
            )
            updated_source_attribution.append("")

    return TopicMetadata(
        topic=input_metadata.topic,
        relevance_score=input_metadata.relevance_score,
        source_citation=updated_source_attribution,
    )


def replace_references_in_topic_collection(
    input_collection: TopicCollection,
    reverse_map: ReportSourcesReverseMap,
    entity,
) -> TopicCollection:
    """
    Replace reference IDs in the source_attribution of all TopicMetadata objects
    in a TopicCollection.

    Args:
        input_collection (TopicCollection): The TopicCollection object to process.
        reverse_map (ReportSourcesReverseMap): A Pydantic model containing a nested mapping of reference IDs
                                to document IDs and chunk mappings.

    Returns:
        TopicCollection: A new TopicCollection object with updated source_attribution.
    """
    updated_topics = [
        replace_references_in_topic_metadata(topic, reverse_map, entity)
        for topic in input_collection.collection
    ]
    return TopicCollection(collection=updated_topics)


def process_topic_collection(
    topic_collection: TopicCollection, report_sources: ReportSources
):
    """
    Processes a TopicCollection object to generate the topics and relevance_score lists
    for the AnalysisResponse model. Only includes references for the document with the highest source rank.

    Args:
        topic_collection (TopicCollection): The parsed response.
        report_sources (ReportSources): A mapping of document IDs to metadata.

    Returns:
        AnalysisResponse: An object containing:
            - topics (list of str): Topics with appended XML ref tags.
            - relevance_score (list of int): Relevance scores for each topic.
    """
    topics = []
    relevance_scores = []

    for topic_metadata in topic_collection.collection:
        # Fetch metadata for all document IDs in the source_citation
        doc_metadata = [
            (source_id, report_sources.get(source_id))
            for source_id in topic_metadata.source_citation
        ]

        # Group metadata by document ID
        doc_grouped_metadata = {}
        for source_id, metadata in doc_metadata:
            if metadata:
                doc_id = metadata.document_id
                if doc_id not in doc_grouped_metadata:
                    doc_grouped_metadata[doc_id] = []
                doc_grouped_metadata[doc_id].append((source_id, metadata))

        # Sort documents by source rank (ascending, lower rank is better)
        doc_sorted_by_rank = sorted(
            doc_grouped_metadata.items(),
            key=lambda x: x[1][0][1].source_rank if x[1] else float("inf"),
        )

        # Select the document with the highest rank
        if doc_sorted_by_rank:
            highest_rank_doc_id, highest_rank_metadata = doc_sorted_by_rank[0]

            # Collect all chunks for the highest-ranked document
            source_ids = [f"CQS:{source_id}" for source_id, _ in highest_rank_metadata]
            if source_ids:  # Check if there are valid references
                refs = f"`:ref[LIST:[{']['.join(source_ids)}]]`"
            else:
                refs = ""
        else:
            refs = ""

        # Add references at the end of the bp
        topics.append(f"{topic_metadata.topic}{refs}")
        relevance_scores.append(topic_metadata.relevance_score)

    return AnalysisResponse(topics=topics, relevance_score=relevance_scores)


def consolidate_report_sources(
    consolidated_sources: ReportSources, new_sources: ReportSources
):
    """
    Consolidates a new ReportSources into the existing consolidated map.

    Args:
        consolidated_sources (ReportSources): The consolidated set of sources for all entities.
        new_sources (ReportSources): The new sources to merge.
    """

    for source_id, new_doc_data in new_sources.items():
        if source_id not in consolidated_sources:
            # If the document ID is not in the consolidated map, add it directly
            consolidated_sources.set(source_id, new_doc_data)
        else:
            # If the document ID exists, consolidate the chunks
            existing_doc_data = consolidated_sources.get(source_id)
            # Sync valid status
            if new_doc_data.is_referenced():
                existing_doc_data.mark_as_used()
