"""Precomputed demo briefs for Commodities and Countries watchlists."""

from datetime import datetime
from typing import Final
from uuid import UUID

from bigdata_briefs.api.sql_models import SQLWorkflowStatus
from bigdata_briefs.sql_models import SQLBriefReport

COMMODITIES_WATCHLIST_ID: Final[str] = "e3e9d089-0668-4e2b-85f6-4179a447e3c9"
COUNTRIES_WATCHLIST_ID: Final[str] = "164fa89e-1aa6-4a38-a84f-ce6063c61023"

COMMODITIES_EXAMPLE_UUID: Final[UUID] = UUID("22222222-2222-2222-2222-222222222222")
COUNTRIES_EXAMPLE_UUID: Final[UUID] = UUID("33333333-3333-3333-3333-333333333333")

COMMODITIES_EXAMPLE_STATUS: Final[SQLWorkflowStatus] = SQLWorkflowStatus(
    id=COMMODITIES_EXAMPLE_UUID,
    last_updated=datetime.now(),
    status="completed",
    logs=[
        "Validating input parameters",
        "Generating report per entity",
        "Generated reports for 4 entities, 4 with information, 0 without information and 0 failed.",
        "Generating introduction section",
        "Introduction section generated",
        "Storing output report",
    ],
)

COUNTRIES_EXAMPLE_STATUS: Final[SQLWorkflowStatus] = SQLWorkflowStatus(
    id=COUNTRIES_EXAMPLE_UUID,
    last_updated=datetime.now(),
    status="completed",
    logs=[
        "Validating input parameters",
        "Generating report per entity",
        "Generated reports for 5 entities, 5 with information, 0 without information and 0 failed.",
        "Generating introduction section",
        "Introduction section generated",
        "Storing output report",
    ],
)

COMMODITIES_EXAMPLE_REPORT: Final[SQLBriefReport] = SQLBriefReport(
    id=COMMODITIES_EXAMPLE_UUID,
    watchlist_id=COMMODITIES_WATCHLIST_ID,
    created_at=datetime.now(),
    is_empty=False,
    report_period_start=datetime.fromisoformat("2026-07-02 00:00:00.000000"),
    report_period_end=datetime.fromisoformat("2026-07-09 00:00:00.000000"),
    novelty_enabled=True,
    brief_report={
        "watchlist_id": COMMODITIES_WATCHLIST_ID,
        "watchlist_name": "Commodities",
        "is_empty": False,
        "start_date": "2026-07-02T00:00:00",
        "end_date": "2026-07-09T00:00:00",
        "novelty": True,
        "report_title": "Oil Rebounds on Middle East Escalation as Gold Stabilizes",
        "introduction": (
            "* **Crude oil** jumped after renewed US-Iran hostilities, with Brent briefly "
            "trading above $80 and WTI near multi-week highs as Hormuz shipping risk returned.\n\n"
            "* **Gold** rebounded above $4,100 as softer oil and dollar dynamics supported "
            "safe-haven demand, even as banks trimmed medium-term price forecasts.\n\n"
            "* **Copper** remained elevated on tight concentrate supply and tariff uncertainty, "
            "though strategists warned of equity-linked downside if risk assets correct.\n\n"
            "* **Natural gas** traded choppily on shifting US weather forecasts, with LNG "
            "export flows and storage builds capping sustained upside."
        ),
        "entity_reports": [
            {
                "entity_id": "OIL001",
                "entity_info": {
                    "id": "OIL001",
                    "name": "Crude Oil",
                    "description": "Global crude oil benchmark complex (Brent / WTI).",
                    "entity_type": "COMM",
                    "company_type": None,
                    "country": None,
                    "sector": "Energy",
                    "industry_group": "Commodities",
                    "industry": "Crude Oil",
                    "ticker": "CL",
                    "webpage": None,
                },
                "content": [
                    {
                        "bullet_point": (
                            "**Brent crude** rose sharply after President Trump said the "
                            "ceasefire with Tehran was \"over\" and the US launched fresh "
                            "strikes, pushing Brent up 6.6% in after-hours trading to $79.06 "
                            "and briefly above $80."
                        ),
                        "sources": ["COMM-OIL-1"],
                    },
                    {
                        "bullet_point": (
                            "WTI futures traded near $73–$74 as Hormuz shipping risk resurfaced; "
                            "USO and BNO ETFs jumped in premarket on the escalation."
                        ),
                        "sources": ["COMM-OIL-2"],
                    },
                    {
                        "bullet_point": (
                            "Russia banned diesel exports after Ukrainian drone attacks on "
                            "refineries, adding refined-product supply stress alongside crude "
                            "geopolitical risk."
                        ),
                        "sources": ["COMM-OIL-1"],
                    },
                ],
            },
            {
                "entity_id": "GLD001",
                "entity_info": {
                    "id": "GLD001",
                    "name": "Gold",
                    "description": "Spot and futures gold market.",
                    "entity_type": "COMM",
                    "company_type": None,
                    "country": None,
                    "sector": "Materials",
                    "industry_group": "Commodities",
                    "industry": "Precious Metals",
                    "ticker": "XAU",
                    "webpage": None,
                },
                "content": [
                    {
                        "bullet_point": (
                            "Gold rebounded above **$4,100**, posting a two-day peak near "
                            "$4,138 as investors reassessed inflation, geopolitics, and "
                            "monetary-policy expectations."
                        ),
                        "sources": ["COMM-GLD-1"],
                    },
                    {
                        "bullet_point": (
                            "HSBC cut its average gold price forecasts for 2026 and 2027 to "
                            "$4,560 and $4,925 from $4,864 and $5,000, while near-term "
                            "technicals still pointed to a recovery attempt."
                        ),
                        "sources": ["COMM-GLD-1"],
                    },
                    {
                        "bullet_point": (
                            "Analysts noted gold can still face selling pressure during "
                            "liquidity stress even as a safe haven, after earlier declines "
                            "tied to stronger USD and delayed rate-cut expectations."
                        ),
                        "sources": ["COMM-GLD-2"],
                    },
                ],
            },
            {
                "entity_id": "CU0001",
                "entity_info": {
                    "id": "CU0001",
                    "name": "Copper",
                    "description": "Global copper market (LME / COMEX).",
                    "entity_type": "COMM",
                    "company_type": None,
                    "country": None,
                    "sector": "Materials",
                    "industry_group": "Commodities",
                    "industry": "Industrial Metals",
                    "ticker": "HG",
                    "webpage": None,
                },
                "content": [
                    {
                        "bullet_point": (
                            "Copper prices remained elevated, with reports of ~3.9% q/q gains "
                            "to about **$13,307/t** (+40% y/y) on tight concentrate supply and "
                            "AI/infrastructure demand."
                        ),
                        "sources": ["COMM-CU-1"],
                    },
                    {
                        "bullet_point": (
                            "EIU expects LME cash copper to average about **$12,141/t** in 2026 "
                            "(+22% vs 2025), supported by AI, EVs, and constrained mine supply."
                        ),
                        "sources": ["COMM-CU-2"],
                    },
                    {
                        "bullet_point": (
                            "Bloomberg Intelligence warned copper remains highly correlated "
                            "with equities and could correct sharply if risk assets sell off."
                        ),
                        "sources": ["COMM-CU-3"],
                    },
                ],
            },
            {
                "entity_id": "NG0001",
                "entity_info": {
                    "id": "NG0001",
                    "name": "Natural Gas",
                    "description": "US and global natural gas / LNG markets.",
                    "entity_type": "COMM",
                    "company_type": None,
                    "country": None,
                    "sector": "Energy",
                    "industry_group": "Commodities",
                    "industry": "Natural Gas",
                    "ticker": "NG",
                    "webpage": None,
                },
                "content": [
                    {
                        "bullet_point": (
                            "US natural gas prices swung with weather: hotter forecasts lifted "
                            "prices toward ~$3.2, while cooler outlooks and ample storage "
                            "capped gains."
                        ),
                        "sources": ["COMM-NG-1"],
                    },
                    {
                        "bullet_point": (
                            "IEA expects global gas demand to decline ~0.5% in 2026, with "
                            "Asian/European prices still elevated vs 2025 amid Gulf-related "
                            "LNG flow uncertainty."
                        ),
                        "sources": ["COMM-NG-2"],
                    },
                ],
            },
        ],
        "source_metadata": {
            "COMM-OIL-1": {
                "ref_id": 1,
                "document_id": "04251046E0E175DDB890851B32A02490",
                "headline": "Are deep reservoirs the next frontier in the US shale revolution?",
                "ts": "2026-07-09T11:00:04+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "FT",
                "source_name": "Financial Times",
                "source_rank": 0,
                "url": "https://app.bigdata.com/documents/04251046E0E175DDB890851B32A02490",
                "chunk_id": 1,
                "text": "Oil prices jumped after Donald Trump said Washington's ceasefire with Tehran was over...",
                "highlights": [],
            },
            "COMM-OIL-2": {
                "ref_id": 2,
                "document_id": "AF20743922F5E6ED8D4CEDF7B5DFF4A8",
                "headline": "Oil Surges Again as US-Iran War Escalates",
                "ts": "2026-07-09T13:07:47+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "BZ",
                "source_name": "Benzinga",
                "source_rank": 0,
                "url": "https://app.bigdata.com/documents/AF20743922F5E6ED8D4CEDF7B5DFF4A8",
                "chunk_id": 3,
                "text": "WTI crude oil futures were trading higher... Brent crude oil futures rose...",
                "highlights": [],
            },
            "COMM-GLD-1": {
                "ref_id": 3,
                "document_id": "57BB46A3341B6B551F422419BF1FB418",
                "headline": "Gold rebounds above $4,100 as falling Oil weighs on US Dollar",
                "ts": "2026-07-09T18:23:30+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "FX",
                "source_name": "FXStreet News",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/57BB46A3341B6B551F422419BF1FB418",
                "chunk_id": 4,
                "text": "HSBC lowered its average Gold price forecasts... Gold recovers $4,100...",
                "highlights": [],
            },
            "COMM-GLD-2": {
                "ref_id": 4,
                "document_id": "003EC22525D12798CD9D81B12BBDF2DC",
                "headline": "Commodity forecast : World",
                "ts": "2026-07-09T13:10:40+00:00",
                "document_scope": "research",
                "language": "English",
                "source_key": "EIU",
                "source_name": "The Economist",
                "source_rank": 0,
                "url": "https://app.bigdata.com/documents/003EC22525D12798CD9D81B12BBDF2DC",
                "chunk_id": 353,
                "text": "Perhaps counter-intuitively, the price of gold slumped as the war in Iran progressed...",
                "highlights": [],
            },
            "COMM-CU-1": {
                "ref_id": 5,
                "document_id": "87DA445BF7BC2C9DDDA2FD5D12BFE892",
                "headline": "Metals: Margins Trail Expectations",
                "ts": "2026-07-09T16:50:28+00:00",
                "document_scope": "research",
                "language": "English",
                "source_key": "EQ",
                "source_name": "Equirus Securities",
                "source_rank": 2,
                "url": "https://app.bigdata.com/documents/87DA445BF7BC2C9DDDA2FD5D12BFE892",
                "chunk_id": 20,
                "text": "Copper prices increased by 3.9% qoq to US$ 13,307/t (+40% yoy)...",
                "highlights": [],
            },
            "COMM-CU-2": {
                "ref_id": 6,
                "document_id": "003EC22525D12798CD9D81B12BBDF2DC",
                "headline": "Commodity forecast : World",
                "ts": "2026-07-09T13:10:40+00:00",
                "document_scope": "research",
                "language": "English",
                "source_key": "EIU",
                "source_name": "The Economist",
                "source_rank": 0,
                "url": "https://app.bigdata.com/documents/003EC22525D12798CD9D81B12BBDF2DC",
                "chunk_id": 312,
                "text": "We expect the London Metal Exchange (LME) cash price to average US$12,141/tonne in 2026...",
                "highlights": [],
            },
            "COMM-CU-3": {
                "ref_id": 7,
                "document_id": "8EE6A1E70A5B24AFF403A97A46C82CC0",
                "headline": "The AI's 2% Reality Check Threatening The Copper Rally",
                "ts": "2026-07-07T10:56:35+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "BZ",
                "source_name": "Benzinga",
                "source_rank": 0,
                "url": "https://app.bigdata.com/documents/8EE6A1E70A5B24AFF403A97A46C82CC0",
                "chunk_id": 3,
                "text": "Copper's main risk is if the stock market goes down...",
                "highlights": [],
            },
            "COMM-NG-1": {
                "ref_id": 8,
                "document_id": "7724AEE244B478075AB00CB12B3A9CF1",
                "headline": "AFCM Weekly Insights (W-25- 2026)",
                "ts": "2026-07-02T06:39:31+00:00",
                "document_scope": "research",
                "language": "English",
                "source_key": "AF",
                "source_name": "Arab Federation of Exchanges",
                "source_rank": 2,
                "url": "https://app.bigdata.com/documents/7724AEE244B478075AB00CB12B3A9CF1",
                "chunk_id": 15,
                "text": "U.S. natural gas prices rallied... then retreated... then rose to around US$ 3.2...",
                "highlights": [],
            },
            "COMM-NG-2": {
                "ref_id": 9,
                "document_id": "308BE4C6F247EEF7A7ED336322C8ECC2",
                "headline": "Global gas demand expected to decline by 0.5% in 2026: IEA",
                "ts": "2026-07-07T19:10:37+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "WAM",
                "source_name": "Emirates News Agency (WAM)",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/308BE4C6F247EEF7A7ED336322C8ECC2",
                "chunk_id": 2,
                "text": "Natural gas prices in Asia and Europe have moderated from recent highs...",
                "highlights": [],
            },
        },
    },
)

COUNTRIES_EXAMPLE_REPORT: Final[SQLBriefReport] = SQLBriefReport(
    id=COUNTRIES_EXAMPLE_UUID,
    watchlist_id=COUNTRIES_WATCHLIST_ID,
    created_at=datetime.now(),
    is_empty=False,
    report_period_start=datetime.fromisoformat("2026-07-02 00:00:00.000000"),
    report_period_end=datetime.fromisoformat("2026-07-09 00:00:00.000000"),
    novelty_enabled=True,
    brief_report={
        "watchlist_id": COUNTRIES_WATCHLIST_ID,
        "watchlist_name": "Countries",
        "is_empty": False,
        "start_date": "2026-07-02T00:00:00",
        "end_date": "2026-07-09T00:00:00",
        "novelty": True,
        "report_title": "Soft US Jobs, China Easing Bias, and BoJ Tightening Frame Macro Week",
        "introduction": (
            "* **United States** added only 57,000 jobs in June, delaying Fed hike expectations "
            "while markets watched FOMC minutes and Middle East escalation.\n\n"
            "* **China** flagged \"structural divergence,\" with PBoC signaling more targeted "
            "easing as CPI cooled and PPI climbed; IMF raised 2026 growth to 4.6%.\n\n"
            "* **Germany** advanced a large reform package and defense spending plans while "
            "manufacturing remains challenged by energy costs and trade frictions.\n\n"
            "* **Japan** kept bank lending strong after the BoJ lifted rates to 1%, with "
            "producer prices accelerating on energy costs.\n\n"
            "* **India** saw the IMF trim 2026 growth to 6.4% but still remains among the "
            "fastest-growing major economies."
        ),
        "entity_reports": [
            {
                "entity_id": "3D4567",
                "entity_info": {
                    "id": "3D4567",
                    "name": "United States",
                    "description": "United States of America",
                    "entity_type": "COUNTRY",
                    "company_type": None,
                    "country": "United States",
                    "sector": None,
                    "industry_group": None,
                    "industry": None,
                    "ticker": None,
                    "webpage": None,
                },
                "content": [
                    {
                        "bullet_point": (
                            "The US economy undershot forecasts with **57,000 jobs** added in "
                            "June; Treasury yields fell and futures pushed the next Fed hike "
                            "expectation out toward December."
                        ),
                        "sources": ["CTRY-US-1"],
                    },
                    {
                        "bullet_point": (
                            "Initial jobless claims later printed near **215,000**, while "
                            "existing home sales fell 2.4% in June, keeping the soft-landing "
                            "vs sticky-inflation debate alive ahead of FOMC minutes."
                        ),
                        "sources": ["CTRY-US-2"],
                    },
                    {
                        "bullet_point": (
                            "Geopolitical risk stayed elevated as US-Iran strikes resumed, "
                            "feeding oil volatility and complicating the Fed's inflation path."
                        ),
                        "sources": ["CTRY-US-3"],
                    },
                ],
            },
            {
                "entity_id": "13FF12",
                "entity_info": {
                    "id": "13FF12",
                    "name": "China",
                    "description": "People's Republic of China",
                    "entity_type": "COUNTRY",
                    "company_type": None,
                    "country": "China",
                    "sector": None,
                    "industry_group": None,
                    "industry": None,
                    "ticker": None,
                    "webpage": None,
                },
                "content": [
                    {
                        "bullet_point": (
                            "PBoC newly flagged **\"structural divergence\"**, which analysts "
                            "read as raising the odds of proactive easing in H2 as imported "
                            "inflation pressures ease."
                        ),
                        "sources": ["CTRY-CN-1"],
                    },
                    {
                        "bullet_point": (
                            "Consumer inflation slowed while producer prices climbed to a "
                            "nearly four-year high, underscoring weak household demand versus "
                            "firmer upstream/high-tech pricing power."
                        ),
                        "sources": ["CTRY-CN-2"],
                    },
                    {
                        "bullet_point": (
                            "The IMF lifted China's 2026 growth forecast by 0.2pp to **4.6%**, "
                            "citing stronger Q1 public investment, high-tech manufacturing, "
                            "and exports."
                        ),
                        "sources": ["CTRY-CN-3"],
                    },
                ],
            },
            {
                "entity_id": "E96159",
                "entity_info": {
                    "id": "E96159",
                    "name": "Germany",
                    "description": "Federal Republic of Germany",
                    "entity_type": "COUNTRY",
                    "company_type": None,
                    "country": "Germany",
                    "sector": None,
                    "industry_group": None,
                    "industry": None,
                    "ticker": None,
                    "webpage": None,
                },
                "content": [
                    {
                        "bullet_point": (
                            "The government agreed a package of **30+ reform bills** "
                            "(tax, labor flexibility, bureaucracy cuts), supporting a better "
                            "business-environment outlook into 2030."
                        ),
                        "sources": ["CTRY-DE-1"],
                    },
                    {
                        "bullet_point": (
                            "Defense spending is set to rise toward **3.1% of GDP** by 2027, "
                            "prioritizing European suppliers and adding industrial demand."
                        ),
                        "sources": ["CTRY-DE-1"],
                    },
                    {
                        "bullet_point": (
                            "May trade surplus widened to **€19.1bn** as exports rose 0.9% m/m "
                            "and imports fell 2.5%, even as manufacturing still faces Chinese "
                            "competition, energy costs, and US tariff risk."
                        ),
                        "sources": ["CTRY-DE-2"],
                    },
                ],
            },
            {
                "entity_id": "3725B9",
                "entity_info": {
                    "id": "3725B9",
                    "name": "Japan",
                    "description": "Japan",
                    "entity_type": "COUNTRY",
                    "company_type": None,
                    "country": "Japan",
                    "sector": None,
                    "industry_group": None,
                    "industry": None,
                    "ticker": None,
                    "webpage": None,
                },
                "content": [
                    {
                        "bullet_point": (
                            "Bank lending remained at the strongest level since March 2021 "
                            "even after the BoJ raised its policy rate to **1%**, the highest "
                            "since 1995."
                        ),
                        "sources": ["CTRY-JP-1"],
                    },
                    {
                        "bullet_point": (
                            "Producer prices accelerated (May PPI +6.3% y/y), reinforcing "
                            "concerns that energy-driven inflation could spill into broader "
                            "price pressures."
                        ),
                        "sources": ["CTRY-JP-2"],
                    },
                    {
                        "bullet_point": (
                            "USD/JPY stayed elevated near **162**, keeping intervention risk "
                            "and energy-import cost sensitivity in focus."
                        ),
                        "sources": ["CTRY-JP-3"],
                    },
                ],
            },
            {
                "entity_id": "C4EEAD",
                "entity_info": {
                    "id": "C4EEAD",
                    "name": "India",
                    "description": "Republic of India",
                    "entity_type": "COUNTRY",
                    "company_type": None,
                    "country": "India",
                    "sector": None,
                    "industry_group": None,
                    "industry": None,
                    "ticker": None,
                    "webpage": None,
                },
                "content": [
                    {
                        "bullet_point": (
                            "The IMF cut India's 2026 growth forecast to **6.4%** (-0.1pp) "
                            "while raising 2027 to 6.7%, still among the fastest major-economy "
                            "growth rates."
                        ),
                        "sources": ["CTRY-IN-1"],
                    },
                    {
                        "bullet_point": (
                            "Domestic momentum remains supported by private consumption and "
                            "services, even as fuel-price volatility from West Asia remains a "
                            "macro risk."
                        ),
                        "sources": ["CTRY-IN-1"],
                    },
                ],
            },
        ],
        "source_metadata": {
            "CTRY-US-1": {
                "ref_id": 1,
                "document_id": "31BEE214B9ED45E6083D02888F07F361",
                "headline": "US economy undershoots forecasts with 57,000 jobs added in June",
                "ts": "2026-07-02T12:31:44+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "FT",
                "source_name": "Financial Times",
                "source_rank": 0,
                "url": "https://app.bigdata.com/documents/31BEE214B9ED45E6083D02888F07F361",
                "chunk_id": 3,
                "text": "US government bonds rallied... Futures traders are now expecting the central bank to lift borrowing costs by December.",
                "highlights": [],
            },
            "CTRY-US-2": {
                "ref_id": 2,
                "document_id": "F45C3555EB2AD79CF18A0EAADDA01CA2",
                "headline": "Sector Update: Financial Stocks Rise Thursday Afternoon",
                "ts": "2026-07-09T17:54:04+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "MT",
                "source_name": "MT Newswires",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/F45C3555EB2AD79CF18A0EAADDA01CA2",
                "chunk_id": 1,
                "text": "US initial jobless claims fell... Existing home sales fell 2.4%...",
                "highlights": [],
            },
            "CTRY-US-3": {
                "ref_id": 3,
                "document_id": "EB91D4736C32011A829890F3750A55BA",
                "headline": "Treasury yields steady as traders await U.S. domestic economic data amid Iran flare-up",
                "ts": "2026-07-09T08:49:43+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "CNBC",
                "source_name": "CNBC",
                "source_rank": 0,
                "url": "https://app.bigdata.com/documents/EB91D4736C32011A829890F3750A55BA",
                "chunk_id": 2,
                "text": "Markets are now awaiting fresh data on jobs and home sales... global energy prices eased after US strikes...",
                "highlights": [],
            },
            "CTRY-CN-1": {
                "ref_id": 4,
                "document_id": "9CB6730E56636E80F2D561BC1EC27D01",
                "headline": "PBOC to enhance policy adjustments and targeted approach",
                "ts": "2026-07-09T16:51:00+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "CD",
                "source_name": "China Daily (English)",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/9CB6730E56636E80F2D561BC1EC27D01",
                "chunk_id": 1,
                "text": "China's central bank has newly flagged structural divergence...",
                "highlights": [],
            },
            "CTRY-CN-2": {
                "ref_id": 5,
                "document_id": "49B4EE63362A313A7A3682BA840A17EB",
                "headline": "China's Consumer Inflation Slows as Producer Prices Climb to Nearly Four-Year High",
                "ts": "2026-07-09T03:41:22+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "MT",
                "source_name": "MT Newswires - Asia Pacific",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/49B4EE63362A313A7A3682BA840A17EB",
                "chunk_id": 3,
                "text": "The latest inflation data highlights the uneven nature of China's economic recovery...",
                "highlights": [],
            },
            "CTRY-CN-3": {
                "ref_id": 6,
                "document_id": "DFDA53754AC359EEBB34BDC49BFB4170",
                "headline": "China's growth outlook boosted by resilience",
                "ts": "2026-07-09T23:04:00+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "CD",
                "source_name": "China Daily (English)",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/DFDA53754AC359EEBB34BDC49BFB4170",
                "chunk_id": 2,
                "text": "the International Monetary Fund lifted its 2026 growth forecast for China by 0.2 percentage points to 4.6 percent...",
                "highlights": [],
            },
            "CTRY-DE-1": {
                "ref_id": 7,
                "document_id": "0CBC05B6BF2E7AEC51FF754B1B8A1D2E",
                "headline": "Five-year forecast : Germany",
                "ts": "2026-07-09T17:41:14+00:00",
                "document_scope": "research",
                "language": "English",
                "source_key": "EIU",
                "source_name": "The Economist",
                "source_rank": 0,
                "url": "https://app.bigdata.com/documents/0CBC05B6BF2E7AEC51FF754B1B8A1D2E",
                "chunk_id": 7,
                "text": "On July 1st the government agreed on a substantial package of more than 30 reform bills...",
                "highlights": [],
            },
            "CTRY-DE-2": {
                "ref_id": 8,
                "document_id": "D9FE44E213B04281116B0BF19BBEC431",
                "headline": "German DAX Index Climbs; SAP Slips After EU Accepts Antitrust Commitments",
                "ts": "2026-07-09T15:54:19+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "MT",
                "source_name": "MT Newswires - EMEA",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/D9FE44E213B04281116B0BF19BBEC431",
                "chunk_id": 2,
                "text": "Germany's calendar and seasonally adjusted trade surplus was 19.1 billion euros in May...",
                "highlights": [],
            },
            "CTRY-JP-1": {
                "ref_id": 9,
                "document_id": "3D934F9E3C458BADB27CC705877E029F",
                "headline": "Japan Bank Lending Remains at Strongest Level Since March 2021",
                "ts": "2026-07-08T03:39:53+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "MT",
                "source_name": "MT Newswires - Asia Pacific",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/3D934F9E3C458BADB27CC705877E029F",
                "chunk_id": 2,
                "text": "The BOJ raised its policy rate to 1% earlier in June...",
                "highlights": [],
            },
            "CTRY-JP-2": {
                "ref_id": 10,
                "document_id": "37D865F627F2A840CB734FFB8A280EAE",
                "headline": "Japan hikes rates to 1%, highest since 1995",
                "ts": "2026-06-16T00:00:00+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "AA",
                "source_name": "Anadolu Agency",
                "source_rank": 2,
                "url": "https://app.bigdata.com/documents/37D865F627F2A840CB734FFB8A280EAE",
                "chunk_id": 2,
                "text": "Japan's producer price index rose 6.3% year-on-year in May...",
                "highlights": [],
            },
            "CTRY-JP-3": {
                "ref_id": 11,
                "document_id": "A945C1C91F1BA8FF7F64B1C2DA999F7F",
                "headline": "Japanese Yen rises as US jobless claims fail to support US Dollar",
                "ts": "2026-07-09T16:12:18+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "FX",
                "source_name": "FXStreet News",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/A945C1C91F1BA8FF7F64B1C2DA999F7F",
                "chunk_id": 2,
                "text": "On the 4-hour chart, USD/JPY trades at 162.37...",
                "highlights": [],
            },
            "CTRY-IN-1": {
                "ref_id": 12,
                "document_id": "DA38B337777EB921B5EEF99E1EA5BC2A",
                "headline": "IMF Cuts India Growth Forecast for 2026 to 6.4%",
                "ts": "2026-07-09T00:32:29+00:00",
                "document_scope": "news",
                "language": "English",
                "source_key": "MT",
                "source_name": "MT Newswires - Asia Pacific",
                "source_rank": 1,
                "url": "https://app.bigdata.com/documents/DA38B337777EB921B5EEF99E1EA5BC2A",
                "chunk_id": 1,
                "text": "the IMF expects the country's economy to grow 6.4% in 2026...",
                "highlights": [],
            },
        },
    },
)


def all_demo_example_models() -> list[tuple[SQLWorkflowStatus, SQLBriefReport]]:
    return [
        (COMMODITIES_EXAMPLE_STATUS, COMMODITIES_EXAMPLE_REPORT),
        (COUNTRIES_EXAMPLE_STATUS, COUNTRIES_EXAMPLE_REPORT),
    ]
