import json
import os

# Function to append a new entry with an updated "id"
def append_entry(data, info, cut, cut_name):
    max_id = max(data.values(), key=lambda x: x['id'])['id']
    new_id = max_id + 1
    new_entry = {
        f"{cut_name}": {
            "cut": cut,
            "id": new_id,
            "info": info
        }
    }
    data.update(new_entry)

input_file = "/sdf/group/hps/users/alspellm/src/hpstr/analysis/selections/Tight_loose_L1L1.json"
output_basename = os.path.basename(input_file).split('.')[0]
for code in range(16):
    binary = format(code, '04b')
    print(binary)
    # Read the input JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)

        # Append as many new entries as you like
        append_entry(data, "< hit code %s"%(binary), float(code), "hitCode_lt")
        append_entry(data, "> hit code %s"%(binary), float(code), "hitCode_gt")

    # Save the updated data to a new JSON file
    output_file = "%s_hc%i_%s.json"%(output_basename, code,binary)
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Updated data saved to {output_file}")
