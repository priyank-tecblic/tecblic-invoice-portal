from django import forms
from .models import *


class UserLogin(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs=
                                                    {'value': '',
                                                     'class': 'form-control'}))
    password = forms.CharField(widget=forms.TextInput(attrs=
                                                      {'type': '',
                                                       'value': "mukul",
                                                       'class': 'form-control'}))

class clientDetailForm(forms.ModelForm):
    class Meta:
        model=clientDetail
        fields='__all__'
        widgets={
            'clientName':forms.TextInput(attrs= {'class':'form-control','id':'nameid','required':'required'}),
            'clientEmail':forms.EmailInput(attrs={'class':'form-control','id':'emailid','required':'required',}),
            'clientAddress':forms.TextInput(attrs= {'class':'form-control','id':'addressid','required':'required',}),
            'clientGSTIN':forms.TextInput(attrs=     {'class':'form-control','id':'gstinid','required':'required',}),
            'clientPAN':forms.TextInput(attrs=     {'class':'form-control','id':'panid','required':'required',}),
            'kindAttn':forms.TextInput(attrs=     {'class':'form-control','id':'kindattnid','required':'required',}),
            'placeofSupply':forms.TextInput(attrs=     {'class':'form-control','id':'placeid','required':'required',}),
        }

class bankForm(forms.ModelForm):
    class Meta:
        model=BankDetails
        fields='__all__'
        widgets={
            'bank_name':forms.TextInput(attrs= {'class':'form-control','id':'banknameid','placeholder':'Bank Name','required':'required',}),
            'bank_branch':forms.TextInput(attrs= {'class':'form-control','id':'branchid','placeholder':'Bank Branch','required':'required',}),
            'account_no':forms.TextInput(attrs= {'class':'form-control','id':'accountid','placeholder':'Account No','required':'required',}),
            'ifsc_code':forms.TextInput(attrs= {'class':'form-control','id':'ifscid','placeholder':'IFSC Code','required':'required',}),
            'supplier_pan':forms.TextInput(attrs= {'class':'form-control','id':'supplier_panid','placeholder':'Supplier PAN','required':'required',}),
            'supplier_gstin':forms.TextInput(attrs= {'class':'form-control','id':'supplier_gstinid','placeholder':'Supplier GSTIN','required':'required',}),
            'swift_code':forms.TextInput(attrs= {'class':'form-control','id':'swiftcode_id','placeholder':'SWIFT Code','required':'required',}),
            'cin':forms.TextInput(attrs= {'class':'form-control','id':'cin_id','placeholder':'CIN','required':'required',}),
            'arn':forms.TextInput(attrs= {'class':'form-control','id':'arn_id','placeholder':'ARN','required':'required',}),
        }

class bankDetailForm(forms.ModelForm):
    class Meta:
        model=Bank
        fields='__all__'


class invoiceForm(forms.ModelForm):
    class Meta:
        
        model=Invoice
        #fields=['invoice_no','invoice_date']
        exclude=('cgst','sgst','igst','slug','uniqueId','gross_amount',)
        widgets={
            'invoice_no':forms.TextInput(attrs= {'class':'form-control','id':'invoiceid','placeholder':'Invoice No','readonly':True}),
            'invoice_date':forms.DateInput(attrs= {'class':'form-control','id':'dateid','placeholder':'Enter date','type': 'date', 'class': 'form_input','required':'required',}),
            'sac_code': forms.TextInput(attrs={'class': 'form-control', 'id': 'sacid', 'placeholder': 'SAC','value':'998314','required':'required',}),
            # 'cost_per_unit1':forms.NumberInput(attrs= {'class':'form-control','id':'costperunitid','placeholder':'Cost Per Unit','required':'required',}),
            # 'description1':forms.TextInput(attrs= {'class':'form-control','id':'desriptionid','placeholder':'Description','required':'required',}),
            # 'quantity1':forms.NumberInput(attrs= {'class':'form-control','id':'quantityid','placeholder':'Quantity','required':'required',}),

            # 'cost_per_unit2': forms.NumberInput(
            #     attrs={'class': 'form-control', 'id': 'costperunitid', 'placeholder': 'Cost Per Unit', }),
            # 'description2': forms.TextInput(
            #     attrs={'class': 'form-control', 'id': 'desriptionid', 'placeholder': 'Description', }),
            # 'quantity2': forms.NumberInput(
            #     attrs={'class': 'form-control', 'id': 'quantityid', 'placeholder': 'Quantity',  }),

            # 'cost_per_unit3': forms.NumberInput(
            #     attrs={'class': 'form-control', 'id': 'costperunitid', 'placeholder': 'Cost Per Unit', }),
            # 'description3': forms.TextInput(
            #     attrs={'class': 'form-control', 'id': 'desriptionid', 'placeholder': 'Description', }),
            # 'quantity3': forms.NumberInput(
            #     attrs={'class': 'form-control', 'id': 'quantityid', 'placeholder': 'Quantity', }),
            'payment_status':forms.Select(attrs = {'id':'payment_status','onchange':'changestatus()'})
        }

class invoiceupdateForm(forms.ModelForm):
    class Meta:
        model=Invoice
        fields='__all__'
        widgets={
            'invoice_no':forms.TextInput(attrs= {'class':'form-control','id':'invoiceid','placeholder':'Invoice No'}),
            'invoice_date':forms.DateInput(attrs= {'class':'form-control','id':'dateid','placeholder':'Enter date','type': 'date', 'class': 'form_input','required':'required',}),
            'cost_per_unit1':forms.TextInput(attrs= {'class':'form-control','id':'costperunitid','placeholder':'Cost Per Unit','required':'required',}),
            'cgst':forms.TextInput(attrs= {'class':'form-control','id':'cgsttid','placeholder':'CGST','required':'required',}),
            'sgst':forms.TextInput(attrs= {'class':'form-control','id':'sgsttid','placeholder':'SGST','required':'required',}),
            'gross_amount':forms.TextInput(attrs= {'class':'form-control','id':'gross_amount_id','placeholder':'Gross Amount','required':'required',}),
            'description1':forms.TextInput(attrs= {'class':'form-control','id':'desriptionid','placeholder':'Description','required':'required',}),
            'quantity1':forms.NumberInput(attrs= {'class':'form-control','id':'quantityid','placeholder':'Quantity','required':'required',}),
        }
class InvoiceDetailForm(forms.ModelForm):
    class Meta:
        model = InvoiceDesription
        fields = ['description','quantity','cost_per_unit']
        widgets={
           'cost_per_unit':forms.NumberInput(attrs= {'class':'form-control','id':'costperunitid','placeholder':'Cost Per Unit','required':'required',}),
            'description':forms.TextInput(attrs= {'class':'form-control','id':'desriptionid','placeholder':'Description','required':'required',}),
            'quantity':forms.NumberInput(attrs= {'class':'form-control','id':'quantityid','placeholder':'Quantity','required':'required',})
        }