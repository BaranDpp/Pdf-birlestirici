import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
from docx2pdf import convert
from pypdf import PdfWriter

# --- AYARLAR ---
ctk.set_appearance_mode("Dark")  # Varsayılan mod: Karanlık
ctk.set_default_color_theme("blue")  # Tema rengi: Mavi (blue, dark-blue, green)

class ModernPDFApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PDF Master Tool - Engineer Edition")
        self.geometry("700x600")
        self.resizable(False, False)
        
        # Dosya listesi
        self.selected_files = []
        self.file_filter = []
        self.current_action = None

        # Ana konteyner (Sayfaların değişeceği yer)
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

        # Uygulamayı başlat
        self.show_main_menu()

    def clear_frame(self):
        """Ekranı temizler."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # --- 1. ANA MENÜ ---
    def show_main_menu(self):
        self.clear_frame()
        
        # Tema Switch'i (Sol üst)
        switch_var = ctk.StringVar(value="Dark")
        def toggle_theme():
            ctk.set_appearance_mode(switch_var.get())
            
        switch = ctk.CTkSwitch(self.main_frame, text="Karanlık Mod", command=toggle_theme,
                               variable=switch_var, onvalue="Dark", offvalue="Light")
        switch.pack(anchor="w", padx=20, pady=10)

        # Başlıklar
        ctk.CTkLabel(self.main_frame, text="PDF MASTER TOOL", font=("Roboto Medium", 32)).pack(pady=(40, 10))
        ctk.CTkLabel(self.main_frame, text="Modern Dosya Yönetim Sistemi", font=("Roboto", 16), text_color="gray").pack(pady=(0, 40))

        # Ana Butonlar
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack()

        # Word to PDF Butonu
        btn_word = ctk.CTkButton(btn_frame, text="📄 Word ➡️PDF", command=self.setup_word_page,
                                 width=250, height=50, font=("Roboto", 16, "bold"), corner_radius=10)
        btn_word.pack(pady=15)

        # Merge PDF Butonu
        btn_merge = ctk.CTkButton(btn_frame, text="🔗 PDF Birleştir", command=self.setup_merge_page,
                                  width=250, height=50, font=("Roboto", 16, "bold"), corner_radius=10,
                                  fg_color="#E04F5F", hover_color="#C03947") # Farklı renk
        btn_merge.pack(pady=15)

        # Footer
        ctk.CTkLabel(self.main_frame, text="v2.0 | CustomTkinter", font=("Arial", 10), text_color="gray").pack(side="bottom", pady=20)

    # --- 2. MODÜL HAZIRLIKLARI ---
    def setup_word_page(self):
        self.file_filter = [("Word Dosyaları", "*.docx")]
        self.current_action = self.process_word_convert
        self.show_operation_page("Word'den PDF'e Dönüştürücü", "#1F6AA5")

    def setup_merge_page(self):
        self.file_filter = [("PDF Dosyaları", "*.pdf")]
        self.current_action = self.process_merge
        self.show_operation_page("PDF Birleştirme Aracı", "#E04F5F")

    # --- 3. ORTAK İŞLEM SAYFASI ---
    def show_operation_page(self, title_text, btn_color):
        self.clear_frame()
        self.selected_files = [] # Listeyi sıfırla

        # Header (Geri Dön Butonu ve Başlık)
        header_frame = ctk.CTkFrame(self.main_frame, height=60, corner_radius=0)
        header_frame.pack(fill="x")
        
        btn_back = ctk.CTkButton(header_frame, text="⬅ Geri", command=self.show_main_menu, 
                                 width=80, height=30, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        btn_back.pack(side="left", padx=20, pady=10)
        
        ctk.CTkLabel(header_frame, text=title_text, font=("Roboto Medium", 18)).pack(side="left", padx=10)

        # Dosya Ekleme Alanı
        control_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        control_frame.pack(fill="x", padx=40, pady=(30, 10))

        ctk.CTkButton(control_frame, text="➕ Dosya Ekle", command=self.add_files, width=150).pack(side="left")
        ctk.CTkButton(control_frame, text="🗑️ Temizle", command=self.clear_list, width=100, fg_color="gray", hover_color="darkgray").pack(side="right")

        # Liste Kutusu (Listbox CTk'da olmadığı için standart olanı modernize ediyoruz)
        list_frame = ctk.CTkFrame(self.main_frame)
        list_frame.pack(fill="both", expand=True, padx=40, pady=10)
        
        # Standart Listbox ama renkleri temaya uygun
        self.listbox = tk.Listbox(list_frame, bg="#2b2b2b", fg="white", selectbackground="#1F6AA5", 
                                  borderwidth=0, highlightthickness=0, font=("Consolas", 11))
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # İşlem Butonu
        self.btn_run = ctk.CTkButton(self.main_frame, text="İŞLEMİ BAŞLAT", command=self.start_thread,
                                     height=50, font=("Roboto", 16, "bold"), fg_color=btn_color)
        self.btn_run.pack(fill="x", padx=40, pady=(10, 20))

        # Log/Durum Alanı
        self.log_box = ctk.CTkTextbox(self.main_frame, height=100, font=("Consolas", 10))
        self.log_box.pack(fill="x", padx=40, pady=(0, 20))
        self.log("Hazır. Dosyaları ekleyip işlemi başlatabilirsiniz.")

    # --- FONKSİYONLAR ---
    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f">> {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=self.file_filter)
        for f in files:
            if f not in self.selected_files:
                self.selected_files.append(f)
                self.listbox.insert("end", os.path.basename(f))
        
        if self.selected_files:
            self.log(f"{len(files)} dosya eklendi.")

    def clear_list(self):
        self.selected_files = []
        self.listbox.delete(0, "end")
        self.log("Liste temizlendi.")

    def start_thread(self):
        if not self.selected_files:
            self.log("⚠️ HATA: Lütfen önce dosya seçin!")
            return
        threading.Thread(target=self.current_action).start()

    # --- İŞLEM MANTIKLARI ---
    def process_word_convert(self):
        output_folder = filedialog.askdirectory(title="PDF'ler Nereye Kaydedilsin?")
        if not output_folder: return

        self.btn_run.configure(state="disabled", text="İşleniyor...")
        self.log("⏳ Dönüştürme başladı...")

        try:
            for file_path in self.selected_files:
                base_name = os.path.basename(file_path)
                pdf_name = base_name.replace(".docx", ".pdf")
                full_out_path = os.path.join(output_folder, pdf_name)
                
                self.log(f"İşleniyor: {base_name}")
                convert(file_path, full_out_path)
            
            self.log("✅ Tüm işlemler başarıyla tamamlandı!")
            messagebox.showinfo("Bitti", "Dosyalar dönüştürüldü.")
        except Exception as e:
            self.log(f"❌ HATA: {str(e)}")
        finally:
            self.btn_run.configure(state="normal", text="İŞLEMİ BAŞLAT")

    def process_merge(self):
        save_path = filedialog.asksaveasfilename(title="Kaydet", defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not save_path: return

        self.btn_run.configure(state="disabled", text="Birleştiriliyor...")
        self.log("⏳ Birleştirme işlemi başladı...")

        merger = PdfWriter()
        try:
            for f in self.selected_files:
                merger.append(f)
                self.log(f"Eklendi: {os.path.basename(f)}")
            
            merger.write(save_path)
            merger.close()
            self.log(f"✅ Başarılı: {save_path}")
            messagebox.showinfo("Bitti", "Dosyalar birleştirildi.")
        except Exception as e:
            self.log(f"❌ HATA: {str(e)}")
        finally:
            self.btn_run.configure(state="normal", text="İŞLEMİ BAŞLAT")

if __name__ == "__main__":
    app = ModernPDFApp()
    app.mainloop()