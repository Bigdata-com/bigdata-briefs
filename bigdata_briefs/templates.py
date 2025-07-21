import textwrap

import jinja2

# -----------------------------------------------------
# Jinja2 Template for Summaries
# -----------------------------------------------------
RESULTS_TEMPLATE = jinja2.Template(
    """\
{% for result in results %}
#### {{ result.headline }}

{% for chunk in result.chunks -%}
* {{ chunk.text }}

{% endfor -%}
{% endfor -%}"""
)

# Define the template with separate sections for this week and last week
QA_TEMPLATE = textwrap.dedent(
    """\
    ### {{ question }}

    {% if answer %}
    {% for result in answer %}
    {% for chunk in result.chunks -%}
    {% set key = result.document_id ~ '-' ~ chunk.chunk %}
    ### Reference ID: {{ report_sources[key].ref_id }}
    {{ chunk.text }}
    {%- endfor %}
    {% endfor %}
    {% endif %}
    """
)

REPORT_TEMPLATE = textwrap.dedent(
    """\
    ## {{ report_title }}

    {{ report_date.strftime("%B %d, %Y") }}

    {% if introduction -%}
    ### Overview
    {{ introduction }}
    {% endif -%}

    {% for report in company_reports %}
    ---
    {{ report.render() }}
    {% endfor %}
    """
)
