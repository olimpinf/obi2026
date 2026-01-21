import os
from io import BytesIO

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Image as rpImage
from reportlab.platypus import (PageBreak, Paragraph, SimpleDocTemplate, Table,
                                TableStyle)

footer_msg = '' # kludge to access it from footer

class PrintPresenceList:
    def __init__(self, footer):
        global footer_msg
        self.buffer = BytesIO()
        self.pagesize = A4
        footer_msg = footer
        self.width, self.height = self.pagesize

    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        #styles = getSampleStyleSheet()
 
        # Header
        #header = Paragraph('Modalidade Iniciação', styles['Normal'])
        #w, h = header.wrap(doc.width, doc.topMargin)
        #header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
 
        # Footer
        #footer = Paragraph('Teste', styles['Normal'])
        #w, h = footer.wrap(doc.width, doc.bottomMargin)
        #footer.drawOn(canvas, doc.leftMargin, h)
        canvas.setFont("Helvetica", 11)
        canvas.drawString(10 * mm, 10 * mm ,
                             "%s" % (footer_msg))

        # Release the canvas
        canvas.restoreState()

    def print_list(self, data, title, subtitle1, subtitle2):
        buffer = self.buffer
        doc = SimpleDocTemplate(buffer,
                                rightMargin=72,
                                leftMargin=72,
                                topMargin=72,
                                bottomMargin=72,
                                pagesize=self.pagesize)
 
        elements = []
 
        styles = getSampleStyleSheet()
        sty_subtitle1 = ParagraphStyle(
            name='Subtitle1',
            fontSize=11,
            alignment = TA_CENTER,
            leading = 15,
            )
        sty_subtitle2 = ParagraphStyle(
            name='Subtitle2',
            fontSize=11,
            alignment = TA_CENTER,
            leading = 25,
            spaceAfter = 15,
            )

        logo = rpImage(os.path.join(settings.BASE_DIR,'sisca','attic','logo-obi-black.png'),45,45)
        #logo = rpImage(os.path.join('.','sisca','attic','logo-obi-black.png'),45,45)
        elements.append(logo)
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Paragraph(subtitle1, sty_subtitle1))
        elements.append(Paragraph(subtitle2, sty_subtitle2))
 
        N=len(data)
        if len(data[0]) == 4:
            t=Table(data,N*[0.9*inch,3.3*inch,0.7*inch,2.5*inch],N*[0.3*inch],repeatRows=1)
        else:
            t=Table(data,N*[0.9*inch,3.3*inch,3.3*inch],N*[0.3*inch],repeatRows=1)
            
        t.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 0.25, colors.black),
                               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                               ]))
 
        elements.append(t)

        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer,
                  canvasmaker=NumberedCanvas)
 
        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    '''
        Usage with django

    @staff_member_required
    def print_users(request):
        # Create the HttpResponse object with the appropriate PDF headers.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="My Users.pdf"'
     
        buffer = BytesIO()
     
        report = PrintPresenceList(buffer, 'Letter')
        pdf = report.print_users()
     
        response.write(pdf)
        return response
    '''


class NumberedCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.footer_msg = "Teste"
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            canvas.Canvas.setFont(self,psfontname='Helvetica',size=10)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
 
    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        styles = getSampleStyleSheet()
        self.drawRightString(200 * mm, 10 * mm,
                             "Página %d de %d" % (self._pageNumber, page_count))




if __name__ == '__main__':
    #buffer = BytesIO()
    data= [['Num. Inscr.','Nome', 'Assinatura'],
               ['12345-A','Mané',''],
               ['01234-B','Zé', ''],
               ['12345-A','Mané',''],
               ['01234-B','Zé', ''],
               ]

    title = 'OBI2018 - Fase Nacional'
    subtitle1 = 'Modalidade Iniciação Nível Júnior'
    subtitle2 = 'Lista de Presença - 11/08/2018'

    report = PrintPresenceList(subtitle1)
    pdf = report.print_list(data, title, subtitle1, subtitle2)
 
    with open('arquivo.pdf', 'wb') as f:
        f.write(pdf)
