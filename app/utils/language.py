from fastapi import Request

def get_preferred_language(request: Request) -> str:
    accept_language = request.headers.get("accept-language", "ko")
    for lang in accept_language.split(","):
        if lang.startswith("ko"):
            return "ko"
        elif lang.startswith("en"):
            return "en"
        elif lang.startswith("ja"):
            return "ja"
    return "ko"
