from data_storage_functions import save_data, load_data, clear_all_data

filename = "test.csv"

print("Clearing existing data...")
print(clear_all_data(filename))

print("Saving first card...")
print(save_data(filename, {
    "name": "USAA",
    "balance": "500"
}))

print("Saving second card...")
print(save_data(filename, {
    "name": "Capital One",
    "balance": "300"
}))

print("Loading data...")
print(load_data(filename))

print("Clearing all data...")
print(clear_all_data(filename))

print("Loading after clear...")
print(load_data(filename))
