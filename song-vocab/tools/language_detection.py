from langdetect import detect

def detect_language(text: str) -> str:
    """
    Detect the language of the given text.

    Args:
        text (str): The text to detect the language for.

    Returns:
        str: The detected language code (e.g., 'de' for German).
    """
    return detect(text)
