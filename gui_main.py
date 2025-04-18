import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLineEdit, QTextEdit, QListWidget, QSplitter,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QPushButton,
    QFileDialog, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor

class DeviceNode(QGraphicsEllipseItem):
    def __init__(self, device, main_window, radius=30):
        super().__init__(-radius, -radius, 2*radius, 2*radius)
        self.device = device
        self.main_window = main_window
        self.update_appearance()
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable, True)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges, True)

        self.label = QGraphicsTextItem(device.device_id, parent=self)
        self.label.setDefaultTextColor(Qt.black)
        bb = self.label.boundingRect()
        self.label.setPos(-bb.width()/2, -bb.height()/2)

        self.setToolTip(f"ID: {device.device_id}\nIP: {device.ip_address}\nStatus: {device.status}")

    def update_appearance(self):
        color = QColor(100, 200, 250) if self.device.status == "enabled" else QColor(180, 180, 180)
        self.setBrush(QBrush(color))

    def itemChange(self, change, value):
        if change == QGraphicsEllipseItem.ItemPositionHasChanged:
            pos = value
            self.device.x = pos.x()
            self.device.y = pos.y()
            self.main_window.refresh_lines()
        return super().itemChange(change, value)

class MainWindow(QMainWindow):
    def __init__(self, network, cli_parser):
        super().__init__()
        self.network = network
        self.cli_parser = cli_parser
        self.node_items = {}
        self.line_items = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("IoT Topology")
        central = QWidget()
        main_layout = QVBoxLayout(central)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        load_btn = QPushButton("Load")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(load_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        splitter = QSplitter(Qt.Horizontal)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        splitter.addWidget(self.view)

        self.device_list = QListWidget()
        splitter.addWidget(self.device_list)
        splitter.setSizes([500, 200])
        main_layout.addWidget(splitter)

        self.cli_line = QLineEdit()
        self.cli_output = QTextEdit()
        self.cli_output.setReadOnly(True)
        main_layout.addWidget(self.cli_line)
        main_layout.addWidget(self.cli_output)

        self.setCentralWidget(central)
        self.cli_line.returnPressed.connect(self.handle_command)
        save_btn.clicked.connect(self.save_topology)
        load_btn.clicked.connect(self.load_topology)

    def handle_command(self):
        cmd = self.cli_line.text()
        res = self.cli_parser.parse_command(cmd)
        self.cli_output.append(f"> {cmd}")
        self.cli_output.append(res)
        self.cli_output.append("")
        self.cli_line.clear()
        self.refresh()

    def save_topology(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save topology", "", "JSON Files (*.json)")
        if filename:
            if not filename.lower().endswith('.json'):
                filename += '.json'
            ok = self.network.save_to_file(filename)
            self.cli_output.append(f"% Configuration saved to {filename}" if ok else "% Save error")

    def load_topology(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load topology", "", "JSON Files (*.json)")
        if filename:
            ok = self.network.load_from_file(filename)
            self.cli_output.append(f"% Configuration loaded from {filename}" if ok else "% Load error")
            self.refresh()

    def update_device_list(self):
        self.device_list.clear()
        for d in self.network.list_devices():
            self.device_list.addItem(str(d))

    def draw_topology(self):
        self.scene.clear()
        self.node_items.clear()
        self.line_items.clear()

        for d in self.network.list_devices():
            node = DeviceNode(d, self)
            if d.x == 0 and d.y == 0:
                d.x = random.randint(-200, 200)
                d.y = random.randint(-200, 200)
            node.setPos(d.x, d.y)
            self.scene.addItem(node)
            self.node_items[d.device_id] = node

        for link in self.network.list_links():
            n1 = self.node_items.get(link.src)
            n2 = self.node_items.get(link.dst)
            if n1 and n2:
                p1 = n1.pos()
                p2 = n2.pos()
                line = QGraphicsLineItem(p1.x(), p1.y(), p2.x(), p2.y())
                line.setToolTip(f"BW: {link.bandwidth}Kbps, Delay: {link.delay}ms")
                # Товщина лінії пропорційна bandwidth (пікселі)
                pen = line.pen()
                pen.setWidth(max(1, min(10, link.bandwidth // 200)))
                line.setPen(pen)
                self.scene.addItem(line)
                self.line_items.append(line)

    def refresh(self):
        self.update_device_list()
        self.draw_topology()

    def refresh_lines(self):
        for ln in self.line_items:
            self.scene.removeItem(ln)
        self.line_items.clear()
        for link in self.network.list_links():
            n1 = self.node_items.get(link.src)
            n2 = self.node_items.get(link.dst)
            if n1 and n2:
                p1 = n1.pos()
                p2 = n2.pos()
                line = QGraphicsLineItem(p1.x(), p1.y(), p2.x(), p2.y())
                line.setToolTip(f"BW: {link.bandwidth}Kbps, Delay: {link.delay}ms")
                pen = line.pen()
                pen.setWidth(max(1, min(10, link.bandwidth // 200)))
                line.setPen(pen)
                self.scene.addItem(line)
                self.line_items.append(line)

if __name__ == '__main__':
    from network import Network
    from cli_parser import CLIParser
    network = Network()
    cli = CLIParser(network)
    network.add_device("sensor")
    network.add_device("lamp")
    network.add_link("sensor_1", "lamp_2")
    app = QApplication(sys.argv)
    win = MainWindow(network, cli)
    win.refresh()
    win.show()
    sys.exit(app.exec_())
