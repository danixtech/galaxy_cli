#!/usr/bin/env python
#
# galaxy_cli
#

# Import modules
import random

# Constants
INVENTORY_COST_PER_UNIT = 0.5

# Set Defaults
tick = 0
player = {
    "credits": 100,
    "inventory": {
        "alloys": 0
    }
}

# Souce Planet
forge = {
    "name": "Forge",
    "price": 6,
    "production_per_tick": 10,
    "production_cost": 1
}

# Destination Planet
haven = {
    "name": "Haven",
    "base_price": 10,
    "current_price": 10,
    "demand_per_tick": 15,
    "demand_remaining": 15
}

# Route data
route = {
    "from": "Forge",
    "to": "Haven",
    "travel_time": 3,
    "shipping_cost": 1,
    "risk": 0.05,
    "base_fee": 5
}

# Shipments currently moving
in_transit = []

# Production
def produce():
    produced = forge['production_per_tick']
    production_cost = forge['production_per_tick'] * forge['production_cost']
    player["inventory"]["alloys"] += produced
    player["credits"] -= production_cost
    print(f"[Production] Forge produced {produced} alloys for {production_cost:.2f} credits.")

# Ship Resources
def ship(amount):
    if player["inventory"]["alloys"] < amount:
        print("Not enough Alloys to ship.")
        return

    cost = route["base_fee"] + (amount * route["shipping_cost"])
    if player["credits"] < cost:
        print("Not enough credits to pay shipping cost.")
        return

    player["inventory"]["alloys"] -= amount
    player["credits"] -= cost

    shipment = {
        "amount": amount,
        "arrival_tick": tick + route["travel_time"]
    }
    in_transit.append(shipment)

    print(f"[Shipping] Sent {amount} Alloys to Haven for {cost} credits. (arrives at Stardate {shipment['arrival_tick']})")

# Resolve Shipments
def resolve_shipments():
    global in_transit

    arrived = [s for s in in_transit if s["arrival_tick"] <= tick]
    in_transit = [s for s in in_transit if s["arrival_tick"] > tick]

    for shipment in arrived:
        amount = shipment["amount"]

        effective_risk = route["risk"] * (amount / 10)

        if random.random() < effective_risk:
            lost = amount // 2
            amount -= lost
            print(f"[Risk] Shipment disrupted! Lost {lost} Alloys.")

        sellable = min(amount, haven["demand_remaining"])
        unsold = amount - sellable

        revenue = sellable * haven["current_price"]
        haven["demand_remaining"] -= sellable

        if unsold > 0:
            print(f"[Market] {unsold} alloys could not be sold due to low demand.")


        player["credits"] += revenue

        print(f"[Arrival] {amount} Alloys sold at Haven for {revenue:.2f} credits.")

# Inventory Storage Costs
def inventory_cost():
    inventory_cost = player["inventory"]["alloys"] * INVENTORY_COST_PER_UNIT
    player["credits"] -= inventory_cost

    if inventory_cost > 0:
        print(f"[Storage] Paid {inventory_cost:.2f} credits to store inventory")

# Advance Time
def advance_time(steps):
    print("Incrementing time by", steps, "tick(s).")
    global tick
    for _ in range(steps):
        tick += 1
        print("Stardate", tick)
        inventory_cost()
        produce()
        resolve_shipments()
        haven["demand_remaining"] = haven["demand_per_tick"]

# Display current status
def status():
    print("\n--- STATUS ---")
    print(f"Stardate: {tick}")
    print(f"Credits: {player['credits']}")
    print(f"Inventory: {player['inventory']}")
    print(f"In Transit: {len(in_transit)} shipments")
    print("--------------\n")

# Help Menu
def help_menu():
    print("""
Commands:
 status                 Show current state
 ship <amount>          Ship Alloys from Forge to Haven
 tick <n>               Advance time by n ticks
 help                   Show this menu
 quit                   Exit
""")

# Main Function Loop
def main():
    print("=== Galactic Trade Simulator (CLI PoC) ===")
    help_menu()

    #civ_name = input("What is your civilizations name?:  ")

    # Menu system
    while True:

        # CLI prompt
        cmd = input("> ").strip().split()

        if not cmd:
            continue

        # Exit
        if cmd[0] == "help":
            help_menu()

        elif cmd[0] == "status":
            status()

        elif cmd[0] == "ship" and len(cmd) == 2:
            ship(int(cmd[1]))

        elif cmd[0] == "tick" and len(cmd) == 2:
            advance_time(int(cmd[1]))

        elif cmd[0] == "quit":
            print("Until next time Space Cowboy...")
            break
        else:
            print("Unknown command.  Type 'help' for assistance.")

# Run Main
main()
input("\n\nPress the enter key to exit.")

#
# vim: set syntax=python
#
