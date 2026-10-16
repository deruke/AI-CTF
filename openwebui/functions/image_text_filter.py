"""
title: image_text_filter
author: open-webui
author_url: Brian Fehrman
version: 0.5
"""

from pydantic import BaseModel, Field
from typing import Optional


class Filter:
    class Valves(BaseModel):
        priority: int = Field(
            default=0, description="Priority level for the filter operations."
        )

    class UserValves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()

    def has_image_files(self, files: list) -> bool:
        return any(
            f.get("type") == "file"
            and f.get("file", {})
            .get("meta", {})
            .get("content_type", "")
            .startswith("image/")
            for f in (files or [])
        )

    def _has_inline_image(self, content) -> bool:
        # This Open WebUI version sends the uploaded image INLINE in the message
        # content as an image_url part: [{"type":"text",...},{"type":"image_url",...}].
        return isinstance(content, list) and any(
            isinstance(p, dict) and p.get("type") == "image_url" for p in content
        )

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        print(f"inlet:{__name__}")
        print(f"inlet:body:{body}")
        print(f"inlet:user:{__user__}")

        response_message = "Respond only with: Please provide an image for processing"

        messages = body.get("messages", [])
        if not messages:
            return body

        # Image can arrive two ways in this OWUI version: inline image_url parts
        # in the last user message content, or as an uploaded file recorded under
        # metadata.user_message.files. Check both; older code checked the wrong key
        # (parent_message.files), so it never detected the image.
        metadata = body.get("metadata", {}) or {}
        user_message = metadata.get("user_message") or {}
        files_has_image = self.has_image_files(user_message.get("files") or [])

        cleaned_messages = []
        for i, msg in enumerate(messages):
            msg = msg.copy()
            is_last = i == len(messages) - 1
            role = msg.get("role", "")

            if role == "user" and is_last:
                content = msg.get("content", "")
                has_image = self._has_inline_image(content) or files_has_image
                if not has_image:
                    # No image on the final turn: prompt the user to provide one.
                    msg["content"] = response_message
                # If an image IS present, leave the multimodal content untouched so
                # the vision model actually receives the image. Do NOT replace it.

            # Prior user messages are left as-is. Never call .strip() on list
            # (multimodal) content -- that raised "list has no attribute strip".
            cleaned_messages.append(msg)

        body = {**body, "messages": cleaned_messages}
        print(f"inlet:cleaned_messages:{cleaned_messages}")
        return body
