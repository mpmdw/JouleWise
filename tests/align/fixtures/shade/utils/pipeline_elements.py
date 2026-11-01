"""The fixture formatter has the same call shape as upstream's formatter."""

import json


def tool_result_to_str(result):
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    return result if isinstance(result, str) else json.dumps(result, sort_keys=True)
