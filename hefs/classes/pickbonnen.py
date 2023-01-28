import fpdf


class Pickbonnen(fpdf.FPDF):

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'B', 10)
        self.write(0,
                   'www.kerstdiner.nl                                                                  contact: bestellen@kerstdiner.nl')
        self.set_font('helvetica', 'B', 10)

    def klantcell(self, naw):
        self.image('hefs/static/images/kerstdiner.png', 2, 10, 30, 30)
        self.cell(32)
        self.set_font('helvetica', 'B', 30)
        self.cell(100, 10, str(naw[0]), ln=1)
        self.set_font('helvetica', '', 12)
        self.cell(32, 10)
        naw_string = f'{naw[1]} {naw[2]}\n {naw[3]} {naw[4]}\n{naw[5]}\n{naw[6]}\n{str(naw[7])}'
        self.multi_cell(100, 5, naw_string)
        self.set_font('helvetica', 'B', 13)
        # self.cell(1, 3, 'Route: ' + str(naw[15]), ln=1)

        self.set_y(10)
        self.set_x(130)
        self.set_font('helvetica', 'B', 30)
        self.cell(100, 10, str(naw[0]), ln=1)
        self.set_x(130)
        self.set_font('helvetica', '', 12)
        naw_string = f'{naw[1]} {naw[2]}\n {naw[3]} {naw[4]}\n{naw[5]}\n{naw[6]}\n{str(naw[7])}'
        self.multi_cell(100, 5, naw_string)
        self.line(0, 48, 210, 48)

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

    def pick_function(self, pick, pickcount):
        self.set_font('helvetica', '', 10)
        self.set_y(55 + (pickcount * 10))
        self.pickcell(pick, 8)


