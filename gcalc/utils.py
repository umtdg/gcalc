from typing import Any, Dict, List, Optional


def check_dict_keys(d: Dict[str, Any],
                    expected: List[str],
                    throw: bool = False) -> Optional[List[str]]:
    missing = [key for key in expected if key not in d]
    if throw:
        if missing:
            raise KeyError("Following keys could not found: {}".format(
                ", ".join(missing)
            ))

    return missing
