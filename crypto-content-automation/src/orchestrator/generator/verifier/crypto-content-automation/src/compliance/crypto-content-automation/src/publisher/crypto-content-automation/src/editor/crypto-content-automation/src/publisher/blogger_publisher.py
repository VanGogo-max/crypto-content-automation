# Copyright 2026 Георги Владимиров
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

from typing import Optional
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


class BloggerPublisher:
    """
    Publishes verified and edited articles to Google Blogger.
    Uses Google Blogger v3 API with Service Account authentication.
    """

    def __init__(self, service_account_json: str, blog_id: str):
        scopes = ["https://www.googleapis.com/auth/blogger"]
        credentials = Credentials.from_service_account_file(
            service_account_json, scopes=scopes
        )
        self.service = build("blogger", "v3", credentials=credentials)
        self.blog_id = blog_id

    def publish_post(
        self,
        title: str,
        content_html: str,
        labels: Optional[list] = None,
        is_draft: bool = False,
    ) -> dict:
        """
        Publishes a post to Blogger.

        :param title: Post title
        :param content_html: HTML body (from ContentEditor)
        :param labels: List of tags/labels
        :param is_draft: If True, post is saved as draft
        :return: Blogger API response
        """

        post_body = {
            "kind": "blogger#post",
            "title": title,
            "content": content_html,
            "labels": labels or [],
        }

        request = self.service.posts().insert(
            blogId=self.blog_id,
            body=post_body,
            isDraft=is_draft,
        )

        return request.execute()
