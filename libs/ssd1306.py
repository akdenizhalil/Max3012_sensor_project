import pigpio
import time
import framebuf

class SSD1306_I2C:
    def __init__(self, width, height, pi, i2c_bus=1, addr=0x3C):
        self.width = width
        self.height = height
        self.pi = pi
        self.addr = addr
        self.i2c = pi.i2c_open(i2c_bus, addr)
        self.buffer = bytearray((self.height // 8) * self.width)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()
    
    def init_display(self):
        for cmd in [
            0xAE, 0xA8, 0x3F, 0xD3, 0x00, 0x40, 0xA1, 0xC8,
            0xDA, 0x12, 0x81, 0x7F, 0xA4, 0xA6, 0xD5, 0x80,
            0x8D, 0x14, 0xAF
        ]:
            self.send_command(cmd)
        self.fill(0)
        self.show()
    
    def send_command(self, cmd):
        self.pi.i2c_write_byte_data(self.i2c, 0x00, cmd)
    
    def fill(self, color):
        self.framebuf.fill(color)
    
    def text(self, text, x, y):
        """Metni OLED ekrana yazdırır."""
        self.framebuf.text(text, x, y, 1)
    
    def show(self):
        for i in range(0, self.height // 8):
            self.send_command(0xB0 + i)
            self.send_command(0x00)
            self.send_command(0x10)
            self.pi.i2c_write_device(self.i2c, bytearray([0x40]) + self.buffer[i * self.width:(i + 1) * self.width])
    
    def close(self):
        """I2C bağlantısını kapatır."""
        self.pi.i2c_close(self.i2c)
