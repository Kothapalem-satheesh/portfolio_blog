from types import SimpleNamespace

from .models import Profile
from .resume_defaults import DEFAULT_PROFILE


def site_profile(_request):
    profile = Profile.objects.order_by("-updated_at").first()
    if profile is None:
        profile = SimpleNamespace(**DEFAULT_PROFILE, photo=None)
    return {"site_profile": profile}
