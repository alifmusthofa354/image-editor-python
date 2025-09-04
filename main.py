import customtkinter
from tkinter import filedialog
from rembg import remove
from PIL import Image
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def remove_background_and_autocrop_enhanced(input_path, output_path, alpha_threshold=15):
    """
    Menghilangkan background dan memotong area transparan berlebih dari sebuah gambar.
    """
    try:
        input_image = Image.open(input_path)
        image_without_bg = remove(input_image)
        image_without_bg = image_without_bg.convert("RGBA")
        
        pixels = image_without_bg.load()
        width, height = image_without_bg.size

        for x in range(width):
            for y in range(height):
                r, g, b, a = pixels[x, y]
                if a < alpha_threshold:
                    pixels[x, y] = (0, 0, 0, 0)

        bbox = image_without_bg.getbbox()
        
        if bbox:
            cropped_image = image_without_bg.crop(bbox)
            cropped_image.save(output_path)
            return True
        else:
            return False

    except FileNotFoundError:
        print(f"File not found: {input_path}")
        return False
    except Exception as e:
        print(f"Error processing image {input_path}: {e}")
        return False

def resize_image_and_save(input_path, output_path, new_width, new_height):
    """
    Mengubah ukuran gambar dan menyimpannya ke jalur output.
    """
    try:
        with Image.open(input_path) as img:
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            resized_img.save(output_path)
            return True
    except FileNotFoundError:
        print(f"File not found: {input_path}")
        return False
    except Exception as e:
        print(f"Error resizing image {input_path}: {e}")
        return False

def compress_image_and_save(input_path, output_path, quality, file_format):
    """
    Mengkompres gambar dan menyimpannya dengan format tertentu.
    """
    try:
        with Image.open(input_path) as img:
            # Konversi gambar ke RGB jika format output tidak mendukung transparansi
            if img.mode in ('RGBA', 'P') and file_format in ['JPEG', 'JPG', 'BMP']:
                img = img.convert('RGB')

            # Atur parameter kualitas, hanya berlaku untuk JPEG dan WebP
            params = {}
            if file_format in ['JPEG', 'WEBP']:
                params['quality'] = quality
            
            # Khusus untuk PNG, gunakan optimize
            if file_format == 'PNG':
                params['optimize'] = True
                params['compress_level'] = int(quality / 10) # Skala 1-9 dari kualitas 0-100
            
            # Ubah ekstensi file jika format output berbeda
            base, _ = os.path.splitext(output_path)
            output_path_with_ext = f"{base}.{file_format.lower()}"

            img.save(output_path_with_ext, format=file_format, **params)
            return True
    except Exception as e:
        print(f"Error compressing image {input_path}: {e}")
        return False


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Konfigurasi jendela utama
        self.title("Image Editor Python")
        self.geometry("600x600")
        self.grid_columnconfigure(0, weight=1)

        # BARIS INI DITAMBAHKAN UNTUK MENGATUR IKON JENDELA
        # Pastikan Anda memiliki file app_icon.ico di folder yang sama
        # BARIS INI ADALAH PERBAIKANNYA
        try:
            # Gunakan resource_path dengan jalur yang benar
            self.iconbitmap(resource_path(os.path.join('assets', 'icons', 'CustomTkinter_icon_Windows.ico')))
        except Exception as e:
            # Opsional: Cetak error untuk debugging (saat di mode dev)
            print(f"Error saat mengatur ikon: {e}")
            pass
        
        # Buat tabview untuk menampung fitur
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Buat tab untuk fitur Hapus Background
        self.tab_bg = self.tabview.add("Hapus Background")
        self.tab_bg.grid_columnconfigure(0, weight=1)

        # Buat tab untuk fitur Ubah Ukuran Gambar
        self.tab_resize = self.tabview.add("Ubah Ukuran Gambar")
        self.tab_resize.grid_columnconfigure(0, weight=1)

        # Buat tab baru untuk fitur Kompres Gambar
        self.tab_compress = self.tabview.add("Kompres Gambar")
        self.tab_compress.grid_columnconfigure(0, weight=1)

        # --- UI untuk Tab Hapus Background ---
        self.setup_background_tab(self.tab_bg)

        # --- UI untuk Tab Ubah Ukuran Gambar ---
        self.setup_resize_tab(self.tab_resize)
        
        # --- UI untuk Tab Kompres Gambar ---
        self.setup_compress_tab(self.tab_compress)

    def setup_background_tab(self, tab):
        self.bg_mode_var = customtkinter.StringVar(value="single")
        self.bg_mode_label = customtkinter.CTkLabel(tab, text="Pilih mode:")
        self.bg_mode_label.grid(row=0, column=0, pady=(10, 0), padx=20, sticky="w")
        
        self.bg_single_mode_radio = customtkinter.CTkRadioButton(tab, text="Satu File", variable=self.bg_mode_var, value="single", command=lambda: self.update_bg_ui(tab))
        self.bg_single_mode_radio.grid(row=1, column=0, pady=(0, 5), padx=20, sticky="w")
        
        self.bg_batch_mode_radio = customtkinter.CTkRadioButton(tab, text="Mode Batch (Folder)", variable=self.bg_mode_var, value="batch", command=lambda: self.update_bg_ui(tab))
        self.bg_batch_mode_radio.grid(row=2, column=0, pady=(0, 10), padx=20, sticky="w")

        self.bg_input_label = customtkinter.CTkLabel(tab, text="Pilih gambar input:")
        self.bg_input_label.grid(row=3, column=0, pady=(10, 0), padx=20, sticky="w")
        self.bg_input_entry = customtkinter.CTkEntry(tab, placeholder_text="Jalur file input")
        self.bg_input_entry.grid(row=4, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        self.bg_select_button = customtkinter.CTkButton(tab, text="Pilih Gambar", command=lambda: self.select_files(tab, "bg"))
        self.bg_select_button.grid(row=5, column=0, pady=5, padx=20, sticky="ew")

        self.bg_threshold_label = customtkinter.CTkLabel(tab, text="Pengaturan Threshold:")
        self.bg_threshold_label.grid(row=6, column=0, pady=(10, 0), padx=20, sticky="w")
        
        self.bg_threshold_value_label = customtkinter.CTkLabel(tab, text="Nilai: 15")
        self.bg_threshold_value_label.grid(row=7, column=0, pady=(5, 0), padx=20, sticky="w")

        self.bg_threshold_slider = customtkinter.CTkSlider(master=tab, from_=0, to=255, number_of_steps=256, command=self.update_threshold_label)
        self.bg_threshold_slider.grid(row=8, column=0, pady=(0, 10), padx=20, sticky="ew")
        self.bg_threshold_slider.set(15)

        self.bg_process_button = customtkinter.CTkButton(tab, text="Hapus Background dan Potong", command=lambda: self.process_image(tab, "bg"), fg_color="#3B82F6")
        self.bg_process_button.grid(row=9, column=0, pady=10, padx=20, sticky="ew")

        self.bg_status_label = customtkinter.CTkLabel(tab, text="", text_color="green", font=("Roboto", 14))
        self.bg_status_label.grid(row=10, column=0, pady=(10, 20), padx=20)

    def setup_resize_tab(self, tab):
        self.resize_mode_var = customtkinter.StringVar(value="single")
        self.resize_mode_label = customtkinter.CTkLabel(tab, text="Pilih mode:")
        self.resize_mode_label.grid(row=0, column=0, pady=(10, 0), padx=20, sticky="w")
        
        self.resize_single_mode_radio = customtkinter.CTkRadioButton(tab, text="Satu File", variable=self.resize_mode_var, value="single", command=lambda: self.update_resize_ui(tab))
        self.resize_single_mode_radio.grid(row=1, column=0, pady=(0, 5), padx=20, sticky="w")
        
        self.resize_batch_mode_radio = customtkinter.CTkRadioButton(tab, text="Mode Batch (Folder)", variable=self.resize_mode_var, value="batch", command=lambda: self.update_resize_ui(tab))
        self.resize_batch_mode_radio.grid(row=2, column=0, pady=(0, 10), padx=20, sticky="w")

        self.resize_input_label = customtkinter.CTkLabel(tab, text="Pilih gambar input:")
        self.resize_input_label.grid(row=3, column=0, pady=(10, 0), padx=20, sticky="w")
        self.resize_input_entry = customtkinter.CTkEntry(tab, placeholder_text="Jalur file input")
        self.resize_input_entry.grid(row=4, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        self.resize_select_button = customtkinter.CTkButton(tab, text="Pilih Gambar", command=lambda: self.select_files(tab, "resize"))
        self.resize_select_button.grid(row=5, column=0, pady=5, padx=20, sticky="ew")

        self.size_frame = customtkinter.CTkFrame(tab)
        self.size_frame.grid(row=6, column=0, pady=10, padx=20, sticky="ew")
        self.size_frame.grid_columnconfigure(0, weight=1)
        self.size_frame.grid_columnconfigure(1, weight=1)

        self.width_label = customtkinter.CTkLabel(self.size_frame, text="Lebar (px):")
        self.width_label.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="w")
        self.width_entry = customtkinter.CTkEntry(self.size_frame, placeholder_text="misal: 128")
        self.width_entry.grid(row=1, column=0, pady=(0, 10), padx=10, sticky="ew")

        self.height_label = customtkinter.CTkLabel(self.size_frame, text="Tinggi (px):")
        self.height_label.grid(row=0, column=1, pady=(10, 0), padx=10, sticky="w")
        self.height_entry = customtkinter.CTkEntry(self.size_frame, placeholder_text="misal: 128")
        self.height_entry.grid(row=1, column=1, pady=(0, 10), padx=10, sticky="ew")

        self.resize_process_button = customtkinter.CTkButton(tab, text="Ubah Ukuran Gambar", command=lambda: self.process_image(tab, "resize"), fg_color="#3B82F6")
        self.resize_process_button.grid(row=7, column=0, pady=10, padx=20, sticky="ew")

        self.resize_status_label = customtkinter.CTkLabel(tab, text="", text_color="green", font=("Roboto", 14))
        self.resize_status_label.grid(row=8, column=0, pady=(10, 20), padx=20)

    def setup_compress_tab(self, tab):
        self.compress_mode_var = customtkinter.StringVar(value="single")
        self.compress_mode_label = customtkinter.CTkLabel(tab, text="Pilih mode:")
        self.compress_mode_label.grid(row=0, column=0, pady=(10, 0), padx=20, sticky="w")
        
        self.compress_single_mode_radio = customtkinter.CTkRadioButton(tab, text="Satu File", variable=self.compress_mode_var, value="single", command=lambda: self.update_compress_ui(tab))
        self.compress_single_mode_radio.grid(row=1, column=0, pady=(0, 5), padx=20, sticky="w")
        
        self.compress_batch_mode_radio = customtkinter.CTkRadioButton(tab, text="Mode Batch (Folder)", variable=self.compress_mode_var, value="batch", command=lambda: self.update_compress_ui(tab))
        self.compress_batch_mode_radio.grid(row=2, column=0, pady=(0, 10), padx=20, sticky="w")

        self.compress_input_label = customtkinter.CTkLabel(tab, text="Pilih gambar input:")
        self.compress_input_label.grid(row=3, column=0, pady=(10, 0), padx=20, sticky="w")
        self.compress_input_entry = customtkinter.CTkEntry(tab, placeholder_text="Jalur file input")
        self.compress_input_entry.grid(row=4, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        self.compress_select_button = customtkinter.CTkButton(tab, text="Pilih Gambar", command=lambda: self.select_files(tab, "compress"))
        self.compress_select_button.grid(row=5, column=0, pady=5, padx=20, sticky="ew")

        self.quality_frame = customtkinter.CTkFrame(tab)
        self.quality_frame.grid(row=6, column=0, pady=10, padx=20, sticky="ew")
        self.quality_frame.grid_columnconfigure(0, weight=1)
        self.quality_frame.grid_columnconfigure(1, weight=1)

        self.quality_label = customtkinter.CTkLabel(self.quality_frame, text="Kualitas Kompresi (0-100):")
        self.quality_label.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="w")
        self.quality_value_label = customtkinter.CTkLabel(self.quality_frame, text="Nilai: 80")
        self.quality_value_label.grid(row=0, column=1, pady=(10, 0), padx=10, sticky="e")
        
        self.quality_slider = customtkinter.CTkSlider(self.quality_frame, from_=0, to=100, number_of_steps=101, command=self.update_quality_label)
        self.quality_slider.grid(row=1, column=0, columnspan=2, pady=(0, 10), padx=10, sticky="ew")
        self.quality_slider.set(80)

        self.format_label = customtkinter.CTkLabel(tab, text="Pilih Format Output:")
        self.format_label.grid(row=7, column=0, pady=(10, 0), padx=20, sticky="w")
        self.format_option_menu = customtkinter.CTkOptionMenu(tab, values=["JPEG", "PNG", "WEBP", "ICO", "BMP"])
        self.format_option_menu.grid(row=8, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        self.compress_process_button = customtkinter.CTkButton(tab, text="Kompres Gambar", command=lambda: self.process_image(tab, "compress"), fg_color="#3B82F6")
        self.compress_process_button.grid(row=9, column=0, pady=10, padx=20, sticky="ew")

        self.compress_status_label = customtkinter.CTkLabel(tab, text="", text_color="green", font=("Roboto", 14))
        self.compress_status_label.grid(row=10, column=0, pady=(10, 20), padx=20)


    def update_bg_ui(self, tab):
        current_mode = self.bg_mode_var.get()
        if current_mode == "single":
            self.bg_select_button.configure(text="Pilih Gambar Input")
            self.bg_input_entry.configure(placeholder_text="Jalur file input")
        else:
            self.bg_select_button.configure(text="Pilih Folder Input")
            self.bg_input_entry.configure(placeholder_text="Jalur folder input")
        
        self.bg_input_entry.delete(0, customtkinter.END)
        self.bg_status_label.configure(text="")

    def update_resize_ui(self, tab):
        current_mode = self.resize_mode_var.get()
        if current_mode == "single":
            self.resize_select_button.configure(text="Pilih Gambar Input")
            self.resize_input_entry.configure(placeholder_text="Jalur file input")
        else:
            self.resize_select_button.configure(text="Pilih Folder Input")
            self.resize_input_entry.configure(placeholder_text="Jalur folder input")
        
        self.resize_input_entry.delete(0, customtkinter.END)
        self.resize_status_label.configure(text="")

    def update_compress_ui(self, tab):
        current_mode = self.compress_mode_var.get()
        if current_mode == "single":
            self.compress_select_button.configure(text="Pilih Gambar Input")
            self.compress_input_entry.configure(placeholder_text="Jalur file input")
        else:
            self.compress_select_button.configure(text="Pilih Folder Input")
            self.compress_input_entry.configure(placeholder_text="Jalur folder input")
        
        self.compress_input_entry.delete(0, customtkinter.END)
        self.compress_status_label.configure(text="")

    def update_threshold_label(self, value):
        self.bg_threshold_value_label.configure(text=f"Nilai: {int(value)}")

    def update_quality_label(self, value):
        self.quality_value_label.configure(text=f"Nilai: {int(value)}")

    def select_files(self, tab, feature):
        if feature == "bg":
            mode_var = self.bg_mode_var
            input_entry = self.bg_input_entry
            status_label = self.bg_status_label
        elif feature == "resize":
            mode_var = self.resize_mode_var
            input_entry = self.resize_input_entry
            status_label = self.resize_status_label
        else: # feature == "compress"
            mode_var = self.compress_mode_var
            input_entry = self.compress_input_entry
            status_label = self.compress_status_label
            
        current_mode = mode_var.get()
        if current_mode == "single":
            file_path = filedialog.askopenfilename(
                title="Pilih file gambar",
                filetypes=(("Image files", "*.png;*.jpg;*.jpeg"), ("All files", "*.*"))
            )
            if file_path:
                input_entry.delete(0, customtkinter.END)
                input_entry.insert(0, file_path)
                status_label.configure(text=f"File terpilih: {os.path.basename(file_path)}", text_color="green")
            else:
                status_label.configure(text="Pemilihan dibatalkan.", text_color="orange")
        else:
            folder_path = filedialog.askdirectory(title="Pilih folder gambar")
            if folder_path:
                input_entry.delete(0, customtkinter.END)
                input_entry.insert(0, folder_path)
                status_label.configure(text=f"Folder terpilih: {os.path.basename(folder_path)}", text_color="green")
            else:
                status_label.configure(text="Pemilihan dibatalkan.", text_color="orange")

    def process_image(self, tab, feature):
        if feature == "bg":
            input_path = self.bg_input_entry.get()
            status_label = self.bg_status_label
            threshold_value = int(self.bg_threshold_slider.get())
            current_mode = self.bg_mode_var.get()
        elif feature == "resize":
            input_path = self.resize_input_entry.get()
            status_label = self.resize_status_label
            current_mode = self.resize_mode_var.get()
            
            try:
                new_width = int(self.width_entry.get())
                new_height = int(self.height_entry.get())
                if new_width <= 0 or new_height <= 0:
                    status_label.configure(text="Ukuran harus lebih dari 0.", text_color="red")
                    return
            except ValueError:
                status_label.configure(text="Masukkan angka valid untuk lebar dan tinggi.", text_color="red")
                return
        else: # feature == "compress"
            input_path = self.compress_input_entry.get()
            status_label = self.compress_status_label
            quality_value = int(self.quality_slider.get())
            selected_format = self.format_option_menu.get()
            current_mode = self.compress_mode_var.get()

        if not input_path:
            status_label.configure(text="Pilih file atau folder input terlebih dahulu.", text_color="red")
            return
        
        status_label.configure(text="Memproses...", text_color="blue")
        self.update()

        if current_mode == "single":
            if feature == "bg":
                output_file_name = f"output_{os.path.basename(input_path)}"
                output_path = filedialog.asksaveasfilename(
                    title="Simpan sebagai",
                    initialfile=output_file_name,
                    defaultextension=".png",
                    filetypes=(("PNG files", "*.png"), ("All files", "*.*"))
                )
                if not output_path:
                    status_label.configure(text="Proses dibatalkan.", text_color="orange")
                    return
                success = remove_background_and_autocrop_enhanced(input_path, output_path, alpha_threshold=threshold_value)
            elif feature == "resize":
                file_name_without_ext, file_ext = os.path.splitext(os.path.basename(input_path))
                output_file_name = f"{file_name_without_ext}_{new_width}x{new_height}.png"
                output_path = filedialog.asksaveasfilename(
                    title="Simpan sebagai",
                    initialfile=output_file_name,
                    defaultextension=".png",
                    filetypes=(("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*"))
                )
                if not output_path:
                    status_label.configure(text="Proses dibatalkan.", text_color="orange")
                    return
                success = resize_image_and_save(input_path, output_path, new_width, new_height)
            else: # feature == "compress"
                file_name_without_ext = os.path.splitext(os.path.basename(input_path))[0]
                output_file_name = f"{file_name_without_ext}_{quality_value}_kompresi.{selected_format.lower()}"
                output_path = filedialog.asksaveasfilename(
                    title="Simpan sebagai",
                    initialfile=output_file_name,
                    defaultextension=f".{selected_format.lower()}",
                    filetypes=((f"{selected_format} files", f"*.{selected_format.lower()}"), ("All files", "*.*"))
                )
                if not output_path:
                    status_label.configure(text="Proses dibatalkan.", text_color="orange")
                    return
                success = compress_image_and_save(input_path, output_path, quality_value, selected_format)
            
            if success:
                status_label.configure(text=f"Berhasil! File disimpan di: {output_path}", text_color="green")
            else:
                status_label.configure(text="Gagal memproses gambar.", text_color="red")
        
        else: # batch mode
            if not os.path.isdir(input_path):
                status_label.configure(text="Jalur input tidak valid. Pastikan Anda memilih folder.", text_color="red")
                return
            
            output_folder = filedialog.askdirectory(title="Pilih folder untuk menyimpan hasil")
            if not output_folder:
                status_label.configure(text="Proses dibatalkan.", text_color="orange")
                return

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            processed_count = 0
            file_extensions = ('.png', '.jpg', '.jpeg')
            image_files = [f for f in os.listdir(input_path) if f.lower().endswith(file_extensions)]
            
            if not image_files:
                status_label.configure(text="Tidak ditemukan file gambar di folder tersebut.", text_color="orange")
                return
            
            for filename in image_files:
                input_file = os.path.join(input_path, filename)
                
                if feature == "bg":
                    output_file = os.path.join(output_folder, f"output_{os.path.splitext(filename)[0]}.png")
                    success = remove_background_and_autocrop_enhanced(input_file, output_file, alpha_threshold=threshold_value)
                elif feature == "resize":
                    file_name_without_ext, file_ext = os.path.splitext(filename)
                    output_file = os.path.join(output_folder, f"{file_name_without_ext}_{new_width}x{new_height}{file_ext}")
                    success = resize_image_and_save(input_file, output_file, new_width, new_height)
                else: # feature == "compress"
                    file_name_without_ext = os.path.splitext(filename)[0]
                    output_file = os.path.join(output_folder, f"{file_name_without_ext}_{quality_value}_kompresi.{selected_format.lower()}")
                    success = compress_image_and_save(input_file, output_file, quality_value, selected_format)

                if success:
                    processed_count += 1
            
            status_label.configure(text=f"Selesai! {processed_count} dari {len(image_files)} gambar berhasil diproses.", text_color="green")

if __name__ == "__main__":
    try:
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Terjadi kesalahan fatal saat memulai aplikasi: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Aplikasi dihentikan oleh pengguna.")
        sys.exit(0)
    except SystemExit:
        print("Aplikasi dihentikan secara paksa.")
        sys.exit(0)
