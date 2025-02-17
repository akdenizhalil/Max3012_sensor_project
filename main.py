import pigpio
import time
from libs.ssd1306 import SSD1306_I2C
import math

# Raspberry Pi'de pigpio başlat
pi = pigpio.pi()

# MAX30102 ve OLED I2C Adresleri
MAX30102_ADDR = 0x57
OLED_ADDR = 0x3C
I2C_BUS = 1

# OLED ve MAX30102 için I2C başlat
max30102_i2c = pi.i2c_open(I2C_BUS, MAX30102_ADDR)
i2c_oled = pi.i2c_open(I2C_BUS, OLED_ADDR)
oled = SSD1306_I2C(128, 64, i2c_oled)


def configure_max30102():
    """MAX30102'yi başlatır."""
    pi.i2c_write_byte_data(max30102_i2c, 0x09, 0x03)  # SpO₂ Modu
    pi.i2c_write_byte_data(max30102_i2c, 0x0A, 0x27)  # ADC 18-bit, 100Hz
    pi.i2c_write_byte_data(max30102_i2c, 0x0C, 0x24)  # RED LED gücü
    pi.i2c_write_byte_data(max30102_i2c, 0x0D, 0x24)  # IR LED gücü
    pi.i2c_write_byte_data(max30102_i2c, 0x08, 0x4F)  # FIFO Ayarları
    print("MAX30102 Başlatıldı!")

configure_max30102()

def read_fifo():
    """FIFO'dan RED ve IR verilerini okur."""
    data = pi.i2c_read_i2c_block_data(max30102_i2c, 0x07, 6)

    red_val = (data[0] << 16) | (data[1] << 8) | data[2]
    ir_val = (data[3] << 16) | (data[4] << 8) | data[5]

    return red_val, ir_val

def calculate_bpm(ir_values, time_intervals):
    """Kalp atış hızını (BPM) hesaplar.
    
    1. Öncelikle sinyalin ortalama değerini hesaplayarak bir eşik değeri belirleriz.
    2. IR verisinde tepe noktalarını (peaks) bulmak için sinyaldeki lokal maksimumları kontrol ederiz.
       - Eğer bir değer hem kendisinden önceki hem de sonraki değerden büyükse ve eşik seviyesinin üzerindeyse,
         bu bir kalp atışı olarak kabul edilir ve zamanı kaydedilir.
    3. Eğer en az iki tepe noktası bulunmuşsa, aralarındaki zaman farklarını hesaplarız.
    4. Ortalama zaman farkını bulup, bunu dakikadaki atış sayısına (BPM) çevirmek için
       60000 / ortalama süre formülünü kullanırız.
    5. Eğer yeterli veri yoksa (örneğin, birden az tepe noktası varsa), BPM 0 olarak döndürülür.
    """
    peaks = []
    threshold = sum(ir_values) / len(ir_values)  # Ortalama değer eşik seviyesi
    
    for i in range(1, len(ir_values) - 1):
        if ir_values[i-1] < ir_values[i] and ir_values[i+1] < ir_values[i] and ir_values[i] > threshold:
            peaks.append(time_intervals[i])
    
    if len(peaks) < 2:
        return 0
    
    intervals = [peaks[i] - peaks[i-1] for i in range(1, len(peaks))]
    avg_interval = sum(intervals) / len(intervals)
    bpm = 60000 / avg_interval  # 1 dakika = 60000 ms
    return int(bpm)

def calculate_spo2(red_values, ir_values):
    """SpO₂ değerini hesaplar.
    
    1. Kirmizi (RED) ve Kizilötesi (IR) isik ölçümlerini kullanarak AC ve DC bileşenlerini hesaplariz.
    2. AC bileşeni, sinyalin maksimum ve minimum değerleri arasindaki farktir.
    3. DC bileşeni, sinyalin ortalama değeridir.
    4. SpO₂ hesaplamak için R oranini kullaniriz:
       - R = (RED_AC / RED_DC) / (IR_AC / IR_DC)
       - SpO₂ = 110 - (25 * R)
    5. Eğer AC veya DC bileşenlerinden biri 0 ise, SpO₂ hesaplanamaz ve 0 döndürülür.
    6. SpO₂ değerinin 90 ile 100 arasında olmasını sağlamak için sınırlandırma uygulanır.
    """
    red_ac = max(red_values) - min(red_values)
    ir_ac = max(ir_values) - min(ir_values)
    red_dc = sum(red_values) / len(red_values)
    ir_dc = sum(ir_values) / len(ir_values)
    
    if ir_ac == 0 or ir_dc == 0 or red_dc == 0:
        return 0
    
    R = (red_ac / red_dc) / (ir_ac / ir_dc)
    spo2 = 110 - (25 * R)
    return max(90, min(100, int(spo2)))

def show_data(bpm, spo2):
    """OLED ekranda nabız ve SpO₂ değerlerini göster."""
    oled.fill(0)
    oled.text(f"HR: {bpm} BPM", 10, 10)
    oled.text(f"SpO2: {spo2}%", 10, 30)
    oled.show()

ir_values = []
red_values = []
time_intervals = []

start_time = time.time()

while True:
    red_val, ir_val = read_fifo()
    current_time = (time.time() - start_time) * 1000
    
    ir_values.append(ir_val)
    red_values.append(red_val)
    time_intervals.append(current_time)
    
    if len(ir_values) > 10:
        ir_values.pop(0)
        red_values.pop(0)
        time_intervals.pop(0)
    
    bpm = calculate_bpm(ir_values, time_intervals)
    spo2 = calculate_spo2(red_values, ir_values)
    
    show_data(bpm, spo2)
    print(f"BPM: {bpm}, SpO₂: {spo2}")
    time.sleep(1)
