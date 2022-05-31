from django.db import models
from apps.choises import *
from django.contrib.auth.models import User
from decimal import Decimal
import uuid


class AbstractModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_user_id = models.CharField(max_length=250)
    is_active = models.CharField(max_length=50, choices=STATUS_CHOICES, default='1')

    class Meta:
        abstract = True
        ordering = ('-created_date',)


class AanAngilal(AbstractModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, null=True)


class DedStantsAngilal(AbstractModel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True)


class DedStants(AbstractModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    angilal = models.ForeignKey(DedStantsAngilal, null=True)
    guidliin_trans = models.CharField(max_length=255, null=True)
    huchdeliin_trans = models.CharField(max_length=255, null=True)
    chadal = models.CharField(max_length=255, null=True)
    s_aimag = models.CharField(max_length=255, null=True)
    s_duureg = models.CharField(max_length=255, null=True)
    s_horoo = models.CharField(max_length=255, null=True)
    s_address = models.CharField(max_length=1000, null=True)
    etseg_ded_stants = models.CharField(max_length=255, null=True)


class Bank(AbstractModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    dans = models.CharField(max_length=255, null=True)


class Cycle(AbstractModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    zaalt_avah = models.CharField(max_length=20, null=True)
    tulbur_garah = models.IntegerField(default=1)
    tulbur_tuluh = models.IntegerField(default=1)
    angilal = models.CharField(max_length=1, null=True)


class AhuinHereglegch(AbstractModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, null=True)
    user_type = models.CharField(max_length=50, choices=STATUS_CHOICES, default='1')


class CallType(AbstractModel):
    name = models.CharField(max_length=255)
    is_active = models.CharField(max_length=50, choices=STATUS_CHOICES, default='1')


class Files(AbstractModel):
    name = models.CharField(max_length=255)
    file_description = models.CharField(max_length=255)
    file_size = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, choices=FILE_TYPE, default='0')
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')
    type = models.CharField(max_length=50, choices=FILE_USAGE_TYPE, default='1')
    created_user_fullname = models.CharField(max_length=255)


class ChartData(models.Model):
    month = models.CharField(max_length=255)
    value = models.FloatField()


class Org(AbstractModel):
    name = models.CharField(max_length=255)
    register = models.CharField(max_length=255)  # org_code
    org_type = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    web = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    address = models.CharField(max_length=1000)


class UserProfile(AbstractModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=100)
    org = models.ForeignKey(Org, on_delete=models.DO_NOTHING, null=True)


class Aimag(AbstractModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)


class Duureg(AbstractModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    aimag = models.ForeignKey(Aimag, on_delete=models.DO_NOTHING)


class Horoo(AbstractModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    duureg = models.ForeignKey(Duureg, on_delete=models.DO_NOTHING)


class Hothon(AbstractModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    horoo = models.ForeignKey(Horoo, on_delete=models.DO_NOTHING)


class Block(AbstractModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    hothon = models.ForeignKey(Hothon, on_delete=models.DO_NOTHING)


class ExecutiveOrg(AbstractModel):
    name = models.CharField(max_length=250, null=True)
    code = models.CharField(max_length=250, null=True)

    def __str__(self):  # __unicode__ on Python 2
        return self.name


class Customer(AbstractModel):
    code = models.CharField(max_length=100)
    register = models.CharField(max_length=20, default=0)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    phone2 = models.CharField(max_length=8, null=True)
    email = models.CharField(max_length=100)
    customer_angilal = models.CharField(max_length=100, null=True)  # 0 - Aj ahui neg, 1 - Huvi hereglegch
    customer_type = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=100, null=True)



class Address(AbstractModel):
    customer = models.OneToOneField(Customer, unique=True, on_delete=models.DO_NOTHING, null=True)
    toot = models.CharField(max_length=100)
    building_number = models.CharField(max_length=100)
    block_code = models.CharField(max_length=100)
    hothon_code = models.CharField(max_length=100)
    horoo_code = models.CharField(max_length=100)
    duureg_code = models.CharField(max_length=100)
    aimag_code = models.CharField(max_length=100)
    address_name = models.CharField(max_length=1000, null=True)


class Bair(AbstractModel):
    name = models.CharField(max_length=20)
    input_id = models.CharField(max_length=20)


class CallGeneralType(AbstractModel):
    name = models.CharField(max_length=100)

    def __str__(self):  # __unicode__ on Python 2
        return self.name


class CallSubType(AbstractModel):
    name = models.CharField(max_length=100)
    general_type = models.ForeignKey(CallGeneralType, on_delete=models.DO_NOTHING)

    def __str__(self):  # __unicode__ on Python 2
        return self.name


class Call(AbstractModel):
    customer_code = models.CharField(max_length=100, null=True)  # Customer code
    assigning_user = models.CharField(max_length=100, null=True)
    call_type = models.ForeignKey(CallType, on_delete=models.DO_NOTHING, null=True)
    call_created_date = models.DateTimeField(null=True)
    call_phone = models.CharField(max_length=20, null=True)
    status = models.CharField(max_length=100)  # 1 - shiidsen, 0 - shiideegui
    completed_date = models.DateTimeField(null=True)
    note = models.CharField(max_length=1500)
    type = models.CharField(max_length=100, null=True)  # 0-Sanal huselt, 1-Gomdol, 2-Duudlaga
    phone = models.CharField(max_length=10, null=True)


class UserTechnicalProposal(AbstractModel):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    ger_unem_file = models.ImageField(upload_to='technical_proposal/', null=True)
    obj_address = models.CharField(max_length=255, null=True)
    obj_todor_file = models.ImageField(upload_to='technical_proposal/', null=True)
    tech_shaltgaan = models.CharField(max_length=2000, null=True)
    tsah_hud_too = models.CharField(max_length=2, null=True)
    tsah_hud_chadal = models.CharField(max_length=5, null=True)
    hal_her_too = models.CharField(max_length=2, null=True)
    hal_her_chadal = models.CharField(max_length=5, null=True)
    gerel_too = models.CharField(max_length=2, null=True)
    gerel_chadal = models.CharField(max_length=5, null=True)
    gag_ap_too = models.CharField(max_length=2, null=True)
    gag_ap_chadal = models.CharField(max_length=5, null=True)
    bus_tsah_too = models.CharField(max_length=2, null=True)
    bus_tsah_chadal = models.CharField(max_length=5, null=True)
    toots_niit_chadal = models.CharField(max_length=5, null=True)
    niit_suuri_chadal = models.CharField(max_length=5, null=True)
    ajil_gorim = models.CharField(max_length=1, choices=AJIL_GORIM, null=True)
    ajil_gorim_tsag = models.CharField(max_length=2)
    zereglel = models.CharField(max_length=1000, null=True)
    urgutguh_eseh_date = models.DateField(null=True)
    urgutguh_eseh_chadal = models.CharField(max_length=5, null=True)
    gazar_zuv_dugaar = models.CharField(max_length=20, null=True)
    gazar_zuv_date = models.DateField(null=True)
    gazar_zuv_file = models.ImageField(upload_to='technical_proposal/', null=True)
    ua_zuv_dugaar = models.CharField(max_length=20, null=True)
    ua_zuv_date = models.DateField(null=True)
    ua_zuv_file = models.ImageField(upload_to='technical_proposal/', null=True)
    tseh_tulbur = models.CharField(max_length=1, choices=TSEH_TULBUR_TYPE, null=True)
    urgudul = models.TextField(null=True)
    tod_hud_position = models.CharField(max_length=100, null=True)
    tod_hud_name = models.CharField(max_length=100)


class TechnicalProposal(AbstractModel):
    tech_code = models.CharField(max_length=255)
    req_chadal = models.CharField(max_length=255, null=True)
    req_date = models.DateTimeField(null=True)
    approve_chadal = models.CharField(max_length=255, null=True)
    approve_date = models.DateTimeField(null=True)
    tech_name = models.CharField(max_length=255, null=True)
    tech_utas = models.CharField(max_length=255, null=True)
    tech_address = models.CharField(max_length=255, null=True)
    zoriulalt = models.CharField(max_length=255, null=True)
    dedstants = models.ForeignKey(DedStants, on_delete=models.DO_NOTHING, null=True)
    file = models.ForeignKey(Files, on_delete=models.DO_NOTHING, null=True)
    request = models.ForeignKey(UserTechnicalProposal, on_delete=models.DO_NOTHING, null=True)


class Geree(AbstractModel):
    contract_number = models.CharField(max_length=100)
    contract_made_date = models.DateTimeField(auto_now_add=True)
    contract_expire_date = models.DateTimeField(auto_now_add=True)
    contract_extend_date = models.DateTimeField(auto_now_add=True)
    customer_code = models.CharField(max_length=100)
    cycle_code = models.CharField(max_length=100)
    dedstants_code = models.CharField(max_length=100)
    ezemshliin_zaag = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=100)
    bank_account = models.CharField(max_length=12)
    bus_type = models.CharField(max_length=1, default=0, null=True)
    description = models.TextField(null=True)
    aldangi = models.FloatField(null=True)
    technical_proposal = models.ForeignKey(TechnicalProposal, on_delete=models.DO_NOTHING, null=True)


class TooluurMark(AbstractModel):
    name = models.CharField(max_length=20)


class Tooluur(AbstractModel):
    number = models.CharField(max_length=20)
    name = models.CharField(max_length=200, null=True)
    mark = models.CharField(max_length=20)
    initial_value = models.CharField(max_length=10)
    balance_value = models.CharField(max_length=10, default='0')
    initial_value_night = models.CharField(max_length=10, null=True)
    balance_value_night = models.CharField(max_length=10, null=True, default='0')
    initial_value_rush = models.CharField(max_length=10, null=True)
    balance_value_rush = models.CharField(max_length=10, null=True, default='0')
    verified_date = models.DateTimeField()
    installed_date = models.DateTimeField()
    stamp_number = models.CharField(max_length=30, null=True)
    cert_number = models.CharField(max_length=30, null=True)
    expire_date = models.DateTimeField()
    status = models.CharField(max_length=1, choices=STATUS, default=0)
    tariff = models.CharField(max_length=1, choices=TARIFF, default=0)  # ('0', 'Өдөр'), ('1', 'Шөнө'), ('2', 'Оргил цаг'),
    amper = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    voltage = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))

    # def __str__(self):              # __unicode__ on Python 2
    #     return self.number


class TransformatorMark(AbstractModel):
    name = models.CharField(max_length=20)
    type = models.IntegerField(default=1)


class Transformator(AbstractModel):
    tip = models.CharField(max_length=50)
    number = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=50, null=True)
    multiply_coef = models.DecimalField(max_digits=20, decimal_places=3, null=True, default=Decimal('1.00'))
    type = models.CharField(max_length=1, choices=TRANFORMATOR_TYPE, default=0)
    dedstants = models.ForeignKey(DedStants, on_delete=models.DO_NOTHING, null=True)
    mark = models.ForeignKey(TransformatorMark, on_delete=models.DO_NOTHING, null=True)
    amper = models.CharField(max_length=20, default='0')
    voltage = models.CharField(max_length=20, default='0')
    power = models.CharField(max_length=20, default='0')
    coefficient = models.CharField(max_length=20, default='0')


# class TranformatorDetail(AbstractModel):
#     transformator = models.ForeignKey(Transformator, on_delete=models.DO_NOTHING)
#     amper = models.CharField(max_length=20)
#     voltage = models.CharField(max_length=20)
#     power = models.CharField(max_length=20)
#     coefficient = models.CharField(max_length=20)


class TooluurCustomer(AbstractModel):
    tooluur = models.ForeignKey(Tooluur, on_delete=models.DO_NOTHING, null=True)
    customer_angilal = models.CharField(max_length=1, default=0)
    customer_code = models.CharField(max_length=20)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True)
    dedstants = models.ForeignKey(DedStants, on_delete=models.DO_NOTHING, null=True)
    bair = models.ForeignKey(Bair, on_delete=models.DO_NOTHING, null=True)
    flow_type = models.CharField(max_length=1, choices=TOOLUUR_FLOW_TYPE, default=0)
    flow_id = models.CharField(max_length=250, default=0, null=True)  # Tolgoi garaltiin TooluurCustomer modeliin id hadgalna
    input_type = models.CharField(max_length=1, choices=TOOLUUR_INPUT_TYPE, default=0)
    guidliin_trans = models.ForeignKey(Transformator, on_delete=models.DO_NOTHING, null=True, related_name='guidliin_trans')
    huchdeliin_trans = models.ForeignKey(Transformator, on_delete=models.DO_NOTHING, null=True, related_name='huchdeliin_trans')
    light = models.BooleanField(default=False)
    ten = models.BooleanField(default=False)

class TaslaltZalgalt(AbstractModel):
    code = models.CharField(null=False, max_length=255)
    last_name = models.CharField(null=False, max_length=255)
    first_name = models.CharField(null=False, max_length=255)

class HasagdahTooluur(AbstractModel):
    head_tool_cus = models.ForeignKey(TooluurCustomer, related_name='head_tooluur', on_delete=models.DO_NOTHING)
    head_tool_cus2 = models.ForeignKey(TooluurCustomer, related_name='head_tooluur2', on_delete=models.DO_NOTHING, null=True)
    child_tool_cus = models.ForeignKey(TooluurCustomer, related_name='child_tooluur', on_delete=models.DO_NOTHING)
    group = models.BooleanField(default=False)
    search_tooluur = models.CharField(max_length=50, null=True)


class TooluurFlow(AbstractModel):
    head_tool_cus = models.ForeignKey(TooluurCustomer, related_name='head_tool', on_delete=models.DO_NOTHING)
    child_tool_cus = models.ForeignKey(TooluurCustomer, related_name='child_tool', on_delete=models.DO_NOTHING)


class PriceTariff(AbstractModel):
    une_start_date = models.DateTimeField(null=True)
    une_end_date = models.DateTimeField(null=True)
    odor_une = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    shono_une = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    orgil_une = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    serg_une = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    chadal_une = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    suuri_une = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    tv_une = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    une_type = models.CharField(max_length=1, choices=UNE_TYPE, default=0)
    bus_type = models.CharField(max_length=1, choices=BUS_TYPE, default=0)
    tariff_type = models.CharField(max_length=1, choices=TARIFF_TYPE, default=0)
    limit = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    high_limit_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    low_limit_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    barimt_une = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    nuat_huvi = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    ald_huvi = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))


class Tuluvluguu(AbstractModel):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    bus_type = models.CharField(max_length=1, choices=TUL_TYPE, default=0)
    tuluvluguu = models.DecimalField(max_digits=65, decimal_places=2, default=Decimal('0.00'))
    year = models.CharField(max_length=5)
    month = models.CharField(max_length=3)


class Payment(AbstractModel):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True)
    uldegdel = models.DecimalField(max_digits=65, decimal_places=2, default=Decimal('0.00'))


class PaymentHistory(AbstractModel):
    payment = models.ForeignKey(Payment, on_delete=models.DO_NOTHING, null=True)
    pay_date = models.DateTimeField(null=True)
    pay_barimt = models.DecimalField(max_digits=65, decimal_places=2, default=Decimal('0.00'))
    pay_total = models.DecimalField(max_digits=65, decimal_places=2, default=Decimal('0.00'))
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True)
    bank = models.ForeignKey(Bank, on_delete=models.DO_NOTHING, null=True)
    bank_ref = models.CharField(max_length=17, null=True)
    description = models.TextField(null=True)


class PosAPI(AbstractModel):
    pay_his = models.ForeignKey(PaymentHistory, on_delete=models.DO_NOTHING, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True)
    billType = models.CharField(max_length=1, null=True)
    nonCashAmount = models.DecimalField(max_digits=65, decimal_places=2, default=Decimal('0.00'), null=True)
    cashAmount = models.DecimalField(max_digits=65, decimal_places=2, default=Decimal('0.00'), null=True)
    districtCode = models.CharField(max_length=2, null=True)
    date = models.DateTimeField(null=True)
    returnBillId = models.CharField(max_length=33, null=True)
    branchNo = models.CharField(max_length=3, null=True)
    posNo = models.CharField(max_length=6, null=True)
    billId = models.CharField(max_length=33, null=True)
    reportMonth = models.CharField(max_length=7, null=True)
    invoiceId = models.CharField(max_length=33, null=True)
    taxType = models.CharField(max_length=1, null=True)
    vat = models.DecimalField(max_digits=65, decimal_places=2, default=Decimal('0.00'), null=True)
    billIdSuffix = models.CharField(max_length=6, null=True)
    merchantId = models.CharField(max_length=10, null=True)
    macAddress = models.CharField(max_length=12, null=True)
    customerNo = models.CharField(max_length=100, null=True)
    amount = models.DecimalField(max_digits=65, decimal_places=2, default=Decimal('0.00'), null=True)
    success = models.BooleanField()
    registerNo = models.CharField(max_length=12, null=True)
    is_send = models.BooleanField(default=False)


class QPay(AbstractModel):
    result_code = models.CharField(max_length=5, null=True)
    result_msg = models.CharField(max_length=50, null=True)
    payment_id = models.CharField(max_length=15, null=True)
    invoice_id = models.CharField(max_length=20, null=True)
    amount = models.CharField(max_length=20, null=True)
    bank_name = models.CharField(max_length=50, null=True)
    account_number = models.CharField(max_length=20, null=True)
    account_name = models.CharField(max_length=50, null=True)
    currency_code = models.CharField(max_length=3, null=True)


class GolomtEcommerce(AbstractModel):
    trans_number = models.CharField(max_length=12, null=True)
    trans_amount = models.CharField(max_length=12, null=True)
    card_number = models.CharField(max_length=20, null=True)
    customer_id = models.CharField(max_length=7, null=True)
    success = models.CharField(max_length=1, null=True)
    error_code = models.CharField(max_length=10, null=True)
    error_desc = models.CharField(max_length=100, null=True)
    soap_code = models.CharField(max_length=6, null=True)


class Salgalt(AbstractModel):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, default=None)
    status = models.CharField(max_length=1, choices=SALGALT, default=0)
    salgasan_date = models.DateTimeField(null=True)
    zalgasan_date = models.DateTimeField(null=True)


class TulburtUilchilgee(AbstractModel):
    name = models.CharField(max_length=255, null=True)
    payment = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    code = models.CharField(max_length=20, null=True)
    angilal = models.CharField(max_length=1, choices=CUSTOMER_TYPE, default=0)


class CallActivity(AbstractModel):
    call = models.ForeignKey(Call, on_delete=models.DO_NOTHING, null=True)
    note = models.CharField(max_length=1500, null=True)
    activity_type = models.CharField(max_length=100, null=True)  # 0-Dotooddoo shiidverleh, 1-shiljuulsen, 2-hereglegchid butsaasan, 3-duussan
    assigning_user = models.CharField(max_length=100, null=True)
    assigning_user_name = models.CharField(max_length=100, null=True)
    assigning_org = models.ForeignKey(ExecutiveOrg, on_delete=models.DO_NOTHING, null=True)
    activity_date = models.DateField(null=True)
    tulburt_uilchilgee = models.ForeignKey(TulburtUilchilgee, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):  # __unicode__ on Python 2
        return self.name


class Avlaga(AbstractModel):
    heregleenii_tulbur = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    prev_year_payment = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    payment_gap = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    uilchilgeenii_tulbur = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    barimt_une = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    tv_huraamj = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    ten = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    light = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    year = models.IntegerField()
    month = models.IntegerField()
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    tulbur_date = models.DateTimeField()
    pay_type = models.CharField(max_length=1, choices=PAY_TYPE, default=0)
    pay_uld = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    balance = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    paid_date = models.DateTimeField(null=True)
    out_of_date = models.CharField(max_length=1, choices=OUT_OF_DATE, default=0)
    ald_huvi = models.FloatField(null=True, default=0.3)
    ald_hemjee = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    payment_history = models.ForeignKey(PaymentHistory, on_delete=models.DO_NOTHING, null=True)
    is_confirm = models.BooleanField(default=0)
    is_discount = models.CharField(max_length=100, null=True)
    aldangi_date = models.DateTimeField()


class Bichilt(AbstractModel):
    bichilt_date = models.DateTimeField()
    tooluur = models.ForeignKey(TooluurCustomer, on_delete=models.DO_NOTHING)
    year = models.CharField(max_length=100, null=True)
    month = models.CharField(max_length=100, null=True)
    day_balance = models.CharField(max_length=10, null=True)
    night_balance = models.CharField(max_length=10, null=True)
    rush_balance = models.CharField(max_length=10, null=True)
    day_diff = models.CharField(max_length=10, null=True)
    night_diff = models.CharField(max_length=10, null=True)
    rush_diff = models.CharField(max_length=10, null=True)
    total_diff = models.CharField(max_length=10, null=True)
    hereglee_price = models.CharField(max_length=20, null=True)
    sergeegdeh_price = models.CharField(max_length=20, null=True)
    chadal_price = models.CharField(max_length=20, null=True)
    suuri_price = models.CharField(max_length=20, null=True)
    total_price = models.CharField(max_length=20, null=True)
    user_type = models.CharField(max_length=1, choices=BICHILT_USER_TYPE, default=0)
    type = models.CharField(max_length=1, choices=BICHILT_TYPE, default=0)
    prev_bichilt_id = models.CharField(max_length=20, null=True)
    is_zadgai = models.BooleanField(default=False)
    description = models.CharField(max_length=2000, null=True)
    is_problem = models.CharField(max_length=1, choices=BICHILT_PROBLEM, default=0)
    avlaga = models.ForeignKey(Avlaga, on_delete=models.DO_NOTHING, null=True)
    price_tariff = models.ForeignKey(PriceTariff, on_delete=models.DO_NOTHING, null=True)
    tool_tariff = models.CharField(max_length=1, choices=TARIFF_TYPE, default=0)
    zadgai_diff = models.CharField(max_length=20, null=True)
    light_balance = models.CharField(max_length=10, null=True)
    static_light = models.CharField(max_length=20, null=True)


class CustomerUilchilgeeTulbur(AbstractModel):
    tooluur = models.ForeignKey(Tooluur, on_delete=models.DO_NOTHING)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    uilchilgee = models.ForeignKey(TulburtUilchilgee, on_delete=models.DO_NOTHING)
    uil_date = models.DateField()
    payment = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    year = models.CharField(max_length=4, null=True)
    month = models.CharField(max_length=2, null=True)
    monter = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    avlaga = models.ForeignKey(Avlaga, on_delete=models.DO_NOTHING, null=True)


class AlbanTushaal(AbstractModel):
    name = models.CharField(max_length=20, null=True)
    code = models.CharField(max_length=20, null=True)


class ZaavarchilgaaCategory(AbstractModel):
    name = models.CharField(max_length=255)


class Zaavarchilgaa(AbstractModel):
    title = models.CharField(max_length=255, null=True)
    category = models.ForeignKey(ZaavarchilgaaCategory, on_delete=models.DO_NOTHING, null=True)
    description = models.TextField(null=True)


class Amper(AbstractModel):
    value = models.CharField(max_length=255, null=True)


class Voltage(AbstractModel):
    value = models.CharField(max_length=255, null=True)


class Shugam(AbstractModel):
    ded_stants = models.ForeignKey(DedStants, on_delete=models.DO_NOTHING, null=True)
    tooluur = models.ForeignKey(Tooluur, on_delete=models.DO_NOTHING, null=True)
    shugam_ner = models.CharField(max_length=255)
    shugam_tip = models.CharField(max_length=1, choices=SHUGAM_TIP_TYPE, default='0')
    shugam_tuluv = models.CharField(max_length=1, choices=SHUGAM_TYPE, default='0')
    suuriluulsan_ognoo = models.DateField()


class Cable(AbstractModel):
    start_ded_stants = models.ForeignKey(DedStants, related_name='start_ded_stants', on_delete=models.DO_NOTHING, null=True)
    orolt = models.ForeignKey(Shugam, related_name='orolt', on_delete=models.DO_NOTHING, null=True)
    end_ded_stants = models.ForeignKey(DedStants, related_name='end_ded_stants', on_delete=models.DO_NOTHING, null=True)
    garalt = models.ForeignKey(Shugam, related_name='garalt', on_delete=models.DO_NOTHING, null=True)
    ner = models.CharField(max_length=255)
    urt = models.CharField(max_length=6)
    tip = models.CharField(max_length=255)
    mulfi_too = models.CharField(max_length=2, null=True)
    suuriluulsan_ognoo = models.DateField()
    trass = models.FileField(upload_to='cable/', null=True)


class Relei(AbstractModel):
    ded_stants = models.ForeignKey(DedStants, on_delete=models.DO_NOTHING, null=True)
    shugam = models.ForeignKey(Shugam, on_delete=models.DO_NOTHING, null=True)
    ner = models.CharField(max_length=255)
    tip = models.CharField(max_length=1, choices=SHUGAM_TIP_TYPE, default='0')
    suuriluulsan_ognoo = models.DateField()
    hugatsaa_barilttai = models.CharField(max_length=7, null=True)
    hugatsaa_bariltgui = models.CharField(max_length=7, null=True)
    gazardalt = models.CharField(max_length=7, null=True)


class PowerTransformator(AbstractModel):
    ded_stants = models.ForeignKey(DedStants, on_delete=models.DO_NOTHING, null=True)
    shugam = models.ForeignKey(Shugam, on_delete=models.DO_NOTHING, null=True)
    ner = models.CharField(max_length=255)
    chadal = models.CharField(max_length=255, null=True)
    tip = models.CharField(max_length=1, choices=POWER_TRANS_TYPE, default='0')
    uildverlesen_ognoo = models.DateField(null=True)
    antsaf = models.CharField(max_length=10, null=True)
    ajillasan_tsag = models.CharField(max_length=20, null=True)
    suuriluulsan_ognoo = models.DateTimeField(null=True)


class Battery(AbstractModel):
    ded_stants = models.ForeignKey(DedStants, on_delete=models.DO_NOTHING, null=True)
    dugaar = models.CharField(max_length=255)
    amper = models.CharField(max_length=7, null=True)
    serial = models.CharField(max_length=255, null=True)
    suuriluulsan_ognoo = models.DateField()
    ajilsan_jil = models.CharField(max_length=20, null=True)


class ShuurhaiAjillagaa(AbstractModel):
    ognoo = models.DateTimeField()
    dispetcher = models.ForeignKey(User, related_name='dispetcher', on_delete=models.DO_NOTHING)
    temdeglel = models.TextField()
    taniltssan_eseh = models.CharField(max_length=1, choices=SHUURHAI_AJILLAGAA, default=0, null=True)
    taniltssan = models.ForeignKey(User, related_name='taniltssan', on_delete=models.DO_NOTHING, null=True)


class NaryadMedeelel(AbstractModel):
    naryad_dugaar = models.CharField(max_length=20, null=True)
    ajil_name = models.CharField(max_length=255)
    ajil_start_date = models.DateTimeField()
    ajil_end_date = models.DateTimeField()
    ayulgui_baidal = models.TextField(null=True)
    naryad_olgogch = models.ForeignKey(User, related_name='naryad_olgogch', on_delete=models.DO_NOTHING, null=True)
    ded_stants = models.ForeignKey(DedStants, on_delete=models.DO_NOTHING, null=True)
    udirdagch = models.ForeignKey(User, related_name='udirdagch', on_delete=models.DO_NOTHING, null=True)
    guitsedgegch = models.ForeignKey(User, related_name='guitsedgegch', on_delete=models.DO_NOTHING, null=True)
    ajiglagch = models.ForeignKey(User, related_name='ajiglagch', on_delete=models.DO_NOTHING, null=True)
    zuv_olgogch = models.ForeignKey(User, related_name='zuv_olgogch', on_delete=models.DO_NOTHING, null=True)
    ajil_oruulagch = models.ForeignKey(User, related_name='ajil_oruulagch', on_delete=models.DO_NOTHING, null=True)
    brigad_members = models.ManyToManyField(User, blank=True)
    other_members = models.TextField(null=True)

    @property
    def brigad_members_list(self):
        return list(self.brigad_members.all())

    @property
    def other_members_list(self):
        other_members = self.other_members.split(';')
        other_members.pop(len(other_members)-1)
        return list(other_members)


class Tasralt(AbstractModel):
    ded_stants = models.ForeignKey(DedStants, on_delete=models.DO_NOTHING)
    shugam = models.ForeignKey(Shugam, on_delete=models.DO_NOTHING, null=True)
    tasarsan_date = models.DateTimeField()
    zalgasan_date = models.DateTimeField()
    tasraltiin_hugatsaa = models.CharField(max_length=20)
    amper = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00')) #guidel
    voltage = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00')) #huchdel
    chadal = models.CharField(max_length=255, null=True)
    dutuu_tugeesen = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    ajillasan_hamgaalalt = models.CharField(max_length=1, choices=AJILLASAN_HAMGAALALT, null=True)
    tasraltiin_shaltgaan = models.TextField()
    avsan_arga_hemjee = models.TextField()


class Taslalt(AbstractModel):
    ded_stants = models.ForeignKey(DedStants, on_delete=models.DO_NOTHING)
    shugam = models.ForeignKey(Shugam, on_delete=models.DO_NOTHING, null=True)
    tasalsan_date = models.DateTimeField()
    zalgasan_date = models.DateTimeField()
    tasalsan_hugatsaa = models.CharField(max_length=20)
    amper = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00')) #guidel
    voltage = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00')) #huchdel
    chadal = models.CharField(max_length=255, null=True)
    dutuu_tugeesen = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    dispetcher = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    taslalt_shaltgaan = models.TextField()


class UzlegShalgalt(AbstractModel):
    ajiltan = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ded_stants = models.ForeignKey(DedStants, on_delete=models.DO_NOTHING)
    ognoo = models.DateTimeField()
    aguulga = models.TextField()


class Gemtel(AbstractModel):
    ded_stants = models.ForeignKey(DedStants, on_delete=models.DO_NOTHING)
    shugam = models.ForeignKey(Shugam, on_delete=models.DO_NOTHING)
    gemtsen_date = models.DateTimeField()
    zalgasan_date = models.DateTimeField()
    gemtsen_hugatsaa = models.CharField(max_length=20)
    amper = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))  # guidel
    voltage = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))  # huchdel
    chadal = models.CharField(max_length=255, null=True)
    dutuu_tugeesen = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    dispetcher = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    gemtsen_shaltgaan = models.TextField()
    zurag = models.FileField(upload_to='gemtel/', null=True)


class AshiglaltZaavarchilgaa(AbstractModel):
    zaavar_ugsun = models.ForeignKey(User, related_name='zaavar_ugsun', on_delete=models.DO_NOTHING)
    zaavar_avsan = models.ManyToManyField(User, blank=True)
    ognoo = models.DateTimeField()
    zaavarchilgaa = models.ManyToManyField(Zaavarchilgaa, blank=True)

    @property
    def zaavar_avsan_list(self):
        return list(self.zaavar_avsan.all())

    @property
    def zaavarchilgaa_list(self):
        return list(self.zaavarchilgaa.all())


class ZaavarchilgaaUsers(AbstractModel):
    ashiglalt_zaavar = models.ForeignKey(AshiglaltZaavarchilgaa, null=True, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING)
    taniltssan_eseh = models.CharField(max_length=1, choices=SHUURHAI_AJILLAGAA, default=0)


class MedeelehZagvar(AbstractModel):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=1, choices=MEDEELEH_ZAGVAR_TYPE, default='1')
    text = models.TextField()


class BichiltBalance(AbstractModel):
    dedstants_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    etseg_stants_id = models.CharField(max_length=255)
    etseg_stants_name = models.CharField(max_length=255)
    self_balance_value = models.CharField(max_length=255)
    child_balance_value = models.CharField(max_length=255)
    month = models.CharField(max_length=255)
    year = models.CharField(max_length=255)


class GolomtTransactions(AbstractModel):
    type = models.CharField(max_length=10)
    account = models.CharField(max_length=20)
    journalid = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    description = models.CharField(max_length=255)
    posted_date = models.DateTimeField(null=True)
    statement_date = models.DateField(null=True)


class RestorPayment(AbstractModel):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True)
    payment_history = models.ForeignKey(PaymentHistory, on_delete=models.DO_NOTHING, related_name='before_pay_his', null=True)
    paymenthistory = models.ForeignKey(PaymentHistory, on_delete=models.DO_NOTHING, related_name='after_pay_his', null=True)
    pay_total = models.DecimalField(max_digits=65, decimal_places=2, null=True)
    avlaga = models.ForeignKey(Avlaga, on_delete=models.DO_NOTHING, null=True)
    pay_type = models.CharField(max_length=1, choices=PAY_TYPE, null=True)
    pay_uld = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    paid_date = models.DateTimeField(null=True)
    payment = models.ForeignKey(Payment, on_delete=models.DO_NOTHING, null=True)
    uldegdel = models.DecimalField(max_digits=65, decimal_places=2, null=True)
    posapi = models.ForeignKey(PosAPI, on_delete=models.DO_NOTHING, null=True)
    billId = models.CharField(max_length=33, null=True)
    date = models.DateTimeField(null=True)


class Final_Balance(models.Model):
    year = models.CharField(max_length=4, null=True)
    month = models.CharField(max_length=2, null=True)
    balance = models.DecimalField(max_digits=65, decimal_places=2, default=Decimal('0.00'), null=True)
    customer_id = models.IntegerField(null=True)
    ehnii = models.DecimalField(max_digits=65, decimal_places=2, default=Decimal('0.00'), null=True)
    status = models.CharField(max_length=1, choices=FINAL_BALANCE_STATUS_TYPE, default='0')


class PriceHistory(AbstractModel):
    customer_code = models.CharField(max_length=20, null=True)
    customer_angilal = models.CharField(max_length=100, null=True)
    customer_type = models.CharField(max_length=100, null=True)
    cycle_code = models.CharField(max_length=100, null=True)
    bus_type = models.CharField(max_length=1, default=0, null=True)
    number = models.CharField(max_length=20, null=True)
    year = models.CharField(max_length=4, null=True)
    month = models.CharField(max_length=2, null=True)
    day = models.CharField(max_length=2, null=True)
    umnu_bichdate = models.DateTimeField(null=True)
    odoo_bichdate = models.DateTimeField(null=True)
    between_days = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=Decimal('1.00'))
    kosp = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=Decimal('0.00'))
    price_tariff_id = models.IntegerField(null=True)
    low150_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    high150_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    day_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    night_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    rush_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    chadal_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    suuri_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    barimt_une = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=Decimal('0.00'))
    nuat = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    total_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    tot_pri_suu_cha = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    total_price_nuat = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))


class TooluurHistory(AbstractModel):
    customer_code = models.CharField(max_length=20, null=True)
    number = models.CharField(max_length=20, null=True)
    customer_angilal = models.CharField(max_length=100, null=True)
    customer_type = models.CharField(max_length=100, null=True)
    tariff = models.CharField(max_length=1, choices=TARIFF, null=True, default=0)
    year = models.CharField(max_length=4, null=True)
    month = models.CharField(max_length=2, null=True)
    day = models.CharField(max_length=2, null=True)
    umnu_bichdate = models.DateTimeField(null=True)
    odoo_bichdate = models.DateTimeField(null=True)
    between_days = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=Decimal('0.00'))
    prev_id = models.IntegerField(null=True)
    guid_coef = models.DecimalField(max_digits=20, decimal_places=3, null=True, default=Decimal('0.00'))
    huch_coef = models.DecimalField(max_digits=20, decimal_places=3, null=True, default=Decimal('0.00'))
    day_balance_prev = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    day_balance = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    night_balance_prev = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    night_balance = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    rush_balance_prev = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    rush_balance = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    day_diff = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    day_diff_coef = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    night_diff = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    night_diff_coef = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    rush_diff = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    rush_diff_coef = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    total_diff = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    total_diff_coef = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))


class HasagdahHistory(AbstractModel):
    customer_code = models.CharField(max_length=20, null=True)
    customer_angilal = models.CharField(max_length=100, null=True)
    customer_type = models.CharField(max_length=100, null=True)
    cycle_code = models.CharField(max_length=100, null=True)
    bus_type = models.CharField(max_length=1, default=0, null=True)
    number = models.CharField(max_length=20, null=True)
    year = models.CharField(max_length=4, null=True)
    month = models.CharField(max_length=2, null=True)
    day = models.CharField(max_length=2, null=True)
    umnu_bichdate = models.DateTimeField(null=True)
    odoo_bichdate = models.DateTimeField(null=True)
    child_tool_his = models.IntegerField(null=True)
    price_tariff_id = models.IntegerField(null=True)
    between_days = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=Decimal('1.00'))
    day_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    night_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    rush_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    chadal_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    total_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))


class TulburtUilchilgeeHistory(AbstractModel):
    customer_code = models.CharField(max_length=20, null=True)
    customer_angilal = models.CharField(max_length=100, null=True)
    year = models.CharField(max_length=4, null=True)
    month = models.CharField(max_length=2, null=True)
    day = models.CharField(max_length=2, null=True)
    uil_date = models.DateTimeField(null=True)
    name = models.CharField(max_length=255, null=True)
    payment = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))


class NiitiinHistory(AbstractModel):
    customer_code = models.CharField(max_length=20, null=True)
    year = models.CharField(max_length=4, null=True)
    month = models.CharField(max_length=2, null=True)
    day = models.CharField(max_length=2, null=True)
    ten_zuruu = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=Decimal('1.00'))
    light_zuruu = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=Decimal('1.00'))
    ten_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    light_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, default=Decimal('0.00'))
    price_tariff_id = models.IntegerField(null=True)

class CustomerHasBank(models.Model):
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField()
    bank_code = models.CharField(max_length=100, null=True)
    bank_id = models.IntegerField(null=True)
    customer_id = models.IntegerField( null=True)
    created_user_id = models.IntegerField( null=True)
    updated_user_id = models.IntegerField( null=True)
    class Meta:
        managed = False
        db_table = 'data_customer_has_bank'
class DataBank(AbstractModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    dans = models.CharField(max_length=255, null=True)
    account_id = models.CharField(max_length=255, null=True)
    created_user_id = models.IntegerField( null=True)
    updated_user_id = models.IntegerField( null=True)
    class Meta:
        managed = False
        db_table = 'data_bank'
class ServiceLog(models.Model):
    invoice_no = models.CharField(max_length=80, null=True)
    request_date = models.DateTimeField(null=True)
    request = models.TextField(null=True)
    response_date = models.DateTimeField(null=True)
    response = models.TextField(null=True)
    type = models.CharField(max_length=50, null=True)
    status = models.IntegerField(default=0,null=True)
    bank_type = models.CharField(max_length=50, null=True)
    error = models.TextField(null=True)
    class Meta:
        managed = False
        db_table = 'data_service_log'

class PaymentOrder(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    order_no = models.CharField(max_length=50, null=True)
    invoice_no =  models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.IntegerField(default=0,null=True)
    payment_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    paid_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    customer_id = models.IntegerField(null=True)
    class Meta:
        managed = False
        db_table = 'data_payment_order'

#------------------- Most money ---------------------#
class customerMost(AbstractModel):
    code = models.CharField(max_length=100)    
    LName = models.CharField(max_length=100)
    FName = models.CharField(max_length=100)
    IsCorporate = models.CharField(max_length=10)
    OrgName = models.CharField(max_length=100)    
    RegisterNo = models.CharField(max_length=20, default=0)    
    PhoneNo = models.CharField(max_length=8)
    MobileNo = models.CharField(max_length=8, null=True)
    AddressShort = models.CharField(max_length=100)
    email = models.CharField(max_length=100)        
    