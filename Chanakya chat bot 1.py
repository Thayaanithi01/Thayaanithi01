import sys
from collections import deque
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel, QComboBox
)
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

LOCATIONS = {
    "Main Gate": (13.221889, 77.755250),
    "Admin Block": (13.222300, 77.756100),
    "Library": (13.222300, 77.756100),
    "Engineering Block": (13.222808311862547, 77.755753305935382),
    "Food Court": (13.223701862580903, 77.75613048429636),
    "Football Court": (13.227170989620399, 77.75681628983873),
    "Hostel Block 1": (13.224896756327583, 77.75914176505472),
    "Sports Road": (13.22558085415475, 77.75936170619394),
    "Cricket Ground": (13.229030051100583, 77.75718375247385),
    "Basketball Court": (13.228889055361652, 77.75833710235025),
    "Volleyball Court": (13.22884727883073, 77.75820916559),
}

GRAPH = {
    "Main Gate": ["Admin Block"],
    "Admin Block": ["Main Gate", "Library", "Engineering Block"],
    "Library": ["Admin Block", "Food Court"],
    "Engineering Block": ["Admin Block", "Food Court"],
    "Food Court": ["Library", "Engineering Block", "Hostel Block 1"],
    "Hostel Block 1": ["Food Court", "Sports Road"],
    "Sports Road": ["Hostel Block 1", "Football Court", "Cricket Ground"],
    "Football Court": ["Sports Road", "Basketball Court"],
    "Basketball Court": ["Football Court", "Volleyball Court"],
    "Volleyball Court": ["Basketball Court", "Cricket Ground"],
    "Cricket Ground": ["Sports Road", "Volleyball Court"]
}

CENTER_LAT, CENTER_LON = 13.224650, 77.757820

MAP_HTML = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>Chanakya Campus Map - BFS</title>
<style>html, body, #map {{ height: 100%; margin: 0; padding: 0; }}</style>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
</head>
<body>
<div id="map"></div>
<script>
  var map = L.map('map').setView([{CENTER_LAT}, {CENTER_LON}], 17);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 19
  }}).addTo(map);

  var routeLayer = null;
  var markers = [];

  function addMarker(lat, lon, label) {{
    var marker = L.marker([lat, lon]).addTo(map).bindPopup(label);
    markers.push(marker);
  }}

  window.showPath = function(coords) {{
    if (routeLayer) map.removeLayer(routeLayer);
    routeLayer = L.polyline(coords, {{color: 'red', weight: 5}}).addTo(map);
    map.fitBounds(routeLayer.getBounds().pad(0.2));
  }}
</script>
</body>
</html>
"""

def bfs(start, goal):
    queue = deque([[start]])
    visited = set()
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            visited.add(node)
            for neighbor in GRAPH.get(node, []):
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    return None

class MainWindow(QMainWindow):
    def _init_(self):
        super()._init_()
        self.setWindowTitle("Chanakya University — BFS Route Finder")
        self.resize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Campus Guide Bot (BFS) 🤖"))
        self.chatview = QTextEdit()
        self.chatview.setReadOnly(True)
        left_layout.addWidget(self.chatview)

        self.start_combo = QComboBox()
        self.end_combo = QComboBox()
        for loc in LOCATIONS:
            self.start_combo.addItem(loc)
            self.end_combo.addItem(loc)
        left_layout.addWidget(QLabel("Start:"))
        left_layout.addWidget(self.start_combo)
        left_layout.addWidget(QLabel("Destination:"))
        left_layout.addWidget(self.end_combo)

        btn_route = QPushButton("Find Route (BFS)")
        btn_route.clicked.connect(self.find_route)
        left_layout.addWidget(btn_route)

        layout.addWidget(left, 35)

        self.web = QWebEngineView()
        layout.addWidget(self.web, 65)
        self.web.setHtml(MAP_HTML)

        self._push_bot("Welcome! Choose two points and click 'Find Route (BFS)'.")

    def _push_bot(self, text):
        self.chatview.append(f"<b>Bot:</b> {text}")

    def find_route(self):
        start = self.start_combo.currentText()
        end = self.end_combo.currentText()

        if start == end:
            self._push_bot("Start and destination are the same.")
            return

        path = bfs(start, end)
        if not path:
            self._push_bot("❌ No path found.")
            return

        self._push_bot(f"✅ Path found: {' → '.join(path)}")

        coords = [[LOCATIONS[node][0], LOCATIONS[node][1]] for node in path]
        js_array = str(coords).replace("(", "[").replace(")", "]")
        self.web.page().runJavaScript(f"window.showPath({js_array});")

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if _name_ == "_main_":
    main()
