import PyInstaller.__main__
import customtkinter
import os

# CustomTkinter kütüphanesinin bilgisayarındaki yerini buluyoruz
ctk_path = os.path.dirname(customtkinter.__file__)

print(f"CustomTkinter yolu bulundu: {ctk_path}")
print("EXE oluşturma işlemi başlıyor...")

PyInstaller.__main__.run([
    'app.py',                       # Dönüştürülecek dosyanın adı
    '--onefile',                    # Tek bir .exe dosyası olsun
    '--noconsole',                  # Arka planda siyah konsol penceresi açılmasın
    '--name=PDF_Master_Tool',       # Oluşacak dosyanın adı
    f'--add-data={ctk_path};customtkinter/' # CustomTkinter dosyalarını içeri aktar (Windows formatı)
])