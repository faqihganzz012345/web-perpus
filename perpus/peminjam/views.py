from urllib import request

from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse


def dictfetchall(cursor):
    """Mengubah semua hasil query menjadi list of dictionaries."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dictfetchone(cursor):
    """Mengubah satu hasil query menjadi dictionary."""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()

    if row is None:
        return None

    return dict(zip(columns, row))

# --- 1. MENAMPILKAN DAFTAR BUKU ---
def buku_list(request):
    # Mengambil kata kunci pencarian dari parameter URL (Method GET)
    query_cari = request.GET.get('buku', '').strip()

    with connection.cursor() as cursor:
        if query_cari:
            # Jika user mengetikkan sesuatu, cari berdasarkan judul atau pengarang
            cursor.execute("""
                SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, stok, isbn, lokasi_rak
                FROM buku
                WHERE judul ILIKE %s OR pengarang ILIKE %s
                ORDER BY id DESC
            """, [f'%{query_cari}%', f'%{query_cari}%'])
            search_text = f"Hasil Pencarian: '{query_cari}'"
        else:
            # Jika tidak ada pencarian, tampilkan semua buku seperti biasa
            cursor.execute("""
                SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, stok, isbn, lokasi_rak
                FROM buku
                ORDER BY id DESC
            """)
            search_text = "Katalog Buku"
            
        data_buku = dictfetchall(cursor)

    return render(request, 'buku_list.html', {
        'keyword': search_text,
        'data': data_buku,
        'query_sekarang': query_cari, # Dikirim balik agar teks di input tidak hilang setelah di-refresh
    })
    
# --- 2. TAMPILAN DETAIL BUKU ---
def buku_detail(request, id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM buku
            WHERE id = %s
            """,
            [id]
        )
        buku = dictfetchone(cursor)    

    return render(request, 'buku_detail.html', {
        'buku': buku,
    })

# --- 3. MENAMBAH DATA BUKU (CREATE) ---
from django.shortcuts import render, redirect
from django.db import connection



def buku_create(request):
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        pengarang = request.POST.get('pengarang', '').strip()
        kategori = request.POST.get('kategori', '').strip()
        penerbit = request.POST.get('penerbit', '').strip()
        tahun_terbit = request.POST.get('tahun_terbit', '').strip()
        stok = request.POST.get('stok', '').strip()
        lokasi_rak = request.POST.get('lokasi_rak', '').strip()
        
        # --- PERBAIKAN DI SINI ---
        # Ambil input angka, jika kosong atau bukan angka, set jadi None (NULL di SQL) atau 0
        tahun_raw = request.POST.get('tahun_terbit_numeric', '').strip()
        tahun_terbit = int(tahun_raw) if tahun_raw.isdigit() else None
        # -------------------------

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO buku (judul, pengarang, kategori, penerbit, tahun_terbit, stok, lokasi_rak)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                # Data dikirim sesuai urutan kolom %s di atas
                [judul, pengarang, kategori, penerbit, tahun_terbit, stok, lokasi_rak]
            )

        return redirect('buku_list')
    
    return render(request, 'buku_create.html')


# --- 4. MENGUBAH DATA BUKU (UPDATE) ---
def buku_update(request, id):
    # Ambil data lama buku dari database
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM buku WHERE id = %s", [id])
        buku = dictfetchone(cursor)

    if not buku:
        return redirect('buku_list')

    # Jika form di-submit (POST)
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        pengarang = request.POST.get('pengarang', '').strip()
        kategori = request.POST.get('kategori', '').strip()
        penerbit = request.POST.get('penerbit', '').strip()
        isbn = request.POST.get('isbn', '').strip()
        lokasi_rak = request.POST.get('lokasi_rak', '').strip()
        
        tahun_raw = request.POST.get('tahun_terbit', '').strip()
        tahun_terbit = int(tahun_raw) if tahun_raw.isdigit() else None

        stok_raw = request.POST.get('stok', '').strip()
        stok = int(stok_raw) if stok_raw.isdigit() else 0

        # --- PERBAIKAN QUERY UPDATE DI SINI ---
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE buku 
                SET judul = %s, pengarang = %s, kategori = %s, penerbit = %s, 
                    tahun_terbit = %s, stok = %s, isbn = %s, lokasi_rak = %s
                WHERE id = %s
            """, [judul, pengarang, kategori, penerbit, tahun_terbit, stok, isbn, lokasi_rak, id])
        
        return redirect('buku_list')

    # Saat diakses biasa (GET)
    return render(request, 'buku_update.html', {
        'buku': buku,
        'is_update': True
    })

# --- 5. MENGHAPUS DATA BUKU (DELETE) ---
def buku_delete(request, id):
    # Ambil data buku yang mau dihapus untuk konfirmasi
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, judul, pengarang
            FROM buku 
            WHERE id = %s
        """, [id])
        
        buku_data = dictfetchall(cursor)
        
        if not buku_data:
            return redirect('buku_list')
            
        buku = buku_data[0]

    # Proses eksekusi hapus jika tombol konfirmasi ditekan
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM buku 
                WHERE id = %s
            """, [id])
        
        return redirect('buku_list')

    return render(request, 'buku_delete.html', {
        'buku': buku
    })

# --- Tambahkan ini di views.py ---
# --- 1. DAFTAR PEMINJAM ---
def peminjam_list(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, nama_peminjam, buku, tanggal_pinjam, jatuh_tempo, keperluan, petugas, status, aksi 
            FROM peminjam
            ORDER BY id DESC
        """)
        data_peminjam = dictfetchall(cursor)
        search_text = "Daftar Peminjam"

    return render(request, 'peminjam_list.html', {
        'keyword': search_text,
        'data': data_peminjam,
    })


# --- 2. TAMBAH PEMINJAM (DENGAN OPSI USER DARI DATABASE) ---
def peminjam_create(request):
    # === PROSES 1: JIKA FORM DI-SUBMIT (POST) ===
    if request.method == 'POST':
        nama_peminjam = request.POST.get('nama_peminjam', '').strip()
        buku = request.POST.get('buku', '').strip()
        tanggal_pinjam = request.POST.get('tanggal_pinjam', '').strip() or None
        jatuh_tempo = request.POST.get('jatuh_tempo', '').strip() or None
        keperluan = request.POST.get('keperluan', '').strip()
        petugas = request.POST.get('petugas', '').strip()       
        status = request.POST.get('status', 'Dipinjam').strip()
        aksi = request.POST.get('aksi', 'Kontrol').strip()

        with connection.cursor() as cursor:
            # 1. Catat transaksi peminjaman baru
            cursor.execute(
                """
                INSERT INTO peminjam (nama_peminjam, buku, tanggal_pinjam, jatuh_tempo, keperluan, petugas, status, aksi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [nama_peminjam, buku, tanggal_pinjam, jatuh_tempo, keperluan, petugas, status, aksi]
            )
            
            # 2. Kurangi stok buku sebanyak 1 berdasarkan judul buku yang dipilih
            cursor.execute(
                """
                UPDATE buku 
                SET stok = stok - 1 
                WHERE judul = %s AND stok > 0
                """,
                [buku]
            )
            
        return redirect('peminjam_list')
    
    # === PROSES 2: JIKA AKSES HALAMAN FORM (GET) ===
    with connection.cursor() as cursor:
        # Ambil data semua buku untuk dropdown pilihan buku
        cursor.execute("SELECT judul, stok FROM buku ORDER BY judul ASC")
        data_buku = dictfetchall(cursor)
        
        # Ambil data semua anggota aktif untuk dropdown nama peminjam
        cursor.execute("SELECT nama FROM peminjam_anggota WHERE status = 'Aktif' ORDER BY nama ASC")
        daftar_user = dictfetchall(cursor)
    
    return render(request, 'peminjam_create.html', {
        'data': data_buku,
        'daftar_user': daftar_user
    })


# --- 3. KEMBALIKAN BUKU ---
def peminjam_kembali(request, id):
    with connection.cursor() as cursor:
        # 1. Cari tahu dulu judul buku apa yang sedang dipinjam berdasarkan ID transaksi
        cursor.execute("SELECT buku, status FROM peminjam WHERE id = %s", [id])
        transaksi = dictfetchone(cursor)
        
        # Validasi: Pastikan datanya ada dan statusnya memang masih 'Dipinjam'
        if transaksi and transaksi['status'] == 'Dipinjam':
            judul_buku = transaksi['buku']
            
            # 2. Update status transaksi peminjaman menjadi 'Dikembalikan'
            cursor.execute(
                """
                UPDATE peminjam 
                SET status = 'Dikembalikan', aksi = 'Kembali' 
                WHERE id = %s
                """, 
                [id]
            )
            
            # 3. Tambahkan kembali stok buku tersebut sebanyak 1 angka
            cursor.execute(
                """
                UPDATE buku 
                SET stok = stok + 1 
                WHERE judul = %s
                """, 
                [judul_buku]
            )
            
    # Kembalikan admin ke halaman daftar peminjam setelah berhasil
    return redirect('peminjam_list')


# --- 4. DAFTAR USER ---
def user_list(request):
     with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, nama, kelas, nis, status, aksi 
            FROM peminjam_anggota
            ORDER BY id DESC
        """)
        data_peminjaman = dictfetchall(cursor)
        search_text = "Daftar Peminjaman"

        return render(request, 'user_list.html', {
            'keyword': search_text,
            'data': data_peminjaman,
        })
     
def user_detail(request, id):
    with connection.cursor() as cursor:
        # 1. Ambil data profil dasar user beserta hitungan total & aktif menggunakan subquery
        cursor.execute(
            """
            SELECT id, nama, kelas, nis, status, aksi,
                   (SELECT COUNT(*) FROM peminjam WHERE nama_peminjam = peminjam_anggota.nama) as total_peminjaman,
                   (SELECT COUNT(*) FROM peminjam WHERE nama_peminjam = peminjam_anggota.nama AND status = 'Dipinjam') as peminjaman_aktif
            FROM peminjam_anggota
            WHERE id = %s
            """,
            [id]
        )
        user_data = dictfetchone(cursor) 

        # 2. Ambil list riwayat buku apa saja yang sedang atau pernah dipinjam siswa ini
        riwayat_buku = []
        if user_data:
            cursor.execute(
                """
                SELECT buku, tanggal_pinjam, jatuh_tempo, status 
                FROM peminjam 
                WHERE nama_peminjam = %s 
                ORDER BY id DESC
                """, 
                [user_data['nama']]
            )
            riwayat_buku = dictfetchall(cursor)

    return render(request, 'user_detail.html', {
        'user_siswa': user_data,   # Digunakan untuk data profil di HTML
        'user_data': user_data,    # Cadangan aman agar tidak terjadi error miss-match key
        'riwayat_buku': riwayat_buku,
    })     

def user_create(request):
    if request.method == 'POST':
        # Ambil data input dari form HTML sesuai nama field-nya
        nama = request.POST.get('nama', '').strip()
        kelas = request.POST.get('kelas', '').strip()
        nis = request.POST.get('nis', '').strip()
        status = request.POST.get('status', 'Aktif').strip()
        aksi = request.POST.get('aksi', 'Kontrol').strip()

        # Jalankan query SQL Raw untuk memasukkan data ke tabel database
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO peminjam_anggota (nama, kelas, nis, status, aksi)
                VALUES (%s, %s, %s, %s, %s)
                """,
                # Data dikirim berurutan sesuai tanda %s di atas
                [nama, kelas, nis, status, aksi]
            )

        # Setelah sukses menyimpan, lempar halaman kembali ke daftar user
        return redirect('user_list')
    
    # Jika method GET (akses halaman pertama kali), tampilkan form kosong
    return render(request, 'user_create.html')
# --- Sisanya fungsi user_update dan user_delete tetap sama seperti kode Anda ---
def user_update(request, id):
    # Ambal data lama user dari database berdasarkan ID
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nama, kelas, nis, status, aksi FROM peminjam_anggota WHERE id = %s", [id])
        user_siswa = dictfetchone(cursor)

    if not user_siswa:
        return redirect('user_list')

    # Jika form di-submit (POST)
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        kelas = request.POST.get('kelas', '').strip()
        nis = request.POST.get('nis', '').strip()
        status = request.POST.get('status', 'Aktif').strip()
        aksi = request.POST.get('aksi', 'Update Data').strip()

        # Eksekusi query UPDATE ke PostgreSQL
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE peminjam_anggota 
                SET nama = %s, kelas = %s, nis = %s, status = %s, aksi = %s
                WHERE id = %s
            """, [nama, kelas, nis, status, aksi, id])
        
        return redirect('user_list')

    # Saat diakses biasa (GET)
    return render(request, 'user_update.html', {
        'user_data': user_siswa
    })


def user_delete(request, id):
    # Ambal data user yang mau dihapus untuk konfirmasi di halaman hapus
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, nama, nis
            FROM peminjam_anggota 
            WHERE id = %s
        """, [id])
        
        user_data = dictfetchall(cursor)
        
        if not user_data:
            return redirect('user_list')
            
        user_siswa = user_data[0]

    # Proses eksekusi hapus jika tombol konfirmasi ditekan (POST)
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM peminjam_anggota 
                WHERE id = %s
            """, [id])
        
        return redirect('user_list')

    return render(request, 'user_delete.html', {
        'user_siswa': user_siswa
    })