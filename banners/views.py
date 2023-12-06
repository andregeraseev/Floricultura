from django.contrib.contenttypes.models import ContentType
from .models import HeroBanner, SecondaryBanner, BannerClick
from django.shortcuts import get_object_or_404, redirect
def track_click(request, banner_id, banner_type):
    if banner_type == 'hero':
        banner_model = HeroBanner
    else:
        banner_model = SecondaryBanner

    banner = get_object_or_404(banner_model, id=banner_id)
    banner_content_type = ContentType.objects.get_for_model(banner_model)

    BannerClick.objects.create(
        content_type=banner_content_type,
        object_id=banner.id,
        clicked_by=request.user if request.user.is_authenticated else None
    )

    return redirect(banner.link)
