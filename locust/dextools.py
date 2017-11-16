import json
import pandas as pd

def get_nested_record(key, grp, parent, plain):
    rec = {}
    for i in range(len(key)):
        rec[plain[i]] = key[i]

    for field in parent:
        rec[field] = list(grp[field].unique())

    return rec

def csv_to_json(csv_path, parent_key, plain_key):
    df = pd.read_csv(csv_path)
    records = []
    for key, grp in df.groupby(plain_key):
        rec = get_nested_record(key, grp, parent_key, plain_key)
        records.append(rec)

    return json.dumps(records, indent=2)
