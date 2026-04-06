import httpx
import json
from ..config import OLLAMA_BASE_URL, OLLAMA_MODEL


async def get_ai_response(messages: list) -> str:
    """Send conversation to Ollama and return the assistant reply."""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={"model": OLLAMA_MODEL, "messages": messages, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get(
                "content",
                "I apologize, but I couldn't generate a response. Please try again.",
            )
    except httpx.ConnectError:
        return (
            "⚠️ Could not connect to Ollama. Please make sure Ollama is running "
            "(`ollama serve`) and the model is pulled (`ollama pull llama3`)."
        )
    except Exception as e:
        return f"⚠️ AI service error: {e}. Please ensure Ollama is running."


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
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("response", "{}")

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                start = text.find("{")
                end = text.rfind("}") + 1
                if start != -1 and end > start:
                    return json.loads(text[start:end])
                return _fallback_cv_data()
    except Exception:
        return _fallback_cv_data()


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
