import qrcode


class QRCodeViewer:
    def __init__(self):
        self.qr = qrcode.QRCode()
        self.qr_img = None

    def url(self, url):
        self.qr.clear()
        self.qr.add_data(url)
        self.qr.make(fit=True)
        self.qr_img = self.qr.make_image(fill_color="black", back_color="white")
        return self.qr_img

    def show(self):
        self.qr_img.show()
