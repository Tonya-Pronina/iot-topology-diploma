import datetime

class IoTDevice:
    """
    Клас, що описує IoT-пристрій.
    Містить координати x, y для GUI та лог змін статусу.
    """
    def __init__(self, device_id, device_type, ip_address=None, x=0, y=0):
        self.device_id = device_id
        self.device_type = device_type  # Наприклад: "sensor", "lamp", "camera"
        self.ip_address = ip_address or "0.0.0.0"
        self.status = "enabled"         # або "disabled"
        self.x = x                       # координата по X для GUI
        self.y = y                       # координата по Y для GUI
        self.log = []                    # список логів подій

    def enable(self):
        self.status = "enabled"
        self._log_event("Enabled")

    def disable(self):
        self.status = "disabled"
        self._log_event("Disabled")

    def _log_event(self, message):
        """
        Додає запис у лог із міткою часу.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log.append(f"[{timestamp}] {message}")

    def get_log(self):
        """
        Повертає повний лог подій у вигляді рядка.
        """
        return "\n".join(self.log)

    def __str__(self):
        return (f"[{self.device_id}] {self.device_type} "
                f"(IP: {self.ip_address}, Status: {self.status})")