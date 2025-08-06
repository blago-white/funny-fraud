from aiogram.filters.callback_data import CallbackData


class LeadCallbackAction:
    VIEW_DETAILED_DATA = "v"


class LeadStatusCallbackData(CallbackData, prefix="lead"):
    session_id: int
    lead_id: int
    action: str = LeadCallbackAction.VIEW_DETAILED_DATA


class RestartSessionData(CallbackData, prefix="restart"):
    session_id: int


class SMSServiceSelectorData(CallbackData, prefix="sms-selector"):
    sms_service: str
