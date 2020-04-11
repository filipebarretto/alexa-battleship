squares_slot = []
number_names = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
for l in letters:
    for n in range(1, 11):
        squares_slot.append({"id": l + "_" + str(n), "name": {"value": l + " " + number_names[n], "synonyms": [l.lower() + " " + number_names[n], l + " " + str(n), l.lower() + " " + str(n)]}})

print(squares_slot)
