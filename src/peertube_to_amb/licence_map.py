"""PeerTube licence ID to Creative Commons URI mapping."""

LICENCE_MAP: dict[str, str] = {
    "1": "https://creativecommons.org/licenses/by/4.0/",
    "2": "https://creativecommons.org/licenses/by-sa/4.0/",
    "3": "https://creativecommons.org/licenses/by-nd/4.0/",
    "4": "https://creativecommons.org/licenses/by-nc/4.0/",
    "5": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    "6": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
    "7": "https://creativecommons.org/publicdomain/zero/1.0/",
}


def get_licence_uri(identifier: str) -> str | None:
    """Return the Creative Commons URI for a PeerTube licence ID.

    Args:
        identifier: PeerTube licence ID as a string (e.g. "1" through "7").

    Returns:
        The corresponding CC licence URI, or None if the identifier is unknown.
    """
    return LICENCE_MAP.get(identifier)
