import os.path
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime

DEST_DIR="/home/tecblic/finance/receivables/"

def render_to_pdf(template_src, filename , context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)

    try:
        split_filename = filename.split("_")
        extract_name = split_filename[0]

        extract_fiscal_year = split_filename[3]
        slice_fiscal_year =extract_fiscal_year[0:9]

        extract_month = split_filename[1]
        convert_to_date = datetime.strptime(extract_month, '%Y-%m-%d')
        month_name = convert_to_date.strftime('%B')

        path = DEST_DIR+slice_fiscal_year+"/"+month_name+"/"+extract_name+"/"
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
            with open(path + f'{filename}', 'wb+') as output:
                pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), output)
        if isExist:
            with open(path + f'{filename}', 'wb+') as output:
                pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), output)
    except Exception as e:
        print(e)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

