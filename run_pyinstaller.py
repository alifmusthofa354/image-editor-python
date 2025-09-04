import PyInstaller.__main__
import os
import shutil

# --- Konfigurasi ---
# Nama file Python utama Anda
main_script = 'main.py'
# Nama file ikon Anda saat ini
icon_file = 'app_icon.ico'
# Nama file ikon yang akan digunakan oleh CustomTkinter
# Ini adalah nama yang dicari oleh CustomTkinter secara default untuk ikon jendela Windows.
ctk_icon_name = 'CustomTkinter_icon_Windows.ico'
# Ganti dengan JALUR LENGKAP ke folder 'customtkinter' di virtual environment Anda.
# Contoh: 'C:\\project\\project\\image-editor-python\\.venv\\Lib\\site-packages\\customtkinter'
path_to_customtkinter = 'C:\\project\\project\\image-editor-python\\.venv\\Lib\\site-packages\\customtkinter'

# --- Persiapan ---
# 1. Pastikan file ikon ada dan salin/ganti namanya
if os.path.exists(icon_file):
    shutil.copyfile(icon_file, ctk_icon_name)
    print(f"Mengganti nama {icon_file} menjadi {ctk_icon_name}")
else:
    print(f"Error: File {icon_file} tidak ditemukan di direktori proyek.")
    exit()

# 2. Pastikan jalur ke CustomTkinter valid
if not os.path.exists(path_to_customtkinter):
    print(f"Error: Jalur ke CustomTkinter tidak valid. Pastikan Anda mengganti 'path_to_customtkinter' dengan jalur yang benar.")
    exit()

# --- Menjalankan PyInstaller ---
print("\nMemulai proses PyInstaller...")
print("Ini mungkin butuh waktu beberapa menit. Harap tunggu...")
# Perintah PyInstaller dijalankan di dalam skrip
PyInstaller.__main__.run([
    main_script,
    '--onefile',
    '--windowed',
    '--name', 'Image Editor Python',
    '--icon', ctk_icon_name,
    '--add-data', f'{ctk_icon_name};assets/icons',
    '--add-data', f'{path_to_customtkinter};customtkinter'
])

print("\nProses build PyInstaller selesai.")
