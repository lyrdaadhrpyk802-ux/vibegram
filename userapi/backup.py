# ============================================
#  userapi/backup.py - export chat history to JSON
#  Resumable, media-aware, works with any chat type.
#  All code and comments are English. No emojis.
# ============================================
import json
import re
from datetime import datetime, timezone
from pathlib import Path


VERSION = 1


def _safe_name(name, max_len=80):
    s = re.sub(r"[^\w\-. ]+", "_", str(name or "chat"))
    s = s.strip(" ._") or "chat"
    return s[:max_len]


def _chat_meta(entity):
    title = (getattr(entity, "title", None)
             or getattr(entity, "first_name", None)
             or getattr(entity, "username", None)
             or str(getattr(entity, "id", "?")))
    return {
        "id": getattr(entity, "id", None),
        "title": title,
        "username": getattr(entity, "username", None),
        "type": type(entity).__name__,
    }


def _guess_ext(msg):
    if getattr(msg, "photo", None):
        return ".jpg"
    doc = getattr(msg, "document", None)
    if doc is not None:
        mime = getattr(doc, "mime_type", "") or ""
        if mime.startswith("image/jpeg"):
            return ".jpg"
        if mime.startswith("image/png"):
            return ".png"
        if mime.startswith("image/webp"):
            return ".webp"
        if mime.startswith("video/mp4"):
            return ".mp4"
        if mime.startswith("audio/ogg"):
            return ".ogg"
        if mime.startswith("audio/mpeg"):
            return ".mp3"
        for attr in getattr(doc, "attributes", []) or []:
            fn = getattr(attr, "file_name", None)
            if fn:
                return Path(fn).suffix or ""
    if getattr(msg, "video", None):
        return ".mp4"
    if getattr(msg, "voice", None):
        return ".ogg"
    if getattr(msg, "audio", None):
        return ".mp3"
    if getattr(msg, "sticker", None):
        return ".webp"
    if getattr(msg, "gif", None):
        return ".mp4"
    return ""


def _media_type(msg):
    for attr, label in [
        ("photo", "photo"),
        ("document", "document"),
        ("video", "video"),
        ("voice", "voice"),
        ("audio", "audio"),
        ("sticker", "sticker"),
        ("gif", "gif"),
        ("poll", "poll"),
        ("contact", "contact"),
        ("geo", "geo"),
        ("venue", "venue"),
        ("dice", "dice"),
    ]:
        if getattr(msg, attr, None):
            return label
    return None


def _msg_to_dict(msg):
    d = {
        "id": msg.id,
        "date": msg.date.isoformat() if getattr(msg, "date", None) else None,
        "sender_id": getattr(msg, "sender_id", None),
        "text": msg.text or "",
        "reply_to_msg_id": getattr(msg, "reply_to_msg_id", None),
        "forward_from": None,
        "media_type": None,
        "media_file": None,
        "media_size": None,
        "reactions": [],
    }

    fwd = getattr(msg, "forward", None)
    if fwd is not None:
        from_name = getattr(fwd, "from_name", None)
        peer = getattr(fwd, "peer_id", None)
        d["forward_from"] = {
            "from_name": from_name,
            "peer_id": (getattr(peer, "user_id", None)
                        or getattr(peer, "channel_id", None)
                        or getattr(peer, "chat_id", None)),
        }

    mt = _media_type(msg)
    if mt:
        d["media_type"] = mt

    poll = getattr(msg, "poll", None)
    if poll is not None:
        q = getattr(poll, "question", None)
        if hasattr(q, "text"):
            q = q.text
        answers = []
        for a in getattr(poll, "answers", []) or []:
            txt = getattr(a, "text", None)
            if hasattr(txt, "text"):
                txt = txt.text
            answers.append(txt)
        d["poll"] = {
            "question": q,
            "answers": answers,
            "closed": getattr(poll, "closed", False),
        }

    geo = getattr(msg, "geo", None)
    if geo is not None:
        d["geo"] = {
            "lat": getattr(geo, "lat", None),
            "long": getattr(geo, "long", None),
        }

    reactions = getattr(msg, "reactions", None)
    if reactions is not None:
        for r in getattr(reactions, "results", []) or []:
            rd = {"count": getattr(r, "count", 0)}
            emoji = getattr(getattr(r, "reaction", None), "emoticon", None)
            if emoji:
                rd["emoticon"] = emoji
            doc_id = getattr(getattr(r, "reaction", None), "document_id", None)
            if doc_id:
                rd["document_id"] = doc_id
            d["reactions"].append(rd)

    return d


async def backup_chat(client, peer, output_root=None, limit=None,
                      download_media=True, progress=None,
                      fresh=False):
    """Backup a chat to JSON (+ optional media files).

    Args:
        client: VibeClient (already connected)
        peer: chat/user/channel
        output_root: base directory (default ~/pyvibe/backups)
        limit: max messages to fetch per run (None = all)
        download_media: also save media files under media/
        progress: callback(step, total, msg_dict); called per message
        fresh: ignore any existing backup and start over

    Returns:
        (json_path, metadata_dict)
    """
    entity = await client.get_entity(peer)
    meta = _chat_meta(entity)

    name = _safe_name(meta.get("title") or meta.get("username") or meta.get("id"))
    root = Path(output_root) if output_root else Path.home() / "pyvibe" / "backups"
    root.mkdir(parents=True, exist_ok=True)
    out_dir = root / f"{name}_{meta['id']}"
    out_dir.mkdir(exist_ok=True)

    media_dir = out_dir / "media"
    if download_media:
        media_dir.mkdir(exist_ok=True)

    json_path = out_dir / "messages.json"

    if fresh and json_path.exists():
        try:
            json_path.unlink()
        except Exception:
            pass

    doc = {
        "chat": meta,
        "version": VERSION,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "last_saved_msg_id": 0,
        "message_count": 0,
        "media_count": 0,
        "messages": [],
    }
    if json_path.exists():
        try:
            doc = json.loads(json_path.read_text())
        except Exception:
            pass

    existing_messages = doc.get("messages", []) or []
    resume_id = doc.get("last_saved_msg_id", 0) or 0

    # Build iterator. Use raw TelegramClient because VibeClient.iter_messages
    # is a simple wrapper that does not accept reverse/min_id kwargs.
    raw = client.raw if hasattr(client, "raw") else client
    if resume_id > 0:
        iterator = raw.iter_messages(entity, min_id=resume_id, reverse=True)
    elif limit is not None:
        iterator = raw.iter_messages(entity, limit=limit, reverse=False)
    else:
        iterator = raw.iter_messages(entity, reverse=True)

    collected = []
    idx = 0
    media_count = doc.get("media_count", 0) or 0

    async for msg in iterator:
        idx += 1
        item = _msg_to_dict(msg)

        if download_media and item["media_type"]:
            try:
                ext = _guess_ext(msg)
                target = media_dir / f"{msg.id}{ext}"
                if not target.exists():
                    res = await client.download_media(msg, file=str(target))
                    if res:
                        item["media_file"] = str(Path(res).relative_to(out_dir))
                        item["media_size"] = target.stat().st_size
                        media_count += 1
                else:
                    item["media_file"] = str(target.relative_to(out_dir))
                    item["media_size"] = target.stat().st_size
            except Exception as e:
                print(f"[backup] media {msg.id} skipped: {type(e).__name__}: {e}")

        collected.append(item)
        if progress is not None:
            try:
                progress(idx, limit, item)
            except Exception:
                pass

    if limit is not None and resume_id == 0:
        collected = list(reversed(collected))

    all_msgs = existing_messages + collected
    all_msgs.sort(key=lambda m: m.get("id") or 0)

    doc["messages"] = all_msgs
    doc["message_count"] = len(all_msgs)
    doc["media_count"] = media_count
    doc["last_saved_msg_id"] = max((m.get("id") or 0) for m in all_msgs) if all_msgs else 0
    doc["finished_at"] = datetime.now(timezone.utc).isoformat()

    json_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False, default=str))
    return json_path, doc
