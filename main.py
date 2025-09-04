import customtkinter
from tkinter import filedialog
from rembg import remove
from PIL import Image
import os
import sys

def remove_background_and_autocrop_enhanced(input_path, output_path, alpha_threshold=15):
    """
    Menghilangkan background dan memotong area transparan berlebih.
    """
    try:
        print(f"[{os.path.basename(input_path)}] - Membuka gambar...")
        input_image = Image.open(input_path)
        
        print(f"[{os.path.basename(input_path)}] - Menghapus background...")
        image_without_bg = remove(input_image)
        
        print(f"[{os.path.basename(input_path)}] - Mengkonversi dan membersihkan piksel samar...")
        image_without_bg = image_without_bg.convert("RGBA")
        
        pixels = image_without_bg.load()
        width, height = image_without_bg.size

        for x in range(width):
            for y in range(height):
                r, g, b, a = pixels[x, y]
                if a < alpha_threshold:
                    pixels[x, y] = (0, 0, 0, 0)

        print(f"[{os.path.basename(input_path)}] - Mengambil bounding box...")
        bbox = image_without_bg.getbbox()
        
        if bbox:
            print(f"[{os.path.basename(input_path)}] - Memotong dan menyimpan gambar...")
            cropped_image = image_without_bg.crop(bbox)
            cropped_image.save(output_path)
            return True
        else:
            print(f"[{os.path.basename(input_path)}] - Tidak ada piksel non-transparan yang ditemukan.")
            return False

    except FileNotFoundError:
        print(f"[{os.path.basename(input_path)}] - ERROR: File tidak ditemukan di jalur: {input_path}")
        return False
    except Exception as e:
        # Menangkap error spesifik dan mencetaknya ke konsol
        print(f"[{os.path.basename(input_path)}] - ERROR: Terjadi kesalahan saat pemrosesan gambar: {e}")
        return False

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Penghapus Background Gambar")
        self.geometry("600x500")
        self.grid_columnconfigure(0, weight=1)

        self.frame = customtkinter.CTkFrame(self)
        self.frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.frame.grid_columnconfigure(0, weight=1)

        self.title_label = customtkinter.CTkLabel(self.frame, text="Aplikasi Penghapus Background", font=("Roboto", 24))
        self.title_label.grid(row=0, column=0, pady=(20, 10), padx=20)

        self.mode_var = customtkinter.StringVar(value="single")
        self.mode_label = customtkinter.CTkLabel(self.frame, text="Pilih mode:")
        self.mode_label.grid(row=1, column=0, pady=(10, 0), padx=20, sticky="w")
        
        self.single_mode_radio = customtkinter.CTkRadioButton(self.frame, text="Satu File", variable=self.mode_var, value="single", command=self.update_ui)
        self.single_mode_radio.grid(row=2, column=0, pady=(0, 5), padx=20, sticky="w")
        
        self.batch_mode_radio = customtkinter.CTkRadioButton(self.frame, text="Mode Batch (Folder)", variable=self.mode_var, value="batch", command=self.update_ui)
        self.batch_mode_radio.grid(row=3, column=0, pady=(0, 10), padx=20, sticky="w")

        self.input_label = customtkinter.CTkLabel(self.frame, text="Pilih gambar input:")
        self.input_label.grid(row=4, column=0, pady=(10, 0), padx=20, sticky="w")
        self.input_entry = customtkinter.CTkEntry(self.frame, placeholder_text="Jalur file input")
        self.input_entry.grid(row=5, column=0, pady=(0, 10), padx=20, sticky="ew")
        
        self.select_button = customtkinter.CTkButton(self.frame, text="Pilih Gambar", command=self.select_files)
        self.select_button.grid(row=6, column=0, pady=5, padx=20, sticky="ew")

        self.threshold_label = customtkinter.CTkLabel(self.frame, text="Pengaturan Threshold:")
        self.threshold_label.grid(row=7, column=0, pady=(10, 0), padx=20, sticky="w")
        
        self.threshold_value_label = customtkinter.CTkLabel(self.frame, text="Nilai: 15")
        self.threshold_value_label.grid(row=8, column=0, pady=(5, 0), padx=20, sticky="w")

        self.threshold_slider = customtkinter.CTkSlider(master=self.frame, from_=0, to=255, number_of_steps=256, command=self.update_threshold_label)
        self.threshold_slider.grid(row=9, column=0, pady=(0, 10), padx=20, sticky="ew")
        self.threshold_slider.set(15)

        self.process_button = customtkinter.CTkButton(self.frame, text="Hapus Background dan Potong", command=self.process_image, fg_color="#3B82F6")
        self.process_button.grid(row=10, column=0, pady=10, padx=20, sticky="ew")

        self.status_label = customtkinter.CTkLabel(self.frame, text="", text_color="green", font=("Roboto", 14))
        self.status_label.grid(row=11, column=0, pady=(10, 20), padx=20)

    def update_ui(self):
        current_mode = self.mode_var.get()
        if current_mode == "single":
            self.select_button.configure(text="Pilih Gambar Input")
            self.input_entry.configure(placeholder_text="Jalur file input")
        else:
            self.select_button.configure(text="Pilih Folder Input")
            self.input_entry.configure(placeholder_text="Jalur folder input")
        
        self.input_entry.delete(0, customtkinter.END)
        self.status_label.configure(text="")

    def update_threshold_label(self, value):
        self.threshold_value_label.configure(text=f"Nilai: {int(value)}")

    def select_files(self):
        current_mode = self.mode_var.get()
        if current_mode == "single":
            file_path = filedialog.askopenfilename(
                title="Pilih file gambar",
                filetypes=(("Image files", "*.png;*.jpg;*.jpeg"), ("All files", "*.*"))
            )
            if file_path:
                self.input_entry.delete(0, customtkinter.END)
                self.input_entry.insert(0, file_path)
                self.status_label.configure(text=f"File terpilih: {os.path.basename(file_path)}", text_color="green")
            else:
                self.status_label.configure(text="Pemilihan dibatalkan.", text_color="orange")
        else:
            folder_path = filedialog.askdirectory(title="Pilih folder gambar")
            if folder_path:
                self.input_entry.delete(0, customtkinter.END)
                self.input_entry.insert(0, folder_path)
                self.status_label.configure(text=f"Folder terpilih: {os.path.basename(folder_path)}", text_color="green")
            else:
                self.status_label.configure(text="Pemilihan dibatalkan.", text_color="orange")

    def process_image(self):
        input_path = self.input_entry.get()
        if not input_path:
            self.status_label.configure(text="Pilih file atau folder input terlebih dahulu.", text_color="red")
            return
        
        threshold_value = int(self.threshold_slider.get())
        current_mode = self.mode_var.get()
        
        self.status_label.configure(text="Memproses...", text_color="blue")
        self.update()

        if current_mode == "single":
            output_file_name = f"output_{os.path.basename(input_path)}"
            output_path = filedialog.asksaveasfilename(
                title="Simpan sebagai",
                initialfile=output_file_name,
                defaultextension=".png",
                filetypes=(("PNG files", "*.png"), ("All files", "*.*"))
            )
            if not output_path:
                self.status_label.configure(text="Proses dibatalkan.", text_color="orange")
                return

            try:
                success = remove_background_and_autocrop_enhanced(input_path, output_path, alpha_threshold=threshold_value)
                if success:
                    self.status_label.configure(text=f"Berhasil! File disimpan di: {output_path}", text_color="green")
                else:
                    self.status_label.configure(text="Gagal memproses gambar.", text_color="red")
            except Exception as e:
                self.status_label.configure(text=f"Terjadi kesalahan: {e}", text_color="red")
        
        else: # batch mode
            if not os.path.isdir(input_path):
                self.status_label.configure(text="Jalur input tidak valid. Pastikan Anda memilih folder.", text_color="red")
                return
            
            output_folder = filedialog.askdirectory(title="Pilih folder untuk menyimpan hasil")
            if not output_folder:
                self.status_label.configure(text="Proses dibatalkan.", text_color="orange")
                return

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            processed_count = 0
            file_extensions = ('.png', '.jpg', '.jpeg')
            image_files = [f for f in os.listdir(input_path) if f.lower().endswith(file_extensions)]
            
            if not image_files:
                self.status_label.configure(text="Tidak ditemukan file gambar di folder tersebut.", text_color="orange")
                return
                
            for filename in image_files:
                input_file = os.path.join(input_path, filename)
                output_file = os.path.join(output_folder, f"output_{os.path.splitext(filename)[0]}.png")
                
                self.status_label.configure(text=f"Memproses {filename}...", text_color="blue")
                self.update()

                success = remove_background_and_autocrop_enhanced(input_file, output_file, alpha_threshold=threshold_value)
                if success:
                    processed_count += 1
            
            self.status_label.configure(text=f"Selesai! {processed_count} dari {len(image_files)} gambar berhasil diproses.", text_color="green")


if __name__ == "__main__":
    try:
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Terjadi kesalahan fatal saat memulai aplikasi: {e}")
        sys.exit(1)
