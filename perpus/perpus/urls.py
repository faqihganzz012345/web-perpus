from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # always redirect to /peminjam
    path('', lambda request: redirect('buku_list')),
    path('admin/', admin.site.urls),
    path('buku/', include('peminjam.urls')),
]

