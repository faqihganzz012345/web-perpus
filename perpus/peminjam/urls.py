from django.urls import path
from . import views

urlpatterns = [
    path('', views.buku_list, name='buku_list'),  # <-- Pastikan 'name' ini ada
    path('tambah/', views.buku_create, name='buku_create'),
    path('detail/<int:id>/', views.buku_detail, name='buku_detail'),
    path('ubah/<int:id>/', views.buku_update, name='buku_update'),
    path('hapus/<int:id>/', views.buku_delete, name='buku_delete'),
    path('peminjam/', views.peminjam_list, name='peminjam_list'),  # <-- Pastikan 'name' ini ada
    path('peminjam/kembali/<int:id>/', views.peminjam_kembali, name='peminjam_kembali'),
    path('peminjam/tambah/', views.peminjam_create, name='peminjam_create'),
    path('user/', views.user_list, name='user_list'),
    path('user/tambah/', views.user_create, name='user_create'),
    path('user/detail/<int:id>/', views.user_detail, name='user_detail'),
    path('user/ubah/<int:id>/', views.user_update, name='user_update'),
    path('user/hapus/<int:id>/', views.user_delete, name='user_delete'),
]