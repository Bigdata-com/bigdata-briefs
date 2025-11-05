from jinja2 import Template

from bigdata_briefs.llm_client import (
    FollowUpQuestionsPromptDefaults,
)
from bigdata_briefs.models import (
    Entity,
    QAPairs,
    ReportDates,
    Result,
    RetrievedSources,
    SingleEntityReport,
)
from bigdata_briefs.templates import loader


def get_followup_questions_user_prompt(
    *,
    entity: Entity,
    results: list[Result],
    report_dates: ReportDates,
    response_format: str,
    user_template: Template,
    topics: list[str],
    config: FollowUpQuestionsPromptDefaults = FollowUpQuestionsPromptDefaults(),
) -> str:
    results_md = (
        loader.get_template("prompts/results.md.jinja").render(results=results).strip()
    )
    topics_md = "\n".join(f"* {t.format(company=entity.name)}" for t in topics)

    return user_template.render(
        entity_info=entity,
        topics=topics_md,
        results_md=results_md,
        n_followup_queries=config.n_followup_queries,
        lookback_days=report_dates.get_lookback_days(),  # TODO do we still want lookback_days in the prompt?
        start_date=report_dates.start.strftime("%B %d, %Y"),
        end_date=report_dates.end.strftime("%B %d, %Y"),
        response_format=response_format,
        current_datetime=report_dates.end.strftime(
            "%A, %B %d, %Y %H:%M %Z"
        ),  # TODO difference with end_day?
    )


def get_report_user_prompt(
    *,
    entity: Entity,
    qa_pairs: QAPairs,
    report_dates: ReportDates,
    user_template: Template,
    response_format: str,
    report_sources: RetrievedSources | None,
    topics: list[str] | None = None,
):
    if report_sources:
        rendered_qapairs = qa_pairs.render_md_with_references(report_sources)
    else:
        rendered_qapairs = qa_pairs.render_md()

    entity_info = f"{entity.name} ({entity.ticker})" if entity.ticker else entity.name

    topics_md = None
    if topics:
        topics_md = "\n".join(f"* {t.format(company=entity.name)}" for t in topics)

    return user_template.render(
        entity_info=entity_info,
        rendered_qapairs=rendered_qapairs,
        topics=topics_md,
        lookback_days=report_dates.get_lookback_days(),
        start_date=report_dates.start.strftime("%B %d, %Y"),
        end_date=report_dates.end.strftime("%B %d, %Y"),
        current_datetime=report_dates.end.strftime(
            "%A, %B %d, %Y %H:%M %Z"
        ),  # TODO difference with end_day?
        response_format=response_format,
    )


def get_compare_reports_user_prompt(
    entity: Entity,
    old_report: SingleEntityReport,
    new_report: SingleEntityReport,
    user_template: Template,
    report_dates: ReportDates,
):
    actionable_company_reports = []
    if len(new_report.relevance_score) == len(
        new_report.report_bulletpoints
    ):  # This is validating the LLM output
        formatted_report_components = []
        for e, score in zip(new_report.report_bulletpoints, new_report.relevance_score):
            if score > 3:
                # Format report
                formatted_report_components.append(f"* {e} \n")
        actionable_company_reports.append("".join(formatted_report_components))
    new_reports_str = "\n".join(actionable_company_reports)

    old_actionable_company_reports = []
    if len(old_report.relevance_score) == len(old_report.report_bulletpoints):
        formatted_report_components = []
        for e, score in zip(old_report.report_bulletpoints, old_report.relevance_score):
            if score > 3:
                # Format report
                formatted_report_components.append(f"* {e} \n")
        old_actionable_company_reports.append("".join(formatted_report_components))

    old_reports_str = "\n".join(old_actionable_company_reports)

    entity_info = f"{entity.name} ({entity.ticker})" if entity.ticker else entity.name

    return user_template.render(
        entity_info=entity_info,
        old_report=old_reports_str,
        new_report=new_reports_str,
        start_date=report_dates.start.strftime("%B %d, %Y"),
        end_date=report_dates.end.strftime("%B %d, %Y"),
        current_datetime=report_dates.end.strftime(
            "%A, %B %d, %Y %H:%M %Z"
        ),  # TODO difference with end_day?
    )


def get_intro_section_user_prompt(
    actionable_company_reports: list[SingleEntityReport],
    user_template: Template,
    report_dates: ReportDates,
    response_format: str,
) -> str:
    def format_report(report: SingleEntityReport) -> str:
        name = report.entity_info.get("name", "Unknown")
        ticker = report.entity_info.get("ticker", None)
        header = f"## {name} ({ticker})" if ticker else f"## {name}"

        return f"{header}\n\n{report.clean_final_report}"

    report = "\n\n".join(format_report(rp) for rp in actionable_company_reports)
    return user_template.render(
        report=report,
        current_datetime=report_dates.end.strftime("%A, %B %d, %Y %H:%M %Z"),
        response_format=response_format,
    )


def get_single_bullet_user_prompt(
    company_report: SingleEntityReport,
    user_template: Template,
    report_dates: ReportDates,
    response_format: str,
) -> str:
    """Generate user prompt for creating a single bullet point from a company report."""
    name = company_report.entity_info.get("name", "Unknown")
    ticker = company_report.entity_info.get("ticker", None)
    header = f"## {name} ({ticker})" if ticker else f"## {name}"

    report = f"{header}\n\n{company_report.clean_final_report}"
    return user_template.render(
        report=report,
        current_datetime=report_dates.end.strftime("%A, %B %d, %Y %H:%M %Z"),
        response_format=response_format,
    )


def get_report_title_user_prompt(
    first_bullet_point: str,
    user_template: Template,
    report_dates: ReportDates,
    response_format: str,
) -> str:
    """Generate user prompt for creating a report title from the first bullet point."""
    return user_template.render(
        first_bullet_point=first_bullet_point,
        current_datetime=report_dates.end.strftime("%A, %B %d, %Y %H:%M %Z"),
        response_format=response_format,
    )
