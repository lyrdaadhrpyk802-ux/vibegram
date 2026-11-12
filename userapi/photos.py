# ============================================
#  userapi/photos.py - Vibe photos API
#  Wraps all functions.photos.* TL requests plus convenience methods.
#  All code and comments are English. No emojis.
# ============================================
from telethon.tl import functions as tl_functions
from userapi._tl_auto import bind as _bind


class PhotosMixin:
    """Hand-written convenience methods for photos."""

    async def upload_profile_photo(self, file):
        """Upload a profile photo file and return Photo."""
        self._require_client()
        from telethon.tl.functions.photos import UploadProfilePhotoRequest
        uploaded = await self._client.upload_file(file)
        result = await self._client(UploadProfilePhotoRequest(file=uploaded))
        return result.photo

    async def delete_profile_photos(self, photo_ids):
        """Delete one or more profile photos by id (or list)."""
        self._require_client()
        from telethon.tl.functions.photos import DeletePhotosRequest
        from telethon.tl.types import InputPhoto
        if not isinstance(photo_ids, (list, tuple)):
            photo_ids = [photo_ids]
        inputs = [InputPhoto(id=pid, access_hash=0, file_reference=b"")
                  for pid in photo_ids]
        return await self._client(DeletePhotosRequest(id=inputs))


def bind_to(client_cls):
    new, skipped = _bind(
        client_cls, tl_functions.photos, "Photos", PhotosMixin(),
    )
    return new, skipped


print("[photos] module loaded; call bind_to(VibeClient) to attach methods")
