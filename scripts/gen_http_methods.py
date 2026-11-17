# ============================================
#  scripts/gen_http_methods.py - generate botapi/http_methods.py
#  Produces typed async methods for all Bot API methods.
# ============================================
from pathlib import Path


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


# name -> (params dict, return_type, one-line doc)
# params dict: param_name -> (type_str, required_bool, default_str_or_None)
METHODS = {
    # ---- messaging (media) ----
    "send_photo": (
        {"chat_id": ("Any", True, None), "photo": ("Any", True, None),
         "caption": ("Optional[str]", False, "None"),
         "parse_mode": ("Optional[str]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send a photo."),
    "send_audio": (
        {"chat_id": ("Any", True, None), "audio": ("Any", True, None),
         "caption": ("Optional[str]", False, "None"),
         "duration": ("Optional[int]", False, "None"),
         "performer": ("Optional[str]", False, "None"),
         "title": ("Optional[str]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send an audio file."),
    "send_document": (
        {"chat_id": ("Any", True, None), "document": ("Any", True, None),
         "caption": ("Optional[str]", False, "None"),
         "parse_mode": ("Optional[str]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send a document."),
    "send_video": (
        {"chat_id": ("Any", True, None), "video": ("Any", True, None),
         "caption": ("Optional[str]", False, "None"),
         "duration": ("Optional[int]", False, "None"),
         "supports_streaming": ("Optional[bool]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send a video."),
    "send_animation": (
        {"chat_id": ("Any", True, None), "animation": ("Any", True, None),
         "caption": ("Optional[str]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send a GIF animation."),
    "send_voice": (
        {"chat_id": ("Any", True, None), "voice": ("Any", True, None),
         "caption": ("Optional[str]", False, "None"),
         "duration": ("Optional[int]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send a voice note."),
    "send_video_note": (
        {"chat_id": ("Any", True, None), "video_note": ("Any", True, None),
         "duration": ("Optional[int]", False, "None"),
         "length": ("Optional[int]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send a round video note."),
    "send_media_group": (
        {"chat_id": ("Any", True, None), "media": ("List[Dict]", True, None)},
        "List[Dict[str, Any]]", "Send a media group (album)."),
    "send_location": (
        {"chat_id": ("Any", True, None),
         "latitude": ("float", True, None), "longitude": ("float", True, None),
         "live_period": ("Optional[int]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send a location."),
    "send_venue": (
        {"chat_id": ("Any", True, None),
         "latitude": ("float", True, None), "longitude": ("float", True, None),
         "title": ("str", True, None), "address": ("str", True, None),
         "foursquare_id": ("Optional[str]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send a venue."),
    "send_contact": (
        {"chat_id": ("Any", True, None),
         "phone_number": ("str", True, None), "first_name": ("str", True, None),
         "last_name": ("Optional[str]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send a phone contact."),
    "send_dice": (
        {"chat_id": ("Any", True, None),
         "emoji": ("Optional[str]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send a dice/game random value."),
    "send_chat_action": (
        {"chat_id": ("Any", True, None), "action": ("str", True, None)},
        "bool", "Send a chat action (typing, upload_photo, ...)."),
    "send_poll": (
        {"chat_id": ("Any", True, None),
         "question": ("str", True, None), "options": ("List[Dict]", True, None),
         "is_anonymous": ("Optional[bool]", False, "None"),
         "type": ("Optional[str]", False, "None"),
         "allows_multiple_answers": ("Optional[bool]", False, "None"),
         "correct_option_id": ("Optional[int]", False, "None"),
         "explanation": ("Optional[str]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send a poll or quiz."),
    "send_rich_message": (
        {"chat_id": ("Any", True, None),
         "rich_message": ("Any", True, None),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send a structured rich message (Vibe-specific)."),

    # ---- message management ----
    "edit_message_text": (
        {"chat_id": ("Optional[Any]", False, "None"),
         "message_id": ("Optional[int]", False, "None"),
         "inline_message_id": ("Optional[str]", False, "None"),
         "text": ("str", True, None),
         "parse_mode": ("Optional[str]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Any", "Edit a previously sent text message."),
    "edit_message_caption": (
        {"chat_id": ("Optional[Any]", False, "None"),
         "message_id": ("Optional[int]", False, "None"),
         "inline_message_id": ("Optional[str]", False, "None"),
         "caption": ("Optional[str]", False, "None"),
         "parse_mode": ("Optional[str]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Any", "Edit the caption of a media message."),
    "edit_message_media": (
        {"chat_id": ("Optional[Any]", False, "None"),
         "message_id": ("Optional[int]", False, "None"),
         "inline_message_id": ("Optional[str]", False, "None"),
         "media": ("Any", True, None),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Any", "Replace media of a message."),
    "edit_message_reply_markup": (
        {"chat_id": ("Optional[Any]", False, "None"),
         "message_id": ("Optional[int]", False, "None"),
         "inline_message_id": ("Optional[str]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Any", "Edit inline keyboard of a message."),
    "delete_message": (
        {"chat_id": ("Any", True, None), "message_id": ("int", True, None)},
        "bool", "Delete one message."),
    "delete_messages": (
        {"chat_id": ("Any", True, None), "message_ids": ("List[int]", True, None)},
        "bool", "Delete a batch of messages."),
    "forward_message": (
        {"chat_id": ("Any", True, None),
         "from_chat_id": ("Any", True, None), "message_id": ("int", True, None),
         "message_thread_id": ("Optional[int]", False, "None")},
        "Dict[str, Any]", "Forward a single message."),
    "forward_messages": (
        {"chat_id": ("Any", True, None),
         "from_chat_id": ("Any", True, None), "message_ids": ("List[int]", True, None),
         "message_thread_id": ("Optional[int]", False, "None")},
        "List[Dict[str, Any]]", "Forward a batch of messages."),
    "copy_message": (
        {"chat_id": ("Any", True, None),
         "from_chat_id": ("Any", True, None), "message_id": ("int", True, None),
         "caption": ("Optional[str]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Copy a message without forward header."),
    "copy_messages": (
        {"chat_id": ("Any", True, None),
         "from_chat_id": ("Any", True, None), "message_ids": ("List[int]", True, None)},
        "List[int]", "Copy a batch of messages."),
    "set_message_reaction": (
        {"chat_id": ("Any", True, None), "message_id": ("int", True, None),
         "reaction": ("Optional[List[Dict]]", False, "None"),
         "is_big": ("Optional[bool]", False, "None")},
        "bool", "Set or clear the reaction on a message."),
    "stop_poll": (
        {"chat_id": ("Any", True, None), "message_id": ("int", True, None),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Stop a running poll."),
    "edit_message_live_location": (
        {"chat_id": ("Optional[Any]", False, "None"),
         "message_id": ("Optional[int]", False, "None"),
         "inline_message_id": ("Optional[str]", False, "None"),
         "latitude": ("float", True, None), "longitude": ("float", True, None),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Any", "Update a live location message."),
    "stop_message_live_location": (
        {"chat_id": ("Optional[Any]", False, "None"),
         "message_id": ("Optional[int]", False, "None"),
         "inline_message_id": ("Optional[str]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Any", "Stop a live location message."),

    # ---- chat / admin ----
    "get_chat": (
        {"chat_id": ("Any", True, None)}, "Dict[str, Any]", "Get chat info."),
    "get_chat_administrators": (
        {"chat_id": ("Any", True, None)}, "List[Dict]", "List chat administrators."),
    "get_chat_member_count": (
        {"chat_id": ("Any", True, None)}, "int", "Get chat member count."),
    "get_chat_member": (
        {"chat_id": ("Any", True, None), "user_id": ("int", True, None)},
        "Dict[str, Any]", "Get a specific member info."),
    "ban_chat_member": (
        {"chat_id": ("Any", True, None), "user_id": ("int", True, None),
         "until_date": ("Optional[int]", False, "None"),
         "revoke_messages": ("Optional[bool]", False, "None")},
        "bool", "Ban a user from a chat."),
    "unban_chat_member": (
        {"chat_id": ("Any", True, None), "user_id": ("int", True, None),
         "only_if_banned": ("Optional[bool]", False, "None")},
        "bool", "Unban a user."),
    "restrict_chat_member": (
        {"chat_id": ("Any", True, None), "user_id": ("int", True, None),
         "permissions": ("Dict", True, None),
         "until_date": ("Optional[int]", False, "None"),
         "use_independent_chat_permissions": ("Optional[bool]", False, "None")},
        "bool", "Restrict a user's permissions."),
    "promote_chat_member": (
        {"chat_id": ("Any", True, None), "user_id": ("int", True, None),
         "is_anonymous": ("Optional[bool]", False, "None"),
         "can_manage_chat": ("Optional[bool]", False, "None"),
         "can_delete_messages": ("Optional[bool]", False, "None"),
         "can_manage_video_chats": ("Optional[bool]", False, "None"),
         "can_restrict_members": ("Optional[bool]", False, "None"),
         "can_promote_members": ("Optional[bool]", False, "None"),
         "can_change_info": ("Optional[bool]", False, "None"),
         "can_invite_users": ("Optional[bool]", False, "None"),
         "can_post_messages": ("Optional[bool]", False, "None"),
         "can_edit_messages": ("Optional[bool]", False, "None"),
         "can_pin_messages": ("Optional[bool]", False, "None"),
         "can_manage_topics": ("Optional[bool]", False, "None")},
        "bool", "Promote/demote a chat member."),
    "set_chat_administrator_custom_title": (
        {"chat_id": ("Any", True, None), "user_id": ("int", True, None),
         "custom_title": ("str", True, None)},
        "bool", "Set a custom title for an administrator."),
    "ban_chat_sender_chat": (
        {"chat_id": ("Any", True, None), "sender_chat_id": ("int", True, None)},
        "bool", "Ban a channel from sending messages in a group."),
    "unban_chat_sender_chat": (
        {"chat_id": ("Any", True, None), "sender_chat_id": ("int", True, None)},
        "bool", "Unban a channel sender in a group."),
    "set_chat_permissions": (
        {"chat_id": ("Any", True, None), "permissions": ("Dict", True, None),
         "use_independent_chat_permissions": ("Optional[bool]", False, "None")},
        "bool", "Set default chat permissions."),
    "export_chat_invite_link": (
        {"chat_id": ("Any", True, None)}, "str", "Export the primary invite link."),
    "create_chat_invite_link": (
        {"chat_id": ("Any", True, None),
         "name": ("Optional[str]", False, "None"),
         "expire_date": ("Optional[int]", False, "None"),
         "member_limit": ("Optional[int]", False, "None"),
         "creates_join_request": ("Optional[bool]", False, "None")},
        "Dict[str, Any]", "Create a custom invite link."),
    "edit_chat_invite_link": (
        {"chat_id": ("Any", True, None), "invite_link": ("str", True, None),
         "name": ("Optional[str]", False, "None"),
         "expire_date": ("Optional[int]", False, "None"),
         "member_limit": ("Optional[int]", False, "None"),
         "creates_join_request": ("Optional[bool]", False, "None")},
        "Dict[str, Any]", "Edit an invite link."),
    "revoke_chat_invite_link": (
        {"chat_id": ("Any", True, None), "invite_link": ("str", True, None)},
        "Dict[str, Any]", "Revoke an invite link."),
    "approve_chat_join_request": (
        {"chat_id": ("Any", True, None), "user_id": ("int", True, None)},
        "bool", "Approve a join request."),
    "decline_chat_join_request": (
        {"chat_id": ("Any", True, None), "user_id": ("int", True, None)},
        "bool", "Decline a join request."),
    "set_chat_title": (
        {"chat_id": ("Any", True, None), "title": ("str", True, None)},
        "bool", "Set chat title."),
    "set_chat_description": (
        {"chat_id": ("Any", True, None), "description": ("Optional[str]", False, "None")},
        "bool", "Set chat description."),
    "set_chat_photo": (
        {"chat_id": ("Any", True, None), "photo": ("Any", True, None)},
        "bool", "Set chat profile photo."),
    "delete_chat_photo": (
        {"chat_id": ("Any", True, None)}, "bool", "Delete chat profile photo."),
    "pin_chat_message": (
        {"chat_id": ("Any", True, None), "message_id": ("int", True, None),
         "disable_notification": ("Optional[bool]", False, "None")},
        "bool", "Pin a chat message."),
    "unpin_chat_message": (
        {"chat_id": ("Any", True, None),
         "message_id": ("Optional[int]", False, "None")},
        "bool", "Unpin a chat message."),
    "unpin_all_chat_messages": (
        {"chat_id": ("Any", True, None)}, "bool", "Unpin all messages in chat."),
    "leave_chat": (
        {"chat_id": ("Any", True, None)}, "bool", "Leave a chat."),
    "set_chat_sticker_set": (
        {"chat_id": ("Any", True, None), "sticker_set_name": ("str", True, None)},
        "bool", "Assign a sticker set to a group."),
    "delete_chat_sticker_set": (
        {"chat_id": ("Any", True, None)}, "bool", "Remove sticker set from a group."),

    # ---- forum topics ----
    "create_forum_topic": (
        {"chat_id": ("Any", True, None), "name": ("str", True, None),
         "icon_color": ("Optional[int]", False, "None"),
         "icon_custom_emoji_id": ("Optional[str]", False, "None")},
        "Dict[str, Any]", "Create a forum topic."),
    "edit_forum_topic": (
        {"chat_id": ("Any", True, None), "message_thread_id": ("int", True, None),
         "name": ("Optional[str]", False, "None"),
         "icon_custom_emoji_id": ("Optional[str]", False, "None")},
        "bool", "Edit forum topic."),
    "close_forum_topic": (
        {"chat_id": ("Any", True, None), "message_thread_id": ("int", True, None)},
        "bool", "Close a forum topic."),
    "reopen_forum_topic": (
        {"chat_id": ("Any", True, None), "message_thread_id": ("int", True, None)},
        "bool", "Reopen a forum topic."),
    "delete_forum_topic": (
        {"chat_id": ("Any", True, None), "message_thread_id": ("int", True, None)},
        "bool", "Delete a forum topic."),
    "unpin_all_forum_topic_messages": (
        {"chat_id": ("Any", True, None), "message_thread_id": ("int", True, None)},
        "bool", "Unpin all messages in a forum topic."),
    "edit_general_forum_topic": (
        {"chat_id": ("Any", True, None), "name": ("str", True, None)},
        "bool", "Edit the general forum topic."),
    "close_general_forum_topic": (
        {"chat_id": ("Any", True, None)}, "bool", "Close the general forum topic."),
    "reopen_general_forum_topic": (
        {"chat_id": ("Any", True, None)}, "bool", "Reopen the general forum topic."),
    "hide_general_forum_topic": (
        {"chat_id": ("Any", True, None)}, "bool", "Hide the general forum topic."),
    "unhide_general_forum_topic": (
        {"chat_id": ("Any", True, None)}, "bool", "Unhide the general forum topic."),
    "get_forum_topic_icon_stickers": (
        {}, "List[Dict]", "Get allowed topic icon stickers."),

    # ---- stickers ----
    "get_sticker_set": (
        {"name": ("str", True, None)}, "Dict[str, Any]", "Get a sticker set."),
    "get_custom_emoji_stickers": (
        {"custom_emoji_ids": ("List[str]", True, None)},
        "List[Dict]", "Get custom emoji stickers."),
    "upload_sticker_file": (
        {"user_id": ("int", True, None), "sticker": ("Any", True, None),
         "sticker_format": ("str", True, None)},
        "Dict[str, Any]", "Upload a sticker file."),
    "create_new_sticker_set": (
        {"user_id": ("int", True, None), "name": ("str", True, None),
         "title": ("str", True, None), "stickers": ("List[Dict]", True, None),
         "sticker_format": ("str", True, None),
         "sticker_type": ("Optional[str]", False, "None"),
         "needs_repainting": ("Optional[bool]", False, "None")},
        "bool", "Create a new sticker set."),
    "add_sticker_to_set": (
        {"user_id": ("int", True, None), "name": ("str", True, None),
         "sticker": ("Dict", True, None)},
        "bool", "Add a sticker to a set."),
    "set_sticker_position_in_set": (
        {"sticker": ("str", True, None), "position": ("int", True, None)},
        "bool", "Move a sticker within a set."),
    "delete_sticker_from_set": (
        {"sticker": ("str", True, None)}, "bool", "Remove a sticker from a set."),
    "set_sticker_set_thumbnail": (
        {"name": ("str", True, None), "user_id": ("int", True, None),
         "thumbnail": ("Optional[Any]", False, "None"),
         "format": ("Optional[str]", False, "None")},
        "bool", "Set the sticker set thumbnail."),
    "delete_sticker_set": (
        {"name": ("str", True, None)}, "bool", "Delete a sticker set."),

    # ---- inline / callback / webapp ----
    "answer_inline_query": (
        {"inline_query_id": ("str", True, None),
         "results": ("List[Dict]", True, None),
         "cache_time": ("Optional[int]", False, "None"),
         "is_personal": ("Optional[bool]", False, "None"),
         "next_offset": ("Optional[str]", False, "None"),
         "button": ("Optional[Dict]", False, "None")},
        "bool", "Answer an inline query."),
    "answer_callback_query": (
        {"callback_query_id": ("str", True, None),
         "text": ("Optional[str]", False, "None"),
         "show_alert": ("Optional[bool]", False, "None"),
         "url": ("Optional[str]", False, "None"),
         "cache_time": ("Optional[int]", False, "None")},
        "bool", "Answer a callback query."),
    "answer_web_app_query": (
        {"web_app_query_id": ("str", True, None),
         "result": ("Dict", True, None)},
        "Dict[str, Any]", "Answer a Web App query."),
    "save_prepared_inline_message": (
        {"user_id": ("int", True, None), "result": ("Dict", True, None),
         "allow_user_chats": ("Optional[bool]", False, "None"),
         "allow_bot_chats": ("Optional[bool]", False, "None"),
         "allow_group_chats": ("Optional[bool]", False, "None"),
         "allow_channel_chats": ("Optional[bool]", False, "None")},
        "Dict[str, Any]", "Save a prepared inline message."),

    # ---- payments / stars / gifts ----
    "send_invoice": (
        {"chat_id": ("Any", True, None), "title": ("str", True, None),
         "description": ("str", True, None), "payload": ("str", True, None),
         "currency": ("str", True, None), "prices": ("List[Dict]", True, None),
         "provider_token": ("Optional[str]", False, "None"),
         "max_tip_amount": ("Optional[int]", False, "None"),
         "suggested_tip_amounts": ("Optional[List[int]]", False, "None"),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send an invoice."),
    "create_invoice_link": (
        {"title": ("str", True, None), "description": ("str", True, None),
         "payload": ("str", True, None), "currency": ("str", True, None),
         "prices": ("List[Dict]", True, None),
         "provider_token": ("Optional[str]", False, "None")},
        "str", "Create a standalone invoice link."),
    "refund_star_payment": (
        {"user_id": ("int", True, None),
         "telegram_payment_charge_id": ("str", True, None)},
        "bool", "Refund a Stars payment."),
    "answer_pre_checkout_query": (
        {"pre_checkout_query_id": ("str", True, None),
         "ok": ("bool", True, None),
         "error_message": ("Optional[str]", False, "None")},
        "bool", "Answer a pre-checkout query."),
    "get_star_transactions": (
        {"offset": ("Optional[int]", False, "None"),
         "limit": ("Optional[int]", False, "None")},
        "Dict[str, Any]", "List star transactions."),
    "edit_user_star_subscription": (
        {"user_id": ("int", True, None),
         "telegram_payment_charge_id": ("str", True, None),
         "is_canceled": ("bool", True, None)},
        "bool", "Manage a user's recurring star subscription."),
    "get_available_gifts": (
        {}, "Dict[str, Any]", "List available star gifts."),
    "send_gift": (
        {"gift_id": ("str", True, None),
         "user_id": ("Optional[int]", False, "None"),
         "chat_id": ("Optional[Any]", False, "None"),
         "text": ("Optional[str]", False, "None"),
         "pay_for_upgrade": ("Optional[bool]", False, "None")},
        "bool", "Send a star gift."),
    "gift_premium_subscription": (
        {"user_id": ("int", True, None), "month_count": ("int", True, None),
         "star_count": ("int", True, None),
         "text": ("Optional[str]", False, "None")},
        "bool", "Gift a premium subscription."),

    # ---- games / boosts / business ----
    "send_game": (
        {"chat_id": ("Any", True, None), "game_short_name": ("str", True, None),
         "reply_markup": ("Optional[Dict]", False, "None")},
        "Dict[str, Any]", "Send an HTML5 game."),
    "set_game_score": (
        {"user_id": ("int", True, None), "score": ("int", True, None),
         "chat_id": ("Optional[Any]", False, "None"),
         "message_id": ("Optional[int]", False, "None"),
         "force": ("Optional[bool]", False, "None"),
         "disable_edit_message": ("Optional[bool]", False, "None")},
        "Any", "Set a game score."),
    "get_game_high_scores": (
        {"user_id": ("int", True, None),
         "chat_id": ("Optional[Any]", False, "None"),
         "message_id": ("Optional[int]", False, "None")},
        "List[Dict]", "Get game high scores."),
    "get_user_chat_boosts": (
        {"chat_id": ("Any", True, None), "user_id": ("int", True, None)},
        "Dict[str, Any]", "Get boosts given by a user to a chat."),
    "get_business_connection": (
        {"business_connection_id": ("str", True, None)},
        "Dict[str, Any]", "Get business connection info."),

    # ---- identity / profile ----
    "get_my_name": (
        {"language_code": ("Optional[str]", False, "None")},
        "Dict[str, Any]", "Get the bot's display name."),
    "set_my_name": (
        {"name": ("str", True, None),
         "language_code": ("Optional[str]", False, "None")},
        "bool", "Set the bot's display name."),
    "get_my_description": (
        {"language_code": ("Optional[str]", False, "None")},
        "Dict[str, Any]", "Get the bot's description."),
    "set_my_description": (
        {"description": ("str", True, None),
         "language_code": ("Optional[str]", False, "None")},
        "bool", "Set the bot's description."),
    "get_my_short_description": (
        {"language_code": ("Optional[str]", False, "None")},
        "Dict[str, Any]", "Get the bot's short description."),
    "set_my_short_description": (
        {"short_description": ("str", True, None),
         "language_code": ("Optional[str]", False, "None")},
        "bool", "Set the bot's short description."),
    "get_my_commands": (
        {"scope": ("Optional[Dict]", False, "None"),
         "language_code": ("Optional[str]", False, "None")},
        "List[Dict]", "Get the bot's command list."),
    "set_my_commands": (
        {"commands": ("List[Dict]", True, None),
         "scope": ("Optional[Dict]", False, "None"),
         "language_code": ("Optional[str]", False, "None")},
        "bool", "Set the bot's command list."),
    "delete_my_commands": (
        {"scope": ("Optional[Dict]", False, "None"),
         "language_code": ("Optional[str]", False, "None")},
        "bool", "Delete the bot's command list."),
    "set_chat_menu_button": (
        {"chat_id": ("Optional[Any]", False, "None"),
         "menu_button": ("Optional[Dict]", False, "None")},
        "bool", "Set the chat menu button."),
    "get_chat_menu_button": (
        {"chat_id": ("Optional[Any]", False, "None")},
        "Dict[str, Any]", "Get the chat menu button."),
    "get_my_default_administrator_rights": (
        {"for_channels": ("Optional[bool]", False, "None")},
        "Dict[str, Any]", "Get default admin rights."),
    "set_my_default_administrator_rights": (
        {"rights": ("Optional[Dict]", False, "None"),
         "for_channels": ("Optional[bool]", False, "None")},
        "bool", "Set default admin rights."),
    "get_user_profile_photos": (
        {"user_id": ("int", True, None),
         "offset": ("Optional[int]", False, "None"),
         "limit": ("Optional[int]", False, "None")},
        "Dict[str, Any]", "Get a user's profile photos."),
    "set_user_emoji_status": (
        {"user_id": ("int", True, None),
         "custom_emoji_id": ("Optional[str]", False, "None"),
         "duration": ("Optional[int]", False, "None")},
        "bool", "Set a user's emoji status."),
    "log_out": (
        {}, "bool", "Log out from the local Bot API server."),
    "close_server": (
        {}, "bool", "Close the local Bot API server (Bot API /close)."),
}


HEADER = """# ============================================
#  botapi/http_methods.py - Bot API method wrappers
#  Auto-generated by scripts/gen_http_methods.py. Do not edit by hand.
# ============================================
from typing import Any, Dict, List, Optional

from botapi.http_client import VibeBotHTTP


_RESERVED = frozenset({"call", "close", "poll_updates", "get_updates", "get_me"})


class _HTTPMethodsMixin:
"""


def build_method(pyname, params, ret, doc):
    camel = _to_camel(pyname)
    if params:
        sig_parts = ["self", "*"]
        for name, (typ, required, default) in params.items():
            if required:
                sig_parts.append(f"{name}: {typ}")
            else:
                sig_parts.append(f"{name}: {typ} = {default}")
        sig = ", ".join(sig_parts)
    else:
        sig = "self"

    if params:
        body_lines = []
        for name in params:
            body_lines.append(f'            "{name}": {name},')
        body = "\n".join(body_lines)
        call = (
            f"        return await self.call(\n"
            f"            \"{camel}\",\n"
            f"            **{{\n"
            f"{body}\n"
            f"            }},\n"
            f"        )\n"
        )
    else:
        call = f"        return await self.call(\"{camel}\")\n"

    return (
        f"    async def {pyname}({sig}) -> {ret}:\n"
        f"        \"\"\"{doc}\"\"\"\n"
        f"{call}\n"
    )


def main():
    chunks = [HEADER]
    for pyname, (params, ret, doc) in METHODS.items():
        chunks.append(build_method(pyname, params, ret, doc))
    chunks.append("\n\nfor _name, _fn in _HTTPMethodsMixin.__dict__.items():\n")
    chunks.append("    if _name.startswith(\"_\"):\n")
    chunks.append("        continue\n")
    chunks.append("    if _name in _RESERVED:\n")
    chunks.append("        continue\n")
    chunks.append("    if not callable(_fn):\n")
    chunks.append("        continue\n")
    chunks.append("    setattr(VibeBotHTTP, _name, _fn)\n")

    out = Path("botapi/http_methods.py")
    out.write_text("".join(chunks))
    print(f"wrote {out} ({len(METHODS)} methods)")


if __name__ == "__main__":
    main()
