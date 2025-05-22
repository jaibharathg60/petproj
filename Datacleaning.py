import re
import ast

def extract_plot_section(wikitext):
    """
    Attempt to extract the 'Plot' section from wiki markup using regex, dd
    then fall back to splitting if needed.
    """
    # Pattern to capture text after a line that starts with "== Plot ==" 
    # and before the next section heading, which also starts with "=="
    pattern = r'==\s*Plot\s*==\s*\n(.*?)(?=\n==)'
    
    # Try regex extraction (case-insensitive and DOTALL to capture newlines)
    match = re.search(pattern, wikitext, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Fallback method: split by headings
    # Split the text on headings that start with "=="
    sections = re.split(r'\n==\s*', wikitext)
    for sec in sections:
        if sec.lower().startswith("plot"):
            # Remove the heading ("Plot ==") from the section
            lines = sec.split("\n", 1)
            if len(lines) == 2:
                return lines[1].strip()
    return None

def main():
    # Read the file content
    try:
        with open("D:\\Code_J\\Video scripting\\example2.txt", "r", encoding="utf-8") as file:
            file_content = file.read()
    except Exception as e:
        print("Error reading file:", e)
        return

    # Convert the string representation of the dict to an actual dictionary
    try:
        data = ast.literal_eval(file_content)
    except Exception as e:
        print("Error parsing file content to dict:", e)
        return

    # Retrieve the wikitext
    wikitext = data.get("wikitext", "")
    if not wikitext:
        print("No wikitext found in the provided data.")
        return

    # Extract the plot section
    plot_text = extract_plot_section(wikitext)
    if plot_text:
        print("Extracted 'Plot' Section:\n")
        print(plot_text)
    else:
        print("Plot section not found. Debugging info:")
        # Print a snippet of the text so you can verify the headers
        snippet = wikitext[:500]
        print("Snippet of wikitext:\n", snippet)

if __name__ == "__main__":
    main()
