import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json, os

def build(state):
    grooming_frame = state["grooming_frame"]
    show = state["show"]
    home_frame = state["home_frame"]

    grooming_logs = state["grooming_logs"]
    groom_prices = state["groom_prices"]
    add_synced_expense = state["add_synced_expense"]
    widgets = state["widgets"]

    GROOMING_JSON = "grooming_logs.json"

    def save_grooming_json():
        try:
            data = [list(x) for x in grooming_logs]  # tuples -> lists
            with open(GROOMING_JSON, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Save grooming failed:", e)

    def load_grooming_json():
        try:
            if os.path.exists(GROOMING_JSON):
                with open(GROOMING_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        grooming_logs[:] = [tuple(x) for x in data]  # lists -> tuples
        except Exception as e:
            print("Load grooming failed:", e)

    groom_frame_top = ttk.Frame(grooming_frame)
    groom_frame_top.pack(fill="x", padx=15, pady=10)

    ttk.Button(groom_frame_top, text="← Home", command=lambda: show(home_frame)).pack(side="left")
    ttk.Label(groom_frame_top, text="C. Grooming Schedule", font=("Arial", 18, "bold")).pack(side="left", padx=10)

    groom_form = ttk.LabelFrame(grooming_frame, text="Add Grooming Task")
    groom_form.pack(fill="x", padx=15, pady=10)

    g_pet_var = tk.StringVar()
    g_task_var = tk.StringVar(value="Bathing")
    g_price_var = tk.StringVar(value=f"{groom_prices['Bathing']:.2f}")
    g_date_var = tk.StringVar()
    g_time_var = tk.StringVar()
    g_status_var = tk.StringVar(value="Not Yet Done")

    ttk.Label(groom_form, text="Pet").grid(row=0, column=0, padx=6, pady=6, sticky="w")
    g_pet_combo = ttk.Combobox(groom_form, textvariable=g_pet_var, state="readonly", width=25)
    g_pet_combo.grid(row=0, column=1, padx=6, pady=6, sticky="w")
    widgets["groom_pet_combo"] = g_pet_combo

    ttk.Label(groom_form, text="Task").grid(row=0, column=2, padx=6, pady=6, sticky="w")
    g_task_combo = ttk.Combobox(
        groom_form,
        textvariable=g_task_var,
        values=list(groom_prices.keys()),
        state="readonly",
        width=22
    )
    g_task_combo.grid(row=0, column=3, padx=6, pady=6, sticky="w")

    ttk.Label(groom_form, text="Price (RM)").grid(row=1, column=2, padx=6, pady=6, sticky="w")
    ttk.Entry(groom_form, textvariable=g_price_var, width=20, state="readonly")\
        .grid(row=1, column=3, padx=6, pady=6, sticky="w")

    def update_groom_price(_=None):
        task = g_task_var.get()
        g_price_var.set(f"{groom_prices.get(task, 0.0):.2f}")

    g_task_combo.bind("<<ComboboxSelected>>", update_groom_price)

    ttk.Label(groom_form, text="Date (dd-mm-yyyy)").grid(row=1, column=0, padx=6, pady=6, sticky="w")
    ttk.Entry(groom_form, textvariable=g_date_var, width=25).grid(row=1, column=1, padx=6, pady=6, sticky="w")

    ttk.Label(groom_form, text="Time (HH:MM)").grid(row=2, column=0, padx=6, pady=6, sticky="w")
    ttk.Entry(groom_form, textvariable=g_time_var, width=25).grid(row=2, column=1, padx=6, pady=6, sticky="w")

    ttk.Label(groom_form, text="Status").grid(row=2, column=2, padx=6, pady=6, sticky="w")
    ttk.Combobox(groom_form, textvariable=g_status_var, values=["Not Yet Done", "Done"],
                 state="readonly", width=22).grid(row=2, column=3, padx=6, pady=6, sticky="w")

    groom_table_frame = ttk.Frame(grooming_frame)
    groom_table_frame.pack(fill="both", padx=15, pady=10, expand=True)

    groom_columns = ("Pet", "Task", "Price (RM)", "Date", "Time", "Status")
    groom_tree = ttk.Treeview(groom_table_frame, columns=groom_columns, show="headings")
    for col in groom_columns:
        groom_tree.heading(col, text=col)
        groom_tree.column(col, anchor="center", width=120)
    groom_tree.pack(fill="both", expand=True)

    def refresh_grooming(app):
        def sort_key(row):
            pet, task, price, date, time, status = row
            return (datetime.strptime(date, "%d-%m-%Y"), datetime.strptime(time, "%H:%M"))

        app["grooming_logs"].sort(key=sort_key)
        tree = app["groom_tree"]
        tree.delete(*tree.get_children())
        for i, row in enumerate(app["grooming_logs"]):
            tree.insert("", "end", iid=str(i), values=row)

    def add_grooming(app):
        pet = app["g_pet_var"].get().strip()
        task = app["g_task_var"].get().strip()
        price = groom_prices.get(task, 0.0)
        date = app["g_date_var"].get().strip()
        time = app["g_time_var"].get().strip()
        status = app["g_status_var"].get().strip()

        if not pet:
            messagebox.showerror("Error", "Please select a pet.")
            return
        if not date or not time:
            messagebox.showerror("Error", "Please fill in Date and Time.")
            return

        try:
            datetime.strptime(date, "%d-%m-%Y")
            datetime.strptime(time, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid format.\nDate: dd-mm-yyyy\nTime: HH:MM")
            return

        app["grooming_logs"].append((pet, task, f"{price:.2f}", date, time, status))

        add_synced_expense(
            pet_name=pet,
            category="Grooming",
            amount=float(price),
            date=date,
            note=f"Task: {task}",
            source="Grooming"
        )

        save_grooming_json()

        app["g_date_var"].set("")
        app["g_time_var"].set("")
        app["g_status_var"].set("Not Yet Done")
        app["g_task_var"].set("Bathing")
        update_groom_price()

        refresh_grooming(app)

    def mark_done(app):
        tree = app["groom_tree"]
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a row first.")
            return
        idx = int(selected[0])
        pet, task, price, date, time, _ = app["grooming_logs"][idx]
        app["grooming_logs"][idx] = (pet, task, price, date, time, "Done")

        save_grooming_json()
        refresh_grooming(app)

    def delete_selected(app):
        tree = app["groom_tree"]
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a row first.")
            return

        idxs = sorted([int(i) for i in selected], reverse=True)
        for idx in idxs:
            if 0 <= idx < len(app["grooming_logs"]):
                app["grooming_logs"].pop(idx)

        save_grooming_json()
        refresh_grooming(app)

    app = {
        "grooming_logs": grooming_logs,
        "g_pet_var": g_pet_var,
        "g_task_var": g_task_var,
        "g_date_var": g_date_var,
        "g_time_var": g_time_var,
        "g_status_var": g_status_var,
        "groom_tree": groom_tree,
    }

    ttk.Button(groom_form, text="Add", command=lambda: add_grooming(app)).grid(row=3, column=0, pady=10, padx=6)
    ttk.Button(groom_form, text="Mark Done", command=lambda: mark_done(app)).grid(row=3, column=1, pady=10, padx=6)
    ttk.Button(groom_form, text="Delete", command=lambda: delete_selected(app)).grid(row=3, column=2, pady=10, padx=6)

    load_grooming_json()
    refresh_grooming(app)

    state["refresh_grooming"] = lambda: refresh_grooming(app)
