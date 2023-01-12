from django.db import models
# Create your models here.

class clientDetail(models.Model):
    clientName=models.CharField(max_length=50,null=True,blank=True)
    clientEmail=models.EmailField(null=True,blank=True)
    clientAddress=models.CharField(max_length=200,null=True,blank=True)
    clientGSTIN=models.CharField(max_length=15,null=True,blank=True)
    clientPAN=models.CharField(max_length=10,null=True,blank=True)
    kindAttn=models.CharField(max_length=40,null=True,blank=True)
    placeofSupply=models.CharField(max_length=40,null=True,blank=True)

    def __str__(self):
        return self.clientName

class clientList(models.Model):
    client_list=models.ForeignKey(clientDetail,on_delete=models.CASCADE)

class AutoNumber(models.Model):
    number = models.IntegerField(primary_key=True, default=100001)

class gstValue(models.Model):
    cgst = models.CharField(max_length=20,null=True, blank=True)
    sgst = models.CharField(max_length=20,null=True, blank=True)
    igst = models.CharField(max_length=20,null=True, blank=True)

class BankDetails(models.Model):
    bank_name=models.CharField(max_length=40,null=True,blank=True)
    account_no=models.CharField(max_length=30,null=True,blank=True)
    ifsc_code=models.CharField(max_length=11,null=True,blank=True)
    bank_branch=models.CharField(max_length=40,null=True,blank=True)
    swift_code=models.CharField(max_length=11,null=True,blank=True)
    cin=models.CharField(max_length=21,null=True,blank=True)
    supplier_pan=models.CharField(max_length=10,null=True,blank=True)
    supplier_gstin=models.CharField(max_length=15,null=True,blank=True)
    arn=models.CharField(max_length=30,null=True,blank=True)

    def __str__(self):
        return self.bank_name
  

class Invoice(models.Model):
    Method = [
    ('----','----'),
    ('Cash', 'Cash'),
    ('Online', 'Online'),
    ('Cheque', 'Cheque'),
    ('Swift Transfer', 'Swift Transfer'),
    ]

    imp=[
        ('DOMESTIC','DOMESTIC'),
        ('EXPORT','EXPORT'),
        ('Inter State', 'Inter State'),

    ]

    Currency = [
    ('INR', 'INR'),
    ('USD', 'USD'),
    ('EUR', 'EUR'),
    ]

    STATUS = [
    ('PENDING', 'PENDING'),
    ('PAID', 'PAID'),
   
    ]

    emails=[
        ('only_generate','Only Generate'),
        ('generate_and_send','Generate And Send Mail')
    ]
    quantity_type = [
        ("No's", "No's"),
        ('HRS', 'HRS'),
        ('DAY', 'DAY'),

    ]

    invoice_no = models.IntegerField(primary_key=True, blank=True)
    sac_code = models.CharField(null=True, blank=True, max_length=6)
    invoice_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(choices=Method, default='Cash', max_length=100)
    payment_status = models.CharField(choices=STATUS, default='PAID', max_length=100)
    gross_amount=models.IntegerField(null=True,blank=True)
    cgst = models.CharField(max_length=20, null=True, blank=True,default=0)
    sgst = models.CharField(max_length=20, null=True, blank=True,default=0)
    igst = models.CharField(max_length=20, null=True, blank=True,default=0)
    currency_type=models.CharField(choices=Currency,max_length=5,default='INR')
    qty_type = models.CharField(choices=quantity_type, default='HRS', max_length=5)
    gst_type=models.CharField(choices=imp,default='DOMESTIC',max_length=20)

    # description1 = models.CharField(max_length=100, null=True, blank=True)
    # description2 = models.CharField(max_length=100, null=True, blank=True, default="")
    # description3 = models.CharField(max_length=100, null=True, blank=True, default="")

    # quantity1 = models.DecimalField(max_digits =9,null=True, blank=True, decimal_places=2)
    # cost_per_unit1 = models.DecimalField(max_digits =9,null=True, blank=True, decimal_places=2)
    # quantity2 = models.DecimalField(max_digits =9,null=True, blank=True, default=0, decimal_places=2)
    # cost_per_unit2 = models.DecimalField(max_digits =9,null=True, blank=True, default=0, decimal_places=2)
    # quantity3 = models.DecimalField(max_digits =9,null=True, blank=True, default=0, decimal_places=2)
    # cost_per_unit3 = models.DecimalField(max_digits =9,null=True, blank=True, default=0, decimal_places=2)

    t_2 = models.TextField(
        default="2) This Bill is payable by Electronic transfer/ DD/ Cheque in favor of Tecblic Private Limited. For payment made by electronic fund transfer, please send details to accounts@tecblic.com (Invoice number, Invoice amount, Tecblic Bank name and Account number, Payment date, Amount paid, TDS if applicable). Queries can be sent to us at accounts@tecblic.com.")
    t_3 = models.TextField(default="3) Please make payment within 7 days of receipt of this invoice.")
    t_4 = models.TextField(
        default="4) TDS certificate, if applicable, should be issued in favor of Tecblic Private Limited, AAHCT7338J of the Billing Entity and emailed to accounts@tecblic.com or couriered to above address.")
    t_5 = models.TextField(
        default="5) We declare that invoice shows the actual price of goods/services described and that all particulars are correct.")
    #Supplier Bank Details

    #RELATED fields
    client = models.ForeignKey(clientDetail, blank=True, null=True, on_delete=models.SET_NULL)
    send_email=models.CharField(choices=emails,max_length=20,default='only_generate')
    bank = models.ForeignKey(BankDetails, blank=True, null=True, on_delete=models.SET_NULL)

    #Utility fields
    date_created = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True,blank=True, null=True)


class Bank(models.Model):
    bank_info=models.ForeignKey(BankDetails,max_length=50,null=True,blank=True,on_delete=models.SET_NULL)

    
class InvoiceDesription(models.Model):
    description_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.DecimalField(max_digits =9,null=True, blank=True, decimal_places=2)
    cost_per_unit = models.DecimalField(max_digits =9,null=True, blank=True, decimal_places=2)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)