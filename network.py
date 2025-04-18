# network.py
import json
from device import IoTDevice

class Link:
    """
    З'єднання між двома пристроями з параметрами bandwidth та delay.
    src, dst — ID пристроїв; bandwidth у Kbps; delay у мс.
    """
    def __init__(self, src, dst, bandwidth=1000, delay=10):
        self.src = src
        self.dst = dst
        self.bandwidth = bandwidth  # Kbps
        self.delay = delay          # ms

    def to_dict(self):
        return {
            "src": self.src,
            "dst": self.dst,
            "bandwidth": self.bandwidth,
            "delay": self.delay
        }

class Network:
    def __init__(self):
        self.devices = {}
        self.ip_counter = 1
        self.links = []  # список об'єктів Link

    def add_device(self, device_type, device_id=None, ip_address=None, x=0, y=0):
        if device_id is None:
            device_id = f"{device_type}_{len(self.devices) + 1}"
        if ip_address is None:
            ip_address = f"192.168.1.{self.ip_counter}"
            self.ip_counter += 1
        new_dev = IoTDevice(device_id, device_type, ip_address, x, y)
        self.devices[device_id] = new_dev
        return new_dev

    def get_device(self, device_id):
        return self.devices.get(device_id)

    def list_devices(self):
        return list(self.devices.values())

    def remove_device(self, device_id):
        if device_id not in self.devices:
            return False
        # Видалити всі зв'язки, що містять цей ID
        self.links = [l for l in self.links if l.src != device_id and l.dst != device_id]
        del self.devices[device_id]
        return True

    def add_link(self, src, dst, bandwidth=1000, delay=10):
        """
        Створити зв'язок між двома пристроями з параметрами.
        Повертає об'єкт Link або None, якщо не вдалося.
        """
        if src not in self.devices or dst not in self.devices:
            return None
        # Перевірка дублювання
        for link in self.links:
            if (link.src == src and link.dst == dst) or (link.src == dst and link.dst == src):
                return None
        new_link = Link(src, dst, bandwidth, delay)
        self.links.append(new_link)
        return new_link

    def connect(self, src, dst):
        # для сумісності з попередніми командами
        return self.add_link(src, dst)

    def list_links(self):
        return list(self.links)

    # JSON persistence
    def to_dict(self):
        devices = []
        for d in self.devices.values():
            devices.append({
                "device_id":   d.device_id,
                "device_type": d.device_type,
                "ip_address":  d.ip_address,
                "status":      d.status,
                "x":           d.x,
                "y":           d.y,
                "log":         d.get_log().split("\n")
            })
        return {
            "ip_counter": self.ip_counter,
            "devices":    devices,
            "links":      [l.to_dict() for l in self.links]
        }

    def save_to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        return True

    def load_from_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Очищення
        self.devices.clear()
        self.links.clear()
        self.ip_counter = data.get("ip_counter", 1)
        # Відновити пристрої
        for dev in data.get("devices", []):
            d = self.add_device(
                dev["device_type"],
                device_id=dev["device_id"],
                ip_address=dev["ip_address"],
                x=dev.get("x", 0),
                y=dev.get("y", 0)
            )
            if dev.get("status") == "disabled":
                d.disable()
            for entry in dev.get("log", []):
                d.log.append(entry)
        # Відновити зв'язки
        for link in data.get("links", []):
            self.add_link(
                link["src"], link["dst"],
                bandwidth=link.get("bandwidth", 1000),
                delay=link.get("delay", 10)
            )
        return True
