from django.urls import path
from pommento.core import views

app_name = "pommento-core"

urlpatterns = [
    path("", views.site_list_view, name="site-list"),
    path("site/<uuid:id>", views.comment_list_view, name="comment-list"),
    path("site/comment/<int:id>/<str:status>", views.comment_status, name="comment_status"),
    path("comment-widget", views.comment_widget, name="comment-widget"),
]
