import fpdf


class Pickbonnen(fpdf.FPDF):

    def footer(self):
        self.set_y(-15)
        self.write(0,
                   'www.kerstdiner.nl                                                                  contact: 085-7430362')
        self.set_font('helvetica', 'B', 10)

    def klantcell(self, naw):
        self.image('hefs/static/images/kerstdiner.png', 2, 10, 30, 30)
        self.cell(32)
        self.set_font('helvetica', 'B', 30)
        self.cell(100, 10, str(naw[0]), ln=1)
        self.set_font('helvetica', '', 12)
        self.cell(32, 10)
        naw_string = f'{naw[1]} {naw[2]}\n {naw[5]} {naw[6]}\n{naw[7]}\n{naw[8]}\n{str(naw[10])[:11]}'
        self.multi_cell(100, 5, naw_string)
        self.set_font('helvetica', 'B', 13)
        self.cell(1, 3, 'Route: ' + str(naw[15]), ln=1)


        self.set_y(10)
        self.set_x(130)
        self.set_font('helvetica', 'B', 30)
        self.cell(100, 10, str(naw[0]), ln=1)
        self.set_x(130)
        self.set_font('helvetica', '', 12)
        naw_string = f'{naw[1]} {naw[2]}\n {naw[5]} {naw[6]}\n{naw[7]}\n{naw[8]}\n{str(naw[10])[:11]}'
        self.multi_cell(100, 5, naw_string)
        self.line(0, 48, 210, 48)


    def pickbon_function(self, naw):
        print(naw)
        self.add_page()
        self.set_font('helvetica', '', 10)
        self.klantcell(naw)

