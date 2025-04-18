# cli_parser.py
import os

class CLIParser:
    """
    Cisco IOS-like CLI для керування IoT мережею.
    Підтримуються команди:
      - show ip interface brief
      - ping <id1> <id2>
      - shutdown <device_id>
      - no shutdown <device_id>
      - link <src> <dst> [bw <Kbps>] [delay <ms>]
      - add <device_type> [<device_id>]
      - remove <device_id>
      - save <filename>
      - load <filename>
    """
    def __init__(self, network):
        self.network = network

    def parse_command(self, command):
        parts = command.strip().split()
        if not parts:
            return ""
        cmd = parts[0].lower()

        # show ip interface brief
        if cmd == "show" and len(parts) == 4 and parts[1].lower() == "ip" and parts[2].lower() == "interface" and parts[3].lower() == "brief":
            return self._show_devices()

        # ping <id1> <id2>
        if cmd == "ping" and len(parts) == 3:
            id1, id2 = parts[1], parts[2]
            if any((l.src == id1 and l.dst == id2) or (l.src == id2 and l.dst == id1) for l in self.network.list_links()):
                return f"Ping {id1} → {id2}: OK"
            else:
                return f"Ping {id1} → {id2}: Timeout"

        # shutdown <device_id>
        if cmd == "shutdown" and len(parts) == 2:
            dev = self.network.get_device(parts[1])
            if not dev:
                return f"% Device {parts[1]} not found"
            dev.disable()
            return f"% Device {dev.device_id} has been shutdown"

        # no shutdown <device_id>
        if cmd == "no" and len(parts) == 3 and parts[1].lower() == "shutdown":
            dev = self.network.get_device(parts[2])
            if not dev:
                return f"% Device {parts[2]} not found"
            dev.enable()
            return f"% Device {dev.device_id} has been enabled"

        # link <src> <dst> [bw <Kbps>] [delay <ms>]
        if cmd == "link" and len(parts) >= 3:
            src, dst = parts[1], parts[2]
            # парсинг опцій
            bw = 1000
            delay = 10
            try:
                for i in range(3, len(parts), 2):
                    if parts[i].lower() == 'bw' and i+1 < len(parts):
                        bw = int(parts[i+1])
                    if parts[i].lower() == 'delay' and i+1 < len(parts):
                        delay = int(parts[i+1])
            except ValueError:
                return "% Invalid parameters for link"
            link = self.network.add_link(src, dst, bandwidth=bw, delay=delay)
            if link:
                return f"% Link {src}↔{dst} established (BW={bw}Kbps, delay={delay}ms)"
            else:
                return f"% Failed to link {src} and {dst}"

        # add <device_type> [<device_id>]
        if cmd == "add" and len(parts) >= 2:
            dev_type = parts[1]
            dev_id = parts[2] if len(parts) == 3 else None
            d = self.network.add_device(dev_type, dev_id)
            return f"% Device {d.device_id} added with IP {d.ip_address}"

        # remove <device_id>
        if cmd == "remove" and len(parts) == 2:
            dev_id = parts[1]
            ok = self.network.remove_device(dev_id)
            return f"% Device {dev_id} removed" if ok else f"% Device {dev_id} not found"

        # save <filename>
        if cmd == "save" and len(parts) == 2:
            fn = parts[1]
            if not fn.lower().endswith('.json'):
                fn += '.json'
            ok = self.network.save_to_file(fn)
            return f"% Configuration saved to {fn}" if ok else "% Save error"

        # load <filename>
        if cmd == "load" and len(parts) == 2:
            fn = parts[1]
            if not os.path.isfile(fn):
                return f"% File {fn} not found"
            ok = self.network.load_from_file(fn)
            return f"% Configuration loaded from {fn}" if ok else "% Load error"

        return "% Unknown command"

    def _show_devices(self):
        devs = self.network.list_devices()
        if not devs:
            return "% No devices"
        lines = [f"Device ID    Type     IP Address        Status"]
        for d in devs:
            lines.append(f"{d.device_id:<12}{d.device_type:<8}{d.ip_address:<16}{d.status}")
        return "\n".join(lines)