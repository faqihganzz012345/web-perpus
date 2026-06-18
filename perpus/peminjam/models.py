from django.db import models


class Buku(models.Model):
    judul = models.CharField(max_length=255)
    pengarang = models.CharField(max_length=255, blank=True, null=True)
    kategori = models.CharField(max_length=100, blank=True, null=True)
    penerbit = models.CharField(max_length=255, blank=True, null=True)
    tahun_terbit = models.IntegerField(blank=True, null=True)
    stok = models.IntegerField(default=0)
    isbn = models.CharField(max_length=50, blank=True, null=True)
    rak = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'buku'

    def __str__(self):
        return self.judul


class Anggota(models.Model):
    nama = models.CharField(max_length=255)
    kelas = models.CharField(max_length=50, blank=True, null=True)
    nis = models.CharField(max_length=50, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, default='Aktif')

    class Meta:
        db_table = 'peminjam_anggota'

    def __str__(self):
        return self.nama


class Peminjam(models.Model):
    nama = models.CharField(max_length=255)
    buku = models.CharField(max_length=255)
    tgl_pinjam = models.CharField(max_length=50, blank=True, null=True)
    tgl_kembali = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'peminjam'

    def __str__(self):
        return f"{self.nama} - {self.buku}"