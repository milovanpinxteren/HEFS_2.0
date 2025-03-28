import fpdf


class Pickbonnen(fpdf.FPDF):
    # def __init__(self):
    #     super().__init__()
    #
    #     self.add_font('DejaVu', '', 'DejaVu.ttf', uni=True)

    def sanitize_text(self, text):
        # Keep only characters in the ASCII range (supported by Helvetica)
        return ''.join(c if ord(c) < 128 else '' for c in text)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'B', 10)
        self.write(0,
                   'www.kerstdiner.nl         Vragen? Neem contact op via bestellen@kerstdiner.nl of in de chat op de website')
        self.set_font('Arial', 'B', 10)

    def klantcell(self, naw):
        self.image('hefs/static/images/kerstdiner.png', 2, 10, 30, 30)
        self.cell(32)
        self.set_font('helvetica', 'B', 30)
        self.cell(100, 10, str(naw[0]), ln=1)
        self.set_font('helvetica', '', 12)
        self.cell(32, 10)
        naw_string = f'{naw[1]} {naw[2]}\n{naw[3]} {naw[4]}\n{naw[5]} {naw[6]}\n{str(naw[7])}\nRoute: {str(naw[8])}'
        sanitized_text = self.sanitize_text(naw_string)
        self.multi_cell(100, 5, sanitized_text)
        self.set_font('helvetica', 'B', 13)
        # self.cell(1, 3, 'Route: ' + str(naw[15]), ln=1)

    def klant_qr_cell(self, img):
        self.set_y(10)
        self.set_x(135)
        self.write(0, 'Scan om label te printen:')
        self.image(img, 137, 12, 40, 40)

    def pickcell(self, pick, offset_x):
        self.set_x(offset_x)
        self.cell(8, 8, border=1, ln=0)
        self.cell(3, 3, ' ', ln=0)
        self.cell(8, 8, border=1, ln=0)
        self.cell(3, 3, ' ', ln=0)
        self.set_font('helvetica', 'B', 12)
        self.cell(8, 8, str(int(pick.hoeveelheid)), border=1, ln=0)
        self.set_font('helvetica', '', 10)
        self.cell(45, 10, '(' + str(pick.product_id) + ') ' + str(pick.omschrijving), ln=0)
        self.cell(12, 10, ' ', ln=1)

    def naw_function(self, naw):
        print(naw)
        self.set_font('helvetica', '', 10)
        self.klantcell(naw)

    def qr_codecell(self, img):
        self.image(img, 130, 200, 70, 70)

    def next_page_cell(self, conversieID, page_nr):
        self.set_font('helvetica', 'B', 25)
        self.write(0, '                                ' + str(conversieID) + ' Pagina ' + str(page_nr))

    def pick_function(self, pick, pickcount, conversieID):
        self.set_font('helvetica', '', 10)
        self.set_y(55 + (pickcount * 10))
        self.set_x(8)
        offset_x = 8
        if 20 < pickcount < 35:
            offset_x = 100
            self.set_y(55 + ((pickcount - 21) * 10))
        if pickcount == 35:
            self.next_page_cell(conversieID, 2)
        if 35 < pickcount < 60:
            offset_x = 8
            self.set_y(10 + ((pickcount - 35) * 10))
        if 60 <= pickcount < 85:
            offset_x = 100
            self.set_y(15 + ((pickcount - 60) * 10))
        if pickcount == 85:
            self.next_page_cell(conversieID, 3)
        if 85 < pickcount < 100:
            offset_x = 8
            self.set_y(15 + ((pickcount - 80) * 10))
        self.pickcell(pick, offset_x)


