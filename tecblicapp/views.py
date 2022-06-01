from io import BytesIO
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import datetime
from .forms import bankDetailForm, bankForm, clientDetailForm, invoiceForm
from .utils import render_to_pdf
from .models import BankDetails, clientDetail,Invoice, AutoNumber,gstValue
from django.core.mail import EmailMessage
from num2words import num2words
from django.contrib import messages
from django.conf import settings
#from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

# Create your views here.
SOURCE_DIR=r"/home/tecblic/Downloads"
DEST_DIR=r"/home/tecblic/finance/receivables/"

#Login Page
def login_user(request):
    if request.user.is_authenticated:
        return redirect('home_page')
    else:
        if request.method=='POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user=authenticate(username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect('home_page')
            else:
                messages.info(request,'Wrong User name or Password')

        context={}
        return render(request,'tecblicapp/login.html',context)
    # if request.method=='POST':
    #     username = request.POST.get('username')
    #     password = request.POST.get('password')
    #     user = authenticate(username=username, password=password)
    #     if user is not None:
    #         auth_login(request, user)
    #         return render(request,'tecblicapp/home_page.html')
    #     else:
    #         return render(request,'tecblicapp/login.html',{'error':'Wrong Username And Password..!!'})
    # else:
    #     return render(request, 'tecblicapp/login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

#home Page
@login_required(login_url='login')
def homePage(request):
    return render(request,'tecblicapp/home_page.html',)

#Client Form
@login_required(login_url='login')
def client_detail(request):
    form=clientDetailForm()
    clientdetails1=clientDetail.objects.all()
    return render(request,'tecblicapp/add_client.html',{'form':form,'clientdetails':clientdetails1})

#Save Client Data
@login_required(login_url='login')
def save_data(request):
    if request.method=='POST':
        form=clientDetailForm(request.POST)
        if form.is_valid():
            id=request.POST['cli_id']
            name=request.POST['name']
            address=request.POST['address']
            gstin=request.POST['gstin']
            pan=request.POST['pan']
            email=request.POST['email']
            kind=request.POST['kind']
            place=request.POST['place']

            if(id==''):
                user=clientDetail(clientName=name,clientAddress=address,clientGSTIN=gstin,clientPAN=pan,clientEmail=email,kindAttn=kind,placeofSupply=place)
            else:
                user=clientDetail(id=id,clientName=name,clientAddress=address,clientGSTIN=gstin,clientPAN=pan,clientEmail=email,kindAttn=kind,placeofSupply=place)
            user.save()
            data_obj=clientDetail.objects.values()
            client_data_obj=list(data_obj)
            return JsonResponse({'status':'Save','cdata':client_data_obj})
        else:
            return JsonResponse({'status':0})
           
#Delete Client Data
@login_required(login_url='login')
def delete_data(request):
    if request.method=="POST":
        id=request.POST.get('cid')
        pi=clientDetail.objects.get(pk=id)
        pi.delete()
        return JsonResponse({'status':1})
    else:
        return JsonResponse({'status':0})

#Edit Client data
@login_required(login_url='login')
def edit_data(request):
    if request.method=="POST":
        id=request.POST.get('cid')
        client=clientDetail.objects.get(pk=id)
        client_data={"id":client.id,"name":client.clientName,"address":client.clientAddress,"gstin":client.clientGSTIN,"pan":client.clientPAN,"email":client.clientEmail,"kind":client.kindAttn,"place":client.placeofSupply}
        return JsonResponse(client_data)

#Invoice Form
@login_required(login_url='login')
def invoice_detail(request):
    invoices=invoiceForm()
    bank_details=bankDetailForm
    return render(request,'tecblicapp/invoice.html',{'invoices':invoices,'bank_details':bank_details})

#Html to pdf 
# def html_to_pdf(template_src, context_dict={}):
#      template = get_template(template_src)
#      html  = template.render(context_dict)
#      result = BytesIO()
#      pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
#      if not pdf.err:
#          return HttpResponse(result.getvalue(), content_type='application/pdf')
#      return None

# def move():
#     while True:
#         for fname in os.listdir(SOURCE_DIR):
#             if fname.lower().endswith('.pdf'):
#                     shutil.move(os.path.join(SOURCE_DIR, fname), DEST_DIR)

# Generate Invoice
@login_required(login_url='login')
def generate_invoice(request):

    if request.method == 'POST':
        form = invoiceForm(request.POST)
        if form.is_valid():
            
            inv_date = request.POST['invoice_date']
            pay_method = request.POST['payment_method']
            sac = request.POST['sac_code']
            #print(pay_method)
            pay_status = request.POST['payment_status']
            c_per_unit = request.POST['cost_per_unit']
            # g_amount=request.POST['gross_amount']
            cl_detail = request.POST['client']
            bank_detail = request.POST['bank_info']
            desc = request.POST['description']
            qty = request.POST['quantity']
            c_type = request.POST['currency_type']
            selectid = request.POST['gst_type']
          
            qty_type = request.POST['qty_type']
            t2 = request.POST['t_2']
            t3 = request.POST['t_3']
            t4 = request.POST['t_4']
            t5 = request.POST['t_5']
            #print(selectid)
            client_name = clientDetail.objects.get(id=cl_detail)

            # Invoice no auto generate
            def num():
                num_id = AutoNumber.objects.all().order_by('number').last()
                new_id = num_id.number
                new_number = int(new_id) + 1
                s=AutoNumber(number=new_number)
                s.save()
                return new_number
            a=num()
            a_strip=str(a)
            print(f"a={a}")

            def fiscal_year():
                retrieved_date = inv_date
                convert_to_date = datetime.datetime.strptime(retrieved_date, '%Y-%m-%d')
                year = convert_to_date.year
                month = convert_to_date.month
                day = convert_to_date.day
                if month >= 4 and day >= 1:
                    year_a=str(year)
                    year_b = str(year+1)
                    fiscal_year = year_a +'-' +year_b
                    return fiscal_year

                elif month <= 3 and day <= 31:
                    year_a=str(year)
                    year_b = str(year-1)
                    fiscal_year = year_b +'-'+ year_a
                    return fiscal_year

            def invoice_num():
                retrieved_date = inv_date
                #print("date=" + retrieved_date)
                convert_to_date = datetime.datetime.strptime(retrieved_date, '%Y-%m-%d')
                year = convert_to_date.year
                month = convert_to_date.month
                day = convert_to_date.day

                if month >= 4 and day >= 1:
                    year_a=str(year)
                    strip_a=year_a[2::]
                    year_b = str(year+1)
                    strip_b = year_b[2::]
                    final_invoice_num= strip_a + strip_b+ str(a_strip[1::])
                    return final_invoice_num

                elif month <= 3 and day <= 31:
                    year_a = str(year)
                    strip_a = year_a[2::]
                    year_b = str(year - 1)
                    strip_b = year_b[2::]
                    final_invoice_num = strip_b +strip_a + str(a_strip[1::])
                    return final_invoice_num

            invoice_detail_obj = invoice_num()
            # GST and Final Amount
            g = c_per_unit
            gstno = gstValue.objects.get(id=1)

            bank_detail_obj = BankDetails.objects.get(id=bank_detail)
            client_detail_obj = clientDetail.objects.get(id=cl_detail)

            if selectid == 'IMPORT':
                cgst = (int(g) * int(gstno.cgst) / 100)
                sgst = (int(g) * int(gstno.cgst) / 100)
                final_amount = (int(cgst) + int(sgst) + int(g))
                s = Invoice(invoice_no=invoice_detail_obj, invoice_date=inv_date, payment_method=pay_method,sac_code=sac,
                            payment_status=pay_status, cost_per_unit=c_per_unit, quantity=qty, currency_type=c_type,
                            t_2=t2, t_3=t3, t_4=t4, t_5=t5,
                            description=desc, client=client_name, cgst=cgst, sgst=sgst, gross_amount=final_amount,qty_type=qty_type)
                s.save()
            else:
                igst = (int(g) * int(gstno.igst) / 100)
                final_amount = (int(igst) + int(g))
                s = Invoice(invoice_no=invoice_detail_obj, invoice_date=inv_date, payment_method=pay_method,
                            sac_code=sac,t_2=t2,t_3=t3,t_4=t4,t_5=t5,
                            payment_status=pay_status, cost_per_unit=c_per_unit, quantity=qty, currency_type=c_type,
                            description=desc, client=client_name,igst=igst, gross_amount=final_amount,qty_type=qty_type)
                s.save()

            # invoice_detail_obj = request.POST.get('invoice_no')
            # print("INVOICE=" + invoice_detail_obj)
            a = datetime.datetime.now()
            invoice = Invoice.objects.get(invoice_no=invoice_detail_obj)
            fiscal_year_new=fiscal_year()
            client_name = client_detail_obj.clientName + '_'+inv_date+'_'+str(a.second)+'_'+str(fiscal_year_new)
            s_email = request.POST['send_email']
            if s_email == 'only_generate':
                filename = f'{client_name}.pdf'
                pdf = render_to_pdf('tecblicapp/invoice_pdf.html',filename,
                                    {'client': client_detail_obj, 'invoice': invoice,'pay_method':pay_method,
                                     'desc':desc, 'gstno':gstno,'sac':sac,
                                     'invoice_date' :inv_date,'bank': bank_detail_obj, 'gross_amount': final_amount,'qty_type':qty_type,
                                     'gross_amount_words': num2words(final_amount, to='cardinal', lang='en_IN')}
                                    )
                if pdf:
                    filename = f'{client_name}.pdf'
                    response = HttpResponse(pdf, content_type='application/pdf')
                    content =f"attachment; filename={filename}"
                    response['Content-Disposition'] = content
                    return response
                return HttpResponse("NOT FOUND..!!")

            elif s_email == 'generate_and_send':
                filename = f'{client_name}.pdf'
                pdf = render_to_pdf('tecblicapp/invoice_pdf.html', filename,
                                    {'client': client_detail_obj, 'invoice': invoice, 'pay_method': pay_method,
                                     'desc': desc, 'gstno': gstno, 'sac': sac,
                                     'invoice_date': inv_date, 'bank': bank_detail_obj, 'gross_amount': final_amount,
                                     'qty_type': qty_type,
                                     'gross_amount_words': num2words(final_amount, to='cardinal', lang='en_IN')}
                                    )
                to_emails = [f'{client_detail_obj.clientEmail}']
                subject = "Tecblic"
                email = EmailMessage(subject, "hello", from_email=settings.EMAIL_HOST_USER, to=to_emails)
                email.attach(filename, pdf.getvalue(), "application/pdf")
                email.send(fail_silently=False)
            return redirect('/')
    else:
        return HttpResponse('GET request')

#Bank Details Page
@login_required(login_url='login')
def bank_detail_view(request):
    form=bankForm()
    data=BankDetails.objects.all()
    return render(request,'tecblicapp/bank_details.html',{'form':form,'bankdetails':data})

#Save Bank Data
@login_required(login_url='login')
def bank_data(request):
    if request.method=='POST':
        form=bankForm(request.POST)
        if form.is_valid():
            id=request.POST['bank_id']
            name=request.POST['bank_name']
            account=request.POST['account_no']
            ifsc=request.POST['ifsc_code']
            branch=request.POST['bank_branch']
            swift=request.POST['swift_code']
            pan=request.POST['supplier_pan']
            gstin=request.POST['supplier_gstin']
            cin=request.POST['cin']
            arn=request.POST['arn']
            if(id==''):
                s=BankDetails(bank_name=name,account_no=account,ifsc_code=ifsc,swift_code=swift,supplier_pan=pan,supplier_gstin=gstin,cin=cin,arn=arn,bank_branch=branch)
            else:
                s=BankDetails(id=id,bank_name=name,account_no=account,ifsc_code=ifsc,swift_code=swift,supplier_pan=pan,supplier_gstin=gstin,cin=cin,arn=arn,bank_branch=branch)
            s.save()
            return redirect('/')
        else:
            return JsonResponse({'status':0})


#Delete bank data
@login_required(login_url='login')
def delete_bank_details(request):
    if request.method=="POST":
        id=request.POST.get('cid')
        pi=BankDetails.objects.get(pk=id)
        pi.delete()
        return JsonResponse({'status':1})
    else:
        return JsonResponse({'status':0})

#Edit bank details
@login_required(login_url='login')
def edit_bank_detail(request):
    if request.method=="POST":
        id=request.POST.get('cid')
        bank_obj=BankDetails.objects.get(pk=id)
        bank_data={"id":bank_obj.id,"bank_name":bank_obj.bank_name,"account_no":bank_obj.account_no,"ifsc":bank_obj.ifsc_code,"bank_branch":bank_obj.bank_branch,'swift_code':bank_obj.swift_code,'cin':bank_obj.cin,'supplier_pan':bank_obj.supplier_pan,"supplier_gstin":bank_obj.supplier_gstin,'arn':bank_obj.arn}
        return JsonResponse(bank_data)

@login_required(login_url='login')
def generate_invoice_and_send_mail_form(request):
    invoices=invoiceForm()
    bank_details=bankDetailForm
    return render(request,'tecblicapp/invoice_send_pdf.html',{'invoices':invoices,'bank_details':bank_details})

@login_required(login_url='login')
def check_invoice(request):
    inv_obj=Invoice.objects.all()
    return render(request,'tecblicapp/check_invoice_status_demo.html',{'inv':inv_obj})

@login_required(login_url='login')
def edit_invoice(request, pk):
    invoice = Invoice.objects.get(invoice_no=pk)
    form = invoiceForm(instance=invoice)
    if request.method == 'POST':
        form = invoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            #selectid=request.POST['gst_type']
            form.save()
            invoice_detail=Invoice.objects.all()
            inv_obj=invoice_detail.filter(invoice_no=pk)

            def fiscal_year():
                retrieved_date = str(i.invoice_date)
                convert_to_date = datetime.datetime.strptime(retrieved_date, '%Y-%m-%d')
                year = convert_to_date.year
                month = convert_to_date.month
                day = convert_to_date.day
                if month >= 4 and day >= 1:
                    year_a = str(year)
                    year_b = str(year + 1)
                    fiscal_year = year_a + '-' + year_b
                    return fiscal_year

                elif month <= 3 and day <= 31:
                    year_a = str(year)
                    year_b = str(year - 1)
                    fiscal_year = year_b + '-' + year_a
                    return fiscal_year

            for i in inv_obj:
                cost=i.cost_per_unit
                qty=i.quantity
                fiscal_year_new = fiscal_year()
                a = datetime.datetime.now()
                client_name=i.client.clientName+'_' + str(i.invoice_date) + '_' + str(a.second) + '_' + str(fiscal_year_new)
                igst=cost*qty*18/100
                cgst=cost*qty*9/100
                sgst=cost*qty*9/100
                total_amt=cost*qty
                amt_after_gst=total_amt*18/100
                final_amt=amt_after_gst+total_amt
                generate_or_mail=i.send_email

                client_email=i.client.clientEmail

            if generate_or_mail=='only_generate':    
                filename = f'{client_name}'
                pdf = render_to_pdf('tecblicapp/inv_edit.html', filename,{'invoice':inv_obj,'igst':igst,'sgst':sgst,'cgst':cgst,'final_amt':int(final_amt),'gross_amount_words': num2words(int(final_amt), to='cardinal', lang='en_IN')})
                if pdf:
                    filename = f"{client_name}.pdf"
                    response = HttpResponse(pdf, content_type='application/pdf')
                    content = f"attachment; filename={filename}"
                    response['Content-Disposition'] = content
                    return response
            else:
                filename = f'{client_name}.pdf'
                pdf = render_to_pdf('tecblicapp/inv_edit.html', filename,{'invoice':inv_obj,'igst':igst,'sgst':sgst,'cgst':cgst,'final_amt':int(final_amt),'gross_amount_words': num2words(int(final_amt), to='cardinal', lang='en_IN')})

                to_emails = [f'{client_email}']
                subject = "Tecblic"
                email = EmailMessage(subject, "hello", from_email=settings.EMAIL_HOST_USER, to=to_emails)
                email.attach(filename, pdf.getvalue(), "application/pdf")
                email.send(fail_silently=False)
                return redirect('/')
                
            return HttpResponse("NOT FOUND..!!")

        return redirect('/')
    context = {'form': form}
    return render(request, 'tecblicapp/invoice_edit_form.html', context)

@login_required(login_url='login')
def delete_invoice(request,pk):
    invoice=Invoice.objects.get(invoice_no=pk)
    if request.method =='POST':
        invoice.delete()
        return redirect('/')
    context = {'item':invoice}
    return render(request, 'tecblicapp/delete_invoice.html', context)

@login_required(login_url='login')
def gst(request):
    gst = gstValue.objects.all()
    return render(request,'tecblicapp/gst.html',{'gst':gst})


