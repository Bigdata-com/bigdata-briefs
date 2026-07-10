from datetime import datetime
from typing import Final
from uuid import UUID

from bigdata_briefs.api.sql_models import SQLWorkflowStatus
from bigdata_briefs.sql_models import SQLBriefReport

EXAMPLE_UUID: Final[UUID] = UUID("11111111-1111-1111-1111-111111111112")
AI_SCENE_WATCHLIST_ID: Final[str] = "db8478c9-34db-4975-8e44-b1ff764098ac"

EXAMPLE_STATUS: Final[SQLWorkflowStatus] = SQLWorkflowStatus(
    id=EXAMPLE_UUID,
    last_updated=datetime.now(),
    status="completed",
    logs=[
        "Validating input parameters",
        "Generating report per entity",
        "Generated reports for 6 entities, 6 with information, 0 without information and 0 failed.",
        "Generating introduction section",
        "Introduction section generated",
        "Storing output report",
    ],
)

EXAMPLE_REPORT: Final[SQLBriefReport] = SQLBriefReport(
    id=EXAMPLE_UUID,
    watchlist_id=AI_SCENE_WATCHLIST_ID,
    created_at=datetime.now(),
    is_empty=False,
    report_period_start=datetime.fromisoformat("2026-07-02 00:00:00.000000"),
    report_period_end=datetime.fromisoformat("2026-07-09 00:00:00.000000"),
    novelty_enabled=True,
    brief_report={
        "watchlist_id": AI_SCENE_WATCHLIST_ID,
        "watchlist_name": "AI Scene Stocks",
        "is_empty": False,
        "start_date": "2026-07-02T00:00:00",
        "end_date": "2026-07-09T00:00:00",
        "novelty": True,
        "report_title": "Broadcom Locks $30B Apple Silicon Deal as Nvidia Guides $91B",
        "introduction": (
            "* **Broadcom Inc.** extended its Apple chip partnership through **2031** under a "
            "multiyear agreement valued at more than **$30B**, including a $1.5B Fort Collins "
            "manufacturing expansion.\n\n"
            "* **NVIDIA Corp.** guided **~$91B** Q2 FY27 revenue (ex-China data-center compute) "
            "after Q1 data-center sales jumped 92%, and launched a DSX revenue-sharing cloud "
            "program to broaden AI compute access.\n\n"
            "* **Alphabet / Amazon / Microsoft** kept pushing custom AI silicon and cloud AI "
            "platforms — TPUs for external customers, Trainium above a $20B ARR, and Microsoft "
            "shifting some Office AI workloads onto proprietary MAI models.\n\n"
            "* **Palantir Technologies** expanded commercially with GNP Seguros (first named "
            "LatAm customer), an SNP SAP partnership, and a Rackspace operating framework for "
            "regulated AI deployments."
        ),
        "entity_reports": [
            {
                "entity_id": "E09E2B",
                "entity_info": {
                    "id": "E09E2B",
                    "name": "NVIDIA Corp.",
                    "description": "NVIDIA designs GPUs and AI data-center platforms.",
                    "entity_type": "COMP",
                    "company_type": "Public",
                    "country": "United States",
                    "sector": "Technology",
                    "industry_group": "Semiconductors",
                    "industry": "Semiconductors",
                    "ticker": "NVDA",
                    "webpage": "http://www.nvidia.com",
                },
                "content": [
                    {
                        "bullet_point": (
                            "NVIDIA guided **~$91B** Q2 FY27 revenue (±2%, excluding China "
                            "data-center compute) after Q1 FY27 revenue of **$81.6B** (+85% y/y), "
                            "with data center at **$75.2B** (+92% y/y)."
                        ),
                        "sources": ["AI-NVDA-1"],
                    },
                    {
                        "bullet_point": (
                            "NVIDIA launched a **DSX AI factories** revenue-sharing program so "
                            "cloud partners (e.g. Sharon AI, Firmus) can offer Grace Blackwell "
                            "capacity while NVIDIA shares in future earnings."
                        ),
                        "sources": ["AI-NVDA-2"],
                    },
                    {
                        "bullet_point": (
                            "NVIDIA inaugurated an expanded Beersheva R&D center (~3,000 sqm, "
                            "150+ employees today) focused on AI infrastructure interconnect "
                            "and data-center software/hardware."
                        ),
                        "sources": ["AI-NVDA-3"],
                    },
                ],
            },
            {
                "entity_id": "09DE1F",
                "entity_info": {
                    "id": "09DE1F",
                    "name": "Broadcom Inc.",
                    "description": "Broadcom designs semiconductors and infrastructure software.",
                    "entity_type": "COMP",
                    "company_type": "Public",
                    "country": "United States",
                    "sector": "Technology",
                    "industry_group": "Semiconductors",
                    "industry": "Semiconductors",
                    "ticker": "AVGO",
                    "webpage": "http://www.broadcom.com",
                },
                "content": [
                    {
                        "bullet_point": (
                            "Broadcom and **Apple** expanded their collaboration through "
                            "**2031** via multiyear agreements for custom ASIC silicon across "
                            "multiple Apple product generations."
                        ),
                        "sources": ["AI-AVGO-1"],
                    },
                    {
                        "bullet_point": (
                            "Apple framed a related commitment of more than **$30B** to develop "
                            "custom silicon and wireless connectivity, including a **$1.5B** "
                            "Broadcom Fort Collins manufacturing expansion under Apple's AMP."
                        ),
                        "sources": ["AI-AVGO-2"],
                    },
                    {
                        "bullet_point": (
                            "Analysts called the Apple win another validation of Broadcom's "
                            "ASIC franchise; CEO Hock Tan has guided AI semiconductor revenue "
                            "to more than triple y/y into the Aug. 2 fiscal Q3 print."
                        ),
                        "sources": ["AI-AVGO-3"],
                    },
                ],
            },
            {
                "entity_id": "4A6F00",
                "entity_info": {
                    "id": "4A6F00",
                    "name": "Alphabet Inc.",
                    "description": "Alphabet is the parent of Google.",
                    "entity_type": "COMP",
                    "company_type": "Public",
                    "country": "United States",
                    "sector": "Technology",
                    "industry_group": "Software",
                    "industry": "Internet Software",
                    "ticker": "GOOGL",
                    "webpage": "http://www.abc.xyz",
                },
                "content": [
                    {
                        "bullet_point": (
                            "Alphabet plans to deliver **TPUs** to select customers for use in "
                            "their own data centers, with Wells Fargo expecting external TPU "
                            "sales to become a meaningful revenue source from Q3."
                        ),
                        "sources": ["AI-GOOG-1"],
                    },
                    {
                        "bullet_point": (
                            "Google Cloud sales jumped **63%** to **$20B** in Q1 2026 as Gemini "
                            "adoption and full-stack AI (TPUs/GPUs + models + data platforms) "
                            "deepened enterprise wins."
                        ),
                        "sources": ["AI-GOOG-2"],
                    },
                ],
            },
            {
                "entity_id": "0157B1",
                "entity_info": {
                    "id": "0157B1",
                    "name": "Amazon.com Inc.",
                    "description": "Amazon operates e-commerce and AWS cloud services.",
                    "entity_type": "COMP",
                    "company_type": "Public",
                    "country": "United States",
                    "sector": "Technology",
                    "industry_group": "Software",
                    "industry": "Internet Software",
                    "ticker": "AMZN",
                    "webpage": "http://www.amazon.com",
                },
                "content": [
                    {
                        "bullet_point": (
                            "AWS grew **28%** (fastest in 15 quarters); Amazon's custom-chip "
                            "business (**Trainium**/Graviton/Nitro) crossed a **$20B** "
                            "annualized revenue run rate with triple-digit growth."
                        ),
                        "sources": ["AI-AMZN-1"],
                    },
                    {
                        "bullet_point": (
                            "AWS invested **$1B** in Forward Deployed Engineering to embed "
                            "engineers with customers for agentic AI deployments, and named "
                            "FOX its preferred AI cloud provider."
                        ),
                        "sources": ["AI-AMZN-2"],
                    },
                ],
            },
            {
                "entity_id": "228D42",
                "entity_info": {
                    "id": "228D42",
                    "name": "Microsoft Corp.",
                    "description": "Microsoft provides software, cloud, and AI platforms.",
                    "entity_type": "COMP",
                    "company_type": "Public",
                    "country": "United States",
                    "sector": "Technology",
                    "industry_group": "Software",
                    "industry": "Software",
                    "ticker": "MSFT",
                    "webpage": "http://www.microsoft.com",
                },
                "content": [
                    {
                        "bullet_point": (
                            "Microsoft began replacing some OpenAI/Anthropic model integrations "
                            "in Office apps with proprietary **MAI** models to cut cost and "
                            "reduce single-supplier dependence, while keeping Azure AI Foundry "
                            "multi-model."
                        ),
                        "sources": ["AI-MSFT-1"],
                    },
                    {
                        "bullet_point": (
                            "Azure revenue grew ~**40%** last quarter and Microsoft's AI "
                            "business annual run rate rose **123%** y/y to **$37B**; the "
                            "company also cut ~4,800 roles (~2.1%) while prioritizing AI "
                            "investments."
                        ),
                        "sources": ["AI-MSFT-2"],
                    },
                ],
            },
            {
                "entity_id": "F1C69A",
                "entity_info": {
                    "id": "F1C69A",
                    "name": "Palantir Technologies Inc.",
                    "description": "Palantir provides data analytics and AI software platforms.",
                    "entity_type": "COMP",
                    "company_type": "Public",
                    "country": "United States",
                    "sector": "Technology",
                    "industry_group": "Software",
                    "industry": "Application Software",
                    "ticker": "PLTR",
                    "webpage": "http://www.palantir.com",
                },
                "content": [
                    {
                        "bullet_point": (
                            "Palantir expanded with **GNP Seguros**, its first publicly named "
                            "commercial customer in Latin America, scaling Foundry/AIP for "
                            "claims fraud, underwriting, and risk across insurance lines."
                        ),
                        "sources": ["AI-PLTR-1"],
                    },
                    {
                        "bullet_point": (
                            "Palantir partnered with **SNP** on AI-powered SAP transformations "
                            "and with **Rackspace** on an operating framework for regulated/"
                            "sovereign AI production deployments."
                        ),
                        "sources": ["AI-PLTR-2"],
                    },
                    {
                        "bullet_point": (
                            "Q1 2026 revenue grew **85%** y/y to **$1.63B**, with U.S. "
                            "commercial revenue up **133%**, underscoring accelerating AIP "
                            "adoption."
                        ),
                        "sources": ["AI-PLTR-3"],
                    },
                ],
            },
        ],
        "source_metadata": {
            "AI-NVDA-1": {
                "ref_id": 1,
                "document_id": "CFB7AC1DB020117C18DD93DA1A6441B4",
                "headline": "AI's $15 Trillion Opportunity Is Just Getting Started",
                "ts": "2026-07-10T16:26:06+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "AOL",
                "source_name": "AOL.com",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/CFB7AC1DB020117C18DD93DA1A6441B4",
                "chunk_id": 1,
                "text": "NVIDIA guided $91 billion for Q2 FY27...",
                "highlights": [],
            },
            "AI-NVDA-2": {
                "ref_id": 2,
                "document_id": "8050BAC9B9581F746B7997A407367104",
                "headline": "Nvidia Is Making it Easier for AI Startups to Get Compute Power With a New Cloud and Revenue-Sharing Program",
                "ts": "2026-07-02T12:55:31+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "BZ",
                "source_name": "Benzinga",
                "source_rank": 0,
                "url": "https://app.bigdata.com/documents/8050BAC9B9581F746B7997A407367104",
                "chunk_id": 1,
                "text": "Nvidia introduced a revenue-sharing and credit-support model...",
                "highlights": [],
            },
            "AI-NVDA-3": {
                "ref_id": 3,
                "document_id": "FCF1EB6021675B5265CEEBF65D386D9D",
                "headline": "Nvidia inaugurates expanded Beersheva R&D center",
                "ts": "2026-07-08T08:29:17+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "JP",
                "source_name": "Jpost.com",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/FCF1EB6021675B5265CEEBF65D386D9D",
                "chunk_id": 2,
                "text": "Nvidia officially inaugurated its new R&D center in Beersheva...",
                "highlights": [],
            },
            "AI-AVGO-1": {
                "ref_id": 4,
                "document_id": "356CAEF7876911BE06CFEE4EBE4CF65A",
                "headline": "NEW YORK MARKET CLOSE: Tech leads stocks higher while DJIA tops 53,000",
                "ts": "2026-07-06T20:21:48+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "AN",
                "source_name": "Alliance News",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/356CAEF7876911BE06CFEE4EBE4CF65A",
                "chunk_id": 3,
                "text": "Broadcom... extended partnership... through to 2031...",
                "highlights": [],
            },
            "AI-AVGO-2": {
                "ref_id": 5,
                "document_id": "E6A785F55F1A0784A6A15ED40E52952E",
                "headline": "AAPL & Broadcom's $30B Deal Boosts AI Chip Strategy: What's Ahead?",
                "ts": "2026-07-10T15:48:29+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "NQ",
                "source_name": "Nasdaq",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/E6A785F55F1A0784A6A15ED40E52952E",
                "chunk_id": 1,
                "text": "Apple expanded partnership with Broadcom... more than $30 billion...",
                "highlights": [],
            },
            "AI-AVGO-3": {
                "ref_id": 6,
                "document_id": "831B8B20F487BFA8F982FE1A4C7B8E06",
                "headline": "3 Tech Stocks Poised for Comebacks",
                "ts": "2026-07-10T10:33:54+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "NQ",
                "source_name": "Nasdaq",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/831B8B20F487BFA8F982FE1A4C7B8E06",
                "chunk_id": 5,
                "text": "AI semiconductor revenue to more than triple... Apple expanding partnership...",
                "highlights": [],
            },
            "AI-GOOG-1": {
                "ref_id": 7,
                "document_id": "17FFB09810BB82CBEC3F7105E50FAE17",
                "headline": "Wells Fargo Cuts Alphabet (GOOGL) Target to $416 and Keeps Overweight Rating",
                "ts": "2026-07-09T18:12:10+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "YF",
                "source_name": "Yahoo! Finance",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/17FFB09810BB82CBEC3F7105E50FAE17",
                "chunk_id": 2,
                "text": "TPUs to become a meaningful external revenue source starting in the third quarter...",
                "highlights": [],
            },
            "AI-GOOG-2": {
                "ref_id": 8,
                "document_id": "A68678EFCE14D5FA3285D7500B5DC29A",
                "headline": "3 AI Stocks That Could Outperform the S&P 500 for Years to Come",
                "ts": "2026-07-07T14:57:47+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "GM",
                "source_name": "The Globe And Mail",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/A68678EFCE14D5FA3285D7500B5DC29A",
                "chunk_id": 4,
                "text": "Google Cloud sales jumping 63% to $20 billion in Q1 2026...",
                "highlights": [],
            },
            "AI-AMZN-1": {
                "ref_id": 9,
                "document_id": "8C1DC14D12998DEC6AFFDF553F7CBBE2",
                "headline": "$130 Billion in AI Data Centers Have Been Blocked or Delayed in 2026",
                "ts": "2026-07-09T12:00:51+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "BZ",
                "source_name": "Benzinga",
                "source_rank": 0,
                "url": "https://app.bigdata.com/documents/8C1DC14D12998DEC6AFFDF553F7CBBE2",
                "chunk_id": 10,
                "text": "AWS grew 28%... Trainium crossed a $20 billion annualized revenue run rate...",
                "highlights": [],
            },
            "AI-AMZN-2": {
                "ref_id": 10,
                "document_id": "3917FE140FBB76B006B9DE32E13CAC70",
                "headline": "Amazon Follows Palantir's Playbook: How Forward Deployed Engineers Target the Enterprise AI Gold Rush",
                "ts": "2026-07-06T23:31:48+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "GM",
                "source_name": "The Globe And Mail",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/3917FE140FBB76B006B9DE32E13CAC70",
                "chunk_id": 1,
                "text": "Amazon investing $1 billion to expand forward deployed engineers...",
                "highlights": [],
            },
            "AI-MSFT-1": {
                "ref_id": 11,
                "document_id": "15F1C2381A99DD1673299AEA952424F9",
                "headline": "Microsoft replaces OpenAI, Anthropic AI with proprietary models in apps",
                "ts": "2026-07-07T16:25:36+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "CB",
                "source_name": "Crypto Briefing",
                "source_rank": 2,
                "url": "https://app.bigdata.com/documents/15F1C2381A99DD1673299AEA952424F9",
                "chunk_id": 1,
                "text": "Microsoft replacing OpenAI and Anthropic integrations with proprietary AI models...",
                "highlights": [],
            },
            "AI-MSFT-2": {
                "ref_id": 12,
                "document_id": "2BBE6B4E8B2C683DEC33FC783DD7729B",
                "headline": "3 Genius Stocks Smart Investors Are Buying Right Now",
                "ts": "2026-07-08T16:31:16+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "NQ",
                "source_name": "Nasdaq",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/2BBE6B4E8B2C683DEC33FC783DD7729B",
                "chunk_id": 4,
                "text": "Azure segment revenues grew at a 40% rate... AI business rose by 123% to $37 billion...",
                "highlights": [],
            },
            "AI-PLTR-1": {
                "ref_id": 13,
                "document_id": "03D6CCA3AF191447AFFAD064C0B14E46",
                "headline": "Palantir enters enterprise expansion agreement with GNP Seguros",
                "ts": "2026-07-07T11:02:38+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "FLY",
                "source_name": "The Fly",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/03D6CCA3AF191447AFFAD064C0B14E46",
                "chunk_id": 1,
                "text": "GNP Seguros becomes Palantir's first publicly announced commercial customer in Latin America...",
                "highlights": [],
            },
            "AI-PLTR-2": {
                "ref_id": 14,
                "document_id": "EB8909B5F46C5A22B3DC35E96D6B8ADE",
                "headline": "Palantir, SNP SE announce strategic partnership at Transformation World",
                "ts": "2026-07-08T09:22:41+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "FLY",
                "source_name": "The Fly",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/EB8909B5F46C5A22B3DC35E96D6B8ADE",
                "chunk_id": 1,
                "text": "SNP SE and Palantir announced a strategic partnership...",
                "highlights": [],
            },
            "AI-PLTR-3": {
                "ref_id": 15,
                "document_id": "FF586D8D23829F850F581FBFDC7BFC83",
                "headline": "Palantir Stock Is Down 36% From Its All-Time High. Time to Buy?",
                "ts": "2026-07-10T10:36:18+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "NQ",
                "source_name": "Nasdaq",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/FF586D8D23829F850F581FBFDC7BFC83",
                "chunk_id": 2,
                "text": "Palantir's first-quarter revenue rose 85% year over year to $1.63 billion...",
                "highlights": [],
            },
        },
    },
)
