import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox, QListWidget, QLabel, QTabWidget, QTextEdit
from PyQt5.QtCore import Qt
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class CognitiveModelApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Четкая когнитивная модель")
        self.setGeometry(100, 100, 1000, 700)

        # Инициализация графа
        self.G = nx.DiGraph()
        self.vertices = []  # Список всех вершин
        self.connections = {}  # Для хранения связей

        # Список для импульсного анализа
        self.vertices_for_analysis = []

        # Инициализация атрибута V_t
        self.V_t = None  # Устанавливаем атрибут в None на старте

        # Центральный виджет
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Главный layout
        main_layout = QHBoxLayout(self.central_widget)

        # Создаем QTabWidget
        self.tab_widget = QTabWidget(self)
        main_layout.addWidget(self.tab_widget)

        # Вторая вкладка
        self.second_tab = QWidget()
        self.tab_widget.addTab(self.second_tab, "Импульсный анализ")
        self.create_second_tab()

        # Третья вкладка
        self.third_tab = QWidget()
        self.tab_widget.addTab(self.third_tab, "График")
        self.create_third_tab()

        # Четвертая вкладка для проверки циклов
        self.fourth_tab = QWidget()
        self.tab_widget.addTab(self.fourth_tab, "Проверка циклов")
        self.create_fourth_tab()

        # Добавление параметров
        parameters = [
            "Идея проекта",
            "Анализ требований",
            "Оценка ресурсов",
            "Техническая осуществимость",
            "Финансовая оценка",
            "Оценка рисков",
            "Командные навыки",
            "Сроки реализации",
            "Качество продукции",
            "Обратная связь от пользователей",
            "Заключение о реализуемости"
        ]
        for param in parameters:
            self.add_parameter(param)

        # Добавление связей с весами
        self.add_connection("Идея проекта", "Анализ требований", weight=1)
        self.add_connection("Идея проекта", "Командные навыки", weight=1)
        self.add_connection("Анализ требований", "Оценка ресурсов", weight=1)
        self.add_connection("Анализ требований", "Финансовая оценка", weight=1)
        self.add_connection("Оценка ресурсов", "Техническая осуществимость", weight=1)
        self.add_connection("Оценка ресурсов", "Командные навыки", weight=-1)
        self.add_connection("Техническая осуществимость", "Финансовая оценка", weight=1)
        self.add_connection("Финансовая оценка", "Оценка рисков", weight=-1)
        self.add_connection("Оценка рисков", "Командные навыки", weight=1)
        self.add_connection("Командные навыки", "Сроки реализации", weight=-1)
        self.add_connection("Командные навыки", "Качество продукции", weight=1)
        self.add_connection("Сроки реализации", "Качество продукции", weight=1)
        self.add_connection("Сроки реализации", "Обратная связь от пользователей", weight=1)
        self.add_connection("Качество продукции", "Обратная связь от пользователей", weight=1)
        self.add_connection("Обратная связь от пользователей", "Заключение о реализуемости", weight=1)
        self.add_connection("Обратная связь от пользователей", "Оценка рисков", weight=1)
        self.add_connection("Заключение о реализуемости", "Анализ требований", weight=1)

    def add_parameter(self, parameter):
        """Добавление параметра как вершины графа."""
        if parameter not in self.G:
            self.G.add_node(parameter)
            self.vertices.append(parameter)
            self.selected_vertices_list.addItem(parameter)

    def add_connection(self, from_param, to_param, weight=1):
        """Добавление связи с весом."""
        self.G.add_edge(from_param, to_param, weight=weight)

    # Вторая вкладка
    def create_second_tab(self):
        layout = QVBoxLayout(self.second_tab)
        self.selected_vertices_list = QListWidget(self)
        self.selected_vertices_list.setSelectionMode(QListWidget.MultiSelection)
        self.selected_vertices_list.setFixedHeight(100)
        layout.addWidget(QLabel("Выберите вершины для анализа:"))
        layout.addWidget(self.selected_vertices_list)

        layout.addWidget(QLabel("Введите исходные значения вершин (ввод через пробел):"))
        self.initial_values_input = QLineEdit(self)
        layout.addWidget(self.initial_values_input)

        layout.addWidget(QLabel("Введите начальное воздействие (ввод через пробел):"))
        self.initial_impulse_input = QLineEdit(self)
        layout.addWidget(self.initial_impulse_input)

        layout.addWidget(QLabel("Введите количество шагов:"))
        self.steps_input = QLineEdit(self)
        layout.addWidget(self.steps_input)

        self.perform_analysis_button = QPushButton("Выполнить импульсный анализ", self)
        self.perform_analysis_button.clicked.connect(self.perform_impulse_analysis)
        layout.addWidget(self.perform_analysis_button)

        self.analysis_output = QTextEdit(self)
        self.analysis_output.setReadOnly(True)
        layout.addWidget(self.analysis_output)

    def perform_impulse_analysis(self):
        selected_items = self.selected_vertices_list.selectedItems()
        selected_vertices = [item.text() for item in selected_items]

        if not selected_vertices:
            self.analysis_output.setText("Не выбраны вершины для анализа.")
            return

        try:
            initial_values = np.array([float(x) for x in self.initial_values_input.text().split()])
            initial_impulse = np.array([float(x) for x in self.initial_impulse_input.text().split()])
            steps = int(self.steps_input.text())
        except ValueError:
            self.analysis_output.setText("Ошибка: Проверьте корректность ввода исходных значений и начального воздействия.")
            return

        if len(initial_values) != len(selected_vertices) or len(initial_impulse) != len(selected_vertices):
            self.analysis_output.setText("Ошибка: Количество исходных значений и воздействий должно совпадать с количеством выбранных вершин.")
            return

        adjacency_matrix = np.zeros((len(selected_vertices), len(selected_vertices)))

        for i, v1 in enumerate(selected_vertices):
            for j, v2 in enumerate(selected_vertices):
                if self.G.has_edge(v1, v2):
                    adjacency_matrix[i, j] = self.G[v1][v2]['weight']

        adjacency_matrix_T = adjacency_matrix.T

        V = np.zeros((steps + 1, len(selected_vertices)))
        P = np.zeros((steps + 1, len(selected_vertices)))

        V[0] = initial_values + initial_impulse
        P[0] = initial_impulse

        for t in range(1, steps + 1):
            P[t] = np.linalg.matrix_power(adjacency_matrix_T, t) @ initial_impulse
            V[t] = V[t-1] + P[t]

        self.V_t = V
        self.vertices_for_analysis = selected_vertices

        result_text = "Результаты импульсного анализа:\n"
        result_text += f"Матрица смежности (A):\n{adjacency_matrix}\n\n"
        for t in range(steps + 1):
            result_text += f"Шаг {t}:\n"
            result_text += f"V({t}) = {V[t]}\n"
            result_text += f"P({t}) = {P[t]}\n\n"

        self.analysis_output.setText(result_text)

    # Третья вкладка
    def create_third_tab(self):
        layout = QVBoxLayout(self.third_tab)

        self.plot_button = QPushButton("Построить график изменения значений", self)
        self.plot_button.clicked.connect(self.plot_graph)
        layout.addWidget(self.plot_button)

        self.graph_button = QPushButton("Построить граф", self)
        self.graph_button.clicked.connect(self.display_graph)
        layout.addWidget(self.graph_button)

        self.plot_canvas = FigureCanvas(plt.Figure())
        layout.addWidget(self.plot_canvas)

    def plot_graph(self):
        if self.V_t is None:
            return

        steps = self.V_t.shape[0]
        fig, ax = plt.subplots(figsize=(10, 6))
        for i, vertex in enumerate(self.vertices_for_analysis):
            ax.plot(range(steps), self.V_t[:, i], label=vertex)
        ax.set_xlabel("Шаги")
        ax.set_ylabel("Значения")
        ax.set_title("График изменения значений")
        ax.legend()
        self.plot_canvas.draw()

    def display_graph(self):
        plt.clf()
        pos = nx.circular_layout(self.G)
        weights = nx.get_edge_attributes(self.G, 'weight')
        nx.draw(self.G, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=2000, font_size=10)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=weights)
        plt.title("Граф параметров проекта")
        plt.show()

    # Четвертая вкладка для проверки циклов
    def create_fourth_tab(self):
        layout = QVBoxLayout(self.fourth_tab)
        self.check_cycles_button = QPushButton("Проверить наличие циклов", self)
        self.check_cycles_button.clicked.connect(self.check_for_cycles)
        layout.addWidget(self.check_cycles_button)

        self.cycles_output = QTextEdit(self)
        self.cycles_output.setReadOnly(True)
        layout.addWidget(self.cycles_output)

        self.check_stability_button = QPushButton("Проверить устойчивость системы", self)
        self.check_stability_button.clicked.connect(self.check_stability)
        layout.addWidget(self.check_stability_button)

        self.stability_output = QTextEdit(self)
        self.stability_output.setReadOnly(True)
        layout.addWidget(self.stability_output)

    def check_for_cycles(self):
        cycles = list(nx.simple_cycles(self.G))
        if cycles:
            result_text = "Обнаружены циклы:\n"
            for cycle in cycles:
                cycle_weight = sum(self.G[u][v]['weight'] for u, v in zip(cycle, cycle[1:] + [cycle[0]]))
                if cycle_weight > 0:
                    result_text += f"Положительный цикл: {cycle} (Сумма весов: {cycle_weight})\n"
                else:
                    result_text += f"Отрицательный цикл: {cycle} (Сумма весов: {cycle_weight})\n"
        else:
            result_text = "Циклы не обнаружены."
        self.cycles_output.setText(result_text)

    def check_stability(self):
        cycles = list(nx.simple_cycles(self.G))
        unstable = False
        for cycle in cycles:
            cycle_weight = sum(self.G[u][v]['weight'] for u, v in zip(cycle, cycle[1:] + [cycle[0]]))
            if cycle_weight <= 0:
                unstable = True
                break
        
        if unstable:
            self.stability_output.setText("Система неустойчива (есть отрицательные циклы).")
        else:
            self.stability_output.setText("Система устойчива (нет отрицательных циклов).")


app = QApplication(sys.argv)
window = CognitiveModelApp()
window.show()
sys.exit(app.exec_())
