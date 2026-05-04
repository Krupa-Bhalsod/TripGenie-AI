import os
import yaml
from functools import lru_cache

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")

@lru_cache()
def load_prompt(file_name: str, key: str = "system_prompt") -> str:
    """
    Load a prompt from a YAML file in the prompts directory.
    """
    if not file_name.endswith(".yaml"):
        file_name += ".yaml"
    
    file_path = os.path.join(PROMPTS_DIR, file_name)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    if key not in data:
        raise KeyError(f"Key '{key}' not found in {file_name}")
        
    return data[key]
