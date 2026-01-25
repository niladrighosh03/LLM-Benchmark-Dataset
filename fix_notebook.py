
import json

nb_path = "/DATA/rohan_kirti/niladri2/benchmark/Without_image_mcq_generator.ipynb"

print(f"Reading {nb_path}...")
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

found_cell_10 = False
found_cell_7 = False

# Iterate through cells
for cell in nb['cells']:
    # Fix 1: max_tokens in Qwen llm_generate
    # We look for the definition line if ID search is not robust (though ID is preferred)
    # Cell ID from view_file: 50c4f5a2
    if cell.get('id') == "50c4f5a2":
        print("Found Qwen llm_generate cell (50c4f5a2).")
        found_cell_10 = True
        new_source = []
        changed = False
        for line in cell['source']:
            if "max_tokens: int = 100" in line:
                print(f"  Replacing line: {line.strip()}")
                line = line.replace("max_tokens: int = 100", "max_tokens: int = 2048")
                print(f"  With:           {line.strip()}")
                changed = True
            new_source.append(line)
        if changed:
            cell['source'] = new_source
        else:
            print("  WARNING: Could not find 'max_tokens: int = 100' in this cell.")
    
    # Fix 2: Add raw response print
    # Cell ID from view_file: 952819fe
    if cell.get('id') == "952819fe":
        print("Found generate_mcqs_from_chunks cell (952819fe).")
        found_cell_7 = True
        new_source = []
        changed = False
        for line in cell['source']:
            new_source.append(line)
            if 'print(f"ERROR: {e}")' in line:
                # Check if next line is already the print we want (idempotency)
                # However, since we are appending to new_source, we can't easily peek ahead in source
                # But simple check: if we already ran this, we might duplicate.
                # Risk accepted for now, or I can check if 'Raw Response' is usually not there.
                print(f"  Inserting raw response print after: {line.strip()}")
                new_line = '                print(f"Raw Response: {response}")\n'
                new_source.append(new_line)
                changed = True
        if changed:
            cell['source'] = new_source
        else:
            print("  WARNING: Could not find 'print(f\"ERROR: {e}\")' in this cell.")

if not found_cell_10:
    print("ERROR: Did not find Cell 10 (50c4f5a2)")
if not found_cell_7:
    print("ERROR: Did not find Cell 7 (952819fe)")

print("Saving file...")
with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print("Done.")
