from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from firstproject import settings
from mainapp import views

handler404 = views.e_handler404

urlpatterns = [
    re_path(r"terms-of-service$", views.termsOfService),
    re_path(r"contact-us$", views.contact),
    re_path(r"site-information$", views.information),
    re_path(r"exit$", views.Exit),
    re_path(r"profile$", views.profile),
    path("my_secure_admin/", admin.site.urls),
    path("authorization/", views.authorization),
    re_path(r"authorization$", views.authorization),
    re_path(r"list-sections$", views.listSections),
    re_path(r"register$", views.register),
    re_path(r"edit$", views.edit),
    re_path(r"add-students$", views.addStudents),
    re_path(r"delete-students$", views.deleteStudents),
    re_path(r"add-coaches$", views.addCoaches),
    re_path(r"list-users$", views.listUsers),
    re_path(r"delete-coaches$", views.deleteCoaches),
    re_path(r"list-lessons$", views.listLessons),
    re_path(r"add-lesson$", views.addLesson),
    re_path(r"add-section$", views.addSection),
    re_path(r"edit-section$", views.editSection),
    re_path(r"search$", views.search),
    re_path(r"section$", views.section),
    re_path(r"more-detailed$", views.detailed),
    path("", views.index),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)