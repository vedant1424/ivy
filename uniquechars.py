def get_unique_chars_from_file(filename):
    unique_chars = ""
    seen_chars = set()
    
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                for char in line.strip():  # Process each character in the line
                    if char not in seen_chars:
                        seen_chars.add(char)
                        unique_chars += char
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    
    return unique_chars

if __name__ == "__main__":
    filename = "names.txt"
    result = get_unique_chars_from_file(filename)
    if result:
        print("Unique characters in order:", result)
