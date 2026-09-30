from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from accounts.models import UserProfile


@login_required
@require_POST
def update_profile(request):
    user = request.user
    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    email = request.POST.get("email", "").strip()

    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.save(update_fields=["first_name", "last_name", "email"])

    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    if "avatar" in request.FILES:
        avatar_file = request.FILES["avatar"]
        # Basic extension validation
        if avatar_file.name.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            profile.avatar = avatar_file
            profile.save()
            messages.success(request, "Profile and photo updated successfully!")
        else:
            messages.error(request, "Invalid image format. Allowed: PNG, JPG, JPEG, WEBP.")
    elif request.POST.get("remove_avatar") == "1":
        if profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = None
            profile.save()
        messages.success(request, "Profile updated and photo removed.")
    else:
        messages.success(request, "Profile details updated successfully!")

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "home"
    return redirect(next_url)


@login_required
@require_POST
def delete_account(request):
    confirm = request.POST.get("confirm_delete")
    if confirm != "DELETE":
        messages.error(request, "Please type DELETE to confirm account deletion.")
        next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "home"
        return redirect(next_url)

    user = request.user
    logout(request)
    user.delete()
    messages.success(request, "Your account and financial data have been permanently deleted.")
    return redirect("login")
