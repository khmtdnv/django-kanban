from django.core.cache import caches
from rest_framework.throttling import (
    AnonRateThrottle,
    ScopedRateThrottle,
    UserRateThrottle,
)

throttle_cache = caches["throttling"]


class AppAnonRateThrottle(AnonRateThrottle):
    cache = throttle_cache
    rate = "50/h"


class AppUserRateThrottle(UserRateThrottle):
    cache = throttle_cache


class AppScopedRateThrottle(ScopedRateThrottle):
    cache = throttle_cache


class BurstRateThrottle(AppUserRateThrottle):
    scope = "burst"


class SustainedRateThrottle(AppUserRateThrottle):
    scope = "sustained"
