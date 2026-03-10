"""Tests for peertube_to_amb.mapper."""

import pytest

from peertube_to_amb.mapper import map_video_to_nostr_tags


def _find_tags(tags, key):
    """Return all tags matching a given key."""
    return [t for t in tags if t[0] == key]


def _find_tag(tags, key):
    """Return the first tag matching a given key, or None."""
    matches = _find_tags(tags, key)
    return matches[0] if matches else None


class TestTypeTagsAlwaysPresent:
    """Type tags must always be LearningResource and VideoObject."""

    def test_includes_learning_resource_type(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert ["type", "LearningResource"] in tags

    def test_includes_video_object_type(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert ["type", "VideoObject"] in tags


class TestHardcodedValues:
    """Hardcoded/default AMB values are always present."""

    def test_learning_resource_type_id(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert ["learningResourceType:id", "http://w3id.org/kim/hcrt/video"] in tags

    def test_learning_resource_type_pref_label(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert ["learningResourceType:prefLabel:en", "Video"] in tags

    def test_is_accessible_for_free(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert ["isAccessibleForFree", "true"] in tags


class TestDTag:
    """The d tag uses the AP object id as identifier."""

    def test_d_tag_uses_video_id(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert _find_tag(tags, "d") == [
            "d",
            "https://peertube.example.com/videos/watch/00000000-0000-4000-a000-000000000001",
        ]


class TestNameMapping:
    """Video name maps to name tag."""

    def test_name_tag_value(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert _find_tag(tags, "name") == [
            "name",
            "Test Video About 3D Printing",
        ]


class TestDurationMapping:
    """Duration maps directly as ISO 8601 duration."""

    def test_duration_tag_value(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert _find_tag(tags, "duration") == ["duration", "PT156S"]


class TestDatePublishedMapping:
    """Published date maps to datePublished tag."""

    def test_date_published(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert _find_tag(tags, "datePublished") == [
            "datePublished",
            "2026-02-28T10:25:54.431Z",
        ]


class TestDateModifiedMapping:
    """Updated date maps to dateModified tag."""

    def test_date_modified(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert _find_tag(tags, "dateModified") == [
            "dateModified",
            "2026-03-01T10:02:46.940Z",
        ]


class TestDateCreatedMapping:
    """originallyPublishedAt maps to dateCreated, falling back to published."""

    def test_date_created_from_originally_published(
        self, sample_video_ap, creator_cache
    ):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert _find_tag(tags, "dateCreated") == [
            "dateCreated",
            "2026-02-20T08:00:00.000Z",
        ]

    def test_date_created_falls_back_to_published_when_null(
        self, sample_video_ap_minimal
    ):
        tags, _ = map_video_to_nostr_tags(sample_video_ap_minimal)

        assert _find_tag(tags, "dateCreated") == [
            "dateCreated",
            "2026-01-15T12:00:00.000Z",
        ]


class TestInLanguageMapping:
    """Language object identifier maps to inLanguage tag."""

    def test_in_language_extraction(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert _find_tag(tags, "inLanguage") == ["inLanguage", "de"]


class TestLicenceMapping:
    """Licence identifier maps through licence_map to CC URI."""

    def test_licence_id_1_maps_to_cc_by_uri(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert _find_tag(tags, "license:id") == [
            "license:id",
            "https://creativecommons.org/licenses/by/4.0/",
        ]

    def test_licence_id_7_maps_to_cc0_uri(self, sample_video_ap_minimal):
        tags, _ = map_video_to_nostr_tags(sample_video_ap_minimal)

        assert _find_tag(tags, "license:id") == [
            "license:id",
            "https://creativecommons.org/publicdomain/zero/1.0/",
        ]


class TestTagKeywordMapping:
    """Hashtag type tags map to t tags; non-Hashtag types are skipped."""

    def test_hashtag_tags_become_t_tags(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        t_tags = _find_tags(tags, "t")
        t_values = [t[1] for t in t_tags]
        assert "3dprinting" in t_values
        assert "orcaslicer" in t_values

    def test_mention_tags_are_not_mapped(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        t_values = [t[1] for t in _find_tags(tags, "t")]
        assert "@admin@peertube.example.com" not in t_values

    def test_empty_tags_produce_no_t_tags(self, sample_video_ap_minimal):
        tags, _ = map_video_to_nostr_tags(sample_video_ap_minimal)

        # Education from category is allowed, but no hashtag-derived t tags
        hashtag_t = [
            t for t in _find_tags(tags, "t") if t[1] != "Education"
        ]
        assert hashtag_t == []


class TestContentAndDescription:
    """Content field and description tag mapping."""

    def test_content_present_maps_to_content_string(
        self, sample_video_ap, creator_cache
    ):
        _, content = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert content != ""

    def test_content_present_produces_description_tag(
        self, sample_video_ap, creator_cache
    ):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        desc = _find_tag(tags, "description")
        assert desc is not None

    def test_content_null_returns_empty_content_string(self, sample_video_ap_minimal):
        _, content = map_video_to_nostr_tags(sample_video_ap_minimal)

        assert content == ""

    def test_content_null_no_summary_skips_description_tag(
        self, sample_video_ap_minimal
    ):
        tags, _ = map_video_to_nostr_tags(sample_video_ap_minimal)

        assert _find_tag(tags, "description") is None

    def test_content_null_with_summary_fallback_uses_summary(
        self, sample_video_ap_with_summary_fallback
    ):
        tags, _ = map_video_to_nostr_tags(sample_video_ap_with_summary_fallback)

        desc = _find_tag(tags, "description")
        assert desc == ["description", "This is the summary text used as fallback"]


class TestIconImageMapping:
    """Icon array maps to image tag using largest resolution."""

    def test_picks_largest_icon_for_image_tag(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        image_tag = _find_tag(tags, "image")
        assert image_tag == [
            "image",
            "https://peertube.example.com/lazy-static/previews/00000000-0000-4000-a000-000000000002.jpg",
        ]

    def test_single_icon_uses_only_available(self, sample_video_ap_minimal):
        tags, _ = map_video_to_nostr_tags(sample_video_ap_minimal)

        image_tag = _find_tag(tags, "image")
        assert image_tag == [
            "image",
            "https://peertube.example.com/lazy-static/thumbnails/minimal-thumb.jpg",
        ]


class TestUrlExtraction:
    """URL extraction: text/html -> r tag, HLS nested video/mp4 -> encoding tags."""

    def test_text_html_link_becomes_r_tag(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        r_tag = _find_tag(tags, "r")
        assert r_tag == [
            "r",
            "https://peertube.example.com/w/ovjzowkYv7vf5Mfa4SoRPb",
        ]

    def test_hls_nested_mp4_produces_encoding_content_url(
        self, sample_video_ap, creator_cache
    ):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        content_urls = _find_tags(tags, "encoding:contentUrl")
        hrefs = [t[1] for t in content_urls]
        assert (
            "https://peertube.example.com/static/streaming-playlists/hls/00000000/9aacda50-1080-fragmented.mp4"
            in hrefs
        )
        assert (
            "https://peertube.example.com/static/streaming-playlists/hls/00000000/e03f254c-720-fragmented.mp4"
            in hrefs
        )


class TestEncodingTagStructure:
    """Each video/mp4 encoding produces a set of four tags."""

    def test_encoding_format_tags(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        format_tags = _find_tags(tags, "encoding:encodingFormat")
        assert all(t[1] == "video/mp4" for t in format_tags)

    def test_encoding_content_size_tags(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        size_tags = _find_tags(tags, "encoding:contentSize")
        sizes = [t[1] for t in size_tags]
        assert "38971443" in sizes
        assert "8552237" in sizes

    def test_encoding_type_is_media_object(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        type_tags = _find_tags(tags, "encoding:type")
        assert len(type_tags) >= 2
        assert all(t[1] == "MediaObject" for t in type_tags)

    def test_torrent_links_not_included_in_encodings(
        self, sample_video_ap, creator_cache
    ):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        content_urls = [t[1] for t in _find_tags(tags, "encoding:contentUrl")]
        assert not any(".torrent" in url for url in content_urls)
        assert not any("magnet:" in url for url in content_urls)


class TestCategoryMapping:
    """Category maps to a t tag (not about, since there is no URI)."""

    def test_category_name_becomes_t_tag(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        t_values = [t[1] for t in _find_tags(tags, "t")]
        assert "Education" in t_values


class TestSubtitleLanguageMapping:
    """subtitleLanguage maps to caption tags."""

    def test_caption_id_tags(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        caption_ids = _find_tags(tags, "caption:id")
        urls = [t[1] for t in caption_ids]
        assert (
            "https://peertube.example.com/lazy-static/video-captions/00000000-en.vtt"
            in urls
        )
        assert (
            "https://peertube.example.com/lazy-static/video-captions/00000000-fr.vtt"
            in urls
        )

    def test_caption_in_language_tags(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        caption_langs = _find_tags(tags, "caption:inLanguage")
        langs = [t[1] for t in caption_langs]
        assert "en" in langs
        assert "fr" in langs

    def test_empty_subtitle_language_produces_no_caption_tags(
        self, sample_video_ap_minimal
    ):
        tags, _ = map_video_to_nostr_tags(sample_video_ap_minimal)

        assert _find_tags(tags, "caption:id") == []
        assert _find_tags(tags, "caption:inLanguage") == []


class TestAttributedToCreatorMapping:
    """attributedTo with creator_cache maps to creator tags."""

    def test_creator_name_from_person_actor(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        creator_name = _find_tag(tags, "creator:name")
        assert creator_name == ["creator:name", "testchannel"]

    def test_creator_type_is_person(self, sample_video_ap, creator_cache):
        tags, _ = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        creator_type = _find_tag(tags, "creator:type")
        assert creator_type == ["creator:type", "Person"]


class TestLiveBroadcastSkipped:
    """isLiveBroadcast=true videos should be skipped or flagged."""

    def test_live_broadcast_is_skipped_or_flagged(self, sample_video_ap_live):
        result = map_video_to_nostr_tags(sample_video_ap_live)

        # The mapper should either return None/empty or raise to signal skip
        # Accept either: returns None, returns empty tags, or raises ValueError
        if result is not None:
            tags, _ = result
            # If it returns tags, there should be some indication it's live
            # or the tags list should be empty to signal "skip"
            assert tags == [] or any(
                t[0] == "isLiveBroadcast" for t in tags
            )


class TestFullVideoMappingMatchesSpec:
    """Integration-style test: full video produces expected tag set from spec."""

    def test_full_mapping_contains_all_required_tags(
        self, sample_video_ap, creator_cache
    ):
        tags, content = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        tag_keys = [t[0] for t in tags]
        required_keys = [
            "d",
            "type",
            "name",
            "duration",
            "datePublished",
            "dateModified",
            "inLanguage",
            "license:id",
            "isAccessibleForFree",
            "learningResourceType:id",
            "learningResourceType:prefLabel:en",
            "image",
            "r",
            "encoding:type",
            "encoding:contentUrl",
            "encoding:encodingFormat",
            "encoding:contentSize",
            "creator:name",
            "creator:type",
        ]
        for key in required_keys:
            assert key in tag_keys, f"Missing required tag: {key}"

    def test_full_mapping_has_nonempty_content(self, sample_video_ap, creator_cache):
        _, content = map_video_to_nostr_tags(sample_video_ap, creator_cache)

        assert isinstance(content, str)
        assert len(content) > 0
