# File: publisher/blogger_publisher.py
# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0

"""
BloggerPublisher module
- Publishes content to Blogger blogs via Google API
- Handles authentication via OAuth2 / Service Account
- Returns published post URL
"""

import os
from typing import Dict
from google.oauth2 import service_account
from googleapiclient.discovery import build

class BloggerPublisherError(Exception):
    pass

class BloggerPublisher:
    def __init__(self, blog_id: str = None, credentials_file: str = None):
        self.blog_id = blog_id or os.getenv("BLOGGER_BLOG_ID")
        self.credentials_file = credentials_file or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not self.blog_id or not self.credentials_file:
            raise BloggerPublisherError("Missing blog_id or credentials file")
        self.service = self._init_service()

    def _init_service(self):
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=["https://www.googleapis.com/auth/blogger"]
            )
            return build("blogger", "v3", credentials=creds)
        except Exception as e:
            raise BloggerPublisherError(f"Failed to initialize Blogger service: {e}")

    def publish(self, text: str, metadata: Dict, language: str = "en") -> str:
        """
        Publishes text to Blogger.
        Returns URL of published post.
        """
        try:
            post_body = {
                "kind": "blogger#post",
                "title": metadata.get("topic", "Crypto Article"),
                "content": text
            }
            post = self.service.posts().insert(blogId=self.blog_id, body=post_body, isDraft=False).execute()
            return post.get("url", "")
        except Exception as e:
            raise BloggerPublisherError(f"Failed to publish to Blogger: {e}")
