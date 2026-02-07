#!/usr/bin/env python
#
# galaxy_cli
#

# =============================
# Import Modules
# =============================
import random

# =============================
# Constants
# =============================

# Production Costs
INVENTORY_COST_PER_UNIT = 0.5

# Return Costs
RETURN_SHIPPING_MULTIPLIER = 1.0

# =============================
# World State
# =============================

# Starting Date
tick = 0

# Player Inventory
player = {
    "credits": 100, # Investment Capitol
    "inventory": {
        "alloys": 0
    }
}

# Source Planet
forge = {
    "name": "Forge",
    "production_per_tick": 10,
    "production_cost": 1
}

# Destination Planet
haven = {
    "name": "Haven",
    "base_price": 10,
    "current_price": 10,
    "demand_per_tick": 15,
    "demand_remaining": 15,
    "warehouse_capacity": 100,
    "warehouse_inventory": 0,
    "warehouse_storage_cost": 1.5
}

# Route Data
route = {
    "from": "Forge",
    "to": "Haven",
    "travel_time": 3,
    "shipping_cost": 1,
    "base_fee": 5,
    "risk": 0.05
}

# All shipments live here
in_transit = []

# =============================
# Core Mechanics
# =============================

# Resource Production
def produce():
    produced = forge["production_per_tick"]
    cost = produced * forge["production_cost"]

    player["inventory"]["alloys"] += produced
    player["credits"] -= cost

    print(f"[Production] Produced {produced} alloys for {cost:.2f} credits.")

# Ship Resources
def ship(amount):
    if player["inventory"]["alloys"] < amount:
        print("Not enough alloys to ship.")
        return

    cost = route["base_fee"] + (amount * route["shipping_cost"])
    if player["credits"] < cost:
        print("Not enough credits to pay shipping costs.")
        return

    player["inventory"]["alloys"] -= amount
    player["credits"] -= cost

    shipment = {
        "amount": amount,
        "arrival_tick": tick + route["travel_time"],
        "type": "outbound"
    }

    in_transit.append(shipment)
    print(f"[Shipping] Sent {amount} alloys to Haven (arrives at Stardate {shipment['arrival_tick']}).")

# Shipment Resolution
def resolve_shipments():
    global in_transit

    arrived = [s for s in in_transit if s["arrival_tick"] <= tick]
    in_transit = [s for s in in_transit if s["arrival_tick"] > tick]

    for shipment in arrived:
        amount = shipment["amount"]

        # -----------------------------
        # RETURN SHIPMENTS
        # -----------------------------
        if shipment["type"] == "return":
            player["inventory"]["alloys"] += amount
            print(f"[Return Arrived] {amount} alloys returned to Forge.")
            continue

        # -----------------------------
        # OUTBOUND SHIPMENTS
        # -----------------------------
        effective_risk = route["risk"] * (amount / 10)
        if random.random() < effective_risk:
            lost = amount // 2
            amount -= lost
            print(f"[Risk] Shipment disrupted! Lost {lost} alloys.")

        sellable = min(amount, haven["demand_remaining"])
        unsold = amount - sellable

        revenue = sellable * haven["current_price"]
        player["credits"] += revenue
        haven["demand_remaining"] -= sellable

        print(f"[Arrival] Sold {sellable} alloys for {revenue:.2f} credits.")

        if unsold <= 0:
            continue

        print(f"[Market] {unsold} alloys unsold.")

        # -----------------------------
        # STORE OPTION
        # -----------------------------
        available_space = haven["warehouse_capacity"] - haven["warehouse_inventory"]
        stored = min(unsold, available_space)
        unsold -= stored

        if stored > 0:
            haven["warehouse_inventory"] += stored
            print(f"[Warehouse] Stored {stored} alloys at Haven.")

        # -----------------------------
        # RETURN OPTION
        # -----------------------------
        if unsold > 0:
            return_shipment = {
                "amount": unsold,
                "arrival_tick": tick + int(route["travel_time"] * RETURN_SHIPPING_MULTIPLIER),
                "type": "return"
            }
            in_transit.append(return_shipment)
            print(f"[Return] {unsold} alloys sent back to Forge.")

# Inventory Upkeep Costs
def inventory_upkeep():
    cost = player["inventory"]["alloys"] * INVENTORY_COST_PER_UNIT
    player["credits"] -= cost

    if cost > 0:
        print(f"[Storage] Paid {cost:.2f} credits to store inventory.")

# Warehouse Upkeep Costs
def warehouse_upkeep():
    cost = haven["warehouse_inventory"] * haven["warehouse_storage_cost"]
    player["credits"] -= cost

    if cost > 0:
        print(f"[Warehouse] Paid {cost:.2f} credits in warehouse fees.")

# Reset Demand
def reset_demand():
    haven["demand_remaining"] = haven["demand_per_tick"]

# Time Management
def advance_time(steps):
    global tick
    print(f"Advancing time by {steps} tick(s).")

    for _ in range(steps):
        tick += 1
        print(f"\nStardate {tick}")

        inventory_upkeep()
        warehouse_upkeep()
        produce()
        resolve_shipments()
        reset_demand()

# =============================
# CLI
# =============================

# Status Menu
def status():
    print("\n--- STATUS ---")
    print(f"Stardate: {tick}")
    print(f"Credits: {player['credits']:.2f}")
    print(f"Inventory: {player['inventory']['alloys']} alloys")
    print(f"In Transit: {len(in_transit)} shipments")
    print(f"Warehouse: {haven['warehouse_inventory']}/{haven['warehouse_capacity']}")
    print("----------------\n")

# Help Manu
def help_menu():
    print("""
Commands:
 status                 Show current state
 ship <amount>          Ship alloys to Haven
 tick <n>               Advance time
 help                   Show help
 quit                   Exit
""")

# Main Function Loop
def main():
    print("=== Galactic Trade Simulator (CLI PoC) ===")
    help_menu()

    while True:
        cmd = input("> ").strip().split()
        if not cmd:
            continue

        if cmd[0] == "help":
            help_menu()
        elif cmd[0] == "status":
            status()
        elif cmd[0] == "ship" and len(cmd) == 2:
            ship(int(cmd[1]))
        elif cmd[0] == "tick" and len(cmd) == 2:
            advance_time(int(cmd[1]))
        elif cmd[0] == "quit":
            print("Until next time, Space Cowboy.")
            break
        else:
            print("Unknown command. Type 'help'.")

# Run Main
main()
input("\n\nPress the enter key to exit.")

#
# vim: set syntax=python
#
