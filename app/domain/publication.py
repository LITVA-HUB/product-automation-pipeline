from __future__ import annotations

from enum import StrEnum


class PublicationMode(StrEnum):
    MS_ONLY = "ms_only"
    MS_AND_SITE_INACTIVE = "ms_and_site_inactive"
    MS_AND_SITE_ACTIVE = "ms_and_site_active"
