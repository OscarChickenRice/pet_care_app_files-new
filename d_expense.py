import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json, os

def build(state):
    expense_frame = state["expense_frame"]
    show = state["show"]
    home_frame = state["home_frame"]

    pet_expenses = state["pet_expenses"]
    find_pet_by_id = state["find_pet_by_id"]
    today_ddmmyyyy = state["today_ddmmyyyy"]
    parse_date_ddmmyyyy = state["parse_date_ddmmyyyy"]
    widgets = state["widgets"]

    EXPENSE_JSON = "pet_expenses.json"

    def save_expense_json():
        try:
            with open(EXPENSE_JSON, "w", encoding="utf-8") as f:
                json.dump(pet_expenses, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Save expenses failed:", e)

    def load_expense_json():
        try:
            if os.path.exists(EXPENSE_JSON):
                with open(EXPENSE_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        pet_expenses[:] = data
        except Exception as e:
            print("Load expenses failed:", e)

    exp_header = ttk.Frame(expense_frame)
    exp_header.pack(fill="x", padx=15, pady=(12, 6))
    ttk.Label(exp_header, text="D. Pet Expense Tracker", font=("Arial", 18, "bold")).pack(side="left")
    ttk.Button(exp_header, text="← Home", command=lambda: show(home_frame)).pack(side="right")

    exp_top = ttk.Frame(expense_frame)
    exp_top.pack(fill="x", padx=15, pady=8)

    exp_pet_var = tk.StringVar()
    exp_category_var = tk.StringVar(value="Food")
    exp_amount_var = tk.StringVar()
    exp_date_var = tk.StringVar(value=today_ddmmyyyy())
    exp_note_var = tk.StringVar()

    ttk.Label(exp_top, text="Pet:").pack(side="left")
    exp_pet_combo = ttk.Combobox(exp_top, textvariable=exp_pet_var, state="readonly", width=28)
    exp_pet_combo.pack(side="left", padx=8)
    widgets["exp_pet_combo"] = exp_pet_combo

    ttk.Label(exp_top, text="Category:").pack(side="left")
    ttk.Combobox(
        exp_top, textvariable=exp_category_var,
        values=["Food", "Grooming", "Vet Visit", "Medicine", "Toys", "Training", "Other"],
        state="readonly", width=18
    ).pack(side="left", padx=8)

    ttk.Label(exp_top, text="Amount (RM):").pack(side="left")
    ttk.Entry(exp_top, textvariable=exp_amount_var, width=12).pack(side="left", padx=8)

    ttk.Label(exp_top, text="Date:").pack(side="left")
    ttk.Entry(exp_top, textvariable=exp_date_var, width=16).pack(side="left", padx=8)

    ttk.Label(exp_top, text="Note:").pack(side="left")
    ttk.Entry(exp_top, textvariable=exp_note_var, width=20).pack(side="left", padx=8)

    exp_table_frame = ttk.Frame(expense_frame)
    exp_table_frame.pack(fill="both", padx=15, pady=6, expand=True)

    exp_columns = ("Pet", "Category", "Amount (RM)", "Date", "Note", "Source", "Edit Reason")
    exp_table = ttk.Treeview(exp_table_frame, columns=exp_columns, show="headings")
    for col in exp_columns:
        exp_table.heading(col, text=col)
        exp_table.column(col, anchor="center", width=120)
    exp_table.pack(fill="both", expand=True)

    def refresh_expense_table():
        exp_table.delete(*exp_table.get_children())
        for idx, e in enumerate(pet_expenses):
            p = find_pet_by_id(e["pet_id"])
            if p:
                exp_table.insert("", "end", iid=str(idx), values=(
                    p["name"],
                    e["category"],
                    f"{e['amount']:.2f}",
                    e["date"],
                    e.get("note", ""),
                    e.get("source", "Manual"),
                    e.get("edit_reason", "")
                ))

    def add_expense():
        if not exp_pet_var.get().strip():
            messagebox.showerror("Error", "Please select a pet.")
            return
        try:
            amt = float(exp_amount_var.get())
            if amt <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Amount must be a positive number.")
            return
        try:
            parse_date_ddmmyyyy(exp_date_var.get())
        except:
            messagebox.showerror("Error", "Date must be in dd-mm-yyyy format.")
            return

        pid = int(exp_pet_var.get().split(" - ")[0])
        p = find_pet_by_id(pid)
        if not p:
            messagebox.showerror("Error", "Pet not found.")
            return

        pet_expenses.append({
            "pet_id": pid,
            "category": exp_category_var.get(),
            "amount": amt,
            "date": exp_date_var.get(),
            "note": exp_note_var.get(),
            "source": "Manual",
            "edit_reason": ""
        })

        save_expense_json()
        refresh_expense_table()
        exp_amount_var.set("")
        exp_note_var.set("")

    def edit_selected_expense():
        sel = exp_table.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select an expense row to edit.")
            return

        idx = int(sel[0])
        if idx < 0 or idx >= len(pet_expenses):
            return

        current = pet_expenses[idx]
        new_amt_str = simpledialog.askstring("Edit Amount", f"Current amount: {current['amount']:.2f}\nEnter new amount:")
        if new_amt_str is None:
            return

        try:
            new_amt = float(new_amt_str)
            if new_amt <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Amount must be a positive number.")
            return

        reason = simpledialog.askstring("Edit Reason", "Why are you changing this amount?")
        if reason is None or not reason.strip():
            messagebox.showerror("Error", "Reason is required.")
            return

        current["amount"] = new_amt
        current["edit_reason"] = reason.strip()

        save_expense_json()
        refresh_expense_table()

    exp_buttons = ttk.Frame(expense_frame)
    exp_buttons.pack(fill="x", padx=15, pady=6)
    ttk.Button(exp_buttons, text="Add Expense", command=add_expense).pack(side="left", padx=6)
    ttk.Button(exp_buttons, text="Edit Selected", command=edit_selected_expense).pack(side="left", padx=6)

    load_expense_json()
    refresh_expense_table()

    state["refresh_expense_table"] = refresh_expense_table
