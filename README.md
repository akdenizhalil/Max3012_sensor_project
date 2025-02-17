
# Raspberry Pi Pico ile MAX30102 Nabız ve SpO₂ Ölçer

Bu proje, Raspberry Pi  kullanarak **MAX30102 nabız ve oksijen sensörü** ile kalp atış hızı (BPM) ve kandaki oksijen seviyesini (SpO₂) ölçmek için geliştirilmiştir. 
Ayrıca, ölçülen değerler **SSD1306 OLED ekranında** görüntülenir.

## 📌 Özellikler
✅ **Nabız ölçümü (BPM)** – Kalp atış hızını hesaplar.  
✅ **SpO₂ ölçümü** – Kandaki oksijen doygunluğunu hesaplar.  
✅ **SSD1306 OLED ekran** – Gerçek zamanlı ölçümleri görüntüler.  
✅ **pigpio kütüphanesi** ile donanımsal I2C haberleşmesi sağlar.  

## 🚀 Gereksinimler
Bu projeyi çalıştırmak için aşağıdaki bileşenlere ihtiyacınız var:

- **Raspberry Pi Pico**
- **MAX30102 Nabız ve SpO₂ Sensörü**
- **SSD1306 OLED Ekran (I2C)**
- **Bağlantı kabloları**

Ayrıca, aşağıdaki Python kütüphanelerinin kurulu olması gerekmektedir:
```bash
pip install pigpio


