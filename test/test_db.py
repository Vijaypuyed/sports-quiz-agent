from src.database import load_data, search_facts

load_data()
print("\nSearching...\n")

result = search_facts(
    "Football",
    "World Cup history"
)

print(result)