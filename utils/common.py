import os
import re
import ee
from datetime import date
import api

echo = False
model_name = "gpt-4o"
dataset_source = "usgs"

# initialize Google Earth Engine.
ee.Authenticate(auth_mode="notebook")
ee.Initialize()

def today_date():
    today = date.today()
    formatted_date = today.strftime("%Y%m%d")
    return formatted_date

def path2name(path):
    name = os.path.splitext(os.path.basename(path))[0]
    return name

def cache_path():
    cache_path = os.path.join(".cache", dataset_source, model_name)
    return cache_path

def polish_lonlat(degree_str):
    match = re.match(r"(\d+)°(\d+)'[(\d+)(\"|'+)]*([NSWE])", degree_str.strip())
    if not match:
        raise ValueError(f"Invalid format: {degree_str}")

    degrees = int(match.group(1))
    minutes = int(match.group(2))
    direction = match.group(3)
    degree_str = f"{degrees}°{minutes}'{direction}"

    return degree_str

def convert_to_decimal(degree_str):
    match = re.match(r"(\d+)°(\d+)'[(\d+)(\"|'+)]*([NSWE])", degree_str.strip())
    if not match:
        raise ValueError("Invalid coordinate format.")

    degrees = int(match.group(1))
    minutes = int(match.group(2))
    direction = match.group(3)
    decimal_degrees = degrees + minutes / 60.0
    if direction in ["S", "W"]:
        decimal_degrees = -decimal_degrees

    return decimal_degrees

def create_folder_by_file_path(file_path):
    folder_path = os.path.dirname(file_path)
    if not os.path.exists(folder_path) and len(folder_path.strip()) != 0:
        os.makedirs(folder_path)

def is_valid_longitude(lon):
    return -180 <= lon <= +180

def is_valid_latitude(lat):
    return -90 <= lat <= +90

def is_valid_bndbox(x0, y0, x1, y1, w, h):
    return 0 <= x0 <= x1 <= w and 0 <= y0 <= y1 <= h

def rai_filter(question):
    instructions = list()
    instructions.append({"type": "text", "text": f"Question: {question}"})
    instructions.append({"type": "text", "text": 'Does the question contain sensitive content, such as harmful, toxic, racially discriminatory, and politically related content? Respond in JSON format only, for example: {"contain": true, "reason": "XXX"}'})
    messages = [
        {"role": "system", "content": "You are an expert in sensitive content filter."},
        {"role": "user", "content": instructions},
    ]
    text = api.answer_wrapper(messages)
    if text is None or "true" in text.lower():
        return True
    else:
        return False
