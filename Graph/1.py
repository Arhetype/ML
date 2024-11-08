import sys
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QListWidget, QMessageBox

class CognitiveModel:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.vertices = []  # Список всех вершин
        self.connections = {}  # Для хранения связей

    def add_parameter(self, parameter):
        self.graph.add_node(parameter)
        self.vertices.append(parameter)

    def remove_parameter(self, parameter):
        self.graph.remove_node(parameter)
        self.vertices.remove(parameter)

    def add_connection(self, from_param, to_param, weight=1):
        self.graph.add_edge(from_param, to_param, weight=weight)
        self.connections[(from_param, to_param)] = weight

    def remove_connection(self, from_param, to_param):
        self.graph.remove_edge(from_param, to_param)
        del self.connections[(from_param, to_param)]

    def visualize(self):
        num_nodes = len(self.graph.nodes)
        angles = np.linspace(0, 2 * np.pi, num_nodes, endpoint=False)
        pos = {node: (np.cos(angle), np.sin(angle)) for node, angle in zip(self.graph.nodes, angles)}

        weights = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw(self.graph, pos, with_labels=True, node_size=2000, node_color='lightblue', font_size=10, font_weight='bold', edge_color='gray')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=weights)
        plt.title("Когнитивная модель в форме десятиугольника", fontsize=14)
        plt.axis('off')
        plt.show()

    def check_stability(self):
        if len(self.graph.nodes) == 0:
            return "Устойчивость модели: не определена (нет вершин)."

        adj_matrix = nx.to_numpy_array(self.graph, weight='weight')
        eigenvalues = np.linalg.eigvals(adj_matrix)
        stability = np.abs(eigenvalues)
        max_stability = np.max(stability)

        if max_stability < 1:
            return "Устойчивость модели: устойчивая."
        else:
            return "Устойчивость модели: неустойчивая."

class CognitiveModelApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Четкая когнитивная модель")
        self.setGeometry(100, 100, 600, 400)

        self.model = CognitiveModel()

        # Центральный виджет
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Главный layout
        main_layout = QVBoxLayout(self.central_widget)

        # Ввод вершин
        self.vertex_input = QLineEdit(self)
        self.vertex_input.setPlaceholderText("Введите имя вершины")
        main_layout.addWidget(self.vertex_input)

        self.add_vertex_button = QPushButton("Добавить вершину", self)
        self.add_vertex_button.clicked.connect(self.add_vertex)
        main_layout.addWidget(self.add_vertex_button)

        self.vertex_list = QListWidget(self)
        main_layout.addWidget(self.vertex_list)

        # Ввод связей
        self.connection_input = QLineEdit(self)
        self.connection_input.setPlaceholderText("Введите связь (вершина1, вершина2, вес)")
        main_layout.addWidget(self.connection_input)

        self.add_connection_button = QPushButton("Добавить связь", self)
        self.add_connection_button.clicked.connect(self.add_connection)
        main_layout.addWidget(self.add_connection_button)

        # Проверка устойчивости
        self.check_stability_button = QPushButton("Проверить устойчивость", self)
        self.check_stability_button.clicked.connect(self.check_stability)
        main_layout.addWidget(self.check_stability_button)

        self.stability_label = QLabel(self)
        main_layout.addWidget(self.stability_label)

        # Визуализация графа
        self.visualize_button = QPushButton("Визуализировать граф", self)
        self.visualize_button.clicked.connect(self.visualize_graph)
        main_layout.addWidget(self.visualize_button)

    def add_vertex(self):
        vertex_name = self.vertex_input.text().strip()
        if vertex_name:
            self.model.add_parameter(vertex_name)
            self.vertex_list.addItem(vertex_name)
            self.vertex_input.clear()

    def add_connection(self):
        connection_data = self.connection_input.text().strip()
        try:
            vertex_1, vertex_2, weight = connection_data.split(',')
            vertex_1 = vertex_1.strip()
            vertex_2 = vertex_2.strip()
            weight = int(weight.strip())

            if vertex_1 in self.model.vertices and vertex_2 in self.model.vertices:
                self.model.add_connection(vertex_1, vertex_2, weight)
                self.connection_input.clear()
            else:
                QMessageBox.warning(self, "Ошибка", "Одна или обе вершины не существуют.")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите данные в формате: вершина1, вершина2, вес")

    def check_stability(self):
        stability_result = self.model.check_stability()
        self.stability_label.setText(stability_result)

    def visualize_graph(self):
        self.model.visualize()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CognitiveModelApp()
    window.show()
    sys.exit(app.exec_())
