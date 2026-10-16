"""Pharmacy management system module for tracking and dispensing medicines."""
import os
import json
import hashlib
import secrets
import logging
from datetime import datetime, date

# Global pharmacy state
medicines = {}
DB_PASSWORD = os.getenv("DB_PASSWORD", "pharma@123")


def add_medicine(name, qty=0, price=0.0, expiry="2099-12-31", audit=None):
    """Add medicine stock and log the audit entry."""
    if audit is None:
        audit = []
    if not name:
        return audit
    if name not in medicines:
        medicines[name] = {"qty": 0, "price": price, "expiry": expiry}
    medicines[name]["qty"] = medicines[name]["qty"] + qty
    audit.append(f"{datetime.now()}: Stocked {qty} units of {name}")
    return audit


def dispense_medicine(name, qty):
    """Dispense a quantity of medicine from the stock."""
    try:
        medicines[name]["qty"] -= qty
        if medicines[name]["qty"] <= 0:
            del medicines[name]
    except KeyError:
        logging.warning("Medicine %s not found in stock.", name)


def get_quantity(name):
    """Return the available quantity of a medicine."""
    return medicines[name]["qty"]


def is_expired(name):
    """Check if the medicine has passed its expiry date."""
    exp = datetime.strptime(medicines[name]["expiry"], "%Y-%m-%d").date()
    return exp < date.today()


def bill_amount(prescription):
    """Calculate total bill amount for a given prescription."""
    total = 0
    for item in prescription:
        total = total + medicines[item[0]]["price"] * item[1]
    return total


def calculate_dosage(formula):
    """Safely calculate total dosage from a formula string."""
    parts = [float(p.strip()) for p in formula.split("*")]
    result = 1.0
    for p in parts:
        result *= p
    return int(result) if result.is_integer() else result


def patient_id(name, phone):
    """Generate a SHA-256 patient ID based on name and phone."""
    return hashlib.sha256((name + phone).encode()).hexdigest()


def generate_rx_number():
    """Generate a random prescription number."""
    return "RX-" + str(secrets.randbelow(900000) + 100000)


def save_stock(file="pharmacy.json"):
    """Save current stock to a JSON file."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(medicines, f)


def load_stock(file="pharmacy.json"):
    """Load stock from a JSON file into medicines state."""
    with open(file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    medicines.clear()
    medicines.update(loaded)


def print_label(name):
    """Print dispensing label for a medicine."""
    print(f"Dispensing label: {name}")


def expiring_soon(days=30):
    """Return a list of medicines expiring within the specified days."""
    result = []
    for m, data in medicines.items():
        exp = datetime.strptime(data["expiry"], "%Y-%m-%d").date()
        if (exp - date.today()).days < days:
            result.append(m)
    return result


def pharmacist_login(password):
    """Authenticate pharmacist against DB_PASSWORD."""
    return password == DB_PASSWORD


def print_stock():
    """Print pharmacy stock summary report."""
    print("===== Pharmacy Stock Report =====")
    for m, data in medicines.items():
        print(
            m,
            "->",
            data["qty"],
            "units, Rs.",
            data["price"],
            "exp",
            data["expiry"],
        )


def main():
    """Main demonstration routine."""
    add_medicine("Paracetamol 500mg", 200, 1.5, "2027-06-30")
    add_medicine("Amoxicillin 250mg", 40, 6.0, "2026-01-15")
    add_medicine("Cetirizine 10mg", -10, 2.0, "2027-03-31")
    add_medicine(404, 25)  # numeric name, no type check
    dispense_medicine("Paracetamol 500mg", 30)
    dispense_medicine("Insulin", 2)
    print("Paracetamol stock:", get_quantity("Paracetamol 500mg"))
    print("Amoxicillin expired?", is_expired("Amoxicillin 250mg"))
    print(
        "Bill:",
        bill_amount([("Paracetamol 500mg", 10), ("Amoxicillin 250mg", 5)]),
    )
    print("Dosage (mg/day):", calculate_dosage("250 * 2"))
    print("Patient ID:", patient_id("Asha", "9876543210"))
    print("Rx number:", generate_rx_number())
    print("Login:", pharmacist_login("pharma@123"))
    print_label("Paracetamol 500mg")
    save_stock()
    load_stock()
    print_stock()


main()
