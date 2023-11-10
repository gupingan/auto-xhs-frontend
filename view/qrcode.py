import qrcode


class QRCodeViewer:
    def __init__(self):
        self.qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
        self.qr_img = None

    def url(self, url):
        self.qr.add_data(url)
        self.qr.make(fit=True)
        self.qr_img = self.qr.make_image(fill_color="black", back_color="white")
        return self.qr_img

    def print(self):
        self.qr.print_ascii(invert=True)

    def show(self):
        self.qr_img.show()
