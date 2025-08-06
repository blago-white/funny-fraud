from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from bot.handlers import data
from db.transfer import LeadGenResult, LeadGenResultStatus
from parser.utils.sms import mapper


def _get_lead_status(status: str):
    try:
        return {
            LeadGenResultStatus.PHONE_CODE_PROGRESS: "⬆",
            LeadGenResultStatus.FAILED: "🚫",
            LeadGenResultStatus.SUCCESS: "✅",
        }[status]
    except:
        return "⬆"


def _get_button_action(status: LeadGenResultStatus):
    return ""  # TODO: View lead credentials


def generate_leads_statuses_kb(leads: list[LeadGenResult]):
    kb, kb_line = [], []

    for result_id, result in enumerate(leads):
        if result_id % 2 == 0:
            kb.append(kb_line)
            kb_line = []

        action = _get_button_action(status=result.status)

        kb_line.append(InlineKeyboardButton(
            text=f"{_get_lead_status(status=result.status)} "
                 f"#{result.lead_id} | "
                 f"{result.ref_link}",
            callback_data=data.LeadStatusCallbackData(
                session_id=result.session_id,
                lead_id=result.lead_id,
                action=action
            ).pack()
        ))

    kb.append(kb_line)

    kb.append([
        InlineKeyboardButton(
            text="♻Рестарт сессии",
            callback_data=data.RestartSessionData(
                session_id=leads[0].session_id
            ).pack(),
        ),
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=kb
    )


def get_session_presets_kb(
        current_sms_service: str = mapper.HELPERSMS.KEY,
        is_supervised: bool = False,
        strict_mode: bool = False,
):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{
                "🚩" if current_sms_service == mapper.HELPERSMS.KEY else ""
                }☎ Helper",
                callback_data=data.SMSServiceSelectorData(
                    sms_service=mapper.HELPERSMS.KEY
                ).pack()
            )],
            [InlineKeyboardButton(
                text=f"{"✅" if is_supervised else ""}🔮 Оптимизировать с ИИ",
                callback_data=data.UseSupervisorData(use=not is_supervised).pack()
            )],
            [InlineKeyboardButton(
                text=f"{"✅" if strict_mode else ""}⚠ Четкое соблюд. кол-в'а лидов [СС]",
                callback_data=data.StrictLeadsCountModeData(
                    use_strict=not strict_mode
                ).pack()
            )]
        ]
    )
