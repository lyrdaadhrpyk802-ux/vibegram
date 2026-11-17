# ============================================
#  botapi/methods.py - Organized Bot Methods
#  All code and comments are English. No emojis.
# ============================================
import asyncio

class BotMethodsMixin:
    """Organized bot-specific methods mixed into VibeBot."""

    # ---- Bot Profile Management ----
    async def set_commands(self, commands):
        """Set bot command menu. List of tuples: [('start', 'Start'), ('help', 'Help')]"""
        from telethon.tl.functions.bots import SetBotCommandsRequest
        from telethon.tl.types import BotCommand, BotCommandScopeDefault
        self._require_client()
        cmds = [BotCommand(command=c[0], description=c[1]) for c in commands]
        return await self._client(SetBotCommandsRequest(
            scope=BotCommandScopeDefault(), lang_code="", commands=cmds
        ))

    async def delete_commands(self):
        """Remove the bot command menu."""
        from telethon.tl.functions.bots import ResetBotCommandsRequest
        from telethon.tl.types import BotCommandScopeDefault
        self._require_client()
        return await self._client(ResetBotCommandsRequest(
            scope=BotCommandScopeDefault(), lang_code=""
        ))

    async def set_bot_description(self, description):
        """Set the bot description (shown before /start)."""
        from telethon.tl.functions.bots import SetBotInfoRequest
        self._require_client()
        # For bots setting their own info, the 'bot' field must be None
        return await self._client(SetBotInfoRequest(bot=None, lang_code="", description=description))

    async def set_bot_about(self, about):
        """Set the bot about text (profile bio)."""
        from telethon.tl.functions.bots import SetBotInfoRequest
        self._require_client()
        return await self._client(SetBotInfoRequest(bot=None, lang_code="", about=about))

    # ---- Chat Action / Status ----
    async def send_typing(self, peer):
        """Show 'typing...' status in a chat."""
        from telethon.tl.functions.messages import SetTypingRequest
        from telethon.tl.types import SendMessageTypingAction
        self._require_client()
        inp = await self._client.get_input_entity(peer)
        return await self._client(SetTypingRequest(peer=inp, action=SendMessageTypingAction()))

    async def send_uploading_photo(self, peer):
        """Show 'sending photo...' status."""
        from telethon.tl.functions.messages import SetTypingRequest
        from telethon.tl.types import SendMessageUploadPhotoAction
        self._require_client()
        inp = await self._client.get_input_entity(peer)
        return await self._client(SetTypingRequest(peer=inp, action=SendMessageUploadPhotoAction(progress=0)))

    # ---- Group Management (Admin Tools) ----
    async def ban_user(self, chat, user):
        """Ban (kick) a user from a group/channel."""
        return await self.edit_permissions(chat, user, view_messages=False)

    async def unban_user(self, chat, user):
        """Unban a user."""
        return await self.edit_permissions(chat, user, view_messages=True)

    async def mute_user(self, chat, user):
        """Mute a user (revoke send_messages permission)."""
        return await self.edit_permissions(chat, user, send_messages=False)

    async def unmute_user(self, chat, user):
        """Unmute a user."""
        return await self.edit_permissions(chat, user, send_messages=True)

    async def promote_admin(self, chat, user, **kwargs):
        """Promote a user to admin."""
        kwargs['is_admin'] = True
        return await self.edit_admin(chat, user, **kwargs)

    async def demote_admin(self, chat, user):
        """Demote an admin to a regular user."""
        return await self.edit_admin(chat, user, is_admin=False)

    async def set_slow_mode(self, chat, seconds):
        """Set slow mode. seconds=0 to disable."""
        return await self.toggle_slow_mode(chat, seconds)

    async def set_anti_spam(self, chat, enabled=True):
        """Enable or disable anti-spam."""
        return await self.toggle_anti_spam(chat, enabled=enabled)

    async def set_protect_content(self, chat, enabled=True):
        """Enable or disable 'Restrict Saving Content' (No Forwards)."""
        return await self.toggle_no_forwards(chat, enabled=enabled)

    # ---- Cleanup Helpers ----
    async def delete_message(self, peer, msg_id, revoke=True):
        """Delete a specific message."""
        return await self.delete_messages(peer, [msg_id], revoke=revoke)
