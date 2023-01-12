
from unicodedata import name
from django.urls import path
from . import views

urlpatterns =[
    path('home',views.homePage,name='home_page'),
    path('', views.login_user, name="login"),
    path('logout', views.logout_user, name="logout"),
    path('add',views.client_detail,name='client-detail'),
    path('save/',views.save_data,name='save'),
    path('delete/',views.delete_data,name='delete'),
    path('edit/',views.edit_data,name='edit'),
    path('invoice/',views.invoice_detail,name="invoice_details"),
    path('generate/',views.generate_invoice,name='generate_invoice'),
    path('bank',views.bank_detail_view,name='bank-detail'),
    path('bank_form',views.bank_data,name='bank_data'),
    path('delete_b',views.delete_bank_details,name='delete_banks'),
    path('edit_b',views.edit_bank_detail,name='edit_bank'),
    path('inv_send',views.generate_invoice_and_send_mail_form,name='invoice_send'),
    path('check', views.check_invoice, name="check_invoices"),
    path('edit_invoice/<int:pk>/', views.edit_invoice, name="edit_invoice"),
    path('delete_invoice/<int:pk>/', views.delete_invoice, name='delete_invoice'),
    path('gst', views.gst, name="gst"),
    path('filter/',views.filter_invoice,name="filter")
    

    #path('inv_send_mail',views.generate_invoice_send mail,name='invoice_send_mail'),

]