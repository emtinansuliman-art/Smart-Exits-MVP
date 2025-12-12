
# processing_and_model.py
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

def load_fcd(FCD_FILE):
    fcd_data = []
    tree = ET.parse(FCD_FILE)
    root = tree.getroot()
    for timestep in root.findall('timestep'):
        time = float(timestep.attrib["time"])
        for v in timestep.findall("vehicle"):
            fcd_data.append({
                "time": time,
                "vehicle_id": v.attrib.get("id", ""),
                "x": float(v.attrib.get("x", 0)),
                "y": float(v.attrib.get("y", 0)),
                "speed": float(v.attrib.get("speed", 0)),
                "angle": float(v.attrib.get("angle", 0)),
                "lane": v.attrib.get("lane", ""),
                "edge": v.attrib.get("edge", "")
            })
    df_fcd = pd.DataFrame(fcd_data)
    df_fcd = df_fcd[(df_fcd["x"] != 0) & (df_fcd["y"] != 0)]
    return df_fcd

def create_grid(df_fcd, GRID_SIZE=100):
    x_min, x_max = df_fcd["x"].min(), df_fcd["x"].max()
    y_min, y_max = df_fcd["y"].min(), df_fcd["y"].max()
    df_fcd["grid_x"] = ((df_fcd["x"] - x_min) // GRID_SIZE).astype(int)
    df_fcd["grid_y"] = ((df_fcd["y"] - y_min) // GRID_SIZE).astype(int)
    df_fcd["minute"] = (df_fcd["time"] // 60).astype(int)
    return df_fcd

def aggregate_grid(df_fcd):
    df_summary = df_fcd.groupby(["grid_x", "grid_y", "minute"]).agg({
        "vehicle_count": ("vehicle_id", "count"),
        "avg_speed": ("speed", "mean"),
    }).reset_index()
    return df_summary

def build_model(df_summary):
    X = df_summary[["grid_x", "grid_y", "minute"]]
    y = df_summary["vehicle_count"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model

def predict_next_minute(df_summary, model, threshold=10):
    next_minute = df_summary["minute"].max() + 1
    df_next = df_summary.copy()
    df_next["minute"] = next_minute
    df_next["predicted_vehicle_count"] = model.predict(
        df_next[["grid_x", "grid_y", "minute"]]
    )
    df_next["smart_exit_action"] = df_next["predicted_vehicle_count"].apply(
        lambda x: "close" if x > threshold else "open"
    )
    final = df_next.groupby(["grid_x", "grid_y"]).agg({
        "predicted_vehicle_count": "mean",
        "smart_exit_action": "first",
    }).reset_index()
    return final

def generate_smart_exits(FCD_FILE):
    df_fcd = load_fcd(FCD_FILE)
    df_fcd = create_grid(df_fcd)
    df_summary = aggregate_grid(df_fcd)
    model = build_model(df_summary)
    smart_exits = predict_next_minute(df_summary, model)
    return smart_exits.to_dict(orient="records")
