ships_slot = []
ships = ["patrol_boat", "battleship", "carrier", "destroyer", "submarine"]
for ship in ships:
    ships_slot.append({"id": ship, "name": {"value": ship.replace("_", " ").title()}})
    
print(ships_slot)

