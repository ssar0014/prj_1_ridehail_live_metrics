import dagster as dg
import csv
import json


@dg.asset
def processed_data():
    data_dictionary = {}
    with open("data/sample_data.csv", newline="") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=" ", quotechar="|")
        for idx, row in enumerate(spamreader):
            data_dictionary[idx] = row
    data_dictionary = json.dumps(data_dictionary, indent=4)
    with open("data/result.json", "w") as fp:
        json.dump(data_dictionary, fp)
    return f"{data_dictionary} file processing complete!"


defs = dg.Definitions(assets=[processed_data])
