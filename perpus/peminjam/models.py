from django.db import models

class Anggota(models.Model):
    nama = models.CharField(max_length=255)
    kelas = models.CharField(max_length=50, blank=True, null=True)
    nis = models.CharField(max_length=50, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, default='Aktif')

    class Meta:
        db_table = 'peminjam_anggota'


class Peminjam(models.Model):
    nama = models.CharField(max_length=255)
    buku = models.CharField(max_length=255)
    tgl_pinjam = models.CharField(max_length=50, blank=True, null=True)
    tgl_kembali = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'peminjam'