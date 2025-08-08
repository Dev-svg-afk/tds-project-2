import json

def summarize_csv(path):
    import pandas as pd
    df = pd.read_csv(path, nrows=1000)
    summary = {
        "type": "csv",
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "sample_rows": df.head(3).to_dict(orient="records"),
        "num_rows": len(df),
    }
    return json.dumps(summary, indent=2)


def summarize_json(path):
    import json
    with open(path) as f:
        data = json.load(f)

    summary ={
        "type": "json",
        "keys": list(data.keys()) if isinstance(data, dict) else None,
        "sample": data[:3] if isinstance(data, list) else None,
        "structure": str(type(data)),
    }

    return json.dumps(summary, indent=2)

def summarize_text(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    summary = {
        "type": "text",
        "length": len(content),
        "preview": content[:500]
    }

    return json.dumps(summary, indent=2)