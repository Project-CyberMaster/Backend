def challenge(value: str) -> int:
    mapping = {
        "one": 2,
        "two": 2,
        "three": 2
    }
    return mapping.get(value, None) 
