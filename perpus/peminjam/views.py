from django.shortcuts import render, redirect
from django.db import connection, IntegrityError
from django.conf import settings
print(settings.DATABASES)

def dictfetchall(cursor):
    """Mengubah semua hasil query menjadi list of dictionaries (Aman Huruf Kecil)."""
    if cursor.description is None:
        return []
    columns = [col[0].lower() for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dictfetchone(cursor):
    """Mengubah satu hasil query menjadi dictionary (Aman Huruf Kecil)."""
    if cursor.description is None:
        return None
    columns = [col[0].lower() for col in cursor.description]
    row = cursor.fetchone()
    if row is None:
        return None
    return dict(zip(columns, row))


# ==========================================
# --- 1. KELOMPOK MANAJEMEN BUKU ---
# ==========================================

def buku_list(request):
    query_cari = request.GET.get('buku', '').strip()
    with connection.cursor() as cursor:
        if query_cari:
            cursor.execute("""
                SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, stok, isbn, rak
                FROM buku
                WHERE judul LIKE %s OR pengarang LIKE %s
                ORDER BY id DESC
            """, [f'%{query_cari}%', f'%{query_cari}%'])
            search_text = f"Hasil Pencarian: '{query_cari}'"
        else:
            cursor.execute("""
                SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, stok, isbn, rak
                FROM buku
                ORDER BY id DESC
            """)
            search_text = "Katalog Buku"
        raw_data = dictfetchall(cursor)
        
        data_buku = []
        for row in raw_data:
            data_buku.append({
                'id': row.get('id'),
                'judul': row.get('judul', ''),
                'pengarang': row.get('pengarang', ''),
                'kategori': row.get('kategori', ''),
                'penerbit': row.get('penerbit', ''),
                'tahun_terbit': row.get('tahun_terbit', ''),
                'stok': row.get('stok', 0),
                'isbn': row.get('isbn', ''),
                'rak': row.get('rak', ''),
                'lokasi_rak': row.get('rak', ''),
            })

    return render(request, 'buku_list.html', {
        'keyword': search_text,
        'data': data_buku,
        'query_sekarang': query_cari,
    })

def buku_detail(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM buku WHERE id = %s", [id])
        buku = dictfetchone(cursor)    
    return render(request, 'buku_detail.html', {'buku': buku})

def buku_create(request):
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        pengarang = request.POST.get('pengarang', '').strip()
        kategori = request.POST.get('kategori', '').strip()
        penerbit = request.POST.get('penerbit', '').strip()
        stok_raw = request.POST.get('stok', '').strip()
        stok = int(stok_raw) if stok_raw.isdigit() else 0
        rak = request.POST.get('lokasi_rak', '').strip() or request.POST.get('rak', '').strip()
        
        tahun_raw = request.POST.get('tahun_terbit', '').strip()
        tahun_terbit = int(tahun_raw) if tahun_raw.isdigit() else None

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO buku (judul, pengarang, kategori, penerbit, tahun_terbit, stok, rak)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [judul, pengarang, kategori, penerbit, tahun_terbit, stok, rak])

        return redirect('buku_list')
    return render(request, 'buku_create.html')

def buku_update(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM buku WHERE id = %s", [id])
        buku_raw = dictfetchone(cursor)

    if not buku_raw:
        return redirect('buku_list')

    # BUAT COPY DAN TAMBAHKAN KUNCI LOKASI_RAK DI SINI UNTUK MENGAMANKAN TEMPLATE HTML
    buku = dict(buku_raw)
    buku['lokasi_rak'] = buku_raw.get('rak', '')
    buku['deskripsi'] = buku_raw.get('deskripsi', '')

    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        pengarang = request.POST.get('pengarang', '').strip()
        kategori = request.POST.get('kategori', '').strip()
        penerbit = request.POST.get('penerbit', '').strip()
        isbn = request.POST.get('isbn', '').strip()
        rak = request.POST.get('lokasi_rak', '').strip() or request.POST.get('rak', '').strip()
        
        tahun_raw = request.POST.get('tahun_terbit', '').strip()
        tahun_terbit = int(tahun_raw) if tahun_raw.isdigit() else None
        stok_raw = request.POST.get('stok', '').strip()
        stok = int(stok_raw) if stok_raw.isdigit() else 0

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE buku 
                SET judul = %s, pengarang = %s, kategori = %s, penerbit = %s, 
                    tahun_terbit = %s, stok = %s, isbn = %s, rak = %s
                WHERE id = %s
            """, [judul, pengarang, kategori, penerbit, tahun_terbit, stok, isbn, rak, id])
        return redirect('buku_list')

    return render(request, 'buku_update.html', {'buku': buku, 'is_update': True})

def buku_delete(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, judul, pengarang FROM buku WHERE id = %s", [id])
        buku_data = dictfetchall(cursor)
        if not buku_data:
            return redirect('buku_list')
        buku = buku_data[0]

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM buku WHERE id = %s", [id])
        return redirect('buku_list')

    return render(request, 'buku_delete.html', {'buku': buku})


# ==========================================
# --- 2. KELOMPOK MANAJEMEN PEMINJAM ---
# ==========================================

def peminjam_list(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, nama, buku, tgl_pinjam, tgl_kembali
            FROM peminjam
            ORDER BY id DESC
        """)
        raw_data = dictfetchall(cursor)
        
        data_peminjam = []
        for row in raw_data:
            data_peminjam.append({
                'id': row.get('id'),
                'nama_peminjam': row.get('nama'),
                'buku': row.get('buku'),
                'tanggal_pinjam': row.get('tgl_pinjam'),
                'jatuh_tempo': row.get('tgl_kembali'),
                'keperluan': 'Membaca',
                'petugas': 'Admin',
                'status': 'Dipinjam',
                'aksi': 'Kontrol'
            })

    return render(request, 'peminjam_list.html', {
        'keyword': "Daftar Peminjam",
        'data': data_peminjam,
    })

def peminjam_create(request):
    if request.method == 'POST':
        nama_peminjam = request.POST.get('nama_peminjam', '').strip()
        buku = request.POST.get('buku', '').strip()
        tanggal_pinjam = request.POST.get('tanggal_pinjam', '').strip() or None
        jatuh_tempo = request.POST.get('jatuh_tempo', '').strip() or None

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO peminjam (nama, buku, tgl_pinjam, tgl_kembali)
                VALUES (%s, %s, %s, %s)
            """, [nama_peminjam, buku, tanggal_pinjam, jatuh_tempo])
            
            cursor.execute("""
                UPDATE buku 
                SET stok = stok - 1 
                WHERE judul = %s AND stok > 0
            """, [buku])
            
        return redirect('peminjam_list')
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT judul, stok FROM buku ORDER BY judul ASC")
        data_buku = dictfetchall(cursor)
        
        cursor.execute("SELECT nama FROM peminjam_anggota ORDER BY nama ASC")
        daftar_user = dictfetchall(cursor)
    
    return render(request, 'peminjam_create.html', {
        'data': data_buku,
        'daftar_user': daftar_user
    })

def peminjam_kembali(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT buku FROM peminjam WHERE id = %s", [id])
        transaksi = dictfetchone(cursor)
        
        if transaksi:
            judul_buku = transaksi['buku']
            cursor.execute("DELETE FROM peminjam WHERE id = %s", [id])
            cursor.execute("UPDATE buku SET stok = stok + 1 WHERE judul = %s", [judul_buku])
            
    return redirect('peminjam_list')


# ==========================================
# --- 3. KELOMPOK MANAJEMEN USER / ANGGOTA ---
# ==========================================

def user_list(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, nama, kelas, nis 
            FROM peminjam_anggota
            ORDER BY id DESC
        """)
        raw_data = dictfetchall(cursor)
        
        data_peminjaman = []
        for row in raw_data:
            data_peminjaman.append({
                'id': row.get('id'),
                'nama': row.get('nama'),
                'kelas': row.get('kelas'),
                'nis': row.get('nis'),
                'status': row.get('status') or 'Aktif',
                'aksi': 'Kontrol'
            })

        return render(request, 'user_list.html', {
            'keyword': "Daftar Peminjaman",
            'data': data_peminjaman,
        })
     
def user_detail(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nama, kelas, nis FROM peminjam_anggota WHERE id = %s", [id])
        user_data = dictfetchone(cursor) 

        riwayat_buku = []
        if user_data:
            cursor.execute("""
                SELECT buku, tgl_pinjam as tanggal_pinjam, tgl_kembali as jatuh_tempo 
                FROM peminjam 
                WHERE nama = %s 
                ORDER BY id DESC
            """, [user_data['nama']])
            riwayat_buku = dictfetchall(cursor)

            user_data['status'] = 'Aktif'
            user_data['total_peminjaman'] = len(riwayat_buku)
            user_data['peminjaman_aktif'] = len(riwayat_buku)

    return render(request, 'user_detail.html', {
        'user_siswa': user_data,
        'user_data': user_data,
        'riwayat_buku': riwayat_buku,
    })     

def user_create(request):
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        kelas = request.POST.get('kelas', '').strip()
        nis = request.POST.get('nis', '').strip()

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO peminjam_anggota (nama, kelas, nis)
                    VALUES (%s, %s, %s)
                """, [nama, kelas, nis])
            return redirect('user_list')
        except IntegrityError:
            return render(request, 'user_create.html', {
                'error_message': 'Gagal Simpan! NIS tersebut sudah terdaftar.',
                'nama': nama, 'kelas': kelas, 'nis': nis
            })
            
    return render(request, 'user_create.html')

def user_update(request, id):
    with connection.cursor() as cursor:
        # Ambil data user beserta statusnya dari PostgreSQL
        cursor.execute("SELECT id, nama, kelas, nis, status FROM peminjam_anggota WHERE id = %s", [id])
        user_siswa = dictfetchone(cursor)

    if not user_siswa:
        return redirect('user_list')

    # Bungkus ke dictionary murni untuk dikirim ke HTML
    user_data = {
        'id': user_siswa.get('id'),
        'nama': user_siswa.get('nama'),
        'kelas': user_siswa.get('kelas'),
        'nis': user_siswa.get('nis'),
        'status': user_siswa.get('status') or 'Aktif',  # Default 'Aktif' jika null
        'aksi': 'Kontrol'
    }

    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        kelas = request.POST.get('kelas', '').strip()
        nis = request.POST.get('nis', '').strip()
        status = request.POST.get('status', '').strip()  # <-- Menangkap pilihan status dari HTML

        with connection.cursor() as cursor:
            # Simpan perubahan termasuk status baru ke PostgreSQL
            cursor.execute("""
                UPDATE peminjam_anggota 
                SET nama = %s, kelas = %s, nis = %s, status = %s
                WHERE id = %s
            """, [nama, kelas, nis, status, id])
        
        return redirect('user_list')

    return render(request, 'user_update.html', {
        'user_data': user_data
    })

def user_delete(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nama, nis FROM peminjam_anggota WHERE id = %s", [id])
        user_data = dictfetchall(cursor)
        
        if not user_data:
            return redirect('user_list')
        user_siswa = user_data[0]

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM peminjam_anggota WHERE id = %s", [id])
        return redirect('user_list')

    return render(request, 'user_delete.html', {
        'user_siswa': user_siswa
    })