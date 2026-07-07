from enum import StrEnum

from bigdata_client import Bigdata
from bigdata_client.tracking_services import TraceEvent
from bigdata_client.tracking_services import send_trace as bigdata_send_trace


class TraceEventName(StrEnum):
    SERVICE_START = "onPremBriefServiceStart"
    REPORT_GENERATED = "onPremBriefReportGenerated"


class TracingService:
    def __init__(self, api_key: str):
        self.client = Bigdata(api_key=api_key)

    def send_trace(self, event_name: TraceEventName, trace: dict):
        try:
            bigdata_send_trace(
                bigdata_client=self.client,
                trace=TraceEvent(event_name=event_name, properties=trace),
            )
        except Exception:
            pass
