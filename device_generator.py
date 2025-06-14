import json
import hashlib
import os
from typing import List, TypeVar, Type, Dict
from pathlib import Path
from dataclasses import dataclass

_T = TypeVar("_T")

@dataclass
class DeviceInfo:
    device_model: str
    system_version: str
    lang_code: str
    system_lang_code: str
    app_version: str
    lang_pack: str
    api_id: str
    api_hash: str

    def to_dict(self) -> Dict:
        return {
            "device_model": self.device_model,
            "system_version": self.system_version,
            "lang_code": self.lang_code,
            "system_lang_code": self.system_lang_code,
            "app_version": self.app_version,
            "lang_pack": self.lang_pack,
            "api_id": self.api_id,
            "api_hash": self.api_hash
        }

class BaseDeviceGenerator:
    device_list: List[DeviceInfo] = []
    device_models: List[str | Dict] = []
    system_versions: List[str | Dict] = []
    lang_codes: List[str] = []
    system_lang_codes: List[str] = []
    app_versions: List[str] = []
    lang_packs: List[str] = []
    api_id: List[str] = []
    api_hash: List[str] = []
    platform: str = ""
    data_dir: str = "data"

    @classmethod
    def load_data(cls) -> None:
        json_path = Path(cls.data_dir) / f"{cls.platform.lower()}.json"
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cls.device_models = data.get("device_models", [])
        cls.system_versions = data.get("system_versions", [])
        cls.lang_codes = data.get("lang_codes", [])
        cls.system_lang_codes = data.get("system_lang_codes", cls.lang_codes)
        cls.app_versions = data.get("app_versions", [])
        cls.lang_packs = data.get("lang_packs", ["default"])
        cls.api_id = data.get("api_id", [""])
        cls.api_hash = data.get("api_hash", [""])
        
        cls.lang_packs = [lp for lp in cls.lang_packs if lp and isinstance(lp, str)]
        if not cls.lang_packs:
            cls.lang_packs = ["en-US"]  

    @classmethod
    def random_device(cls: Type['BaseDeviceGenerator'], unique_id: str = None) -> str:
        hash_id = cls._str_to_hash_id(unique_id)
        device_info = cls._random_device(hash_id)
        return json.dumps(device_info.to_dict(), ensure_ascii=False)

    @classmethod
    def _random_device(cls, hash_id: int) -> DeviceInfo:
        cls._generate()
        device = cls._hash_to_value(hash_id, cls.device_list)
        lang_code = cls._hash_to_value(hash_id + 1, cls.lang_codes)
        system_lang_code = cls._hash_to_value(hash_id + 2, cls.system_lang_codes)
        app_version = cls._hash_to_value(hash_id + 3, cls.app_versions)
        lang_pack = cls._hash_to_value(hash_id + 4, cls.lang_packs)
        api_id = cls._hash_to_value(hash_id + 5, cls.api_id)
        api_hash = cls._hash_to_value(hash_id + 6, cls.api_hash)
        return DeviceInfo(
            device_model=device.device_model,
            system_version=device.system_version,
            lang_code=lang_code,
            system_lang_code=system_lang_code,
            app_version=app_version,
            lang_pack=lang_pack,
            api_id=api_id,
            api_hash=api_hash
        )

    @classmethod
    def _generate(cls) -> None:
        if not cls.device_list:
            cls.load_data()
            cls.device_list = []
            if cls.platform == "iOS":
                for model_id, suffixes in cls.device_models.items():
                    base_model = f"iPhone {model_id}" if model_id != "SE" else "iPhone SE"
                    for suffix in suffixes:
                        model_name = f"{base_model}{suffix}".strip()
                        for major, minors in cls.system_versions.items():
                            for minor, patches in minors.items():
                                version = f"{major}.{minor}" if not patches else f"{major}.{minor}.{patches[0]}"
                                cls.device_list.append(DeviceInfo(
                                    device_model=model_name,
                                    system_version=version,
                                    lang_code=cls.lang_codes[0] if cls.lang_codes else "en",
                                    system_lang_code=cls.system_lang_codes[0] if cls.system_lang_codes else "en-US",
                                    app_version=cls.app_versions[0] if cls.app_versions else "1.0.0",
                                    lang_pack=cls.lang_packs[0] if cls.lang_packs else "default",
                                    api_id=cls.api_id[0] if cls.api_id else "",
                                    api_hash=cls.api_hash[0] if cls.api_hash else ""
                                ))
            elif cls.platform == "macOS":
                for model in cls.device_models:
                    for version in cls.system_versions:
                        cls.device_list.append(DeviceInfo(
                            device_model=model,
                            system_version=version,
                            lang_code=cls.lang_codes[0] if cls.lang_codes else "en",
                            system_lang_code=cls.system_lang_codes[0] if cls.system_lang_codes else "en-US",
                            app_version=cls.app_versions[0] if cls.app_versions else "1.0.0",
                            lang_pack=cls.lang_packs[0] if cls.lang_packs else "macos",
                            api_id=cls.api_id[0] if cls.api_id else "",
                            api_hash=cls.api_hash[0] if cls.api_hash else ""
                        ))
            else:
                
                for model in cls.device_models:
                    for version in cls.system_versions:
                        cls.device_list.append(DeviceInfo(
                            device_model=model,
                            system_version=version,
                            lang_code=cls.lang_codes[0] if cls.lang_codes else "en",
                            system_lang_code=cls.system_lang_codes[0] if cls.system_lang_codes else "en-US",
                            app_version=cls.app_versions[0] if cls.app_versions else "1.0.0",
                            lang_pack=cls.lang_packs[0] if cls.lang_packs else "default",
                            api_id=cls.api_id[0] if cls.api_id else "",
                            api_hash=cls.api_hash[0] if cls.api_hash else ""
                        ))

    @classmethod
    def _str_to_hash_id(cls, unique_id: str = None) -> int:
        if unique_id is not None and not isinstance(unique_id, str):
            unique_id = str(unique_id)
        byte_id = os.urandom(32) if unique_id is None else unique_id.encode("utf-8")
        return int(hashlib.sha1(byte_id).hexdigest(), 16) % (10 ** 12)

    @classmethod
    def _hash_to_value(cls, hash_id: int, values: List[_T]) -> _T:
        if not values:
            raise ValueError(f"No values available for {cls.platform}")
        return values[hash_id % len(values)]

    @classmethod
    def _clean_and_simplify(cls, text: str) -> str:
        return " ".join(word for word in text.split() if word)

class WindowsDevice(BaseDeviceGenerator):
    platform = "Windows"

class LinuxDevice(BaseDeviceGenerator):
    platform = "Linux"

class macOSDevice(BaseDeviceGenerator):
    platform = "macOS"

class AndroidDevice(BaseDeviceGenerator):
    platform = "Android"

class iOSDevice(BaseDeviceGenerator):
    platform = "iOS"

def get_random_device(platform: str, unique_id: str = None, data_dir: str = "data") -> str:
    platform_classes = {
        "Windows": WindowsDevice,
        "Linux": LinuxDevice,
        "macOS": macOSDevice,
        "Android": AndroidDevice,
        "iOS": iOSDevice
    }
    device_class = platform_classes.get(platform)
    if not device_class:
        raise ValueError(f"Unsupported platform: {platform}")
    device_class.data_dir = data_dir
    return device_class.random_device(unique_id)