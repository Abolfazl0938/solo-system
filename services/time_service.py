"""Time Service: Provides dual Gregorian and Jalali (Solar Hijri) date & time."""

from datetime import datetime
import jdatetime


class TimeService:

    @staticmethod
    def get_current_timestamps() -> dict:
        """Returns structured Gregorian and Jalali date and time."""
        now = datetime.now()
        j_now = jdatetime.datetime.now()

        return {
            "gregorian_date": now.strftime("%Y-%m-%d"),
            "gregorian_time": now.strftime("%H:%M:%S"),
            "jalali_date": j_now.strftime("%Y/%m/%d"),
            "jalali_time": j_now.strftime("%H:%M:%S"),
            "iso_timestamp": now.isoformat(),
        }

    @staticmethod
    def get_formatted_display() -> dict:
        """Returns clean human-readable strings for UI display."""
        now = datetime.now()
        j_now = jdatetime.datetime.now()

        # Day of week in English and Persian
        days_fa = {
            0: "دوشنبه",
            1: "سه‌شنبه",
            2: "چهارشنبه",
            3: "پنج‌شنبه",
            4: "جمعه",
            5: "شنبه",
            6: "یکشنبه",
        }
        day_fa = days_fa[now.weekday()]
        day_en = now.strftime("%A")

        return {
            "gregorian": f"{day_en}, {now.strftime('%b %d, %Y - %H:%M:%S')}",
            "jalali": f"{day_fa}، {j_now.strftime('%d %B %Y - %H:%M:%S')}",
        }
