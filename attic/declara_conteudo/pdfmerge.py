import io

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Image as rpImage

from PyPDF2 import PdfReader, PdfWriter


def merge(orig_fname, fromaddress, toaddress, num_medals, day, month, year):
    packet = io.BytesIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=A4)
    # from address
    can.setFont('Helvetica', 9)
    can.drawString(50, 727 , "{} (e{})".format(fromaddress['name'],toaddress['id']))
    can.drawString(65, 727-17 , fromaddress['address1'])
    can.drawString(20, 727-35 , fromaddress['address2'])
    can.drawString(53, 727-53 , fromaddress['city'])
    can.drawString(255, 727-53 , fromaddress['state'])
    can.drawString(40, 727-71 , fromaddress['zip'])
    #can.drawString(180, 727-71 , fromaddress['cpf'])
    can.drawString(180, 727-71 , fromaddress['cnpj'])

    # to address
    half_page = 280
    can.drawString(half_page+50, 727 , toaddress['name'])
    can.drawString(half_page+65, 727-17 , toaddress['address1'])
    can.drawString(half_page+20, 727-35 , toaddress['address2'])
    can.drawString(half_page+53, 727-53 , toaddress['city'])
    can.drawString(half_page+265, 727-53 , toaddress['state'])
    can.drawString(half_page+40, 727-71 , toaddress['zip'])
    can.drawString(half_page+180, 727-71 , toaddress['cpf'])

    # contents
    can.drawString(25, 600, '001')
    can.drawString(60, 600, 'Medalhas da Olimpíada Brasileira de Informática')
    can.drawString(430, 600, str(num_medals))
    can.drawString(510, 600, 'R$ {:.2f}'.format(20.0*num_medals))
    # total
    can.drawString(430, 345, str(num_medals))
    can.drawString(510, 345, 'R$ {:.2f}'.format(20.0*num_medals))

    # date and signature
    can.drawString(20, 190, 'Campinas')
    can.drawString(150, 190, day)
    can.drawString(220, 190, month)
    can.drawString(320, 190, year)

    signature = rpImage('signature_blue_transp.png',150,45)
    signature.drawOn(can,390,190)

    can.save()

    #move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfReader(packet)
    # read your existing PDF
    existing_pdf = PdfReader(open(orig_fname, "rb"))
    #output = PdfWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    #output.add_page(page)
    return(page)
    # finally, write "output" to a real file

if __name__=="__main__":
    fromaddress = {'name':'Olimpíada Brasileira de Informática','address1':'Instituto de Computação - UNICAMP','address2':'Av. Albert Einstein, 1251', 'city':'Campinas', 'state':'SP', 'zip':'13083-852', 'cpf':'019.350.398-06'}
    toaddress = {'name':'Ricardo Anido','address1':'Instituto de Computação - UNICAMP','address2':'Av. Albert Einstein, 1251', 'city':'Campinas', 'state':'SP', 'zip':'13083-852', 'cpf':'', 'id': '001'}
    toaddress2 = {'name':'Maria Clara Silva Souza','address1':'Rua Hélio de Oliveira Barbosa, 55','address2':'Casa 2, Bairro Isadora II', 'city':'Campo Grande', 'state':'SP', 'zip':'23093-690', 'cpf':'', 'id': '001'}
    orig_name = 'formularioA4.pdf'
    new_fname = 'output.pdf'
    num_medals = 1
    output = PdfWriter()
    #page = merge(orig_name, fromaddress, toaddress, num_medals)
    #output.add_page(page)
    page = merge(orig_name, fromaddress, toaddress2, num_medals, '13', 'dezembro', '2019')
    output.add_page(page)

    outputStream = open(new_fname, "wb")
    output.write(outputStream)
    outputStream.close()
