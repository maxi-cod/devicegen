from device_generator import get_random_device
import json


platforms = ["macOS", "Windows", "Linux", "Android", "iOS"]


for platform in platforms:
    try:
        device_json = get_random_device(platform, unique_id="user123", data_dir="data")
        device = json.loads(device_json)
        print(f"{platform}:")
        print(json.dumps(device, indent=2, ensure_ascii=False))
        print() 
    except Exception as e:
        print(f"Ошибка для {platform}: {str(e)}\n")