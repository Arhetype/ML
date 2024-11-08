import tkinter as tk
from tkinter import messagebox, ttk
import networkx as nx
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Функция для загрузки правил из файла
def load_rules(file_name="input.txt"):
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            rules = file.readlines()
        return [rule.strip() for rule in rules]
    except FileNotFoundError:
        return []

# Функция для сохранения правил в файл
def save_rules(rules, file_name="input.txt"):
    with open(file_name, "w", encoding="utf-8") as file:
        for rule in rules:
            file.write(rule + "\n")

# Функция для обновления списка правил в интерфейсе
def update_rule_list():
    rules = load_rules()
    listbox.delete(0, tk.END)
    for idx, rule in enumerate(rules):
        listbox.insert(tk.END, f"{idx + 1}. {rule}")

# Функция для добавления нового правила
def add_rule():
    new_rule = entry.get()
    if new_rule:
        rules = load_rules()
        rules.append(new_rule)
        save_rules(rules)
        entry.delete(0, tk.END)
        update_rule_list()
    else:
        messagebox.showwarning("Input Error", "Введите правило!")

# Функция для удаления выбранного правила
def delete_rule():
    selected_index = listbox.curselection()
    if selected_index:
        index = selected_index[0]
        rules = load_rules()
        rules.pop(index)
        save_rules(rules)
        update_rule_list()
    else:
        messagebox.showwarning("Selection Error", "Выберите правило для удаления!")

# Функция для изменения выбранного правила
def edit_rule():
    selected_index = listbox.curselection()
    if selected_index:
        index = selected_index[0]
        rules = load_rules()
        current_rule = rules[index]
        entry.delete(0, tk.END)
        entry.insert(0, current_rule)

        def apply_edit():
            edited_rule = entry.get()
            if edited_rule:
                rules[index] = edited_rule
                save_rules(rules)
                update_rule_list()
                entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Input Error", "Введите новое правило!")

        edit_button.config(text="Применить изменение", command=apply_edit)
    else:
        messagebox.showwarning("Selection Error", "Выберите правило для редактирования!")

# Проверка на противоречивость
def check_contradictions(rules):
    contradictions = []
    condition_to_results = {}
    condition_matrix = []

    for rule in rules:
        match = re.match(r"Если (.+?), то (.+)", rule)
        if match:
            condition = match.group(1).strip()
            result = match.group(2).strip()

            if condition not in condition_to_results:
                condition_to_results[condition] = []

            if result in condition_to_results[condition]:
                continue
            condition_to_results[condition].append(result)

            for existing_result in condition_to_results[condition]:
                if existing_result != result:
                    contradictions.append(f"Противоречие: '{rule}' и результат для '{condition}'")
    
    # Матрица противоречий
    conditions = list(condition_to_results.keys())
    num_conditions = len(conditions)
    matrix = np.zeros((num_conditions, num_conditions), dtype=int)

    for i, condition in enumerate(conditions):
        for j, other_condition in enumerate(conditions):
            if i != j:
                if condition != other_condition:
                    if condition in condition_to_results and other_condition in condition_to_results[condition]:
                        matrix[i][j] = 1
    condition_matrix = matrix

    return contradictions, condition_matrix, conditions

# Проверка на избыточность
def check_redundancy(rules):
    seen_conditions = set()
    redundant_rules = []
    condition_count = {}

    for rule in rules:
        match = re.match(r"Если (.+?), то (.+)", rule)
        if match:
            condition = match.group(1).strip()

            if condition in seen_conditions:
                redundant_rules.append(rule)
            else:
                seen_conditions.add(condition)

            condition_count[condition] = condition_count.get(condition, 0) + 1

    return redundant_rules, condition_count

# Проверка на цикличность зависимостей
def check_cyclic_dependencies(rules):
    G = nx.DiGraph()

    for rule in rules:
        match = re.match(r"Если (.+?), то (.+)", rule)
        if match:
            condition = match.group(1).strip()
            result = match.group(2).strip()
            G.add_edge(condition, result)

    cycles = list(nx.simple_cycles(G))
    return G, cycles

# Матрица в текстовое поле
def print_matrix(matrix, conditions, title):
    output_text.insert(tk.END, title + ":\n")
    output_text.insert(tk.END, "\t" + "\t".join(conditions) + "\n")
    for i, row in enumerate(matrix):
        output_text.insert(tk.END, conditions[i] + "\t" + "\t".join(map(str, row)) + "\n")
    output_text.insert(tk.END, "\n")

# Вывод графа в полноэкранном окне
def show_graph_in_fullscreen(G):
    graph_window = tk.Toplevel(root)
    graph_window.title("Граф зависимостей")

    graph_window.attributes('-fullscreen', True)

    fig, ax = plt.subplots(figsize=(12, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=12, font_weight='bold', ax=ax)

    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
    canvas.draw()

    exit_button = tk.Button(graph_window, text="Выйти из полноэкранного режима", command=graph_window.destroy)
    exit_button.pack(pady=10)

# Выполнение всех проверок
def check_all_rules():
    rules = load_rules()
    contradictions, condition_matrix, conditions = check_contradictions(rules)
    redundancy, condition_count = check_redundancy(rules)
    G, cycles = check_cyclic_dependencies(rules)

    output_text.delete(1.0, tk.END)
    
    # Противоречия
    output_text.insert(tk.END, "Проверка на противоречивость:\n")
    if contradictions:
        output_text.insert(tk.END, "\nПротиворечивые правила:\n" + "\n".join(contradictions) + "\n\n")
    else:
        output_text.insert(tk.END, "\nПротиворечий нет.\n\n")
    
    # Матрица противоречий
    print_matrix(condition_matrix, conditions, "Матрица противоречий")

    # Избыточность
    output_text.insert(tk.END, "Проверка на избыточность:\n")
    if redundancy:
        output_text.insert(tk.END, "\nИзбыточные правила:\n" + "\n".join(redundancy) + "\n\n")
    else:
        output_text.insert(tk.END, "\nИзбыточности нет.\n\n")

    # Цикличность
    output_text.insert(tk.END, "Проверка на цикличность:\n")
    if cycles:
        output_text.insert(tk.END, "\nЦиклические зависимости:\n" + "\n".join(map(str, cycles)) + "\n\n")
    else:
        output_text.insert(tk.END, "\nЦиклических зависимостей нет.\n\n")

    show_graph_button = tk.Button(tab_check, text="Показать граф на полном экране", command=lambda: show_graph_in_fullscreen(G))
    show_graph_button.pack(pady=10)

root = tk.Tk()
root.title("Проверка правил")

tab_control = ttk.Notebook(root)
tab_edit = ttk.Frame(tab_control)
tab_check = ttk.Frame(tab_control)

tab_control.add(tab_edit, text="Правила")
tab_control.add(tab_check, text="Проверка правил")
tab_control.pack(expand=1, fill="both")

listbox = tk.Listbox(tab_edit, width=80, height=20)
listbox.pack(pady=10)

entry = tk.Entry(tab_edit, width=80)
entry.pack(pady=5)

add_button = tk.Button(tab_edit, text="Добавить правило", command=add_rule)
add_button.pack(pady=5)

delete_button = tk.Button(tab_edit, text="Удалить правило", command=delete_rule)
delete_button.pack(pady=5)

edit_button = tk.Button(tab_edit, text="Редактировать правило", command=edit_rule)
edit_button.pack(pady=5)

update_rule_list()

check_button = tk.Button(tab_check, text="Проверить все правила", command=check_all_rules)
check_button.pack(pady=10)

output_text = tk.Text(tab_check, wrap=tk.WORD, width=100, height=20)
output_text.pack(pady=10)

root.mainloop()