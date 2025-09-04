Aplikasi Editor Gambar
Aplikasi desktop sederhana berbasis Python yang dikembangkan menggunakan customtkinter dan Pillow. Aplikasi ini memiliki dua fitur utama:

Penghapus Background: Menghilangkan background dari gambar dan memotongnya secara otomatis.

Pengubah Ukuran Gambar: Mengubah ukuran gambar secara massal atau satu per satu.

Prasyarat
Sebelum menjalankan aplikasi, pastikan Anda telah menginstal Python 3.x di sistem operasi Windows Anda.

Instalasi
Ikuti langkah-langkah berikut untuk menginstal dan menjalankan aplikasi.

1. Klon Repositori
Buka Command Prompt atau PowerShell dan klon repositori ini ke komputer Anda:



2. Pindah ke Direktori Proyek
Masuk ke folder proyek yang baru saja Anda klon:

cd aplikasi-editor-gambar

3. Instalasi Pustaka (Libraries) yang Dibutuhkan
Aplikasi ini bergantung pada beberapa pustaka Python. Instal semua pustaka tersebut menggunakan pip:

pip install customtkinter
pip install Pillow
pip install rembg

4. Menjalankan Aplikasi
Setelah semua pustaka terinstal, Anda dapat menjalankan aplikasi dengan perintah berikut:

python main.py

Aplikasi akan terbuka dalam jendela baru, dan Anda siap menggunakannya.

Fitur
Hapus Background:

Pilih mode Satu File atau Mode Batch.

Atur nilai threshold untuk mengontrol transparansi piksel.

Aplikasi akan menyimpan gambar tanpa background dalam format PNG.

Ubah Ukuran Gambar:

Pilih mode Satu File atau Mode Batch.

Masukkan ukuran lebar dan tinggi yang Anda inginkan.

Aplikasi akan mengubah ukuran gambar dan menyimpannya ke folder yang Anda tentukan.