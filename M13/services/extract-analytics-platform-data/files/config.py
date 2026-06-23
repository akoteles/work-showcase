#!/usr/bin/env python

import os
import json
from helpers import get_secret

DATAPOOL_BIGQUERY_SA = json.loads(
    get_secret(os.getenv("DATAPOOL_BIGQUERY_SA"), os.getenv("GCP_SECRET_PROJECT_ID"))
)

ANALYTICS_PLATFORM_API_URL = "https://api.atinternet.io"

ANALYTICS_PLATFORM_GET_ROW_COUNT_URL = "/v3/data/getRowCount"

ANALYTICS_PLATFORM_GET_DATA_URL = "/v3/data/getData"

ANALYTICS_PLATFORM_QUERIES = {
    "Account1": {
        "get_all_data": {
            "columns": [
                "date",
                "content_id",
                "content_url",
                "page_title_html",
                "content_broadcast_series",
                "content_creator",
                "m_visits",
                "m_bounce_rate",
                "page_chapter1",
                "page_chapter2",
                "src",
                "m_k_suchmaschinen_in_",
                "product_distribution",
                "m_discover_anteil",
            ],
            "sort": ["-m_visits"],
            "space": {"s": [100001]},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "options": {"ignore_null_properties": True, "eco_mode": True},
        },
        "get_search_traffic_data": {
            "columns": ["date", "src", "m_visits"],
            "sort": ["-m_visits"],
            "space": {"s": [100001]},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "page-num": 1,
            "options": {},
        },
        "get_discover_data": {
            "columns": [
                "date",
                "m_discover_anteil",
            ],
            "sort": ["-m_discover_anteil"],
            "space": {"s": [100001]},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "page-num": 1,
            "options": {},
        },
    },
    "Account3": {
        "get_all_data": {
            "columns": [
                "date",
                "content_id",
                "event_url",
                "page_title_html",
                "av_show",
                "tgp_content_creator_institution",
                "m_visits",
                "m_bounce_rate",
                "tgp_page_chapter1",
                "src",
                "tgp_product_platform",
            ],
            "sort": ["-m_visits"],
            "space": {"l2s": {"s": 100002, "l2": 1, "l2name": "www.example-broadcaster.com"}},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "page-num": 1,
            "options": {},
        },
        "get_search_traffic_data": {
            "columns": ["date", "src", "m_visits"],
            "sort": ["-m_visits"],
            "space": {"l2s": {"s": 100002, "l2": 1, "l2name": "www.example-broadcaster.com"}},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "page-num": 1,
            "options": {},
        },
        "get_discover_data": {
            "columns": ["date", "m_visits", "m_visits_chrome_content_suggestions"],
            "sort": ["-m_visits_chrome_content_suggestions"],
            "space": {"l2s": {"s": 100002, "l2": 1, "l2name": "www.example-broadcaster.com"}},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "page-num": 1,
            "options": {},
        },
    },
    "Account2": {
        "get_all_data": {
            "columns": [
                "date",
                "content_id",
                "event_url",
                "page_title_html",
                "av_show",
                "brand",
                "page_chapter1",
                "m_visits",
                "m_bounce_rate",
                "page_chapter2",
                "src",
                "m_visits_traffic_quelle_search_engine",
                "platform",
                "m_visits_google_discover",
            ],
            "sort": ["-m_visits"],
            "space": {"s": [100003, 100004]},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "page-num": 1,
            "options": {},
        },
        "get_search_traffic_data": {
            "columns": ["date", "src", "m_visits"],
            "sort": ["-m_visits"],
            "space": {"s": [100003, 100004]},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "page-num": 1,
            "options": {},
        },
    },
    "Account4": {
        "get_all_data": {
            "columns": [
                "date",
                "page_content_id",
                "event_url",
                "page_content_title",
                "page_show",
                "page_institution",
                "m_visits",
                "m_bounce_rate",
                "src",
                "m_suchmaschinenanteil",
                "application_group",
                "m_anteil_google_discover_am_suchmaschinent",
                "page_publisher",
            ],
            "sort": ["-m_visits"],
            "space": {"s": [100005]},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "options": {"ignore_null_properties": True, "eco_mode": True},
        },
        "get_search_traffic_data": {
            "columns": ["date", "src", "m_visits"],
            "sort": ["-m_visits"],
            "space": {"s": [100005]},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "page-num": 1,
            "options": {},
        },
        "get_discover_data": {
            "columns": [
                "date",
                "m_anteil_google_discover_am_suchmaschinent",
            ],
            "sort": ["-m_anteil_google_discover_am_suchmaschinent"],
            "space": {"s": [100005]},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "page-num": 1,
            "options": {},
        },
    },
    "Account5": {
        "get_all_data": {
            "columns": [
                "date",
                "av_content_id",
                "page_url",
                "page_content_title",
                "av_show",
                "page_publisher",
                "m_visits",
                "m_bounce_rate",
                "src",
                "m_suchmaschinenanteil",
                "application_group",
                "m_anteil_google_discover_am_suchmaschinent",
            ],
            "sort": ["-m_visits"],
            "space": {"s": [100006]},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "options": {"ignore_null_properties": True, "eco_mode": True},
        },
        "get_search_traffic_data": {
            "columns": ["date", "src", "m_visits"],
            "sort": ["-m_visits"],
            "space": {"s": [100006]},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "page-num": 1,
            "options": {},
        },
        "get_discover_data": {
            "columns": [
                "date",
                "m_anteil_google_discover_am_suchmaschinent",
            ],
            "sort": ["-m_anteil_google_discover_am_suchmaschinent"],
            "space": {"s": [100006]},
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "max-results": 10000,
            "page-num": 1,
            "options": {},
        },
    },
    "Account6": {
        "get_all_data": {
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "page-num": 1,
            "max-results": 10000,
        },
        "get_search_traffic_data": {
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "page-num": 1,
            "max-results": 10000,
        },
        "get_discover_data": {
            "period": {"p1": [{"type": "D", "start": "", "end": ""}]},
            "page-num": 1,
            "max-results": 10000,
        },
    },
}

ACCOUNT1_ANALYTICS_PLATFORM_MAPPING = {
    "date": "Date",
    "content_id": "ContentID",
    "content_url": "URL",
    "page_title_html": "PageTitle",
    "content_broadcast_series": "Series",
    "content_creator": "Publisher",
    "m_visits": "Visits",
    "m_bounce_rate": "BounceRate",
    "src": "TrafficSource",
    "m_k_suchmaschinen_in_": "SearchEngineShare",
    "product_distribution": "DistributionGroup",
    "m_discover_anteil": "GoogleDiscoverSearchEngineShare",
}

ACCOUNT3_ANALYTICS_PLATFORM_MAPPING = {
    "date": "Date",
    "content_id": "ContentID",
    "event_url": "URL",
    "page_title_html": "PageTitle",
    "av_show": "Series",
    "tgp_content_creator_institution": "Publisher",
    "m_visits": "Visits",
    "m_bounce_rate": "BounceRate",
    "tgp_page_chapter1": "Category",
    "src": "TrafficSource",
    "tgp_product_platform": "DistributionGroup",
}

ACCOUNT2_ANALYTICS_PLATFORM_MAPPING = {
    "date": "Date",
    "content_id": "ContentID",
    "event_url": "URL",
    "page_title_html": "PageTitle",
    "av_show": "Series",
    "brand": "Publisher",
    "page_chapter1": "Genre",
    "m_visits": "Visits",
    "m_bounce_rate": "BounceRate",
    "page_chapter2": "Category",
    "src": "TrafficSource",
    "m_visits_traffic_quelle_search_engine": "SearchEngineShare",
    "platform": "DistributionGroup",
    "m_visits_google_discover": "GoogleDiscoverSearchEngineShare",
}

ACCOUNT4_ANALYTICS_PLATFORM_MAPPING = {
    "date": "Date",
    "page_content_id": "ContentID",
    "event_url": "URL",
    "page_content_title": "PageTitle",
    "page_show": "Series",
    "page_institution": "Publisher",
    "m_visits": "Visits",
    "m_bounce_rate": "BounceRate",
    "src": "TrafficSource",
    "m_suchmaschinenanteil": "SearchEngineShare",
    "application_group": "DistributionGroup",
    "m_anteil_google_discover_am_suchmaschinent": "GoogleDiscoverSearchEngineShare",
    "page_publisher": "Broadcaster",
}

ACCOUNT5_ANALYTICS_PLATFORM_MAPPING = {
    "date": "Date",
    "av_content_id": "ContentID",
    "page_url": "URL",
    "page_content_title": "PageTitle",
    "av_show": "Series",
    "page_publisher": "Publisher",
    "m_visits": "Visits",
    "m_bounce_rate": "BounceRate",
    "src": "TrafficSource",
    "m_suchmaschinenanteil": "SearchEngineShare",
    "application_group": "DistributionGroup",
    "m_anteil_google_discover_am_suchmaschinent": "GoogleDiscoverSearchEngineShare",
}

ACCOUNT6_ANALYTICS_PLATFORM_MAPPING = {
    "date": "Date",
    "content_id": "ContentID",
    "url": "URL",
    "page": "PageTitle",
    "src": "TrafficSource",
    "src_referrer_site_url": "Referrer",
    "herkunft": "DistributionGroup",
    "m_visits": "Visits",
    "m_visits_web": "VisitsWeb",
    "m_visits_app": "VisitsApp",
    "m_bounces": "Bounces",
    "m_visits_search": "Visits_SearchEngine",
    "m_visits_chrome_content_suggestions": "Visits_Google_Discover",
}

ACCOUNT_ANALYTICS_PLATFORM_MAPPINGS = {
    "Account1": ACCOUNT1_ANALYTICS_PLATFORM_MAPPING,
    "Account3": ACCOUNT3_ANALYTICS_PLATFORM_MAPPING,
    "Account2": ACCOUNT2_ANALYTICS_PLATFORM_MAPPING,
    "Account4": ACCOUNT4_ANALYTICS_PLATFORM_MAPPING,
    "Account5": ACCOUNT5_ANALYTICS_PLATFORM_MAPPING,
    "Account6": ACCOUNT6_ANALYTICS_PLATFORM_MAPPING,
}

BQ_ANALYTICS_PLATFORM_COLUMNS = {
    "Account1": [
        "Date",
        "ContentID",
        "URL",
        "PageTitle",
        "Series",
        "Publisher",
        "Genre",
        "Category",
        "TrafficSource",
        "DistributionGroup",
        "Visits",
        "BounceRate",
        "GoogleDiscoverSearchEngineShare",
        "SearchEngineShare",
    ],
    "Account3": [
        "Date",
        "ContentID",
        "URL",
        "PageTitle",
        "Series",
        "Publisher",
        "Genre",
        "Category",
        "TrafficSource",
        "DistributionGroup",
        "Visits",
        "BounceRate",
        "GoogleDiscoverSearchEngineShare",
        "SearchEngineShare",
    ],
    "Account2": [
        "Date",
        "ContentID",
        "URL",
        "PageTitle",
        "Series",
        "Publisher",
        "Genre",
        "Category",
        "TrafficSource",
        "DistributionGroup",
        "Visits",
        "BounceRate",
        "GoogleDiscoverSearchEngineShare",
        "SearchEngineShare",
    ],
    "Account4": [
        "Date",
        "ContentID",
        "URL",
        "PageTitle",
        "Series",
        "Publisher",
        "Genre",
        "Category",
        "TrafficSource",
        "DistributionGroup",
        "Visits",
        "BounceRate",
        "GoogleDiscoverSearchEngineShare",
        "SearchEngineShare",
        "Broadcaster",
    ],
    "Account5": [
        "Date",
        "ContentID",
        "URL",
        "PageTitle",
        "Series",
        "Publisher",
        "Genre",
        "Category",
        "TrafficSource",
        "DistributionGroup",
        "Visits",
        "BounceRate",
        "GoogleDiscoverSearchEngineShare",
        "SearchEngineShare",
    ],
    "Account6": [
        "Date",
        "ContentID",
        "URL",
        "PageTitle",
        "TrafficSource",
        "Referrer",
        "DistributionGroup",
        "Visits",
        "VisitsWeb",
        "VisitsApp",
        "Bounces",
        "Visits_SearchEngine",
        "Visits_Google_Discover",
        "Series",
        "Publisher",
        "Genre",
        "Category",
        "BounceRate_calc",
        "SearchEngineShare_calc",
        "GoogleDiscoverSearchEngineShare_calc",
    ],
}

BQ_ANALYTICS_PLATFORM_STR_COLUMNS = {
    "Account1": [
        "ContentID",
        "URL",
        "PageTitle",
        "Series",
        "Publisher",
        "Genre",
        "Category",
        "TrafficSource",
        "DistributionGroup",
    ],
    "Account3": [
        "ContentID",
        "URL",
        "PageTitle",
        "Series",
        "Publisher",
        "Genre",
        "Category",
        "TrafficSource",
        "DistributionGroup",
    ],
    "Account2": [
        "ContentID",
        "URL",
        "PageTitle",
        "Series",
        "Publisher",
        "Genre",
        "Category",
        "TrafficSource",
        "DistributionGroup",
    ],
    "Account4": [
        "ContentID",
        "URL",
        "PageTitle",
        "Series",
        "Publisher",
        "Genre",
        "Category",
        "TrafficSource",
        "DistributionGroup",
        "Broadcaster",
    ],
    "Account5": [
        "ContentID",
        "URL",
        "PageTitle",
        "Series",
        "Publisher",
        "Genre",
        "Category",
        "TrafficSource",
        "DistributionGroup",
    ],
    "Account6": [
        "ContentID",
        "URL",
        "PageTitle",
        "TrafficSource",
        "Referrer",
        "DistributionGroup",
        "Series",
        "Publisher",
        "Genre",
        "Category",
    ],
}

BQ_ANALYTICS_PLATFORM_INT_COLUMNS = {
    "Account1": ["Visits"],
    "Account3": ["Visits"],
    "Account2": ["Visits"],
    "Account4": ["Visits"],
    "Account5": ["Visits"],
    "Account6": [
        "Visits",
        "VisitsWeb",
        "VisitsApp",
        "Bounces",
        "Visits_SearchEngine",
        "Visits_Google_Discover",
    ],
}

BQ_ANALYTICS_PLATFORM_FLOAT_COLUMNS = {
    "Account1": ["BounceRate", "GoogleDiscoverSearchEngineShare", "SearchEngineShare"],
    "Account3": [
        "BounceRate",
        "GoogleDiscoverSearchEngineShare",
        "SearchEngineShare",
    ],
    "Account2": [
        "BounceRate",
        "GoogleDiscoverSearchEngineShare",
        "SearchEngineShare",
    ],
    "Account4": [
        "BounceRate",
        "GoogleDiscoverSearchEngineShare",
        "SearchEngineShare",
    ],
    "Account5": [
        "BounceRate",
        "GoogleDiscoverSearchEngineShare",
        "SearchEngineShare",
    ],
    "Account6": [
        "BounceRate_calc",
        "SearchEngineShare_calc",
        "GoogleDiscoverSearchEngineShare_calc",
    ],
}

BQ_ANALYTICS_PLATFORM_CALCULATED_COLUMNS = {
    "Account1": [],
    "Account3": [],
    "Account2": [],
    "Account4": [],
    "Account5": [],
    "Account6": [
        {
            "output": "BounceRate_calc",
            "numerator": "Bounces",
            "denominator": "Visits",
        },
        {
            "output": "SearchEngineShare_calc",
            "numerator": "Visits_SearchEngine",
            "denominator_fallbacks": ["VisitsWeb", "Visits"],
        },
        {
            "output": "GoogleDiscoverSearchEngineShare_calc",
            "numerator": "Visits_Google_Discover",
            "denominator_fallbacks": ["VisitsWeb", "Visits"],
        },
    ],
}

BQ_SEARCH_TRAFFIC_COLUMNS = {
    "Account1": ["Date", "TrafficSource", "Visits"],
    "Account3": ["Date", "TrafficSource", "Visits"],
    "Account2": ["Date", "TrafficSource", "Visits"],
    "Account4": ["Date", "TrafficSource", "Visits"],
    "Account5": ["Date", "TrafficSource", "Visits"],
    "Account6": ["Date", "TrafficSource", "Visits"],
}

ACCOUNT1_DISCOVER_MAPPING = {
    "date": "Date",
    "m_discover_anteil": "GoogleDiscoverSearchEngineShare",
}

ACCOUNT3_DISCOVER_MAPPING = {
    "date": "Date",
    "m_visits": "Visits",
    "m_visits_chrome_content_suggestions": "GoogleDiscoverSearchEngineShare",
}

ACCOUNT4_DISCOVER_MAPPING = {
    "date": "Date",
    "m_anteil_google_discover_am_suchmaschinent": "GoogleDiscoverSearchEngineShare",
}

ACCOUNT5_DISCOVER_MAPPING = {
    "date": "Date",
    "m_anteil_google_discover_am_suchmaschinent": "GoogleDiscoverSearchEngineShare",
}

ACCOUNT6_DISCOVER_MAPPING = {
    "date": "Date",
    "m_visits": "Visits",
    "m_visits_web": "VisitsWeb",
    "m_visits_app": "VisitsApp",
    "m_visits_search": "Visits_SearchEngine",
    "m_visits_chrome_content_suggestions": "Visits_Google_Discover",
}

ACCOUNT_DISCOVER_MAPPINGS = {
    "Account1": ACCOUNT1_DISCOVER_MAPPING,
    "Account3": ACCOUNT3_DISCOVER_MAPPING,
    "Account4": ACCOUNT4_DISCOVER_MAPPING,
    "Account5": ACCOUNT5_DISCOVER_MAPPING,
    "Account6": ACCOUNT6_DISCOVER_MAPPING,
}

BQ_DISCOVER_COLUMNS = {
    "Account1": ["Date", "GoogleDiscoverSearchEngineShare"],
    "Account3": ["Date", "Visits", "GoogleDiscoverSearchEngineShare"],
    "Account4": ["Date", "GoogleDiscoverSearchEngineShare"],
    "Account5": ["Date", "GoogleDiscoverSearchEngineShare"],
    "Account6": [
        "Date",
        "Visits",
        "VisitsWeb",
        "VisitsApp",
        "Visits_SearchEngine",
        "Visits_Google_Discover",
        "SearchEngineShare_calc",
        "GoogleDiscoverSearchEngineShare_calc",
    ],
}

BQ_DISCOVER_INT_COLUMNS = {
    "Account1": [],
    "Account3": ["Visits", "GoogleDiscoverSearchEngineShare"],
    "Account4": [],
    "Account5": [],
    "Account6": [
        "Visits",
        "VisitsWeb",
        "VisitsApp",
        "Visits_SearchEngine",
        "Visits_Google_Discover",
    ],
}

BQ_DISCOVER_FLOAT_COLUMNS = {
    "Account1": ["GoogleDiscoverSearchEngineShare"],
    "Account3": [],
    "Account4": ["GoogleDiscoverSearchEngineShare"],
    "Account5": ["GoogleDiscoverSearchEngineShare"],
    "Account6": [
        "SearchEngineShare_calc",
        "GoogleDiscoverSearchEngineShare_calc",
    ],
}

BQ_DISCOVER_CALCULATED_COLUMNS = {
    "Account1": {},
    "Account3": {},
    "Account4": {},
    "Account5": {},
    "Account6": {
        "SearchEngineShare_calc": {
            "numerator": "Visits_SearchEngine",
            "denominator_primary": "VisitsWeb",
            "denominator_fallback": "Visits",
        },
        "GoogleDiscoverSearchEngineShare_calc": {
            "numerator": "Visits_Google_Discover",
            "denominator_primary": "VisitsWeb",
            "denominator_fallback": "Visits",
        },
    },
}
