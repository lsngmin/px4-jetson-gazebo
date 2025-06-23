import threading, logging, time

class Streamer(threading.Thread):
    def __init__(self, command, sleep=0.02):
        super().__init__(daemon=True)
        self.manager = None
        self.command = command
        self.sleep = sleep
        self._stop_event = threading.Event()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._x = None
        self._y = None
        self._z = None

    def with_manager(self , manager, sleep=0.02):
        self.manager = manager
        self.sleep = sleep
        return self

    def with_xyz(self, x, y, z, sleep=0.02):
        self._x = x
        self._y = y
        self._z = z
        self.sleep = sleep
        print("cc")
        return self

    def run(self):
        self._logger.info("Setpoint 스트리밍 시작")

        while not self._stop_event.is_set():
            try:
                x = self.manager.current['x'] if self._x is None else self._x
                y = self.manager.current['y'] if self._y is None else self._y
                z = self.manager.current['z'] if self._z is None else self._z
                print(x, y, z)

                self.command.send_setpoint(x, y, z)
                time.sleep(self.sleep)
            except Exception as e:
                self._logger.error(f"Setpoint 전송 오류: {e}")
                time.sleep(self.sleep)
        self._logger.info("Setpoint 스트리밍 종료")

    def stop(self):
        self._stop_event.set()