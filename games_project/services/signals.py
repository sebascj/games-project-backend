def user_post_save(sender, **kwargs):
    from tastypie.models import create_api_key
    create_api_key(sender, **kwargs)
