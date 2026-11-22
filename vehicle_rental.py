"""
Vehicle Rental Management System
PS No.: 65
Language: Python 3
Concepts: OOP, Lists, Dictionaries, File Handling

Run:
    python vehicle_rental.py

Data is stored in vehicles.txt in the same folder as this program.
"""

from pathlib import Path

DATA_FILE = Path(__file__).with_name("vehicles.txt")


class Vehicle:
    """Stores the details and current rental status of one vehicle."""

    def __init__(self, vehicle_id, vehicle_type, model, rate, available=True,
                 customer="", days=0):
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.model = model
        self.rate = float(rate)
        self.available = available
        self.customer = customer
        self.days = int(days)

    def display(self):
        status = "Available" if self.available else f"Rented to {self.customer}"
        print(
            f"{self.vehicle_id:<5} | {self.vehicle_type:<8} | "
            f"{self.model:<15} | Rs. {self.rate:>8.2f}/day | {status}"
        )

    def to_file_line(self):
        # A pipe is used as the separator. Input validation prevents it in text fields.
        return (
            f"{self.vehicle_id}|{self.vehicle_type}|{self.model}|{self.rate}|"
            f"{self.available}|{self.customer}|{self.days}\n"
        )


class VehicleRentalSystem:
    """Manages vehicles, rentals, billing and file storage."""

    def __init__(self):
        self.vehicles = []          # List of Vehicle objects
        self.vehicle_map = {}       # Vehicle ID -> rental details
        self.load_vehicles()

    def load_vehicles(self):
        """Load saved vehicles when the program starts."""
        if not DATA_FILE.exists():
            return

        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                for line in file:
                    parts = line.rstrip("\n").split("|")
                    if len(parts) != 7:
                        continue

                    vehicle_id, v_type, model, rate, available, customer, days = parts
                    vehicle = Vehicle(
                        vehicle_id, v_type, model, float(rate),
                        available.lower() == "true", customer, int(days)
                    )
                    self.vehicles.append(vehicle)

                    if not vehicle.available:
                        self.vehicle_map[vehicle_id] = {
                            "customer": customer,
                            "days": int(days)
                        }
        except (ValueError, OSError) as error:
            print("Warning: Could not read saved vehicle data:", error)

    def save_vehicles(self):
        """Save all vehicles and their current status in vehicles.txt."""
        try:
            with DATA_FILE.open("w", encoding="utf-8") as file:
                for vehicle in self.vehicles:
                    file.write(vehicle.to_file_line())
        except OSError as error:
            print("Error: Could not save vehicle data:", error)

    def find_vehicle(self, vehicle_id):
        for vehicle in self.vehicles:
            if vehicle.vehicle_id.lower() == vehicle_id.lower():
                return vehicle
        return None

    @staticmethod
    def get_text(prompt):
        while True:
            value = input(prompt).strip()
            if value and "|" not in value:
                return value
            print("Please enter a valid value. The | symbol is not allowed.")

    def add_vehicle(self):
        print("\n--- ADD VEHICLE ---")
        vehicle_type = self.get_text("Enter vehicle type (Car/Bike): ")
        model = self.get_text("Enter vehicle model: ")

        while True:
            try:
                rate = float(input("Enter rent per day (Rs.): "))
                if rate <= 0:
                    print("Rate must be greater than zero.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")

        next_number = 1
        existing_ids = {int(v.vehicle_id[1:]) for v in self.vehicles
                        if v.vehicle_id.startswith("V") and v.vehicle_id[1:].isdigit()}
        while next_number in existing_ids:
            next_number += 1

        vehicle_id = f"V{next_number}"
        vehicle = Vehicle(vehicle_id, vehicle_type, model, rate)
        self.vehicles.append(vehicle)
        self.save_vehicles()

        print(
            f"\nVehicle added. ID: {vehicle_id} | {vehicle_type} | "
            f"{model} | Rs. {rate:.0f}/day | Available"
        )

    def rent_vehicle(self):
        print("\n--- RENT A VEHICLE ---")
        vehicle_id = input("Enter vehicle ID: ").strip()
        vehicle = self.find_vehicle(vehicle_id)

        if vehicle is None:
            print("Vehicle ID not found.")
            return

        if not vehicle.available:
            print(f"Vehicle {vehicle.vehicle_id} is not available.")
            return

        customer = self.get_text("Enter customer name: ")

        while True:
            try:
                days = int(input("Enter number of rental days: "))
                if days < 1:
                    print("Days must be 1 or more.")
                    continue
                break
            except ValueError:
                print("Please enter a whole number of days.")

        total = vehicle.rate * days
        discount = 0.10 * total if days >= 7 else 0
        bill = total - discount

        vehicle.available = False
        vehicle.customer = customer
        vehicle.days = days
        self.vehicle_map[vehicle.vehicle_id] = {
            "customer": customer,
            "days": days
        }
        self.save_vehicles()

        print(f"\n{vehicle.vehicle_id} rented to {customer} for {days} days.")
        if discount:
            print("10% discount applied.")
        print(f"Total bill: Rs. {bill:.2f}")

    def return_vehicle(self):
        print("\n--- RETURN VEHICLE ---")
        vehicle_id = input("Enter vehicle ID: ").strip()
        vehicle = self.find_vehicle(vehicle_id)

        if vehicle is None:
            print("Vehicle ID not found.")
            return

        if vehicle.available:
            print(f"Vehicle {vehicle.vehicle_id} is already available.")
            return

        vehicle.available = True
        vehicle.customer = ""
        vehicle.days = 0
        self.vehicle_map.pop(vehicle.vehicle_id, None)
        self.save_vehicles()

        print(f"Vehicle {vehicle.vehicle_id} returned. Status: Available")

    def view_available_vehicles(self):
        print("\n--- AVAILABLE VEHICLES ---")
        available = [vehicle for vehicle in self.vehicles if vehicle.available]

        if not available:
            print("No vehicles are currently available.")
            return

        self.print_vehicle_table(available)

    def view_all_vehicles(self):
        print("\n--- ALL VEHICLES ---")
        if not self.vehicles:
            print("No vehicles have been added yet.")
            return
        self.print_vehicle_table(self.vehicles)

    @staticmethod
    def print_vehicle_table(vehicles):
        print(f"{'ID':<5} | {'Type':<8} | {'Model':<15} | {'Rate':<15} | Status")
        print("-" * 85)
        for vehicle in vehicles:
            vehicle.display()

    def run(self):
        print("=" * 55)
        print("          VEHICLE RENTAL MANAGEMENT SYSTEM")
        print("=" * 55)

        while True:
            print("\n1. Add Vehicle")
            print("2. Rent Vehicle")
            print("3. Return Vehicle")
            print("4. View Available Vehicles")
            print("5. View All Vehicles")
            print("6. Exit")

            choice = input("\nEnter your choice (1-6): ").strip()

            if choice == "1":
                self.add_vehicle()
            elif choice == "2":
                self.rent_vehicle()
            elif choice == "3":
                self.return_vehicle()
            elif choice == "4":
                self.view_available_vehicles()
            elif choice == "5":
                self.view_all_vehicles()
            elif choice == "6":
                self.save_vehicles()
                print("Thank you for using Vehicle Rental Management System!")
                break
            else:
                print("Invalid choice. Please select a number from 1 to 6.")


if __name__ == "__main__":
    system = VehicleRentalSystem()
    system.run()
