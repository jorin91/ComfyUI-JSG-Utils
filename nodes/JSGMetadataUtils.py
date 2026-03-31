import datetime
import html
import json
import os
import re
import struct
import zlib
import xml.etree.ElementTree as ET

from PIL import ExifTags, Image, PngImagePlugin


SAFE_TEXT_METADATA_FIELDS = (
    # Windows Details tab - Beschrijving
    "Title",
    "Subject",
    "Rating",
    "Tags",
    "Comments",
    # Windows Details tab - Oorsprong
    "Authors",
    "DateTaken",
    "ProgramName",
    "Copyright",
    # Windows Details tab - Camera
    "CameraMaker",
    "CameraModel",
    # Extended / not standard Windows visible
    "Description",
    "Source",
    "Publisher",
    "Category",
    "Disclaimer",
    "Warning",
    "Producer",
    "Instructions",
    "Credit",
    "License",
    "UsageTerms",
    "Identifier",
    "Language",
    "URL",
    "Series",
    "Project",
    "Client",
    "Company",
    "Manager",
)

JSG_TEXT_METADATA_KEY = "JSGMetadataText"
PNG_XMP_KEY = "XML:com.adobe.xmp"
JSG_XMP_NAMESPACE = "https://github.com/jsg/comfyui-jsg-utils/metadata/1.0/"

EXIF_TAG_IDS = {
    "ImageDescription": 270,
    "Make": 271,
    "Model": 272,
    "Software": 305,
    "Artist": 315,
    "Copyright": 33432,
    "DateTimeOriginal": 36867,
    "UserComment": 37510,
    "XPTitle": 40091,
    "XPComment": 40092,
    "XPAuthor": 40093,
    "XPKeywords": 40094,
    "XPSubject": 40095,
}

XMP_NAMESPACES = {
    "x": "adobe:ns:meta/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "dc": "http://purl.org/dc/elements/1.1/",
    "xmp": "http://ns.adobe.com/xap/1.0/",
    "tiff": "http://ns.adobe.com/tiff/1.0/",
    "exif": "http://ns.adobe.com/exif/1.0/",
    "jsg": JSG_XMP_NAMESPACE,
}

for prefix, uri in XMP_NAMESPACES.items():
    ET.register_namespace(prefix, uri)


def create_blank_metadata():
    return {
        "__type": "JSGMETADATA",
        "file": {},
        "pil": {},
        "dpi": None,
        "icc_profile": None,
        "exif": {"exif_dict": {}, "exif_bytes": None},
        "text": {field: "" for field in SAFE_TEXT_METADATA_FIELDS},
        "raw_info_keys": [],
        "warnings": [],
    }


def _safe_iso_dt(ts):
    try:
        return datetime.datetime.fromtimestamp(ts).isoformat()
    except Exception:
        return None


def _stringify_metadata_value(value):
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return str(value)


def _normalize_text_value(value):
    return _stringify_metadata_value(value).strip()


def _decode_bytes_value(value):
    if isinstance(value, tuple):
        try:
            value = bytes(value)
        except Exception:
            value = str(value)

    if isinstance(value, bytes):
        for encoding in ("utf-8", "utf-16le", "latin-1"):
            try:
                return value.decode(encoding).rstrip("\x00")
            except Exception:
                continue
        return f"[bytes:{len(value)}]"

    return _stringify_metadata_value(value)


def _encode_xp_value(value):
    return (_normalize_text_value(value) + "\x00").encode("utf-16le")


def _decode_xp_value(value):
    decoded = _decode_bytes_value(value)
    return decoded.rstrip("\x00")


def _encode_user_comment_payload(text):
    payload = json.dumps(text, ensure_ascii=True, separators=(",", ":"))
    return b"ASCII\x00\x00\x00" + payload.encode("ascii")


def _decode_user_comment_payload(value):
    if isinstance(value, tuple):
        try:
            value = bytes(value)
        except Exception:
            return None

    if not isinstance(value, (bytes, bytearray)):
        return None

    raw = bytes(value)
    if raw.startswith(b"ASCII\x00\x00\x00"):
        raw = raw[8:]
    elif raw.startswith(b"UNICODE\x00"):
        try:
            return json.loads(raw[8:].decode("utf-16-be").strip("\x00"))
        except Exception:
            return None

    try:
        return json.loads(raw.decode("ascii"))
    except Exception:
        return None


def _merge_text_values(base, updates):
    merged = dict(base)
    for key, value in (updates or {}).items():
        field = str(key)
        normalized = _stringify_metadata_value(value)
        if normalized == "" and merged.get(field, "") != "":
            continue
        merged[field] = normalized
    return merged


def _add_alt_text(parent, tag_name, value):
    if not value:
        return
    element = ET.SubElement(parent, f"{{{XMP_NAMESPACES['dc']}}}{tag_name}")
    alt = ET.SubElement(element, f"{{{XMP_NAMESPACES['rdf']}}}Alt")
    item = ET.SubElement(alt, f"{{{XMP_NAMESPACES['rdf']}}}li")
    item.set("{http://www.w3.org/XML/1998/namespace}lang", "x-default")
    item.text = value


def _add_seq_text(parent, tag_name, values):
    clean = [value for value in values if value]
    if not clean:
        return
    element = ET.SubElement(parent, f"{{{XMP_NAMESPACES['dc']}}}{tag_name}")
    seq = ET.SubElement(element, f"{{{XMP_NAMESPACES['rdf']}}}Seq")
    for value in clean:
        item = ET.SubElement(seq, f"{{{XMP_NAMESPACES['rdf']}}}li")
        item.text = value


def _add_bag_text(parent, tag_name, values):
    clean = [value for value in values if value]
    if not clean:
        return
    element = ET.SubElement(parent, f"{{{XMP_NAMESPACES['dc']}}}{tag_name}")
    bag = ET.SubElement(element, f"{{{XMP_NAMESPACES['rdf']}}}Bag")
    for value in clean:
        item = ET.SubElement(bag, f"{{{XMP_NAMESPACES['rdf']}}}li")
        item.text = value


def _split_keywords(value):
    if not value:
        return []
    return [part.strip() for part in re.split(r"[,;]", value) if part.strip()]


def _load_text_from_info(info):
    text = {field: "" for field in SAFE_TEXT_METADATA_FIELDS}
    payload = info.get(JSG_TEXT_METADATA_KEY)

    if isinstance(payload, bytes):
        try:
            payload = payload.decode("utf-8")
        except Exception:
            payload = None

    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
            if isinstance(parsed, dict):
                for key, value in parsed.items():
                    text[str(key)] = _stringify_metadata_value(value)
        except Exception:
            pass

    for key, value in info.items():
        if key in ("icc_profile", JSG_TEXT_METADATA_KEY, PNG_XMP_KEY):
            continue
        if isinstance(value, bytes):
            try:
                value = value.decode("utf-8")
            except Exception:
                try:
                    value = value.decode("latin-1")
                except Exception:
                    value = f"[bytes:{len(value)}]"
        text[str(key)] = _stringify_metadata_value(value)

    return text


def _load_text_from_exif(im, info):
    text = {}

    try:
        exif = im.getexif()
    except Exception:
        exif = None

    if exif:
        description = _normalize_text_value(exif.get(EXIF_TAG_IDS["ImageDescription"], ""))
        artist = _normalize_text_value(exif.get(EXIF_TAG_IDS["Artist"], ""))
        copyright_text = _normalize_text_value(exif.get(EXIF_TAG_IDS["Copyright"], ""))
        software = _normalize_text_value(exif.get(EXIF_TAG_IDS["Software"], ""))
        xp_title = _decode_xp_value(exif.get(EXIF_TAG_IDS["XPTitle"], b""))
        xp_comment = _decode_xp_value(exif.get(EXIF_TAG_IDS["XPComment"], b""))
        xp_author = _decode_xp_value(exif.get(EXIF_TAG_IDS["XPAuthor"], b""))
        xp_keywords = _decode_xp_value(exif.get(EXIF_TAG_IDS["XPKeywords"], b""))
        xp_subject = _decode_xp_value(exif.get(EXIF_TAG_IDS["XPSubject"], b""))

        if xp_title:
            text["Title"] = xp_title
        if xp_comment:
            text["Comments"] = xp_comment
        if xp_author:
            text["Authors"] = xp_author
        if xp_keywords:
            text["Tags"] = xp_keywords
        if xp_subject:
            text["Subject"] = xp_subject
        if description:
            text.setdefault("Description", description)
        if artist:
            text.setdefault("Authors", artist)
        if copyright_text:
            text["Copyright"] = copyright_text
        if software:
            text["ProgramName"] = software

        payload = _decode_user_comment_payload(exif.get(EXIF_TAG_IDS["UserComment"], b""))
        if isinstance(payload, dict):
            text = _merge_text_values(text, payload)

    comment = info.get("comment")
    if comment is not None:
        decoded_comment = _decode_bytes_value(comment).strip("\x00")
        if decoded_comment:
            text.setdefault("Comments", decoded_comment)

    return text


def _load_text_from_xmp(info):
    payload = None
    for key in ("xmp", "XML:com.adobe.xmp"):
        if key in info:
            payload = info.get(key)
            break

    if payload is None:
        return {}

    if isinstance(payload, bytes):
        xml_data = payload.decode("utf-8", errors="ignore")
    else:
        xml_data = str(payload)

    if not xml_data.strip():
        return {}

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        return {}

    text = {}

    metadata_json = root.find(f".//{{{JSG_XMP_NAMESPACE}}}MetadataText")
    if metadata_json is not None and metadata_json.text:
        try:
            parsed = json.loads(metadata_json.text)
            if isinstance(parsed, dict):
                text = _merge_text_values(text, parsed)
        except Exception:
            pass

    def first_alt_text(tag_name):
        element = root.find(f".//{{{XMP_NAMESPACES['dc']}}}{tag_name}/{{{XMP_NAMESPACES['rdf']}}}Alt/{{{XMP_NAMESPACES['rdf']}}}li")
        return element.text.strip() if element is not None and element.text else ""

    def first_seq_text(tag_name):
        element = root.find(f".//{{{XMP_NAMESPACES['dc']}}}{tag_name}/{{{XMP_NAMESPACES['rdf']}}}Seq/{{{XMP_NAMESPACES['rdf']}}}li")
        return element.text.strip() if element is not None and element.text else ""

    def bag_text(tag_name):
        return [
            item.text.strip()
            for item in root.findall(f".//{{{XMP_NAMESPACES['dc']}}}{tag_name}/{{{XMP_NAMESPACES['rdf']}}}Bag/{{{XMP_NAMESPACES['rdf']}}}li")
            if item.text and item.text.strip()
        ]

    mappings = {
        "Title": first_alt_text("title"),
        "Comments": (root.findtext(f".//{{{XMP_NAMESPACES['exif']}}}UserComment") or "").strip() or first_alt_text("description"),
        "Description": first_alt_text("description"),
        "Copyright": first_alt_text("rights"),
        "Authors": first_seq_text("creator"),
        "Publisher": first_seq_text("publisher"),
        "Source": (root.findtext(f".//{{{XMP_NAMESPACES['dc']}}}source") or "").strip(),
        "ProgramName": (root.findtext(f".//{{{XMP_NAMESPACES['xmp']}}}CreatorTool") or "").strip(),
        "DateTaken": (root.findtext(f".//{{{XMP_NAMESPACES['xmp']}}}CreateDate") or "").strip(),
        "Rating": (root.findtext(f".//{{{XMP_NAMESPACES['xmp']}}}Rating") or "").strip(),
        "CameraMaker": (root.findtext(f".//{{{XMP_NAMESPACES['tiff']}}}Make") or "").strip(),
        "CameraModel": (root.findtext(f".//{{{XMP_NAMESPACES['tiff']}}}Model") or "").strip(),
    }

    for key, value in mappings.items():
        if value:
            text.setdefault(key, value)

    subject_values = bag_text("subject")
    if subject_values:
        text.setdefault("Tags", ", ".join(subject_values))

    return text


def read_metadata(path, im):
    meta = create_blank_metadata()

    try:
        im.load()
    except Exception:
        pass

    try:
        st = os.stat(path)
        meta["file"] = {
            "path": os.path.abspath(path),
            "size_bytes": st.st_size,
            "mtime": _safe_iso_dt(st.st_mtime),
            "atime": _safe_iso_dt(st.st_atime),
            "ctime": _safe_iso_dt(st.st_ctime),
        }
    except Exception as exc:
        meta["warnings"].append(f"stat_failed: {exc}")

    try:
        meta["pil"] = {
            "format": getattr(im, "format", None),
            "mode": getattr(im, "mode", None),
            "size": list(getattr(im, "size", (0, 0))),
        }
    except Exception as exc:
        meta["warnings"].append(f"pil_basic_failed: {exc}")

    try:
        info = dict(getattr(im, "info", {}) or {})
        text_attr = dict(getattr(im, "text", {}) or {})
        for key, value in text_attr.items():
            info.setdefault(key, value)
        meta["raw_info_keys"] = sorted([str(key) for key in info.keys()])

        if "dpi" in info:
            meta["dpi"] = info.get("dpi")

        if "icc_profile" in info:
            meta["icc_profile"] = info.get("icc_profile")

        meta["text"] = _load_text_from_info(info)
        meta["text"] = _merge_text_values(meta["text"], _load_text_from_xmp(info))
        meta["text"] = _merge_text_values(meta["text"], _load_text_from_exif(im, info))
    except Exception as exc:
        meta["warnings"].append(f"pil_info_failed: {exc}")

    try:
        exif_obj = None
        try:
            exif_obj = im.getexif()
        except Exception:
            exif_obj = None

        if exif_obj:
            tag_map = ExifTags.TAGS
            exif_dict = {}
            for tag_id, value in exif_obj.items():
                name = tag_map.get(tag_id, str(tag_id))
                if isinstance(value, bytes):
                    exif_dict[name] = f"[bytes:{len(value)}]"
                else:
                    exif_dict[name] = value
            meta["exif"]["exif_dict"] = exif_dict

        try:
            exif_bytes = im.info.get("exif", None)
            meta["exif"]["exif_bytes"] = exif_bytes
        except Exception:
            pass
    except Exception as exc:
        meta["warnings"].append(f"exif_failed: {exc}")

    return ensure_metadata(meta)


def build_pnginfo_from_metadata(metadata):
    meta = ensure_metadata(metadata)
    text = meta.get("text") or {}
    pnginfo = PngImagePlugin.PngInfo()
    has_entries = False

    for key, value in text.items():
        string_value = _stringify_metadata_value(value)
        if string_value == "":
            continue
        try:
            string_value.encode("latin-1")
            pnginfo.add_text(str(key), string_value)
        except Exception:
            pnginfo.add_itxt(str(key), string_value)
        has_entries = True

    payload = json.dumps(text, ensure_ascii=False)
    pnginfo.add_itxt(JSG_TEXT_METADATA_KEY, payload)
    has_entries = True

    return pnginfo if has_entries else None


def _build_windows_png_xmp_bytes(metadata):
    meta = ensure_metadata(metadata)
    text = meta.get("text") or {}

    description_parts = []
    title = _normalize_text_value(text.get("Title", ""))
    comments = _normalize_text_value(text.get("Comments", ""))
    description = _normalize_text_value(text.get("Description", ""))
    copyright_text = _normalize_text_value(text.get("Copyright", ""))
    author = _normalize_text_value(text.get("Authors", ""))

    if title:
        description_parts.append(
            "<dc:title><rdf:Alt xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">"
            f"<rdf:li xml:lang=\"x-default\">{html.escape(title)}</rdf:li>"
            "</rdf:Alt></dc:title>"
        )

    # Windows "Opmerkingen" (System.Comment) reads exif:UserComment from XMP
    if comments:
        description_parts.append(
            "<exif:UserComment><rdf:Alt xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">"
            f"<rdf:li xml:lang=\"x-default\">{html.escape(comments)}</rdf:li>"
            "</rdf:Alt></exif:UserComment>"
        )

    if description:
        description_parts.append(
            "<dc:description><rdf:Alt xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">"
            f"<rdf:li xml:lang=\"x-default\">{html.escape(description)}</rdf:li>"
            "</rdf:Alt></dc:description>"
        )

    if copyright_text:
        description_parts.append(
            "<dc:rights><rdf:Alt xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">"
            f"<rdf:li xml:lang=\"x-default\">{html.escape(copyright_text)}</rdf:li>"
            "</rdf:Alt></dc:rights>"
        )

    if author:
        description_parts.append(
            "<dc:creator><rdf:Seq xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">"
            f"<rdf:li>{html.escape(author)}</rdf:li>"
            "</rdf:Seq></dc:creator>"
        )

    rating = _normalize_text_value(text.get("Rating", ""))
    if rating:
        description_parts.append(
            f"<xmp:Rating>{html.escape(rating)}</xmp:Rating>"
        )

    software = _normalize_text_value(text.get("ProgramName", ""))
    if software:
        description_parts.append(
            f"<xmp:CreatorTool>{html.escape(software)}</xmp:CreatorTool>"
        )

    date_taken = _normalize_text_value(text.get("DateTaken", ""))
    if date_taken:
        description_parts.append(
            f"<xmp:CreateDate>{html.escape(date_taken)}</xmp:CreateDate>"
        )

    camera_maker = _normalize_text_value(text.get("CameraMaker", ""))
    if camera_maker:
        description_parts.append(
            f"<tiff:Make>{html.escape(camera_maker)}</tiff:Make>"
        )

    camera_model = _normalize_text_value(text.get("CameraModel", ""))
    if camera_model:
        description_parts.append(
            f"<tiff:Model>{html.escape(camera_model)}</tiff:Model>"
        )

    source = _normalize_text_value(text.get("Source", ""))
    if source:
        description_parts.append(
            "<dc:source>"
            f"{html.escape(source)}"
            "</dc:source>"
        )

    publisher = _normalize_text_value(text.get("Publisher", ""))
    if publisher:
        description_parts.append(
            "<dc:publisher><rdf:Bag xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">"
            f"<rdf:li>{html.escape(publisher)}</rdf:li>"
            "</rdf:Bag></dc:publisher>"
        )

    keywords = _split_keywords(text.get("Tags", ""))
    if keywords:
        bag_items = "".join(f"<rdf:li>{html.escape(value)}</rdf:li>" for value in keywords)
        description_parts.append(
            "<dc:subject><rdf:Bag xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">"
            f"{bag_items}"
            "</rdf:Bag></dc:subject>"
        )

    identifier = _normalize_text_value(text.get("Identifier", ""))
    if identifier:
        description_parts.append(f"<dc:identifier>{html.escape(identifier)}</dc:identifier>")

    language = _normalize_text_value(text.get("Language", ""))
    if language:
        description_parts.append(
            "<dc:language><rdf:Bag xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">"
            f"<rdf:li>{html.escape(language)}</rdf:li>"
            "</rdf:Bag></dc:language>"
        )

    category = _normalize_text_value(text.get("Category", ""))
    if category:
        description_parts.append(f"<photoshop:Category>{html.escape(category)}</photoshop:Category>")

    instructions = _normalize_text_value(text.get("Instructions", ""))
    if instructions:
        description_parts.append(f"<photoshop:Instructions>{html.escape(instructions)}</photoshop:Instructions>")

    credit = _normalize_text_value(text.get("Credit", ""))
    if credit:
        description_parts.append(f"<photoshop:Credit>{html.escape(credit)}</photoshop:Credit>")

    usage_terms = _normalize_text_value(text.get("UsageTerms", ""))
    if usage_terms:
        description_parts.append(
            "<xmpRights:UsageTerms><rdf:Alt xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">"
            f"<rdf:li xml:lang=\"x-default\">{html.escape(usage_terms)}</rdf:li>"
            "</rdf:Alt></xmpRights:UsageTerms>"
        )

    license_url = _normalize_text_value(text.get("License", ""))
    if license_url:
        description_parts.append(f"<xmpRights:WebStatement>{html.escape(license_url)}</xmpRights:WebStatement>")

    url = _normalize_text_value(text.get("URL", ""))
    if url:
        description_parts.append(f"<xmp:BaseURL>{html.escape(url)}</xmp:BaseURL>")

    for _field in ("Disclaimer", "Warning", "Company", "Manager", "Producer", "Series", "Project", "Client"):
        _val = _normalize_text_value(text.get(_field, ""))
        if _val:
            description_parts.append(f"<jsg:{_field}>{html.escape(_val)}</jsg:{_field}>")

    body = "".join(description_parts)
    if not body:
        return None

    packet = (
        "<?xpacket begin='' id='W5M0MpCehiHzreSzNTczkc9d'?>\n"
        "<x:xmpmeta xmlns:x=\"adobe:ns:meta/\">"
        "<rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">"
        "<rdf:Description rdf:about=\"uuid:faf5bdd5-ba3d-11da-ad31-d33d75182f1b\" xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:xmp=\"http://ns.adobe.com/xap/1.0/\" xmlns:exif=\"http://ns.adobe.com/exif/1.0/\" xmlns:tiff=\"http://ns.adobe.com/tiff/1.0/\" xmlns:photoshop=\"http://ns.adobe.com/photoshop/1.0/\" xmlns:xmpRights=\"http://ns.adobe.com/xap/1.0/rights/\" xmlns:jsg=\"https://github.com/jsg/comfyui-jsg-utils/metadata/1.0/\">"
        f"{body}"
        "</rdf:Description></rdf:RDF></x:xmpmeta>\n"
        "<?xpacket end='w'?>"
    )
    return packet.encode("utf-8")


def _iter_png_chunks(png_bytes):
    position = 8
    total_length = len(png_bytes)

    while position + 12 <= total_length:
        length = struct.unpack(">I", png_bytes[position:position + 4])[0]
        chunk_type = png_bytes[position + 4:position + 8]
        data_start = position + 8
        data_end = data_start + length
        crc_end = data_end + 4

        if crc_end > total_length:
            raise ValueError("Invalid PNG chunk length")

        yield {
            "start": position,
            "type": chunk_type,
            "data": png_bytes[data_start:data_end],
            "end": crc_end,
        }

        position = crc_end
        if chunk_type == b"IEND":
            break


def _build_png_chunk(chunk_type, data):
    chunk_body = chunk_type + data
    crc = zlib.crc32(chunk_body) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_body + struct.pack(">I", crc)


def _decode_png_text_keyword(chunk_data):
    separator_index = chunk_data.find(b"\x00")
    if separator_index <= 0:
        return None
    return chunk_data[:separator_index].decode("latin-1", errors="ignore")


def _build_png_itxt_chunk(keyword, text_value):
    keyword_bytes = str(keyword).encode("latin-1")
    text_bytes = str(text_value).encode("utf-8")
    compression_flag = b"\x00"
    compression_method = b"\x00"
    language_tag = b""
    translated_keyword = b""
    data = (
        keyword_bytes
        + b"\x00"
        + compression_flag
        + compression_method
        + language_tag
        + b"\x00"
        + translated_keyword
        + b"\x00"
        + text_bytes
    )
    return _build_png_chunk(b"iTXt", data)


def ensure_png_xmp_chunk(path, xmp_bytes):
    if not path or not isinstance(xmp_bytes, (bytes, bytearray)):
        return False

    with open(path, "rb") as handle:
        png_bytes = handle.read()

    if not png_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return False

    xmp_text = bytes(xmp_bytes).decode("utf-8", errors="strict")
    xmp_chunk = _build_png_itxt_chunk(PNG_XMP_KEY, xmp_text)

    chunks = list(_iter_png_chunks(png_bytes))
    before = bytearray(png_bytes[:8])
    inserted = False
    changed = False

    for chunk in chunks:
        chunk_bytes = png_bytes[chunk["start"]:chunk["end"]]
        chunk_type = chunk["type"]

        if chunk_type == b"iTXt":
            keyword = _decode_png_text_keyword(chunk["data"])
            if keyword == PNG_XMP_KEY:
                if not inserted:
                    before.extend(xmp_chunk)
                    inserted = True
                    if chunk_bytes != xmp_chunk:
                        changed = True
                else:
                    changed = True
                continue

        if not inserted and chunk_type == b"IDAT":
            before.extend(xmp_chunk)
            inserted = True
            changed = True

        if not inserted and chunk_type == b"eXIf":
            before.extend(chunk_bytes)
            before.extend(xmp_chunk)
            inserted = True
            changed = True
            continue

        before.extend(chunk_bytes)

    if not inserted:
        changed = True

    if not changed and inserted:
        return False

    if not inserted:
        rebuilt = bytearray(png_bytes[:8])
        for chunk in chunks:
            chunk_bytes = png_bytes[chunk["start"]:chunk["end"]]
            if chunk["type"] == b"IEND":
                rebuilt.extend(xmp_chunk)
                inserted = True
            rebuilt.extend(chunk_bytes)
        png_bytes = bytes(rebuilt)
    else:
        png_bytes = bytes(before)

    with open(path, "wb") as handle:
        handle.write(png_bytes)

    return True


def ensure_windows_png_metadata_layout(path, metadata):
    xmp_bytes = _build_windows_png_xmp_bytes(metadata)
    if not isinstance(xmp_bytes, (bytes, bytearray)):
        return False
    return ensure_png_xmp_chunk(path, xmp_bytes)


def build_exif_bytes_from_metadata(metadata):
    meta = ensure_metadata(metadata)
    text = meta.get("text") or {}
    exif = Image.Exif()

    existing_exif_bytes = ((meta.get("exif") or {}).get("exif_bytes"))
    if isinstance(existing_exif_bytes, (bytes, bytearray)):
        try:
            exif.load(bytes(existing_exif_bytes))
        except Exception:
            pass

    mappings = {
        EXIF_TAG_IDS["ImageDescription"]: text.get("Description", ""),
        EXIF_TAG_IDS["Make"]: text.get("CameraMaker", ""),
        EXIF_TAG_IDS["Model"]: text.get("CameraModel", ""),
        EXIF_TAG_IDS["Artist"]: text.get("Authors", ""),
        EXIF_TAG_IDS["Copyright"]: text.get("Copyright", ""),
        EXIF_TAG_IDS["Software"]: text.get("ProgramName", ""),
    }

    for tag_id, value in mappings.items():
        normalized = _normalize_text_value(value)
        if normalized:
            exif[tag_id] = normalized

    date_taken = _normalize_text_value(text.get("DateTaken", ""))
    if date_taken:
        exif[EXIF_TAG_IDS["DateTimeOriginal"]] = date_taken

    xp_mappings = {
        EXIF_TAG_IDS["XPTitle"]: text.get("Title", ""),
        EXIF_TAG_IDS["XPComment"]: text.get("Comments", ""),
        EXIF_TAG_IDS["XPAuthor"]: text.get("Authors", ""),
        EXIF_TAG_IDS["XPKeywords"]: text.get("Tags", ""),
        EXIF_TAG_IDS["XPSubject"]: text.get("Subject", ""),
    }

    for tag_id, value in xp_mappings.items():
        normalized = _normalize_text_value(value)
        if normalized:
            exif[tag_id] = _encode_xp_value(normalized)

    exif[EXIF_TAG_IDS["UserComment"]] = _encode_user_comment_payload(text)
    return exif.tobytes()


def build_xmp_bytes_from_metadata(metadata):
    meta = ensure_metadata(metadata)
    text = meta.get("text") or {}

    root = ET.Element(f"{{{XMP_NAMESPACES['x']}}}xmpmeta")
    rdf = ET.SubElement(root, f"{{{XMP_NAMESPACES['rdf']}}}RDF")
    description = ET.SubElement(rdf, f"{{{XMP_NAMESPACES['rdf']}}}Description")

    _add_alt_text(description, "title", _normalize_text_value(text.get("Title", "")))
    _add_alt_text(description, "description", _normalize_text_value(text.get("Comments", "")))
    _add_alt_text(description, "rights", _normalize_text_value(text.get("Copyright", "")))
    _add_seq_text(description, "creator", [_normalize_text_value(text.get("Authors", ""))])
    _add_seq_text(description, "publisher", [_normalize_text_value(text.get("Publisher", ""))])
    _add_bag_text(description, "subject", _split_keywords(text.get("Tags", "")))

    source = _normalize_text_value(text.get("Source", ""))
    if source:
        source_element = ET.SubElement(description, f"{{{XMP_NAMESPACES['dc']}}}source")
        source_element.text = source

    software = _normalize_text_value(text.get("ProgramName", ""))
    if software:
        creator_tool = ET.SubElement(description, f"{{{XMP_NAMESPACES['xmp']}}}CreatorTool")
        creator_tool.text = software

    metadata_text = ET.SubElement(description, f"{{{JSG_XMP_NAMESPACE}}}MetadataText")
    metadata_text.text = json.dumps(text, ensure_ascii=False)

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def ensure_metadata(metadata):
    if metadata is None:
        return create_blank_metadata()

    if not isinstance(metadata, dict):
        raise ValueError("JSGMETADATA must be a dict")

    out = create_blank_metadata()
    out.update(dict(metadata))

    text = {field: "" for field in SAFE_TEXT_METADATA_FIELDS}
    incoming_text = out.get("text") or {}
    if isinstance(incoming_text, dict):
        for key, value in incoming_text.items():
            text[str(key)] = "" if value is None else str(value)
    out["text"] = text

    if not isinstance(out.get("file"), dict):
        out["file"] = {}
    if not isinstance(out.get("pil"), dict):
        out["pil"] = {}
    if not isinstance(out.get("raw_info_keys"), list):
        out["raw_info_keys"] = []
    if not isinstance(out.get("warnings"), list):
        out["warnings"] = []

    exif = out.get("exif") or {}
    if not isinstance(exif, dict):
        exif = {}
    exif_dict = exif.get("exif_dict") or {}
    if not isinstance(exif_dict, dict):
        exif_dict = {}
    out["exif"] = {
        "exif_dict": exif_dict,
        "exif_bytes": exif.get("exif_bytes"),
    }

    return out
