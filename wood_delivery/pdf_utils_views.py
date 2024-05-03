import os
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO

from pgsystem import settings
from .forms import DownloadForm
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist



def convert_to_japanese_date(english_date):
    if not isinstance(english_date, datetime):
        english_date = datetime.strptime(english_date, "%Y%m%d")

    # Define the era transitions
    era_transitions = [
        (datetime(2019, 5, 1), "令和"),  # Reiwa era begins
    ]

    for transition_date, era_name in reversed(era_transitions):
        if english_date >= transition_date:
            japanese_year = english_date.year - transition_date.year + 1
            return f"{era_name}{japanese_year}年{english_date.month}月{english_date.day}日"

    return f"{english_date.year}年{english_date.month}月{english_date.day}日"
    pass

def draw_common_elements(pdf_document, entry):
    print("------------------------Time to create PDF---------------------------")
    print(entry.id)
    formatted_date = entry.weighing_day.strftime("%Y%m%d")
    slip_no = entry.slip_no
    combined_value = f"{formatted_date}-{slip_no}"
    pdf_document.drawString(400, 780, f"証明書番号:　 {combined_value}") 
    japanese_date = convert_to_japanese_date(formatted_date)
    pdf_document.drawString(400, 762, f"発行日:　 {japanese_date}")
    pdf_document.drawString(150, 690, f"発電用チップに係る間伐材等由来の木質バイオマス証明")
    pdf_document.drawString(50, 630, f"森林美化バイオマス合同会社　殿")
    pdf_document.drawString(380, 590, f"{entry.wood_supplier.name} 　")
    pdf_document.drawString(530, 590, f" 　印")
    pdf_document.drawString(380, 570, f"認定番号　{entry.wood_supplier.registration_name} ")
    pdf_document.drawString(50, 520, f"下記の物件は、間伐材由来の木質バイオマスであり、")
    pdf_document.drawString(50, 500, f"適切に分別管理されていることを証明します。")
    pdf_document.drawString(300, 450, f"記")
    pdf_document.drawString(70, 420, f"1. 　間伐材等由来の木質バイオマスの種類")
    pdf_document.drawString(80, 400, f" 　{entry.wood_sources.classification} ")
    pdf_document.drawString(70, 370, f"2. 　{entry.wood_sources.removal}")
    formatted_d = entry.wood_sources.registration_date.strftime("%Y%m%d")
    japanese_d = convert_to_japanese_date(formatted_d)
    pdf_document.drawString(70, 340, f"3. 　伐採許可（届出）の年月日　{japanese_d}")
    pdf_document.drawString(80, 320, f" 　許可書発行者　{entry.wood_sources.authority}")
    pdf_document.drawString(80, 300, f" 　伐採許可番号　{entry.wood_sources.registration_name}")
    pdf_document.drawString(70, 270, f"4. 　物件（森林）所在地")
    pdf_document.drawString(80, 250, f" 　{entry.wood_sources.location}")
    pdf_document.drawString(70, 220, f"5. 　伐採面積　 {entry.wood_sources.area}   ヘクタール")
    pdf_document.drawString(70, 190, f"6. 　樹種　  {entry.woods_type.wood_name}")
    pdf_document.drawString(70, 160, f"7. 　数量　 {entry.net_weight}")
    pdf_document.drawString(490, 130, f"以上")




def generate_upload_pdf(entry):
    try:
        pdfmetrics.registerFont(TTFont("BIZUDPGothic-Regular", "static/file/BIZUDPGothic-Regular.ttf"))
        buffer = BytesIO()
        pdf_document = canvas.Canvas(buffer)

        pdf_document.setFont("BIZUDPGothic-Regular", 12)

        #calling draw_common_elements function
        draw_common_elements(pdf_document, entry)

        pdf_document.save()

        # Move the buffer's position to the beginning
        buffer.seek(0)

        # Save the PDF buffer to a file with the filename as the id of the delivery record
        file_path = os.path.join(settings.MEDIA_ROOT, 'certificates', 'unverified',f"{entry.id}.pdf")
        with open(file_path, 'wb') as f:
            f.write(buffer.getvalue())

    except Exception as e:
        # Print the exception for debugging
        print(f"An error occurred in generate_pdf: {str(e)}")
        raise  # Re-raise the exception to see the full traceback

def pdf_data(delivery_records):

    for entry in delivery_records:
        generate_upload_pdf(entry)




def generate_pdf(selected_data):
    try:
        pdfmetrics.registerFont(TTFont("BIZUDPGothic-Regular", "static/file/BIZUDPGothic-Regular.ttf"))
        buffer = BytesIO()
        pdf_document = canvas.Canvas(buffer)

        pdf_document.setFont("BIZUDPGothic-Regular", 12)

        # Loop through wood_type_data and draw strings
        for entry in selected_data:
            #calling draw_common_elements function
            draw_common_elements(pdf_document, entry)

        pdf_document.save()
        # Move the buffer's position to the beginning
        buffer.seek(0)
        return buffer

    except Exception as e:
        # Print the exception for debugging
        print(f"An error occurred in generate_pdf: {str(e)}")
        raise  # Re-raise the exception to see the full traceback



def download_certificate(request):
    try:
        if request.method == 'POST':
            form = DownloadForm(request.POST)
            if form.is_valid():
                selected_data = form.cleaned_data['selected_data']
                pdf_buffer = generate_pdf(selected_data)

                # Set up the HttpResponse for the PDF file
                response = HttpResponse(pdf_buffer, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=certificate.pdf'

                return response
            else:
                # Handle the case where the form is not valid
                return HttpResponse("Invalid form data")

        # Handle the case where the request method is not POST
        return render(request, 'wood_delivery/index.html', {'error_message': f"{str(e)}: Go back "})

    except ObjectDoesNotExist as e:
        # Render the template with the custom error message
        return render(request, 'wood_delivery/index.html', {'error_message': f"{str(e)}: Go back "})
    except Exception as e:
        # Print the exception for debugging
        print(f"An error occurred in download_certificate: {str(e)}")
        # Log the exception or take appropriate action
        return render(request, 'wood_delivery/index.html', {'error_message': f"{str(e)}: Go back "})