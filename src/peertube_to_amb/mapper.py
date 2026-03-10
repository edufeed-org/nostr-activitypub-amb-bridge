"""Map PeerTube video metadata to AMB Nostr event tags."""

import logging

from peertube_to_amb.licence_map import get_licence_uri

logger = logging.getLogger(__name__)


def map_video_to_nostr_tags(
    video: dict,
    creator_cache: dict | None = None,
) -> tuple[list[list[str]], str]:
    """Convert a PeerTube video object into Nostr event tags and content.

    Transforms ActivityPub video metadata into the tag structure expected by
    the AMB (Nostr) protocol, including licence, creator, and media tags.

    Args:
        video: A dict of video metadata from the PeerTube ActivityPub outbox.
        creator_cache: Optional cache of creator profile lookups, keyed by
            actor URL. Mutated in-place if provided.

    Returns:
        A tuple of (tags, content) where tags is a list of [key, value, ...]
        lists and content is a human-readable summary string.
    """
    # Step 0: Skip live broadcasts
    if video.get("isLiveBroadcast"):
        return ([], "")

    tags: list[list[str]] = []

    # Step 1: d tag — AP object id
    tags.append(["d", video["id"]])

    # Step 2: type tags
    tags.append(["type", "LearningResource"])
    tags.append(["type", "VideoObject"])

    # Step 3: name
    tags.append(["name", video["name"]])

    # Step 4: description — from content, falling back to summary
    content_value = video.get("content") or ""
    summary_value = video.get("summary") or ""
    description = content_value or summary_value
    if description:
        tags.append(["description", description])

    # Step 5: datePublished
    tags.append(["datePublished", video["published"]])

    # Step 6: dateModified
    tags.append(["dateModified", video["updated"]])

    # Step 7: dateCreated — originallyPublishedAt, fallback to published
    date_created = video.get("originallyPublishedAt") or video["published"]
    tags.append(["dateCreated", date_created])

    # Step 8: duration
    if video.get("duration"):
        tags.append(["duration", video["duration"]])

    # Step 9: inLanguage
    language = video.get("language")
    if language and language.get("identifier"):
        tags.append(["inLanguage", language["identifier"]])

    # Step 10: license:id
    licence = video.get("licence")
    if licence and licence.get("identifier"):
        uri = get_licence_uri(licence["identifier"])
        if uri:
            tags.append(["license:id", uri])

    # Step 11: hardcoded AMB tags
    tags.append(["learningResourceType:id", "http://w3id.org/kim/hcrt/video"])
    tags.append(["learningResourceType:prefLabel:en", "Video"])
    tags.append(["isAccessibleForFree", "true"])

    # Step 12: image — pick largest icon by width
    icons = video.get("icon") or []
    if icons:
        largest = max(icons, key=lambda i: i.get("width", 0))
        tags.append(["image", largest["url"]])

    # Step 13: t tags from hashtags
    for tag_item in video.get("tag") or []:
        if tag_item.get("type") == "Hashtag":
            tags.append(["t", tag_item["name"]])

    # Step 13b: category as t tag
    category = video.get("category")
    if category and category.get("name"):
        tags.append(["t", category["name"]])

    # Step 14: creator from attributedTo
    if creator_cache is not None:
        for attr in video.get("attributedTo") or []:
            actor_uri = attr if isinstance(attr, str) else attr.get("id", "")
            actor = creator_cache.get(actor_uri)
            if actor and actor.get("type") == "Person":
                tags.append(["creator:name", actor.get("name", "")])
                tags.append(["creator:type", "Person"])
                break

    # Step 15: r tag — text/html link
    for url_item in video.get("url") or []:
        if url_item.get("mediaType") == "text/html":
            tags.append(["r", url_item["href"]])
            break

    # Step 16: encoding tags — HLS nested video/mp4 links and flat video/mp4
    for url_item in video.get("url") or []:
        media_type = url_item.get("mediaType", "")
        if media_type == "application/x-mpegURL":
            # HLS: look for nested video/mp4 in tag array
            for nested in url_item.get("tag") or []:
                if nested.get("mediaType") == "video/mp4":
                    tags.append(["encoding:type", "MediaObject"])
                    tags.append(["encoding:contentUrl", nested["href"]])
                    tags.append(["encoding:encodingFormat", "video/mp4"])
                    tags.append(["encoding:contentSize", str(nested.get("size", ""))])
        elif media_type == "video/mp4":
            # Flat video/mp4 link
            tags.append(["encoding:type", "MediaObject"])
            tags.append(["encoding:contentUrl", url_item["href"]])
            tags.append(["encoding:encodingFormat", "video/mp4"])
            tags.append(["encoding:contentSize", str(url_item.get("size", ""))])

    # Step 17: caption tags from subtitleLanguage
    for sub in video.get("subtitleLanguage") or []:
        sub_url = sub.get("url")
        if isinstance(sub_url, list):
            # PeerTube returns a list of Link objects; pick the text/vtt one
            vtt = next(
                (link["href"] for link in sub_url if link.get("mediaType") == "text/vtt"),
                None,
            )
            if vtt:
                tags.append(["caption:id", vtt])
        elif isinstance(sub_url, str) and sub_url:
            tags.append(["caption:id", sub_url])
        if sub.get("identifier"):
            tags.append(["caption:inLanguage", sub["identifier"]])

    # Content string
    content_str = content_value if isinstance(content_value, str) else ""

    # Validate: every tag element must be a string
    validated_tags: list[list[str]] = []
    for tag in tags:
        if all(isinstance(elem, str) for elem in tag):
            validated_tags.append(tag)
        else:
            logger.warning(
                "Dropping tag with non-string element: %s (video %s)",
                tag,
                video.get("id", "?"),
            )

    return (validated_tags, content_str)
