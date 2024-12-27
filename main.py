import json

if __name__ == "__main__":
    new_json = []

    # read json
    with open('./config/platforms.json') as f:
        data = json.load(f)

    for record in data:
        record['cost'] = 0
        record['in_service'] = True
        record['components'] = 0
        record['components_list_id'] = ""

        new_json.append(record)

    # save json
    with open('config/data/dict/platforms_dict.json', 'w') as f:
        json.dump(new_json, f, indent=4)