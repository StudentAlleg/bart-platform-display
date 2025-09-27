import time


class UtilTime():
    @staticmethod
    def absolute_time(time_s: float) -> str:
        """

        :param time_s: UNIX time (seconds)
        :return: the formatted time string
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_s))

    @staticmethod
    def relative_seconds(time_s: float) -> float:
        """

        :param time_s: UNIX time (seconds)
        :return: the number of seconds until time_s
        """
        return time_s - UtilTime.now()

    @staticmethod
    def now() -> int:
        return int(time.time())