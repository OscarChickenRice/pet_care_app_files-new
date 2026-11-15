import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
from datetime import datetime

def build(state):
    vet_frame = state["vet_frame"]
    show = state["show"]
    home_frame = state["home_frame"]
    widgets = state["widgets"]

    class EmbeddedVetLog:
        def __init__(self, parent_frame):
            self.filename = "vet_appointments.txt"
            self.json_file = "vet_appointments.json"
            self._ensure_file()
            self._ensure_json()
            self.frame = parent_frame
            self.build_gui()

        def _ensure_file(self):
            if not os.path.exists(self.filename):
                with open(self.filename, "w", encoding="utf-8"):
                    pass

        def _ensure_json(self):
            if not os.path.exists(self.json_file):
                with open(self.json_file, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)

        def add_line(self, line):
            with open(self.filename, "a", encoding="utf-8") as f:
                f.write(line + "\n")

        def read_all(self):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    return f.readlines()
            except FileNotFoundError:
                return []

        def add_appointment(self, pet_name, date, time, purpose, disease):
            line = f"{pet_name}|{date}|{time}|{purpose}|{disease}"
            self.add_line(line)

        def save_json_appointment(self, pet_name, date, time, purpose, disease):
            record = {"pet": pet_name, "date": date, "time": time, "purpose": purpose, "disease": disease}
            data = []
            try:
                if os.path.exists(self.json_file):
                    with open(self.json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if not isinstance(data, list):
                            data = []
            except:
                data = []

            data.append(record)
            try:
                with open(self.json_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print("Save vet json failed:", e)

        def format_appointments(self):
            lines = self.read_all()
            if not lines:
                return "No appointments yet."
            output = ""
            for idx, line in enumerate(lines, start=1):
                parts = line.strip().split("|")
                if len(parts) != 5:
                    continue
                pet, date, time, purpose, disease = parts
                output += (f"Appointment {idx}\n"
                           f"  Pet Name : {pet}\n"
                           f"  Date     : {date}\n"
                           f"  Time     : {time}\n"
                           f"  Purpose  : {purpose}\n"
                           f"  Disease  : {disease}\n\n")
            return output

        def build_gui(self):
            top = ttk.Frame(self.frame)
            top.pack(fill="x", padx=15, pady=10)

            ttk.Button(top, text="← Home", command=lambda: show(home_frame)).grid(row=0, column=0, sticky="w", pady=(0, 8))
            ttk.Label(top, text="B. Vet Appointment Log", font=("Arial", 18, "bold")).grid(row=0, column=1, sticky="w", padx=10)

            form = ttk.Frame(self.frame)
            form.pack(fill="x", padx=15, pady=8)

            ttk.Label(form, text="Pet Name:").grid(row=0, column=0, sticky="w")
            ttk.Label(form, text="Date (dd-mm-yyyy):").grid(row=1, column=0, sticky="w")
            ttk.Label(form, text="Time (HH:MM):").grid(row=2, column=0, sticky="w")
            ttk.Label(form, text="Purpose:").grid(row=3, column=0, sticky="w")
            ttk.Label(form, text="Disease:").grid(row=4, column=0, sticky="w")

            self.pet_name_var = tk.StringVar()
            self.pet_combo = ttk.Combobox(form, textvariable=self.pet_name_var, state="readonly", width=27)
            self.pet_combo.grid(row=0, column=1, sticky="w")
            widgets["vet_pet_combo"] = self.pet_combo

            self.date_var = tk.Entry(form)
            self.time_var = tk.Entry(form)
            self.purpose_var = tk.Entry(form)

            self.date_var.grid(row=1, column=1, sticky="w")
            self.time_var.grid(row=2, column=1, sticky="w")
            self.purpose_var.grid(row=3, column=1, sticky="w")

            self.disease_var = tk.StringVar(value="Select Disease")
            self.disease_options = ["Periodontal (Dental) Disease", "Ear Infections", "Obesity"]
            self.disease_menu = tk.OptionMenu(form, self.disease_var, *self.disease_options)
            self.disease_menu.grid(row=4, column=1, sticky="w")

            ttk.Button(form, text="Add Appointment", command=self.add_appointment_gui).grid(row=5, column=0, pady=10)
            ttk.Button(form, text="View Appointments", command=self.view_appointments_gui).grid(row=5, column=1, sticky="w")

            self.output = tk.Text(self.frame, width=500, height=300)
            self.output.pack(padx=15, pady=8)

        def add_appointment_gui(self):
            pet = self.pet_name_var.get().strip()
            date = self.date_var.get().strip()
            time = self.time_var.get().strip()
            purpose = self.purpose_var.get().strip()
            disease = self.disease_var.get()

            if not pet:
                messagebox.showerror("Error", "Please select a pet.")
                return
            if not all([date, time, purpose]):
                messagebox.showerror("Error", "Date, Time, and Purpose must be filled.")
                return
            if disease == "Select Disease":
                messagebox.showerror("Error", "Please select a disease.")
                return

            try:
                datetime.strptime(date, "%d-%m-%Y")
            except ValueError:
                messagebox.showerror("Invalid Date", "Use dd-mm-yyyy format.")
                return
            try:
                datetime.strptime(time, "%H:%M")
            except ValueError:
                messagebox.showerror("Invalid Time", "Use HH:MM 24-hour format.")
                return

            self.add_appointment(pet, date, time, purpose, disease)
            self.save_json_appointment(pet, date, time, purpose, disease)

            messagebox.showinfo("Success", "Appointment added successfully!")
            self.clear_fields()

        def view_appointments_gui(self):
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, self.format_appointments())

        def clear_fields(self):
            self.pet_name_var.set("")
            self.date_var.delete(0, tk.END)
            self.time_var.delete(0, tk.END)
            self.purpose_var.delete(0, tk.END)
            self.disease_var.set("Select Disease")

    EmbeddedVetLog(vet_frame)
