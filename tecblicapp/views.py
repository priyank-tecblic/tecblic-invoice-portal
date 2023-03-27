import os.path
import time

from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
import datetime
from .forms import bankDetailForm, bankForm, clientDetailForm, invoiceForm
from .utils import render_to_pdf
from .models import BankDetails, clientDetail,Invoice, AutoNumber,gstValue,InvoiceDesription
from django.core.mail import EmailMessage
from num2words import num2words
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
import csv

# Create your views here.
SOURCE_DIR=r"/home/tecblic/Downloads"
DEST_DIR=r"/home/tecblic/finance/receivables/"
inv = None
def append_to_csv():
    invoice = Invoice.objects.all().values()
    isExist = os.path.exists(DEST_DIR)

    def makeinvoice():
        with open(DEST_DIR + 'tecblic_invoice.csv', 'w') as f:
            fieldname = ['Invoice No', 'Invoice Date', 'Client Name', 'Description of services', 'Currency',
                         'Invoice Amount', 'SGST', 'CGST', 'IGST', 'Payment Status'
                         ]
            writer = csv.DictWriter(f, fieldnames=fieldname)
            writer.writeheader()

            for i in invoice:
                dict = {}
                dict['Invoice No'] = i["invoice_no"]
                dict['Invoice Date'] = i["invoice_date"]
                dict['Invoice Amount'] = i["gross_amount"]

                client = clientDetail.objects.get(id=i["client_id"])
                dict['Client Name'] = client

                dict['Description of services'] = i["description"]
                dict['Currency'] = i["currency_type"]
                dict['Invoice Amount'] = i["gross_amount"]
                dict['SGST'] = i["sgst"]
                dict['CGST'] = i["cgst"]
                dict['IGST'] = i["igst"]
                dict['Payment Status'] = i["payment_status"]
                writer.writerow(dict)

    if not isExist:
        os.makedirs(DEST_DIR)
        makeinvoice()
    if isExist:
        makeinvoice()
# append_to_csv()
#Login Pager
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
                # append_to_csv()
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
filter_data = None
def logout_user(request):
    logout(request)
    return redirect('login')

#home Page
@login_required(login_url='login')
def homePage(request):
    invoice = Invoice.objects.all()
    # append_to_csv()
    return render(request,'tecblicapp/home_page.html',)

#Client Form
@login_required(login_url='login')
def client_detail(request):
    form=clientDetailForm()
    clientdetails1=clientDetail.objects.all()
    paginator = Paginator(clientdetails1,5)
    page_number = request.GET.get('page',paginator)
    finaldata =  paginator.get_page(page_number)
    totalpage = finaldata.paginator.num_pages
    return render(request,'tecblicapp/add_client.html',{'clientdetails':finaldata,'totalpages':[n+1 for n in range(totalpage)]})

    return render(request,'tecblicapp/add_client.html',{'form':form,'clientdetails':clientdetails1})

#Save Client Data
@login_required(login_url='login')
def save_data(request):
    if request.method=='POST':
        form=clientDetailForm(request.POST)
        if form.is_valid():
            id=request.POST.get('cli_id','')
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
            return redirect("/add")
            # return JsonResponse({'status':'Save','cdata':client_data_obj})
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
    id=request.GET.get('cid')
    client=clientDetail.objects.filter(pk=id)
    # client_data={"id":client.id,"name":client.clientName,"address":client.clientAddress,"gstin":client.clientGSTIN,"pan":client.clientPAN,"email":client.clientEmail,"kind":client.kindAttn,"place":client.placeofSupply}
    return render(request,'tecblicapp/edit_client.html',{"client_data":client})

#Invoice Form
@login_required(login_url='login')
def invoice_detail(request):
    invoices=invoiceForm()
    bank_details=bankDetailForm
    clientActive = clientDetail.objects.filter(activeClient=True)
    bank = BankDetails.objects.all()
    return render(request,'tecblicapp/invoice.html',{'invoices':invoices,'bank_details':bank_details,'client_details':clientActive,'bank':bank})

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
            # if 'payment_method' not in request.POST:
            #     pay_method = '----'
            # else:
            pay_method = request.POST['payment_method']
            sac = request.POST['sac_code']
            #print(pay_method)
            pay_status = request.POST['payment_status']
            # g_amount=request.POST['gross_amount']
            cl_detail = request.POST['client']
            bank_detail = request.POST['bank_info']
            c_type = request.POST['currency_type']
            selectid = request.POST['gst_type']

            qty_type = request.POST['qty_type']
            t2 = request.POST['t_2']
            t3 = request.POST['t_3']
            t4 = request.POST['t_4']
            t5 = request.POST['t_5']
            quantity = []
            desc = []
            c_per_unit = []
            k = 1
            a = "hello"
            while True:
                a=request.POST.get(f"description{k}","")
                if a=="":
                    break
                desc.append(request.POST.get(f"description{k}",""))
                quantity.append(int(request.POST.get(f"quantity{k}",0)))
                c_per_unit.append(int(request.POST.get(f"cost{k}",0)))
                k=k+1
            print("description=",desc)
            print("qty=",quantity)
            print("c_per_unit=",c_per_unit)

            # desc1 = request.POST['description1']

            # desc2 = request.POST['description2']
            # desc3 = request.POST['description3']
            # c_per_unit1 = request.POST['cost_per_unit1']
            # qty1 = request.POST['quantity1']
            # c_per_unit2 = request.POST['cost_per_unit2']
            # qty2 = request.POST['quantity2']
            # c_per_unit3 = request.POST['cost_per_unit3']
            # print('**************************************************', c_per_unit3)
            # qty3 = request.POST['quantity3']


            #print(selectid)
            client_name = clientDetail.objects.get(id=cl_detail)
            
            # Invoice no auto generate
            def num():                
                num_id = AutoNumber.objects.all().order_by('number').last()
                if num_id is None:
                    new_number = 1000
                else:
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
            g1=[]

            # g1 = float(c_per_unit1) * float(qty1)
            # g2 = float(c_per_unit2) * float(qty2)
            # g3 = float(c_per_unit3) * float(qty3)
            g= 0
            qty = 0
            for (a, b) in zip(quantity,c_per_unit):
                qty = a+qty
                g1.append(float(a)*float(b))
                g = g+(float(a)*float(b))
            
        

            # g = g1 + g2 + g3
            # print("AMOUNT======================", g)
            # qty = float(qty1) + float(qty2) + float(qty3)
            print("QTY======================", qty,g)

            total_cost = g

            gstno = gstValue.objects.get(id=1)

            bank_detail_obj = BankDetails.objects.get(id=bank_detail)
            client_detail_obj = clientDetail.objects.get(id=cl_detail)

            if selectid == 'DOMESTIC':
                cgst = round((total_cost * float(gstno.cgst) / 100),2)
                print("CGST=====================", cgst)
                sgst = round((total_cost * float(gstno.sgst) / 100),2)
                print("SGST=====================", sgst)
                a = float(float(cgst) + float(sgst) + float(total_cost))
                final_amount = round(a,2)

                s = Invoice(invoice_no=invoice_detail_obj, invoice_date=inv_date, payment_method=pay_method,sac_code=sac,
                            payment_status=pay_status,  currency_type=c_type,
                            t_2=t2, t_3=t3, t_4=t4, t_5=t5,bank=bank_detail_obj,client=client_name, cgst=cgst,
                            sgst=sgst, gross_amount=final_amount,qty_type=qty_type)
                s.save()

            elif selectid == 'Inter State':
                igst = round((total_cost * float(gstno.igst) / 100), 2)
                print("IGST=====================", igst)

                a = float(float(igst) + float(total_cost))
                final_amount = round(a, 2)
                print("FINAL AMOUNT==============",final_amount)

                s = Invoice(invoice_no=invoice_detail_obj, invoice_date=inv_date, payment_method=pay_method,
                            sac_code=sac,
                            payment_status=pay_status, currency_type=c_type,
                            t_2=t2, t_3=t3, t_4=t4, t_5=t5, bank=bank_detail_obj, client=client_name, igst=igst,
                            gross_amount=final_amount, qty_type=qty_type)
                s.save()
            else:
                # final_amount = (int(igst) + int(g))
                igst = round(float(g),2)
                a = round(float(g), 2)
                final_amount = float(a)
                s = Invoice(invoice_no=invoice_detail_obj, invoice_date=inv_date, payment_method=pay_method,
                            sac_code=sac,t_2=t2,t_3=t3,t_4=t4,t_5=t5,
                            currency_type=c_type,bank=bank_detail_obj,
                            client=client_name,igst=0, gross_amount=final_amount,qty_type=qty_type)
                s.save()
            for (a, b,c) in zip(quantity,c_per_unit,desc):
                invoicedesription = InvoiceDesription(description=c,quantity=a,cost_per_unit=b,invoice = s)
                invoicedesription.save()
            # invoice_detail_obj = request.POST.get('invoice_no')
            # print("INVOICE=" + invoice_detail_obj)
            a = datetime.datetime.now()
            invoice = Invoice.objects.get(invoice_no=invoice_detail_obj)
            fiscal_year_new=fiscal_year()
            client_name = client_detail_obj.clientName + '_'+inv_date+'_'+str(a.second)+'_'+str(fiscal_year_new)
            s_email = request.POST['send_email']
            a = num2words(final_amount, to='cardinal', lang='en_IN')
            convert_word_num = a.replace(",", "")
            if s_email == 'only_generate':
                filename = f'{client_name}.pdf'
                # pdf = render_to_pdf('tecblicapp/invoice_pdf.html',filename,
                #                     {'client': client_detail_obj, 'invoice': invoice,'pay_method':pay_method,
                #                      'desc1': desc1, 'desc2': desc2, 'desc3': desc3, 'gstno':gstno,'sac':sac, 'total':total_cost,
                #                      'invoice_date' :inv_date,'bank': bank_detail_obj, 'gross_amount': final_amount,
                #                      'qty_type':qty_type, 'g1':round(g1,2),'g2':round(g2,2),'g3':round(g3,2),
                #                      'gross_amount_words':convert_word_num.title()}
                #                     )
                pdf = render_to_pdf('tecblicapp/invoice_pdf.html',filename,
                                    {'client': client_detail_obj, 'invoice': invoice,'pay_method':pay_method,
 'gstno':gstno,'sac':sac, 'total':total_cost,
                                     'invoice_date' :inv_date,'bank': bank_detail_obj, 'gross_amount': final_amount,
                                     'qty_type':qty_type,
                                     'gross_amount_words':convert_word_num.title(),'zip':zip(desc,quantity,c_per_unit,g1)}
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
                pdf = render_to_pdf('tecblicapp/invoice_pdf.html',filename,
                                    {'client': client_detail_obj, 'invoice': invoice,'pay_method':pay_method,
 'gstno':gstno,'sac':sac, 'total':total_cost,
                                     'invoice_date' :inv_date,'bank': bank_detail_obj, 'gross_amount': final_amount,
                                     'qty_type':qty_type,
                                     'gross_amount_words':convert_word_num.title(),'zip':zip(desc,quantity,c_per_unit,g1)}
                                    )
                to_emails = [f'{client_detail_obj.clientEmail}']
                subject = "Tecblic"
                email = EmailMessage(subject, "hello", from_email=settings.EMAIL_HOST_USER, to=to_emails)
                email.attach(filename, pdf.getvalue(), "application/pdf")
                email.send(fail_silently=False)

            return redirect('/')
        # append_to_csv()
    else:
        return HttpResponse('GET request')

#Bank Details Page
@login_required(login_url='login')
def bank_detail_view(request):
    form=bankForm()
    data=BankDetails.objects.all()
    paginator = Paginator(data,5)
    page_number = request.GET.get('page',paginator)
    finaldata =  paginator.get_page(page_number)
    totalpage = finaldata.paginator.num_pages
    return render(request,'tecblicapp/bank_details.html',{'bankdetails':finaldata,'totalpages':[n+1 for n in range(totalpage)]})
    # return render(request,'tecblicapp/bank_details.html',{'form':form,'bankdetails':data})

#Save Bank Data
@login_required(login_url='login')
def bank_data(request):
    if request.method=='POST':
        form=bankForm(request.POST)
        if form.is_valid():
            id=request.POST.get('bank_id')
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
            return redirect('/bank')
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
    print("-------------------------------")
    id=request.GET.get('pk')
    bank_obj=BankDetails.objects.filter(id=id)
    print(bank_obj)
    # bank_data={"id":bank_obj.id,"bank_name":bank_obj.bank_name,"account_no":bank_obj.account_no,"ifsc":bank_obj.ifsc_code,"bank_branch":bank_obj.bank_branch,'swift_code':bank_obj.swift_code,'cin':bank_obj.cin,'supplier_pan':bank_obj.supplier_pan,"supplier_gstin":bank_obj.supplier_gstin,'arn':bank_obj.arn}
    return render(request,'tecblicapp/edit_bank.html',{"bank":bank_obj})

@login_required(login_url='login')
def generate_invoice_and_send_mail_form(request):
    invoices=invoiceForm()
    bank_details=bankDetailForm
    return render(request,'tecblicapp/invoice_send_pdf.html',{'invoices':invoices,'bank_details':bank_details})

@login_required(login_url='login')
def filter_invoice(request):
    global filter_data
    if request.method == "POST":
        filter_data = Invoice.objects.filter(Q(invoice_date__gte = request.POST['startdate'])& Q(invoice_date__lte = request.POST['enddate']))
        paginator = Paginator(filter_data,5)
        page_number = request.GET.get('page')
        finaldata =  paginator.get_page(page_number)
        totalpage = finaldata.paginator.num_pages
        return render(request,'tecblicapp/filter.html',{'inv':finaldata,'totalpages':[n+1 for n in range(totalpage)]})
    else:
        paginator = Paginator(filter_data,5)
        page_number = request.GET.get('page')
        finaldata =  paginator.get_page(page_number)
        totalpage = finaldata.paginator.num_pages
        return render(request,'tecblicapp/filter.html',{'inv':finaldata,'totalpages':[n+1 for n in range(totalpage)]})

@login_required(login_url='login')
def check_invoice(request):
    inv_obj=Invoice.objects.filter(is_deleted=False)
    paginator = Paginator(inv_obj,5)
    page_number = request.GET.get('page')
    finaldata =  paginator.get_page(page_number)
    totalpage = finaldata.paginator.num_pages
    return render(request,'tecblicapp/check_invoice_status_demo.html',{'inv':finaldata,'totalpages':[n+1 for n in range(totalpage)]})

@login_required(login_url='login')
def edit_invoice(request, pk):
    invoice = Invoice.objects.get(invoice_no=pk)
    invoice_det = InvoiceDesription.objects.filter(invoice=invoice)
    form = invoiceForm(instance=invoice)
    if request.method == 'POST':
        form = invoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            #selectid=request.POST['gst_type']
            form.save()

            invoice_detail=Invoice.objects.all()
            # InvoiceDesription.objects.filter(invoice = )
            inv_obj=invoice_detail.filter(invoice_no=pk)
            invoice_det = InvoiceDesription.objects.filter(invoice=inv_obj[0])
            quantity = []
            desc = []
            c_per_unit = []
            k = 1
            a = "hello"
            while True:
                a=request.POST.get(f"description{k}","")
                if a=="":
                    break
                desc.append(request.POST.get(f"description{k}",""))
                quantity.append(float(request.POST.get(f"quantity{k}",0)))
                c_per_unit.append(float(request.POST.get(f"cost{k}",0)))
                k=k+1
            def fiscal_year():
                retrieved_date = i.invoice_date
                convert_to_date = datetime.datetime.strptime(str(retrieved_date), '%Y-%m-%d')
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
            g1=[]
            g= 0
            qty = 0
            for (a, b) in zip(quantity,c_per_unit):
                qty = a+qty
                g1.append(float(a)*float(b))
                g = g+(float(a)*float(b))

            for i in inv_obj:
                selcid = request.POST.get('gst_type')
                print("SELECTTTTTTTTTTT", selcid)

                # first = i.cost_per_unit1 * i.quantity1
                # second = i.cost_per_unit2 * i.quantity2
                # third = i.cost_per_unit3 * i.quantity3

                total = g

                fiscal_year_new = fiscal_year()
                a = datetime.datetime.now()
                client_name=i.client.clientName+'_' + str(i.invoice_date) + '_' + str(a.second) + '_' + str(fiscal_year_new)

                if selcid=="DOMESTIC":
                    cgst = round(total * 9 / 100,2)
                    sgst = round(total * 9 / 100,2)
                    igst=0
                    total_amt = total
                    amt_after_gst = total_amt + cgst + sgst
                    a = round(amt_after_gst,2)
                    final_amt = float(a)
                    generate_or_mail=i.send_email
                    client_email=i.client.clientEmail
                    inv_obj.update(cgst=cgst,
                            sgst=sgst,igst=0,gross_amount=final_amt)

                elif selcid=="Inter State":
                    cgst=0
                    sgst=0
                    igst = round(total * 18 / 100,2)
                    total_amt = total
                    amt_after_gst = total_amt + igst
                    a = round(amt_after_gst,2)
                    final_amt = float(a)
                    generate_or_mail=i.send_email
                    client_email=i.client.clientEmail
                    inv_obj.update(cgst=cgst,
                            sgst=sgst,igst=igst, gross_amount=final_amt)

                else:
                    cgst = 0
                    sgst = 0
                    igst=0
                    total_amt = total
                    a = round(total_amt,2)
                    final_amt = float(a)
                    generate_or_mail = i.send_email
                    client_email = i.client.clientEmail
                    inv_obj.update(cgst=cgst,
                            sgst=sgst,igst=igst,gross_amount=final_amt)

            a = num2words(final_amt, to='cardinal', lang='en_IN')
            convert_word_num = a.replace(",", "")
            for a,b,c,d in zip(desc,quantity,c_per_unit,invoice_det):
                d.description = a
                d.quantity = b
                d.cost_per_unit = c
                d.save()
                print("d = ",d.description)

            if generate_or_mail=='only_generate':
                filename = f'{client_name}'
                pdf = render_to_pdf('tecblicapp/inv_edit.html', filename,{'invoice':inv_obj, 'igst':igst,
                      'inv_date':str(invoice.invoice_date),'sgst':sgst,'cgst':cgst,'final_amt':final_amt,
                      'gross_amount_words': convert_word_num.title(),'zip':zip(desc,quantity,c_per_unit,g1)})
                if pdf:
                    filename = f"{client_name}.pdf"
                    response = HttpResponse(pdf, content_type='application/pdf')
                    content = f"attachment; filename={filename}"
                    response['Content-Disposition'] = content
                    # return response 
                    return redirect('/check')

            else:
                filename = f'{client_name}.pdf'
                pdf = render_to_pdf('tecblicapp/inv_edit.html', filename,{'invoice':inv_obj, 'igst':igst,
                      'inv_date':str(invoice.invoice_date),'sgst':sgst,'cgst':cgst,'final_amt':final_amt,
                      'gross_amount_words': convert_word_num.title(),'zip':zip(desc,quantity,c_per_unit,g1)})
                to_emails = [f'{client_email}']
                subject = "Tecblic"
                email = EmailMessage(subject, "hello", from_email=settings.EMAIL_HOST_USER, to=to_emails)
                email.attach(filename, pdf.getvalue(), "application/pdf")
                email.send(fail_silently=False)
                return redirect('/check')
            return HttpResponse("NOT FOUND..!!")

        return redirect('/check')
    # append_to_csv()
    print("invoice_detail = >",invoice_det)
    client = clientDetail.objects.all()
    bank = BankDetails.objects.all()
    context = {'invoice': invoice,'invoice_detail':invoice_det,"client":client,"bank":bank}
    return render(request, 'tecblicapp/invoice_edit_form.html', context)

@login_required(login_url='login')
def delete_invoice(request,pk):
    invoice=Invoice.objects.get(invoice_no=pk)
    page = request.GET.get('page')
    invoice.soft_delete()
    return redirect(f'/check?page={page}')
    context = {'item':invoice}
    return render(request, 'tecblicapp/delete_invoice.html', context)

@login_required(login_url='login')
def gst(request):
    gst = gstValue.objects.all()
    return render(request,'tecblicapp/gst.html',{'gst':gst})

@login_required(login_url='login')
def banksearch(request):
    global inv
    query = request.GET.get('query','')
    if query.isnumeric():
        inv =BankDetails.objects.filter(Q(bank_name__contains=query)|Q(account_no__contains=int(query))|Q(ifsc_code__contains=query)|Q(bank_branch__contains=query)|Q(swift_code__contains = query)|Q(cin__contains = query)|Q(supplier_pan__contains = query)|Q(supplier_gstin__contains = query)|Q(arn__contains = query))
    else:            
        inv =BankDetails.objects.filter(Q(bank_name__contains=query)|Q(account_no__contains=query)|Q(ifsc_code__contains=query)|Q(bank_branch__contains=query)|Q(swift_code__contains = query)|Q(cin__contains = query)|Q(supplier_pan__contains = query)|Q(supplier_gstin__contains = query)|Q(arn__contains = query))

    paginator = Paginator(inv,5)
    page_number = request.GET.get('page')
    ServiceDatafinal = paginator.get_page(page_number)
    totalpage = ServiceDatafinal.paginator.num_pages
    params = {'inv':ServiceDatafinal,'totalpages':[n+1 for n in range(totalpage)]}
    return render(request,'tecblicapp/search_bank.html',params)

@login_required(login_url='login')
def clientsearch(request):
    global inv
    query = request.GET.get('query','')
    inv =clientDetail.objects.filter(Q(clientName__contains=query)|Q(clientEmail__contains=query)|Q(clientAddress__contains=query)|Q(clientGSTIN__contains=query)|Q(clientPAN__contains = query)|Q(kindAttn__contains = query)|Q(placeofSupply__contains = query))
    
    paginator = Paginator(inv,5)
    page_number = request.GET.get('page')
    ServiceDatafinal = paginator.get_page(page_number)
    totalpage = ServiceDatafinal.paginator.num_pages
    params = {'inv':ServiceDatafinal,'totalpages':[n+1 for n in range(totalpage)]}
    print("im here ---------------",inv)
    return render(request,'tecblicapp/search_client.html',params)

@login_required(login_url='login')
def search(request):
    global inv
    query = request.GET.get('query',0)
    if query==0:
        pass
    else:
        if query.isnumeric():
            inv =Invoice.objects.filter(Q(invoice_no__contains = int(query)))
        else:            
            inv =Invoice.objects.filter(Q(payment_method__contains=query)|Q(sac_code__contains=query)|Q(invoice_date__contains=query)|Q(client__clientName__contains = query)|Q(gst_type__contains = query)|Q(currency_type__contains = query)|Q(send_email__contains = query))

    paginator = Paginator(inv,5)
    page_number = request.GET.get('page')
    ServiceDatafinal = paginator.get_page(page_number)
    totalpage = ServiceDatafinal.paginator.num_pages
    params = {'inv':ServiceDatafinal,'totalpages':[n+1 for n in range(totalpage)]}
    return render(request,'tecblicapp/search.html',params)


def test(request):
    return render(request,'tecblicapp/test.html')

def activeClient(request):
    
    client = clientDetail.objects.get(id=request.GET.get('idd'))
    
    if request.GET.get('radio') == 'true':
        print("im in true",client)
        client.activeClient = True
    else:
        print("im in false")
        client.activeClient = False
    client.save()
    page=request.GET.get('page')
    return redirect(f"/add?page={page}")

def shelveInvoice(request):
    inv_obj=Invoice.objects.filter(is_deleted=True)
    paginator = Paginator(inv_obj,5)
    page_number = request.GET.get('page')
    finaldata =  paginator.get_page(page_number)
    totalpage = finaldata.paginator.num_pages
    return render(request,'tecblicapp/shelve_invoice.html',{'inv':finaldata,'totalpages':[n+1 for n in range(totalpage)]})

def unshelveInvoice(request,pk):
    invoice=Invoice.objects.get(invoice_no=pk)
    page = request.GET.get('page')
    invoice.restore()
    return redirect(f'/shelve?page={page}')

def downloadInvoice(request,pk):
    invoice = Invoice.objects.get(invoice_no=pk)
    invoice_det = InvoiceDesription.objects.filter(invoice=invoice)

    invoice_detail=Invoice.objects.all()
    # InvoiceDesription.objects.filter(invoice = )
    inv_obj=invoice_detail.filter(invoice_no=pk)
    invoice_det = InvoiceDesription.objects.filter(invoice=inv_obj[0])
    quantity = []
    desc = []
    c_per_unit = []
    k = 1
    a = "hello"
    # while True:
    #     a=request.POST.get(f"description{k}","")
    #     if a=="":
    #         break
    #     desc.append(request.POST.get(f"description{k}",""))
    #     quantity.append(float(request.POST.get(f"quantity{k}",0)))
    #     c_per_unit.append(float(request.POST.get(f"cost{k}",0)))
    for i in invoice_det:
        desc.append(i.description)
        quantity.append(i.quantity)
        c_per_unit.append(i.cost_per_unit)
        k=k+1
        
    def fiscal_year():
        retrieved_date = i.invoice_date
        convert_to_date = datetime.datetime.strptime(str(retrieved_date), '%Y-%m-%d')
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
    g1=[]
    g= 0
    qty = 0
    for (a, b) in zip(quantity,c_per_unit):
        qty = a+qty
        g1.append(float(a)*float(b))
        g = g+(float(a)*float(b))

    for i in inv_obj:
        selcid = inv_obj[0].gst_type
        print("SELECTTTTTTTTTTT", selcid)

        # first = i.cost_per_unit1 * i.quantity1
        # second = i.cost_per_unit2 * i.quantity2
        # third = i.cost_per_unit3 * i.quantity3

        total = g

        fiscal_year_new = fiscal_year()
        a = datetime.datetime.now()
        client_name=i.client.clientName+'_' + str(i.invoice_date) + '_' + str(a.second) + '_' + str(fiscal_year_new)

        if selcid=="DOMESTIC":
            cgst = round(total * 9 / 100,2)
            sgst = round(total * 9 / 100,2)
            igst=0
            total_amt = total
            amt_after_gst = total_amt + cgst + sgst
            a = round(amt_after_gst,2)
            final_amt = float(a)
            generate_or_mail=i.send_email
            client_email=i.client.clientEmail
            inv_obj.update(cgst=cgst,
                    sgst=sgst,igst=0,gross_amount=final_amt)

        elif selcid=="Inter State":
            cgst=0
            sgst=0
            igst = round(total * 18 / 100,2)
            total_amt = total
            amt_after_gst = total_amt + igst
            a = round(amt_after_gst,2)
            final_amt = float(a)
            generate_or_mail=i.send_email
            client_email=i.client.clientEmail
            inv_obj.update(cgst=cgst,
                    sgst=sgst,igst=igst, gross_amount=final_amt)

        else:
            cgst = 0
            sgst = 0
            igst=0
            total_amt = total
            a = round(total_amt,2)
            final_amt = float(a)
            generate_or_mail = i.send_email
            client_email = i.client.clientEmail
            inv_obj.update(cgst=cgst,
                    sgst=sgst,igst=igst,gross_amount=final_amt)

    a = num2words(final_amt, to='cardinal', lang='en_IN')
    convert_word_num = a.replace(",", "")
    for a,b,c,d in zip(desc,quantity,c_per_unit,invoice_det):
        d.description = a
        d.quantity = b
        d.cost_per_unit = c
        d.save()
        print("d = ",d.description)


    filename = f'{client_name}'
    pdf = render_to_pdf('tecblicapp/inv_edit.html', filename,{'invoice':inv_obj, 'igst':igst,
            'inv_date':str(invoice.invoice_date),'sgst':sgst,'cgst':cgst,'final_amt':final_amt,
            'gross_amount_words': convert_word_num.title(),'zip':zip(desc,quantity,c_per_unit,g1)})
    if pdf:
        filename = f"{client_name}.pdf"
        response = HttpResponse(pdf, content_type='application/pdf')
        content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
        return response 
        return redirect('/check')