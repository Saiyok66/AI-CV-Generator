import httpx
import json
from ..config import OLLAMA_BASE_URL, OLLAMA_MODEL, AI_PROVIDER, GROQ_API_KEY, GROQ_MODEL

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


async def _ollama_chat(messages: list) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "")


async def _groq_chat(messages: list) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"model": GROQ_MODEL, "messages": messages, "temperature": 0.7, "max_tokens": 2048},
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def _ollama_generate(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "format": "json"},
        )
        response.raise_for_status()
        return response.json().get("response", "{}")


async def _groq_generate(prompt: str) -> str:
    messages = [
        {"role": "system", "content": "You are a JSON extraction assistant. You MUST respond with valid JSON only. Never use null — use empty string \"\" for missing text and empty array [] for missing lists."},
        {"role": "user", "content": prompt},
    ]
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"model": GROQ_MODEL, "messages": messages, "temperature": 0.2, "max_tokens": 3000,
                  "response_format": {"type": "json_object"}},
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


async def get_ai_response(messages: list) -> str:
    """Send conversation to AI provider and return the assistant reply."""
    try:
        if AI_PROVIDER == "groq":
            text = await _groq_chat(messages)
        else:
            text = await _ollama_chat(messages)
        return text or "I apologize, but I couldn't generate a response. Please try again."
    except httpx.ConnectError:
        return (
            "⚠️ Could not connect to the AI service. Please make sure it is running."
        )
    except Exception as e:
        return f"⚠️ AI service error: {e}"


async def extract_cv_data(conversation: str) -> dict:
    """Extract structured CV data from the conversation using the LLM."""
    prompt = (
        "Analyze the following conversation and extract ALL CV/resume information "
        "into a structured JSON format.\n"
        "Return ONLY valid JSON with no additional text.\n\n"
        "The JSON must have this exact structure:\n"
        "{\n"
        '  "name": "Full Name",\n'
        '  "email": "email@example.com",\n'
        '  "phone": "phone number",\n'
        '  "location": "City, Country",\n'
        '  "linkedin": "LinkedIn URL if provided",\n'
        '  "summary": "Professional summary (2-3 sentences)",\n'
        '  "experience": [\n'
        "    {\n"
        '      "title": "Job Title",\n'
        '      "company": "Company Name",\n'
        '      "duration": "Start - End",\n'
        '      "achievements": ["achievement 1", "achievement 2"]\n'
        "    }\n"
        "  ],\n"
        '  "education": [\n'
        "    {\n"
        '      "degree": "Degree Name",\n'
        '      "institution": "University Name",\n'
        '      "year": "Year or Duration"\n'
        "    }\n"
        "  ],\n"
        '  "skills": ["skill1", "skill2"],\n'
        '  "certifications": ["cert1"],\n'
        '  "projects": [\n'
        "    {\n"
        '      "name": "Project Name",\n'
        '      "description": "Brief description"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "If any field was not provided, use an empty string or empty array.\n\n"
        f"Conversation:\n{conversation}\n\n"
        "Return ONLY the JSON:"
    )

    try:
        if AI_PROVIDER == "groq":
            text = await _groq_generate(prompt)
        else:
            text = await _ollama_generate(prompt)

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                data = json.loads(text[start:end])
            else:
                print(f"[extract_cv_data] Could not parse JSON from: {text[:200]}")
                return _fallback_cv_data()

        return _normalize_cv_data(data)
    except Exception as e:
        print(f"[extract_cv_data] Error: {type(e).__name__}: {e}")
        return _fallback_cv_data()


def _normalize_cv_data(data: dict) -> dict:
    """Replace None/null values with empty strings or empty lists."""
    defaults = _fallback_cv_data()
    result = {}
    for key, default_val in defaults.items():
        val = data.get(key)
        if val is None:
            result[key] = default_val
        elif isinstance(default_val, list) and not isinstance(val, list):
            result[key] = default_val
        else:
            result[key] = val
    return result


def _fallback_cv_data() -> dict:
    return {
        "name": "Your Name",
        "email": "email@example.com",
        "phone": "",
        "location": "",
        "linkedin": "",
        "summary": "Professional seeking new opportunities.",
        "experience": [],
        "education": [],
        "skills": [],
        "certifications": [],
        "projects": [],
    }
