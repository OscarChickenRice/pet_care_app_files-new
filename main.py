import tkinter as tk
from tkinter import ttk, messagebox
import os
import re
import json
from datetime import datetime

import a_feeding
import b_vet
import c_grooming
import d_expense

# ======================================================
# In-memory "database"
# ======================================================
pets = []            # list of dicts
feeding_logs = []    # list of dicts
grooming_logs = []   # list of tuples
pet_expenses = []    # list of dicts

# ======================================================
# Prices (RM)
# ======================================================
meal_prices = {"Breakfast": 5.0, "Lunch": 7.5, "Dinner": 10.0, "Snack": 3.0}

groom_prices = {
    "Bathing": 20.0,
    "Nail Trim": 10.0,
    "Hair Cut": 35.0,
    "Ear Cleaning": 12.0,
    "Teeth Brushing": 15.0,
}

# ======================================================
# JSON files
# ======================================================
PETS_JSON = "pets.json"
EXPENSE_JSON = "pet_expenses.json"

# ======================================================
# Helper Functions
# ======================================================
def today_ddmmyyyy():
    return datetime.today().strftime("%d-%m-%Y")

def parse_date_ddmmyyyy(date_str):
    return datetime.strptime(date_str, "%d-%m-%Y")

def find_pet_by_id(pid: int):
    for p in pets:
        if p["id"] == pid:
            return p
    return None

def find_pet_by_name(name: str):
    for p in pets:
        if p["name"] == name:
            return p
    return None

def next_pet_id():
    if not pets:
        return 1
    return max(p["id"] for p in pets) + 1

def normalize_pet_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r"\s+", " ", name)
    return name

def pet_name_exists(name: str) -> bool:
    name_lower = name.lower()
    return any(p["name"].lower() == name_lower for p in pets)

# ======================================================
# JSON (Pets)
# ======================================================
def save_pets_json():
    try:
        with open(PETS_JSON, "w", encoding="utf-8") as f:
            json.dump(pets, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save pets failed:", e)

def load_pets_json():
    try:
        if os.path.exists(PETS_JSON):
            with open(PETS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    pets[:] = data
    except Exception as e:
        print("Load pets failed:", e)

# ======================================================
# JSON (Expenses) - so synced expenses get saved too
# ======================================================
def save_expenses_json():
    try:
        with open(EXPENSE_JSON, "w", encoding="utf-8") as f:
            json.dump(pet_expenses, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save expenses failed:", e)

def load_expenses_json():
    try:
        if os.path.exists(EXPENSE_JSON):
            with open(EXPENSE_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    pet_expenses[:] = data
    except Exception as e:
        print("Load expenses failed:", e)

def add_synced_expense(pet_name: str, category: str, amount: float, date: str, note: str, source: str):
    pet_obj = find_pet_by_name(pet_name)
    if not pet_obj:
        return
    pet_expenses.append({
        "pet_id": pet_obj["id"],
        "category": category,
        "amount": float(amount),
        "date": date,
        "note": note,
        "source": source,
        "edit_reason": ""
    })
    save_expenses_json()
    try:
        state["refresh_expense_table"]()
    except KeyError:
        pass

# ======================================================
# Main Window
# ======================================================
root = tk.Tk()
root.title("Pet Care Assistant App")
root.geometry("1200x700")

container = ttk.Frame(root)
container.pack(fill="both", expand=True)

sidebar = ttk.Frame(container, width=260)
sidebar.pack_propagate(False)
content = ttk.Frame(container)
content.pack(side="right", fill="both", expand=True)

# ======================================================
# Pages
# ======================================================
home_frame = ttk.Frame(content)
pets_frame = ttk.Frame(content)
feeding_frame = ttk.Frame(content)
vet_frame = ttk.Frame(content)
grooming_frame = ttk.Frame(content)
expense_frame = ttk.Frame(content)

for f in (home_frame, pets_frame, feeding_frame, vet_frame, grooming_frame, expense_frame):
    f.place(relx=0, rely=0, relwidth=1, relheight=1)

def show(frame):
    if frame == home_frame:
        hide_sidebar()
    else:
        show_sidebar()
    frame.tkraise()

# ======================================================
# Widgets registry for dropdown sync
# ======================================================
widgets = {
    "feeding_pet_combo": None,
    "vet_pet_combo": None,
    "groom_pet_combo": None,
    "exp_pet_combo": None,
    "pets_tree": None,
}

def rebuild_pet_dropdowns():
    pet_names = [p["name"] for p in pets]
    pet_id_name = [f"{p['id']} - {p['name']}" for p in pets]

    if widgets["feeding_pet_combo"] is not None:
        widgets["feeding_pet_combo"]["values"] = pet_names
    if widgets["vet_pet_combo"] is not None:
        widgets["vet_pet_combo"]["values"] = pet_names
    if widgets["groom_pet_combo"] is not None:
        widgets["groom_pet_combo"]["values"] = pet_names
    if widgets["exp_pet_combo"] is not None:
        widgets["exp_pet_combo"]["values"] = pet_id_name

# ======================================================
# Shared state passed into modules
# ======================================================
state = {
    "root": root,
    "show": show,
    "home_frame": home_frame,

    "pets_frame": pets_frame,
    "feeding_frame": feeding_frame,
    "vet_frame": vet_frame,
    "grooming_frame": grooming_frame,
    "expense_frame": expense_frame,

    "pets": pets,
    "feeding_logs": feeding_logs,
    "grooming_logs": grooming_logs,
    "pet_expenses": pet_expenses,

    "meal_prices": meal_prices,
    "groom_prices": groom_prices,

    "widgets": widgets,
    "rebuild_pet_dropdowns": rebuild_pet_dropdowns,

    "today_ddmmyyyy": today_ddmmyyyy,
    "parse_date_ddmmyyyy": parse_date_ddmmyyyy,
    "find_pet_by_id": find_pet_by_id,
    "find_pet_by_name": find_pet_by_name,
    "next_pet_id": next_pet_id,
    "normalize_pet_name": normalize_pet_name,
    "pet_name_exists": pet_name_exists,
    "add_synced_expense": add_synced_expense,

    "save_pets_json": save_pets_json,
    "load_pets_json": load_pets_json,
    "save_expenses_json": save_expenses_json,
    "load_expenses_json": load_expenses_json,
}

# ======================================================
# HOME PAGE (Select a Function)
# ======================================================
ttk.Label(home_frame, text="Pet Care Assistant App", font=("Arial", 22, "bold")).pack(pady=(30, 10))
ttk.Label(home_frame, text="Select a function:", font=("Arial", 12)).pack(pady=(0, 20))

home_center = ttk.Frame(home_frame)
home_center.pack(expand=True)
home_center.columnconfigure(0, weight=1)
home_center.rowconfigure(0, weight=1)

content_frame = ttk.Frame(home_center)
content_frame.grid(row=0, column=0)

ttk.Button(content_frame, text="Pets Hub", command=lambda: show(pets_frame), padding=26, width=30)\
    .grid(row=0, column=0, columnspan=2, pady=(0, 30))

grid_frame = ttk.Frame(content_frame)
grid_frame.grid(row=1, column=0, columnspan=2)

for i in range(2):
    grid_frame.columnconfigure(i, weight=1)
    grid_frame.rowconfigure(i, weight=1)

btn_opts = {"padding": 22, "width": 30}

ttk.Button(grid_frame, text="A. Feeding Tracker", command=lambda: show(feeding_frame), **btn_opts)\
    .grid(row=0, column=0, padx=25, pady=20, sticky="nsew")
ttk.Button(grid_frame, text="B. Vet Appointment Log", command=lambda: show(vet_frame), **btn_opts)\
    .grid(row=0, column=1, padx=25, pady=20, sticky="nsew")
ttk.Button(grid_frame, text="C. Grooming Schedule", command=lambda: show(grooming_frame), **btn_opts)\
    .grid(row=1, column=0, padx=25, pady=20, sticky="nsew")
ttk.Button(grid_frame, text="D. Pet Expense Tracker", command=lambda: show(expense_frame), **btn_opts)\
    .grid(row=1, column=1, padx=25, pady=20, sticky="nsew")

ttk.Button(content_frame, text="Exit", command=root.destroy, padding=14, width=20)\
    .grid(row=2, column=0, columnspan=2, pady=(30, 0))
# ======================================================
# PETS HUB
# ======================================================
top = ttk.Frame(pets_frame)
top.pack(fill="x", padx=15, pady=10)
ttk.Button(top, text="← Home", command=lambda: show(home_frame)).pack(side="left")
ttk.Label(top, text="Pets Hub", font=("Arial", 18, "bold")).pack(side="left", padx=10)

pets_form = ttk.LabelFrame(pets_frame, text="Add / Edit Pet")
pets_form.pack(fill="x", padx=15, pady=10)

pet_name_var = tk.StringVar()
pet_species_var = tk.StringVar(value="Dog")
pet_breed_var = tk.StringVar()
pet_age_var = tk.StringVar()
pet_gender_var = tk.StringVar(value="Male")
pet_colour_var = tk.StringVar()
pet_remark_var = tk.StringVar()

editing_pet_id = None
edit_status_var = tk.StringVar(value="")

ttk.Label(pets_form, text="Pet Name").grid(row=0, column=0, padx=6, pady=6, sticky="w")
ttk.Entry(pets_form, textvariable=pet_name_var, width=28).grid(row=0, column=1, padx=6, pady=6, sticky="w")

ttk.Label(pets_form, text="Species").grid(row=0, column=2, padx=6, pady=6, sticky="w")
ttk.Combobox(
    pets_form,
    textvariable=pet_species_var,
    values=["Dog", "Cat", "Rabbit", "Bird", "Fish", "Other"],
    state="readonly",
    width=25
).grid(row=0, column=3, padx=6, pady=6, sticky="w")

ttk.Label(pets_form, text="Breed").grid(row=1, column=0, padx=6, pady=6, sticky="w")
ttk.Entry(pets_form, textvariable=pet_breed_var, width=28).grid(row=1, column=1, padx=6, pady=6, sticky="w")

ttk.Label(pets_form, text="Age").grid(row=1, column=2, padx=6, pady=6, sticky="w")
ttk.Entry(pets_form, textvariable=pet_age_var, width=28).grid(row=1, column=3, padx=6, pady=6, sticky="w")

ttk.Label(pets_form, text="Gender").grid(row=2, column=0, padx=6, pady=6, sticky="w")
ttk.Combobox(
    pets_form,
    textvariable=pet_gender_var,
    values=["Male", "Female", "Unknown"],
    state="readonly",
    width=25
).grid(row=2, column=1, padx=6, pady=6, sticky="w")

ttk.Label(pets_form, text="Colour").grid(row=2, column=2, padx=6, pady=6, sticky="w")
ttk.Entry(pets_form, textvariable=pet_colour_var, width=28).grid(row=2, column=3, padx=6, pady=6, sticky="w")

ttk.Label(pets_form, text="Remark").grid(row=3, column=0, padx=6, pady=6, sticky="w")
ttk.Entry(pets_form, textvariable=pet_remark_var, width=72)\
    .grid(row=3, column=1, columnspan=3, padx=6, pady=6, sticky="w")

ttk.Label(pets_form, textvariable=edit_status_var, foreground="blue")\
    .grid(row=5, column=0, columnspan=4, padx=6, pady=(0, 6), sticky="w")

def refresh_pets_table():
    tree = widgets["pets_tree"]
    if tree is None:
        return
    tree.delete(*tree.get_children())
    for p in pets:
        tree.insert("", "end", iid=str(p["id"]), values=(
            p["id"], p["name"], p["species"], p["breed"], p["age"], p["gender"], p["colour"], p["remark"]
        ))

def clear_pet_form():
    global editing_pet_id
    editing_pet_id = None
    pet_name_var.set("")
    pet_species_var.set("Dog")
    pet_breed_var.set("")
    pet_age_var.set("")
    pet_gender_var.set("Male")
    pet_colour_var.set("")
    pet_remark_var.set("")
    edit_status_var.set("")

def add_pet():
    name = normalize_pet_name(pet_name_var.get())
    species = pet_species_var.get().strip()
    breed = pet_breed_var.get().strip()
    age_str = pet_age_var.get().strip()
    gender = pet_gender_var.get().strip()
    colour = pet_colour_var.get().strip()
    remark = pet_remark_var.get().strip()

    if not name:
        messagebox.showerror("Error", "Pet name cannot be empty.")
        return
    if not re.match(r"^[A-Za-z ]+$", name):
        messagebox.showerror("Error", "Pet name must contain only letters and spaces.")
        return
    if pet_name_exists(name):
        messagebox.showerror("Error", f"Pet name '{name}' already exists.")
        return

    if age_str:
        if not age_str.isdigit() or int(age_str) < 0:
            messagebox.showerror("Error", "Age must be a positive whole number.")
            return
        age = int(age_str)
    else:
        age = ""

    pets.append({
        "id": next_pet_id(),
        "name": name,
        "species": species,
        "breed": breed,
        "age": age,
        "gender": gender,
        "colour": colour,
        "remark": remark
    })

    save_pets_json()
    refresh_pets_table()
    rebuild_pet_dropdowns()
    clear_pet_form()
    messagebox.showinfo("Success", f"Pet '{name}' added.")

def delete_selected_pet():
    tree = widgets["pets_tree"]
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("No selection", "Select a pet row to delete.")
        return

    pid = int(sel[0])
    pet = find_pet_by_id(pid)
    if not pet:
        return

    pet_name = pet["name"]

    pets[:] = [p for p in pets if p["id"] != pid]
    grooming_logs[:] = [g for g in grooming_logs if g[0] != pet_name]
    feeding_logs[:] = [f for f in feeding_logs if f["pet"] != pet_name]
    pet_expenses[:] = [e for e in pet_expenses if e["pet_id"] != pid]

    save_pets_json()
    save_expenses_json()

    refresh_pets_table()
    rebuild_pet_dropdowns()

    if "refresh_feeding_table" in state:
        state["refresh_feeding_table"]()
    if "refresh_grooming" in state:
        state["refresh_grooming"]()
    if "refresh_expense_table" in state:
        state["refresh_expense_table"]()

    clear_pet_form()
    messagebox.showinfo("Deleted", f"Pet '{pet_name}' deleted (and related records removed).")

def load_selected_pet_for_edit():
    global editing_pet_id
    tree = widgets["pets_tree"]
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("No selection", "Select a pet row to edit.")
        return

    pid = int(sel[0])
    pet = find_pet_by_id(pid)
    if not pet:
        messagebox.showerror("Error", "Pet not found.")
        return

    editing_pet_id = pid
    pet_name_var.set(pet.get("name", ""))
    pet_species_var.set(pet.get("species", "Dog"))
    pet_breed_var.set(pet.get("breed", ""))
    pet_age_var.set("" if pet.get("age", "") == "" else str(pet.get("age", "")))
    pet_gender_var.set(pet.get("gender", "Male"))
    pet_colour_var.set(pet.get("colour", ""))
    pet_remark_var.set(pet.get("remark", ""))
    edit_status_var.set(f"Editing Pet ID {pid} (update then click 'Update Pet').")

def update_pet():
    global editing_pet_id
    if editing_pet_id is None:
        messagebox.showwarning("Not in edit mode", "Click 'Edit Selected' first.")
        return

    pet = find_pet_by_id(editing_pet_id)
    if not pet:
        messagebox.showerror("Error", "Pet not found.")
        clear_pet_form()
        return

    old_name = pet.get("name", "")

    name = normalize_pet_name(pet_name_var.get())
    species = pet_species_var.get().strip()
    breed = pet_breed_var.get().strip()
    age_str = pet_age_var.get().strip()
    gender = pet_gender_var.get().strip()
    colour = pet_colour_var.get().strip()
    remark = pet_remark_var.get().strip()

    if not name:
        messagebox.showerror("Error", "Pet name cannot be empty.")
        return
    if not re.match(r"^[A-Za-z ]+$", name):
        messagebox.showerror("Error", "Pet name must contain only letters and spaces.")
        return
    if name.lower() != old_name.lower() and pet_name_exists(name):
        messagebox.showerror("Error", f"Pet name '{name}' already exists.")
        return

    if age_str:
        if not age_str.isdigit() or int(age_str) < 0:
            messagebox.showerror("Error", "Age must be a positive whole number.")
            return
        age = int(age_str)
    else:
        age = ""

    pet["name"] = name
    pet["species"] = species
    pet["breed"] = breed
    pet["age"] = age
    pet["gender"] = gender
    pet["colour"] = colour
    pet["remark"] = remark

    if old_name != name:
        for row in feeding_logs:
            if row.get("pet") == old_name:
                row["pet"] = name
        for i, g in enumerate(grooming_logs):
            if g[0] == old_name:
                grooming_logs[i] = (name, g[1], g[2], g[3], g[4], g[5])

    save_pets_json()
    refresh_pets_table()
    rebuild_pet_dropdowns()

    if "refresh_feeding_table" in state:
        state["refresh_feeding_table"]()
    if "refresh_grooming" in state:
        state["refresh_grooming"]()
    if "refresh_expense_table" in state:
        state["refresh_expense_table"]()

    messagebox.showinfo("Updated", f"Pet ID {editing_pet_id} updated successfully.")
    clear_pet_form()

ttk.Button(pets_form, text="Edit Selected", command=load_selected_pet_for_edit)\
    .grid(row=4, column=0, padx=6, pady=10, sticky="w")
ttk.Button(pets_form, text="Add Pet", command=add_pet)\
    .grid(row=4, column=1, padx=6, pady=10, sticky="w")
ttk.Button(pets_form, text="Update Pet", command=update_pet)\
    .grid(row=4, column=2, padx=6, pady=10, sticky="w")
ttk.Button(pets_form, text="Delete Selected Pet", command=delete_selected_pet)\
    .grid(row=4, column=3, padx=6, pady=10, sticky="e")

pets_table_frame = ttk.LabelFrame(pets_frame, text="Pets List")
pets_table_frame.pack(fill="both", padx=15, pady=10, expand=True)

pets_tree = ttk.Treeview(
    pets_table_frame,
    columns=("ID", "Name", "Species", "Breed", "Age", "Gender", "Colour", "Remark"),
    show="headings"
)
for col in ("ID", "Name", "Species", "Breed", "Age", "Gender", "Colour", "Remark"):
    pets_tree.heading(col, text=col)

pets_tree.column("ID", width=60, anchor="center")
pets_tree.column("Name", width=140, anchor="w")
pets_tree.column("Species", width=100, anchor="center")
pets_tree.column("Breed", width=140, anchor="w")
pets_tree.column("Age", width=60, anchor="center")
pets_tree.column("Gender", width=90, anchor="center")
pets_tree.column("Colour", width=110, anchor="w")
pets_tree.column("Remark", width=260, anchor="w")

pets_tree.pack(fill="both", expand=True)
widgets["pets_tree"] = pets_tree

# ======================================================
# Build A/B/C/D modules
# ======================================================
a_feeding.build(state)
b_vet.build(state)
c_grooming.build(state)
d_expense.build(state)

# ======================================================
# Sidebar Functions
# ======================================================
def show_sidebar():
    if not sidebar.winfo_ismapped():
        sidebar.pack(side="left", fill="y")
        content.pack(side="right", fill="both", expand=True)

def hide_sidebar():
    if sidebar.winfo_ismapped():
        sidebar.pack_forget()
        content.pack(fill="both", expand=True)
# ======================================================
# Sidebar Menu (Only visible when not on the home page)
# ======================================================
ttk.Label(sidebar, text="Menu", font=("Arial", 14, "bold")).pack(pady=(18, 12))
ttk.Button(sidebar, text="Home", command=lambda: show(home_frame)).pack(fill="x", padx=12, pady=6)
ttk.Button(sidebar, text="Pets Hub", command=lambda: (refresh_pets_table(), show(pets_frame))).pack(fill="x", padx=12, pady=6)
ttk.Separator(sidebar).pack(fill="x", padx=12, pady=12)

ttk.Button(sidebar, text="A. Feeding Tracker", command=lambda: show(feeding_frame)).pack(fill="x", padx=12, pady=6)
ttk.Button(sidebar, text="B. Vet Appointment Log", command=lambda: show(vet_frame)).pack(fill="x", padx=12, pady=6)
ttk.Button(sidebar, text="C. Grooming Schedule", command=lambda: show(grooming_frame)).pack(fill="x", padx=12, pady=6)
ttk.Button(sidebar, text="D. Pet Expense Tracker",
           command=lambda: (rebuild_pet_dropdowns(), state["refresh_expense_table"](), show(expense_frame))).pack(fill="x", padx=12, pady=6)

ttk.Separator(sidebar).pack(fill="x", padx=12, pady=14)
ttk.Button(sidebar, text="Exit", command=root.destroy).pack(fill="x", padx=12, pady=6)

# ======================================================
# Initial load
# ======================================================
load_pets_json()
load_expenses_json()
rebuild_pet_dropdowns()
refresh_pets_table()

# Let modules load their own JSON + refresh their tables
state["refresh_expense_table"]()
state["refresh_feeding_table"]()
state["refresh_grooming"]()

show(home_frame)
hide_sidebar()
root.mainloop()
