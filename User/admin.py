# from django.contrib import admin
#
# # Register your models here.
#
# from django.contrib import admin
# from User.models import User
#
#
# class UserAdmin(admin.ModelAdmin):
#     def has_module_perms(self, app_label):
#         return self.is_superuser
#
#     def has_perm(self, perm, obj=None):
#         return self.is_superuser
#
#
# # from django.contrib.auth.models import User
# anonymous_user = User.objects.all().first()
# admin.site.has_permission = lambda r: setattr(r, 'user', anonymous_user) or True
#
# admin.site.register(User)
