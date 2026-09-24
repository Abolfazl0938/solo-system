import datetime

# اگر jdatetime نصب نیست: pip install jdatetime
try:
    import jdatetime
except ImportError:
    jdatetime = None


class TimeService:
    @staticmethod
    def format_dual_timestamp() -> str:
        """Returns string with Gregorian and Jalali date/time."""
        now = datetime.datetime.now()
        gregorian_str = now.strftime("%Y-%m-%d %H:%M")

        if jdatetime:
            jalali = jdatetime.datetime.now()
            jalali_str = jalali.strftime("%Y/%m/%d")
            return f"{gregorian_str} | {jalali_str}"

        return f"{gregorian_str}"

    @staticmethod
    def get_current_timestamps() -> str:
        """Helper to get current time for logs."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
