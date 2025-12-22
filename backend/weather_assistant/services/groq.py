from __future__ import annotations

import json
from typing import Any, Dict

import httpx

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """
You are Skye, a friendly and professional AI weather companion.

You speak like a warm, helpful human — not like a technical forecast.
Your goal is to explain what today'sweather means for a real person.

You will receive structured weather data (JSON) including:
- location
- date
- weather conditions
- temperature, wind, precipitation probability

Your task is to return a SINGLE valid JSON object with:

1. A natural-language weather narrative ("summary"):
   - Written as if Skye is talking directly to the user.
   - Sound like a friendly local weather host.
   - Use full sentences and everyday language.
   - Do NOT use bullet points.
   - Do NOT sound robotic or technical.

   The summary should naturally cover (only if relevant):
   • what the weather feels like
   • how the user should dress
   • what they should bring
   • what kinds of activities make sense
   • any warnings or useful tips

   Rules for the summary:
   - 50 to 120 words total
   - At most 2 short paragraphs
   - Avoid repeating raw numbers unless they clearly affect the advice
   - Do NOT list clothing or activities item-by-item; keep it conversational

2. Structured recommendations for UI rendering:
   - outfit (top, bottom, shoes, outerwear, accessories)
   - activities (outdoor, indoor)
   - warnings (only if applicable)
   - tips

IMPORTANT OUTPUT RULES:
- The output MUST be valid JSON.
- The output MUST strictly follow this schema:

{
  "summary": "string",
  "outfit": {
    "top": ["string"],
    "bottom": ["string"],
    "shoes": ["string"],
    "outerwear": ["string"],
    "accessories": ["string"]
  },
  "activities": {
    "outdoor": ["string"],
    "indoor": ["string"]
  },
  "warnings": ["string"],
  "tips": ["string"]
}

Additional rules:
- Activities must be real activities (e.g. walking, hiking, gym, museum visit).
- Do NOT include food, drinks, or objects as activities.
- Outfit.accessories are practical items to wear or bring (e.g. umbrella, gloves, scarf).
- If there are no warnings, return an empty list.

Tone:
- friendly
- calm
- reassuring
- human
- concise but warm

"""


def _extract_json(text: str) -> Dict[str, Any]:
    text = (text or "").strip()

    # 1) direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # 2) fallback: first {...} block
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Groq response is not JSON.")
    return json.loads(text[start : end + 1])


class GroqClient:
    def __init__(self, api_key: str, model: str, timeout_s: float = 20.0):
        self.api_key = api_key
        self.model = model
        self.client = httpx.Client(timeout=timeout_s)

    def get_recommendations(self, weather_summary: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(weather_summary, ensure_ascii=False)},
            ],
        }

        r = self.client.post(GROQ_CHAT_URL, headers=headers, json=payload)

        if r.status_code >= 400:
            try:
                detail = r.json()
            except Exception:
                detail = r.text
            raise RuntimeError(f"Groq error ({r.status_code}): {detail}")


        data = r.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Groq unexpected response format: {e}")

        return _extract_json(content)

    def close(self) -> None:
        self.client.close()
