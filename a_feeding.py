import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import json, os

def build(state):
    feeding_frame = state["feeding_frame"]
    show = state["show"]
    home_frame = state["home_frame"]

    feeding_logs = state["feeding_logs"]
    meal_prices = state["meal_prices"]
    add_synced_expense = state["add_synced_expense"]
    widgets = state["widgets"]

    FEEDING_JSON = "feeding_logs.json"

    def save_feeding_json():
        try:
            with open(FEEDING_JSON, "w", encoding="utf-8") as f:
                json.dump(feeding_logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Save feeding failed:", e)

    def load_feeding_json():
        try:
            if os.path.exists(FEEDING_JSON):
                with open(FEEDING_JSON, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        feeding_logs[:] = data
        except Exception as e:
            print("Load feeding failed:", e)

    top = ttk.Frame(feeding_frame)
    top.pack(fill="x", padx=15, pady=10)
    ttk.Button(top, text="← Home", command=lambda: show(home_frame)).pack(side="left")
    ttk.Label(top, text="A. Feeding Tracker", font=("Arial", 18, "bold")).pack(side="left", padx=10)

    feed_form = ttk.LabelFrame(feeding_frame, text="Log / Schedule Meal")
    feed_form.pack(fill="x", padx=15, pady=10)

    feeding_pet_var = tk.StringVar()
    feeding_meal_var = tk.StringVar(value="Breakfast")
    feeding_date_var = tk.StringVar()
    feeding_time_var = tk.StringVar()
    feeding_status_var = tk.StringVar(value="Not Yet Done")

    ttk.Label(feed_form, text="Pet").grid(row=0, column=0, padx=6, pady=6, sticky="w")
    feeding_pet_combo = ttk.Combobox(feed_form, textvariable=feeding_pet_var, state="readonly", width=27)
    feeding_pet_combo.grid(row=0, column=1, padx=6, pady=6, sticky="w")
    widgets["feeding_pet_combo"] = feeding_pet_combo

    ttk.Label(feed_form, text="Meal").grid(row=0, column=2, padx=6, pady=6, sticky="w")
    ttk.Combobox(feed_form, textvariable=feeding_meal_var, values=list(meal_prices.keys()),
                 state="readonly", width=20).grid(row=0, column=3, padx=6, pady=6, sticky="w")

    ttk.Label(feed_form, text="Date (dd-mm-yyyy)").grid(row=1, column=0, padx=6, pady=6, sticky="w")
    ttk.Entry(feed_form, textvariable=feeding_date_var, width=30).grid(row=1, column=1, padx=6, pady=6, sticky="w")

    ttk.Label(feed_form, text="Time (HH:MM)").grid(row=1, column=2, padx=6, pady=6, sticky="w")
    ttk.Entry(feed_form, textvariable=feeding_time_var, width=20).grid(row=1, column=3, padx=6, pady=6, sticky="w")

    ttk.Label(feed_form, text="Status").grid(row=2, column=0, padx=6, pady=6, sticky="w")
    ttk.Combobox(feed_form, textvariable=feeding_status_var, values=["Not Yet Done", "Done"],
                 state="readonly", width=27).grid(row=2, column=1, padx=6, pady=6, sticky="w")

    price_list_frame = ttk.LabelFrame(feeding_frame, text="Meal Price List (RM)")
    price_list_frame.pack(fill="x", padx=15, pady=10)

    price_table = ttk.Treeview(price_list_frame, columns=("Meal", "Price (RM)"), show="headings", height=4)
    price_table.heading("Meal", text="Meal")
    price_table.heading("Price (RM)", text="Price (RM)")
    price_table.column("Meal", width=120, anchor="center")
    price_table.column("Price (RM)", width=100, anchor="center")
    price_table.pack(fill="x")

    for meal, price in meal_prices.items():
        price_table.insert("", "end", values=(meal, f"{price:.2f}"))

    feeding_table_frame = ttk.Frame(feeding_frame)
    feeding_table_frame.pack(fill="both", padx=15, pady=10, expand=True)

    feed_cols = ("Pet", "Meal", "Price (RM)", "Date", "Time", "Status")
    feeding_table = ttk.Treeview(feeding_table_frame, columns=feed_cols, show="headings")
    for col in feed_cols:
        feeding_table.heading(col, text=col)
        feeding_table.column(col, anchor="center", width=120)
    feeding_table.pack(fill="both", expand=True)

    def refresh_feeding_table():
        feeding_table.delete(*feeding_table.get_children())
        for row in feeding_logs:
            feeding_table.insert("", "end", iid=row["id"], values=(
                row["pet"], row["meal"], f"{row['price']:.2f}",
                row["date"], row["time"], row["status"]
            ))

    def add_feeding():
        pet = feeding_pet_var.get().strip()
        meal = feeding_meal_var.get()
        price = meal_prices.get(meal, 0.0)
        date = feeding_date_var.get().strip()
        time = feeding_time_var.get().strip()
        status = feeding_status_var.get()

        if not pet:
            messagebox.showwarning("Missing Info", "Please select a Pet.")
            return
        if not date or not time:
            messagebox.showwarning("Missing Info", "Please fill in Date and Time.")
            return

        try:
            datetime.strptime(date, "%d-%m-%Y")
            datetime.strptime(time, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid format.\nDate: dd-mm-yyyy\nTime: HH:MM")
            return

        log_id = f"FEED-{len(feeding_logs)+1}"
        feeding_logs.append({
            "id": log_id,
            "pet": pet,
            "meal": meal,
            "price": float(price),
            "date": date,
            "time": time,
            "status": status
        })

        add_synced_expense(
            pet_name=pet,
            category="Food",
            amount=float(price),
            date=date,
            note=f"Meal: {meal}",
            source="Feeding"
        )

        save_feeding_json()
        refresh_feeding_table()

        feeding_pet_var.set("")
        feeding_date_var.set("")
        feeding_time_var.set("")
        feeding_status_var.set("Not Yet Done")
        feeding_meal_var.set("Breakfast")

    def mark_feeding_done():
        selected = feeding_table.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a meal to mark as done")
            return

        for iid in selected:
            for row in feeding_logs:
                if row["id"] == iid:
                    row["status"] = "Done"
                    break

        save_feeding_json()
        refresh_feeding_table()

    def edit_selected_feeding():
        selected = feeding_table.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a meal row to edit.")
            return

        iid = selected[0]
        row = None
        for r in feeding_logs:
            if r["id"] == iid:
                row = r
                break
        if row is None:
            return

        new_pet = simpledialog.askstring("Edit Pet", f"Current Pet: {row['pet']}\nEnter new pet (must be existing):")
        if new_pet is None or new_pet.strip() == "":
            new_pet = row["pet"]
        else:
            new_pet = new_pet.strip()

        if widgets["feeding_pet_combo"] is not None:
            valid_pets = list(widgets["feeding_pet_combo"]["values"])
            if new_pet not in valid_pets:
                messagebox.showerror("Error", "Pet name must be one of the existing pets in Pets Hub.")
                return

        new_meal = simpledialog.askstring("Edit Meal", f"Current Meal: {row['meal']}\nEnter new meal (Breakfast/Lunch/Dinner/Snack):")
        if new_meal is None or new_meal.strip() == "":
            new_meal = row["meal"]
        else:
            new_meal = new_meal.strip()

        if new_meal not in meal_prices:
            messagebox.showerror("Error", "Invalid meal. Use: Breakfast, Lunch, Dinner, Snack.")
            return

        new_date = simpledialog.askstring("Edit Date", f"Current Date: {row['date']}\nEnter new date (dd-mm-yyyy):")
        if new_date is None or new_date.strip() == "":
            new_date = row["date"]
        else:
            new_date = new_date.strip()

        new_time = simpledialog.askstring("Edit Time", f"Current Time: {row['time']}\nEnter new time (HH:MM):")
        if new_time is None or new_time.strip() == "":
            new_time = row["time"]
        else:
            new_time = new_time.strip()

        new_status = simpledialog.askstring("Edit Status", f"Current Status: {row['status']}\nEnter status (Not Yet Done/Done):")
        if new_status is None or new_status.strip() == "":
            new_status = row["status"]
        else:
            new_status = new_status.strip()

        if new_status not in ["Not Yet Done", "Done"]:
            messagebox.showerror("Error", "Status must be: Not Yet Done or Done.")
            return

        try:
            datetime.strptime(new_date, "%d-%m-%Y")
            datetime.strptime(new_time, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid format.\nDate: dd-mm-yyyy\nTime: HH:MM")
            return

        row["pet"] = new_pet
        row["meal"] = new_meal
        row["price"] = float(meal_prices.get(new_meal, 0.0))
        row["date"] = new_date
        row["time"] = new_time
        row["status"] = new_status

        save_feeding_json()
        refresh_feeding_table()
        messagebox.showinfo("Updated", f"{iid} updated successfully.")

    btns = ttk.Frame(feeding_frame)
    btns.pack(fill="x", padx=15, pady=10)
    ttk.Button(btns, text="Add Meal", command=add_feeding).pack(side="left")
    ttk.Button(btns, text="Mark Done", command=mark_feeding_done).pack(side="left", padx=10)
    ttk.Button(btns, text="Edit Selected", command=edit_selected_feeding).pack(side="left", padx=10)

    load_feeding_json()
    refresh_feeding_table()

    state["refresh_feeding_table"] = refresh_feeding_table
