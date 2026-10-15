import sqlite3
import streamlit as st

# --- KONSTANTA & INISIALISASI DATABASE ---
DB_NAME = "kitab_kuning.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  # Tabel Kategori / Fan Ilmu
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS kategori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_fan TEXT UNIQUE NOT NULL
        )
    """)

  # Tabel Kitab
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS kitab (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            judul TEXT NOT NULL,
            pengarang TEXT,
            kategori_id INTEGER,
            tingkatan TEXT,
            FOREIGN KEY (kategori_id) REFERENCES kategori (id)
        )
    """)

  # Tabel Isi / Bab Kitab
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS isi_kitab (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kitab_id INTEGER,
            bab TEXT,
            teks_arab TEXT,
            terjemahan TEXT,
            FOREIGN KEY (kitab_id) REFERENCES kitab (id)
        )
    """)

  conn.commit()

  # Masukkan data dummy jika tabel masih kosong
  cursor.execute("SELECT COUNT(*) FROM kategori")
  if cursor.fetchone()[0] == 0:
    # Kategori
    cursor.executemany(
        "INSERT INTO kategori (nama_fan) VALUES (?)",
        [("Fiqih",), ("Nahwu & Shorof",), ("Akhlak & Tasawuf",), ("Hadits",)],
    )

    # Kitab Dummy
    cursor.executemany(
        """INSERT INTO kitab (judul, pengarang, kategori_id, tingkatan) VALUES (?, ?, ?, ?)""",
        [
            (
                "Fathul Qarib",
                "Syeikh Muhammad bin Qasim al-Ghazi",
                1,
                "Menengah",
            ),
            ("Imriti", "Syeikh Syarifuddin Yahya al-Imriti", 2, "Pemula"),
            ("Ta'lim Muta'allim", "Syeikh Az-Zarnuji", 3, "Pemula"),
        ],
    )

    # Isi Kitab Dummy
    cursor.executemany(
        """INSERT INTO isi_kitab (kitab_id, bab, teks_arab, terjemahan) VALUES (?, ?, ?, ?)""",
        [
            (
                1,
                "Bab Thaharah (Bersuci)",
                "فَصْلٌ: الْمِيَاهُ الَّتِي يَجُوْزُ بِهَا الطَّهَارَةُ سَبْعُ مِيَاهٍ...",
                (
                    "Pasal: Air yang sah digunakan untuk bersuci ada tujuh"
                    " macam..."
                ),
            ),
            (
                2,
                "Bab Kalam",
                (
                    "كَلَامُنَا لَفْظٌ مُفِيْدٌ كَاسْتَقِمْ... وَاسْمٌ"
                    " وَفِعْلٌ ثُمَّ حَرْفٌ الْكَلِمْ"
                ),
                (
                    "Kalam kami adalah lafaz yang berfaedah (bisa dipahami)"
                    " seperti 'Istaqim'..."
                ),
            ),
            (
                3,
                "Bab Niat Belajar",
                (
                    "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ. قَالَ الشَّيْخُ"
                    " الإِمَامُ الأَجَلُ بُرْهَانُ الإِسْلَامِ..."
                ),
                (
                    "Dengan nama Allah Yang Maha Pengasih lagi Maha Penyayang."
                    " Berkata Syeikh al-Imam Burhanul Islam..."
                ),
            ),
        ],
    )
    conn.commit()

  conn.close()


# --- APLIKASI UTAMA STREAMLIT ---
def main():
  st.set_page_config(
      page_title="Perpustakaan Kitab Kuning", page_icon="📚", layout="wide"
  )
  init_db()

  st.title("📚 Perpustakaan Digital Kitab Kuning Terlengkap")
  st.write(
      "Platform referensi turats digital berbasis arsitektur logika terstruktur."
  )

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  # Sidebar Navigasi
  menu = st.selectbox(
      "Pilih Menu", ["Katalog Kitab", "Pencarian Pintar", "Tambah Kitab Baru"]
  )

  if menu == "Katalog Kitab":
    st.subheader("📖 Daftar Kitab Berdasarkan Fan Ilmu")

    # Ambil kategori
    cursor.execute("SELECT id, nama_fan FROM kategori")
    kategori_list = cursor.fetchall()
    kategori_dict = {nama: kid for kid, nama in kategori_list}

    pilihan_fan = st.selectbox("Pilih Fan Ilmu", ["Semua"] + list(kategori_dict.keys()))

    if pilihan_fan == "Semua":
      cursor.execute("""
                SELECT kitab.id, kitab.judul, kitab.pengarang, kategori.nama_fan, kitab.tingkatan 
                FROM kitab JOIN kategori ON kitab.kategori_id = kategori.id
            """)
    else:
      kid = kategori_dict[pilihan_fan]
      cursor.execute(
          """
                SELECT kitab.id, kitab.judul, kitab.pengarang, kategori.nama_fan, kitab.tingkatan 
                FROM kitab JOIN kategori ON kitab.kategori_id = kategori.id 
                WHERE kitab.kategori_id = ?
            """,
          (kid,),
      )

    kitab_data = cursor.fetchall()

    for k in kitab_data:
      with st.expander(f"📘 {k[1]} — (Pengarang: {k[2]})"):
        st.write(f"**Fan Ilmu:** {k[3]} | **Tingkatan:** {k[4]}")

        # Ambil isi teks kitab
        cursor.execute(
            "SELECT bab, teks_arab, terjemahan FROM isi_kitab WHERE kitab_id ="
            " ?",
            (k[0],),
        )
        isinya = cursor.fetchall()
        for isi in isinya:
          st.markdown(f"### {isi[0]}")
          st.info(f"**Teks Arab:**\n\n{isi[1]}")
          st.success(f"**Terjemahan:**\n\n{isi[2]}")

  elif menu == "Pencarian Pintar":
    st.subheader("🔍 Cari Kitab atau Kata Kunci")
    keyword = st.text_input(
        "Masukkan judul kitab atau kata kunci terjemahan:"
    )

    if keyword:
      cursor.execute(
          """
                SELECT kitab.judul, isi_kitab.bab, isi_kitab.teks_arab, isi_kitab.terjemahan 
                FROM isi_kitab JOIN kitab ON isi_kitab.kitab_id = kitab.id 
                WHERE kitab.judul LIKE ? OR isi_kitab.terjemahan LIKE ? OR isi_kitab.teks_arab LIKE ?
            """,
          (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
      )
      hasil = cursor.fetchall()

      if hasil:
        st.success(f"Ditemukan {len(hasil)} hasil pencarian:")
        for h in hasil:
          st.markdown(f"**Kitab:** {h[0]} | **Bab:** {h[1]}")
          st.text(f"Arab: {h[2]}")
          st.write(f"Terjemah: {h[3]}")
          st.divider()
      else:
        st.warning("Data tidak ditemukan.")

  elif menu == "Tambah Kitab Baru":
    st.subheader("➕ Tambah Koleksi Kitab")
    judul_baru = st.text_input("Judul Kitab")
    pengarang_baru = st.text_input("Pengarang / Mushannif")

    cursor.execute("SELECT nama_fan FROM kategori")
    cats = [c[0] for c in cursor.fetchall()]
    fan_pilihan = st.selectbox("Fan Ilmu", cats)
    tingkat_pilihan = st.selectbox(
        "Tingkatan", ["Pemula", "Menengah", "Lanjutan"]
    )

    bab_baru = st.text_input("Nama Bab")
    arab_baru = st.text_area("Teks Arab")
    terjemahan_baru = st.text_area("Terjemahan / Penjelasan")

    if st.button("Simpan Kitab"):
      if judul_baru and bab_baru:
        cursor.execute(
            "SELECT id FROM kategori WHERE nama_fan = ?", (fan_pilihan,)
        )
        kid = cursor.fetchone()[0]

        cursor.execute(
            """INSERT INTO kitab (judul, pengarang, kategori_id, tingkatan) VALUES (?, ?, ?, ?)""",
            (judul_baru, pengarang_baru, kid, tingkat_pilihan),
        )
        kitab_id_baru = cursor.lastrowid

        cursor.execute(
            """INSERT INTO isi_kitab (kitab_id, bab, teks_arab, terjemahan) VALUES (?, ?, ?, ?)""",
            (kitab_id_baru, bab_baru, arab_baru, terjemahan_baru),
        )
        conn.commit()
        st.success("Kitab berhasil ditambahkan ke database!")
      else:
        st.error("Mohon isi judul dan bab dengan lengkap.")

  conn.close()


if __name__ == "__main__":
  main()
