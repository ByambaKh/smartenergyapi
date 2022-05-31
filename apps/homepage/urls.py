from django.conf.urls import *
from django.contrib.auth import views as auth_views
from apps.homepage.viewz.ashiglalt.ded_stants import AshiglaltDedStants
from apps.homepage.viewz.ashiglalt.taslalt import *
from apps.homepage.viewz.ashiglalt.tasralt import *
from apps.homepage.viewz.ashiglalt.zaavarchilgaa import *
from apps.homepage.viewz.ashiglalt.gemtel import *
from apps.homepage.viewz.ashiglalt.naryad_medeelel import *
from apps.homepage.viewz.ashiglalt.shuurhai_ajillagaa import *
from apps.homepage.viewz.ashiglalt.uzleg_shalgalt import *
from apps.homepage.viewz.avlaga import *
from apps.homepage.viewz.bichilt import *
from apps.homepage.viewz.bichilt_bair import *
from apps.homepage.viewz.bichilt_balance import *
from apps.homepage.viewz.bichilt_full import *
from apps.homepage.viewz.call_center import *
from apps.homepage.viewz.change_password import ChangePassword
from apps.homepage.viewz.dashboard import *
from apps.homepage.viewz.file import *
from apps.homepage.viewz.geree import *
from apps.homepage.viewz.input_output import *
from apps.homepage.viewz.invoice1 import InvoiceAhui1, InvoiceAan1
from apps.homepage.viewz.invoice_detail import InvoiceDetailAhui, InvoiceDetailAan
from apps.homepage.viewz.lavlagaa.lavlagaa_aan_angilal import *
from apps.homepage.viewz.lavlagaa.lavlagaa_ahui_hereglegch import *
from apps.homepage.viewz.lavlagaa.lavlagaa_aimag import *
from apps.homepage.viewz.lavlagaa.lavlagaa_alban_tushaal import *
from apps.homepage.viewz.lavlagaa.lavlagaa_aldangi import *
from apps.homepage.viewz.lavlagaa.lavlagaa_amper import *
from apps.homepage.viewz.lavlagaa.lavlagaa_bag_horoo import *
from apps.homepage.viewz.lavlagaa.lavlagaa_bair import *
from apps.homepage.viewz.lavlagaa.lavlagaa_bank import *
from apps.homepage.viewz.lavlagaa.lavlagaa_battery import *
from apps.homepage.viewz.lavlagaa.lavlagaa_cable import *
from apps.homepage.viewz.lavlagaa.lavlagaa_calltype import *
from apps.homepage.viewz.lavlagaa.lavlagaa_cycle import *
from apps.homepage.viewz.lavlagaa.lavlagaa_ded_stants_angilal import *
from apps.homepage.viewz.lavlagaa.lavlagaa_ded_stants import *
from apps.homepage.viewz.lavlagaa.lavlagaa_egnee import *
from apps.homepage.viewz.lavlagaa.lavlagaa_guidliin_trans import *
from apps.homepage.viewz.lavlagaa.lavlagaa_hothon import *
from apps.homepage.viewz.lavlagaa.lavlagaa_huchdeliin_trans import *
from apps.homepage.viewz.lavlagaa.lavlagaa_huchnii_trans import *
from apps.homepage.viewz.lavlagaa.lavlagaa_relei import *
from apps.homepage.viewz.lavlagaa.lavlagaa_shugam import *
from apps.homepage.viewz.lavlagaa.lavlagaa_sub_call_view import *
from apps.homepage.viewz.lavlagaa.lavlagaa_sum_duureg import *
from apps.homepage.viewz.lavlagaa.lavlagaa_tooluur import *
from apps.homepage.viewz.lavlagaa.lavlagaa_uilchilgee import *
from apps.homepage.viewz.lavlagaa.lavlagaa_une_tarif import *
from apps.homepage.viewz.lavlagaa.lavlagaa_voltage import *
from apps.homepage.viewz.lavlagaa.lavlagaa_zaavarchilgaa import *
from apps.homepage.viewz.medeeleh import *
from apps.homepage.viewz.org_list import *
from apps.homepage.viewz.orlogo import *
from apps.homepage.viewz.report_ehzh import report_ehzh_3, report_ehzh_4, report_ehzh_5, report_ehzh_6, report_negtgel, report_zaalt
from apps.homepage.viewz.role import *
from apps.homepage.viewz.taslalt_zalgalt import *
from apps.homepage.viewz.tatvar import Tatvar
from apps.homepage.viewz.technical_proposal import *
from apps.homepage.viewz.tooluur import *
from apps.homepage.viewz.tuluvluguu import *
from apps.homepage.viewz.users import *
from apps.homepage.viewz.vilchilgee import *
from apps.homepage.viewz.report import *
from apps.homepage.viewz.report_bichilt import *
from apps.homepage.viewz.reports.report_contract import *
from apps.homepage.viewz.bank.most import *
from apps.homepage.viewz.bank.khan import *
from apps.homepage.viewz.bank.golomt import *
#from apps.homepage.viewz.smart_tooluur import *
from . import views
from apps.homepage.views import pos_init

urlpatterns = [
    url(r'^logout', auth_views.logout, {'next_page': '/login'}),

    url(r'^org_list', OrgList.as_view(), name='org_list'),
    url(r'^org_add', OrgAdd.as_view()),
    url(r'^org_edit/(\d+)/', OrgEdit.as_view()),
    url(r'^org_delete/(\d+)/', OrgDelete.as_view()),

    url(r'^user_list', UserList.as_view(), name='user_list'),
    url(r'^user_add', UserAdd.as_view()),
    url(r'^user_edit/(\d+)', UserEdit.as_view()),
    url(r'^user_del/(\d+)', UserDel.as_view()),
    url(r'^user_res/(\d+)', UserRestore.as_view()),

    url(r'^role_list', RoleList.as_view(), name='role_list'),
    url(r'^role_add', RoleAdd.as_view()),
    url(r'^role_edit/(\d+)', RoleEdit.as_view()),

    url(r'^index', Dashboard.as_view(), name='index'),
    url(regex='^bar/$', view=BarView.as_view(), name='bar'),
    url(regex='^line/$', view=LineView.as_view(), name='line'),
    url(regex='^line_time/$', view=LineViewTime.as_view(), name='line_time'),

    url(r'^tech_nuhtsul/(\d+)/', TechList.as_view(), name='tech_list'),
    url(r'^tech_add/(\d+)/', ProposalEdit.as_view()),
    url(r'^add_tech', TechAdd.as_view(), name='tech_add'),
    url(r'^tech_confirm/(\d+)/', ConfirmTech.as_view()),

    url(r'^orolt_and_garalt_list', OroltGaraltList.as_view(), name='orolt_and_garalt_list'),
    url(r'^orolt_and_garalt_delete/(\d+)/', OroltGaraltDelete.as_view(), name='orolt_and_garalt_delete'),
    url(r'^orolt_and_garalt', OroltGaraltView.as_view(), name='orolt_garalt_list'),
    url(r'^add_orolt_garalt', OroltGaraltAdd.as_view(), name='add_orolt_garalt'),
    url(r'^new_add_orolt_garalt', NewOroltGaraltAdd.as_view(), name='new_add_orolt_garalt'),

    url(r'^set_pin_number', set_pin_code),

    url(r'^geree_list/(\d+)/', GereeList.as_view(), name='geree_list'),
    url(r'^geree_add', GereeAdd.as_view()),
    url(r'^geree_edit/(\d+)/', GereeEdit.as_view()),
    url(r'^geree_del/(\d+)/', GereeDel.as_view()),
    url(r'^get_type', get_type),
    url(r'^get_duureg', get_duureg),
    url(r'^get_horoo', get_horoo),
    url(r'^get_hothon', get_hothon),
    url(r'^get_block', get_block),
    url(r'^get_dans', get_dans),

    url(r'^tooluur_list', TooluurList.as_view(), name='tool_cus_list'),
    url(r'^tooluur_add', TooluurAdd.as_view()),
    url(r'^tooluur_edit/(\d+)/', TooluurEdit.as_view()),
    url(r'^tooluur_del/(\d+)/', TooluurDel.as_view()),
    url(r'^get_tooluur', getTooluur),
    url(r'^get_cus', getCus),
    url(r'^get_input_customer', get_input_customers),
    url(r'^get_selected_input_tooluur', get_selected_input_tooluur),
    url(r'^get_angilal_tooluur', get_tooluur_by_angilal),
    url(r'^get_input_tooluur', get_tooluur_input),
    url(r'^new_get_input_tooluur', new_get_tooluur_input),
    url(r'^tuluvluguu', TuluvluguuList.as_view(), name='tuluvluguu_list'),
    url(r'^add_tuluv', TuluvluguuAdd.as_view()),
    url(r'^tul_del/(\d+)/', TuluvluguuDel.as_view()),

    url(r'^borluulalt/bichilt_list/(\d+)/', BichiltList.as_view()),
    url(r'^borluulalt/bichilt_edit/(\d+)/', BichiltEdit.as_view()),
    url(r'^borluulalt/bichilt_remove/(\d+)', BichiltRemove.as_view()),
    url(r'^borluulalt/bichilt_add', BichiltAdd.as_view()),
    url(r'^borluulalt/bichilt_view/(\d+)', BichiltView.as_view()),
    url(r'^borluulalt/bichilt_ded_stants_add', BichiltSubStationAdd.as_view()),
    url(r'^borluulalt/bichilt_ded_stants_edit/(\d+)/', BichiltSubStationEdit.as_view()),
    url(r'^borluulalt/bichilt_ded_stants_view/(\d+)/', BichiltSubStationView.as_view()),
    url(r'^borluulalt/bichilt_bair_add', BichiltBairAdd.as_view()),
    url(r'^borluulalt/bichilt_bair_edit/(\d+)/', BichiltBairEdit.as_view()),
    url(r'^borluulalt/bichilt_bair_view/(\d+)/', BichiltBairView.as_view()),
    url(r'^borluulalt/bichilt_balance/(\d+)', BalanceView.as_view()),
    url(r'^borluulalt/balance_export/(\d+)/(\d+)/(\d+)/(\d+)/$', BalanceView.export_balance_xls),
    url(r'^borluulalt/balance_submit/(\d+)/(\d+)/(\d+)/(\d+)/$', BalanceView.submit_balance),
    url(r'^borluulalt/bichilt_export_indi/$', BichiltList.export_bichilt_indi_xls),
    url(r'^borluulalt/bichilt_export_station/$', BichiltList.export_bichilt_station_xls),
    url(r'^borluulalt/tatvar', Tatvar.as_view(), name='tatvar'),
    url(r'^get_user_zaalt', get_user_zaalt),
    url(r'^export_xls', get_user_zaalt),
    url(r'^get_zaalt_bytooluur', get_tooluur_zaalt),
    url(r'^get_sub_stations_tooluur', get_sub_stations_tooluur),
    url(r'^get_bair_tooluur', get_bair_tooluur),

    url(r'^borluulalt/avlaga/(?P<type>\d{1})/', AvlagaList.as_view()),
    url(r'^borluulalt/delete_avlaga/(?P<id>\d+)/(?P<code>\d{7})/', AvlagaDelete.as_view()),
    url(r'^borluulalt/new_invoice_ahui/(?P<type>\d{1})/(?P<code>\d{8})/(?P<start_date>\d{4}-\d{2}-\d{2})/(?P<end_date>\d{4}-\d{2}-\d{2})/(?P<ehnii>-?\d+\.\d{2})/(?P<before_payment>\d+\.\d{2})/(?P<payment>\d+\.\d{2})/(?P<bichilt>-?\d+\.\d{2})/$', InvoiceAhui1.as_view()),
    url(r'^borluulalt/new_invoice_aan/(?P<type>\d{1})/(?P<code>\d{8})/(?P<start_date>\d{4}-\d{2}-\d{2})/(?P<end_date>\d{4}-\d{2}-\d{2})/(?P<ehnii>-?\d+\.\d{2})/(?P<before_payment>\d+\.\d{2})/(?P<payment>\d+\.\d{2})/(?P<bichilt>-?\d+\.\d{2})/$', InvoiceAan1.as_view()),
    url(r'^borluulalt/invoice_detail_ahui/(?P<code>\d{7})/(?P<start_date>\d{4}-\d{2}-\d{2})/(?P<end_date>\d{4}-\d{2}-\d{2})/(?P<ehnii>-?\d+\.\d{2})/$', InvoiceDetailAhui.as_view()),
    url(r'^borluulalt/invoice_detail_aan/(?P<code>\d{7})/(?P<start_date>\d{4}-\d{2}-\d{2})/(?P<end_date>\d{4}-\d{2}-\d{2})/(?P<ehnii>-?\d+\.\d{2})/$', InvoiceDetailAan.as_view()),
    url(r'^send_invoice', send_invoice),
    url(r'^disconnect', disconnect),
    url(r'^avlaga_confirm', avlaga_confirm),
    url(r'^borluulalt/send_email', send_email),
    url(r'^salgalt_one', salgalt_one),
    url(r'^salgalt_all', salgalt_all),
    url(r'^avlaga_neh', av_nehemjleh),

    url(r'^borluulalt/orlogo_list/delete/(?P<id>\d+)/(?P<code>\d{8})/(?P<orlogo>-?\d+\.\d{2})/', OrlogoDelete.as_view(), name='orlogo_delete'),
    url(r'^borluulalt/orlogo_list/edit/(?P<id>\d+)/', OrlogoEdit.as_view(), name='orlogo_edit'),
    url(r'^borluulalt/orlogo_list', OrlogoList.as_view(), name='orlogo_list'),
    url(r'^export/orlogoxls/$', OrlogoList.export_xls, name='export_orlogo_xls'),
    url(r'^borluulalt/orlogo_add', OrlogoAdd.as_view()),
    url(r'^borluulalt/orlogo_import', OrlogoImport.as_view()),
    url(r'^orlogo_nehemjleh', orlogo_nehemjleh),

    url(r'^vilchilgee/delete/(?P<id>\d+)/', UilchilgeeDelete.as_view(), name='uilchilgee_delete'),
    url(r'^vilchilgee', UilchilgeeList.as_view(), name='uilchilgee_list'),
    url(r'^add_vilchilgee', Uilchilgee_add.as_view()),
    url(r'^get_toobyuser', get_tooluur_byuser),
    url(r'^get_username_addr', get_username_addr),
    url(r'^get_uilchilgee_bytype', get_uilchilgee_bytype),

    url(r'^borluulalt/taslalt', TaslaltZalgaltList.as_view(), name='taslaltzalgalt_list'),
    url(r'^borluulalt/taslah/(\d+)/', TaslaltHiih.as_view()),
    url(r'^borluulalt/zalgah/(\d+)/', ZalgaltHiih.as_view()),

    url(r'^borluulalt/bichilt_full', BichiltFull.as_view()),

    url(r'^duudlaga', views.duudlaga, name='duudlaga'),
    url(r'^call_customerdetail/(\d+)', CustomerDetail.as_view()),
    url(r'^call_list', CallList.as_view()),
    url(r'^get_bair_block', get_bair_block),
    url(r'^get_default_start', get_default_start, name='get_default_start'),
    url(r'^get_khotkhon', get_khotkhon, name='get_khotkhon'),
    url(r'^get_bairs', get_bairs, name='get_bairs'),
    url(r'^get_toots', get_toots, name='get_toots'),
    url(r'^call_add/(\d+)/', CallAdd.as_view(), name='call_add'),
    url(r'^call_edit/(\d+)/(\d+)/', CallEdit.as_view()),
    url(r'^call_delete/(\d+)/', CallDelete.as_view()),
    url(r'^call_detail/(\d+)/', CallDetail.as_view()),
    url(r'^call_activity_add/(\d+)/', CallActivityAdd.as_view()),
    url(r'^call_activity_delete/(\d+)/(\d+)/', CallActivityDelete.as_view()),
    url(r'^call_activity_edit/(\d+)/(\d+)/', CallActivityEdit.as_view()),
    url(r'^get_sub_call_types', get_sub_call_types),
    url(r'^get_detail_bytooluur', get_tooluur_detail),

    url(r'^lavlah', views.lavlah.as_view(), name='lavlah'),
    url(r'^lavlagaa/ahui_hereglegch', AhuiListView.as_view(), name='ahui_hereglegch'),
    url(r'^lavlagaa/ahui_delete/(\d+)/', AhuiDeleteView.as_view(), name='ahui_delete'),
    url(r'^lavlagaa/ahui_edit/(\d+)/', AhuiEditView.as_view(), name='ahui_edit'),
    url(r'^lavlagaa/ahui_add', AhuiAddView.as_view(), name='ahui_add'),
    url(r'^lavlagaa/enquire_price', views.enquire_price, name='enquire_price'),

    url(r'^lavlagaa/aan_angilal', AANListView.as_view(), name='aan_angilal'),
    url(r'^lavlagaa/aan_del/(\d+)/', AANDeleteiew.as_view(), name='aan_angilal_del'),
    url(r'^lavlagaa/aan_edit/(\d+)/', AANEditView.as_view(), name='aan_angilal_edit'),
    url(r'^lavlagaa/aan_add', AANAddView.as_view(), name='aan_angilal_add'),

    url(r'^lavlagaa/sub_calltype_add', SubTypeList.as_view(), name='sub_calltype_add'),

    url(r'^lavlagaa/guidliin_trans', guidliin_trans.as_view(), name='guidel'),
    url(r'^lavlagaa/add_guidliin_trans', GuidliinTransAdd.as_view(), name='guidel'),
    url(r'^lavlagaa/guidel_edit/(\d+)/', GuidliinTransEdit.as_view()),
    url(r'^lavlagaa/guidel_del/(\d+)/', GuidelDel.as_view()),

    url(r'^lavlagaa/huchdeliin_trans', HuchdeliinTrans.as_view(), name='guidel'),
    url(r'^lavlagaa/add_huchdeliin_trans', HuchdeliinTransAdd.as_view(), name='guidel'),
    url(r'^lavlagaa/huchdel_edit/(\d+)/', HuchdeliinTransEdit.as_view()),
    url(r'^lavlagaa/huchdel_del/(\d+)/', HuchdelDel.as_view()),

    url(r'^lavlagaa/une_tarif', UneTarif.as_view(), name='une'),
    url(r'^lavlagaa/add_unetarif', UneTarifAdd.as_view(), name='une'),
    url(r'^lavlagaa/edit_unetarif/(\d+)/', UneTarifEdit.as_view()),
    url(r'^lavlagaa/del_unetarif/(\d+)/', UneDel.as_view()),

    url(r'^lavlagaa/list_ded_stants_angilal', DedStantsAngilalList.as_view(), name='list_ded_stants_angilal'),
    url(r'^lavlagaa/add_ded_stants_angilal', DedStantsAngilalAdd.as_view(), name='add_ded_stants_angilal'),
    url(r'^lavlagaa/edit_ded_stants_angilal/(\d+)/', DedStantsAngilalEdit.as_view(), name='edit_ded_stants_angilal'),
    url(r'^lavlagaa/del_ded_stants_angilal/(\d+)/', DedStantsAngilalDel.as_view(), name='del_ded_stants_angilal'),

    url(r'^lavlagaa/ded_stants', DedStantsList.as_view(), name='stants'),
    url(r'^lavlagaa/dedstants_del/(\d+)/', DedStantsDel.as_view()),
    url(r'^lavlagaa/add_ded_stants', DedStantsAdd.as_view(), name='stants'),
    url(r'^lavlagaa/dedstants_edit/(\d+)/', DedStantsEdit.as_view()),

    url(r'^lavlagaa/tooluur', LavlahTooluur.as_view(), name='tooluur'),
    url(r'^lavlagaa/add_tooluur', LavlahTooluurAdd.as_view(), name='tooluur'),
    url(r'^lavlagaa/t_del/(\d+)/', LavlagaaTooluurDel.as_view()),
    url(r'^lavlagaa/t_edit/(\d+)/', LavlagaaTooluurEdit.as_view()),

    url(r'^lavlagaa/cycle', CycleList.as_view(), name='cycle'),
    url(r'^lavlagaa/del_cycle/(\d+)/', CycleDel.as_view()),
    url(r'^lavlagaa/add_cycle', CycleAdd.as_view(), name='cycle'),
    url(r'^lavlagaa/edit_cycle/(\d+)/', CycleEdit.as_view()),

    url(r'^lavlagaa/bank', BankList.as_view(), name='bank'),
    url(r'^lavlagaa/del_bank/(\d+)/', BankDel.as_view()),
    url(r'^lavlagaa/add_bank', BankAdd.as_view(), name='bank'),
    url(r'^lavlagaa/edit_bank/(\d+)/', BankEdit.as_view()),

    url(r'^lavlagaa/call_type', CallTypeList.as_view(), name='calltype'),
    url(r'^lavlagaa/del_calltype/(\d+)/', CallTypeDel.as_view()),
    url(r'^lavlagaa/edit_calltype/(\d+)/', CallTypeEdit.as_view()),
    url(r'^lavlagaa/add_calltype', CallTypeAdd.as_view(), name='calltype'),

    url(r'^lavlagaa/aimag_niislel', AimagList.as_view(), name='aimag'),
    url(r'^lavlagaa/del_niislel/(\d+)/', AimagDel.as_view()),
    url(r'^lavlagaa/add_niislel', AimagAdd.as_view(), name='aimag'),
    url(r'^lavlagaa/edit_niislel/(\d+)/', AimagNiislelEdit.as_view()),

    url(r'^lavlagaa/sum_duureg', DuuregList.as_view(), name='duureg'),
    url(r'^lavlagaa/del_sum_duureg/(\d+)/', SumDuuregDel.as_view()),
    url(r'^lavlagaa/add_sum_duureg', SumDuuregAdd.as_view(), name='duureg'),
    url(r'^lavlagaa/edit_sum_duureg/(\d+)/', SumDuuregEdit.as_view()),

    url(r'^lavlagaa/bag_horoo', BagHorooList.as_view(), name='horoo'),
    url(r'^lavlagaa/del_baghoroo/(\d+)/', BagHorooDel.as_view()),
    url(r'^lavlagaa/add_baghoroo', BagHorooAdd.as_view(), name='horoo'),
    url(r'^lavlagaa/edit_baghoroo/(\d+)/', BagHorooEdit.as_view()),

    url(r'^lavlagaa/hothon', HothonList.as_view(), name='hothon'),
    url(r'^lavlagaa/del_hothon/(\d+)/', HothonDel.as_view()),
    url(r'^lavlagaa/add_hothon', HothonAdd.as_view(), name='horoo'),
    url(r'^lavlagaa/edit_hothon/(\d+)/', HothonEdit.as_view()),

    url(r'^lavlagaa/egnee', EgneeList.as_view(), name='egnee'),
    url(r'^lavlagaa/del_egnee/(\d+)/', EgneeDel.as_view()),
    url(r'^lavlagaa/add_egnee', EgneeAdd.as_view(), name='egnee'),
    url(r'^lavlagaa/edit_egnee/(\d+)/', EgneeEdit.as_view()),

    url(r'^lavlagaa/uilchilgee', LavlahUilchilgeeList.as_view(), name='uilchilgee'),
    url(r'^lavlagaa/del_service/(\d+)/', LavlahUilchilgeeDel.as_view()),
    url(r'^lavlagaa/add_service', LavlahUilchilgeeAdd.as_view(), name='egnee'),
    url(r'^lavlagaa/edit_service/(\d+)/', LavlahUilchilgeeEdit.as_view()),

    url(r'^lavlagaa/alban_tushaal', AlbanTushaalList.as_view(), name='tushaal'),
    url(r'^lavlagaa/tushaal_del/(\d+)/', TushaalDel.as_view()),
    url(r'^lavlagaa/add_alban_tushaal', TushaalAdd.as_view(), name='tushaal'),
    url(r'^lavlagaa/tushaal_edit/(\d+)/', TushaalEdit.as_view()),

    url(r'^lavlagaa/aldangi', AldangiList.as_view(), name='aldangi'),
    url(r'^lavlagaa/del_aldangi/(\d+)/', AldangiDel.as_view()),
    url(r'^lavlagaa/add_aldangi', AldangiAdd.as_view(), name='aldangi'),
    url(r'^lavlagaa/edit_aldangi/(\d+)/', AldangiEdit.as_view()),

    url(r'^lavlagaa/bair', LavlagaaBair.as_view(), name='aldangi'),
    url(r'^lavlagaa/add_bair', LavlagaaBairAdd.as_view(), name='aldangi'),
    url(r'^lavlagaa/edit_bair/(\d+)/', LavlagaaBairEdit.as_view()),
    url(r'^lavlagaa/del_bair/(\d+)/', LavlagaaBairDelete.as_view()),

    url(r'^lavlagaa/add_zaavarchilgaa_category', ZaavarchilgaaCatgoryAdd.as_view(), name='zaavarchilgaa_category'),
    url(r'^lavlagaa/edit_zaavarchilgaa_category/(\d+)/', ZaavarchilgaaCatgoryEdit.as_view()),
    url(r'^lavlagaa/del_zaavarchilgaa_category/(\d+)/', ZaavarchilgaaCatgoryDel.as_view()),

    url(r'^lavlagaa/zaavarchilgaa/(\d+)/', ZaavarchilgaaList.as_view(), name='zaavarchilgaa'),
    url(r'^lavlagaa/del_zaavarchilgaa/(\d+)/', ZaavarchilgaaDel.as_view()),
    url(r'^lavlagaa/add_zaavarchilgaa', ZaavarchilgaaAdd.as_view(), name='zaavarchilgaa'),
    url(r'^lavlagaa/edit_zaavarchilgaa/(\d+)/', ZaavarchilgaaEdit.as_view()),

    url(r'^lavlagaa/amper', AmperList.as_view(), name='amper'),
    url(r'^lavlagaa/del_amper/(\d+)/', AmperDel.as_view()),
    url(r'^lavlagaa/add_amper', AmperAdd.as_view(), name='amper'),
    url(r'^lavlagaa/edit_amper/(\d+)/', AmperEdit.as_view()),

    url(r'^lavlagaa/voltage', VoltageList.as_view(), name='voltage'),
    url(r'^lavlagaa/del_voltage/(\d+)/', VoltageDel.as_view()),
    url(r'^lavlagaa/add_voltage', VoltageAdd.as_view(), name='voltage'),
    url(r'^lavlagaa/edit_voltage/(\d+)/', VoltageEdit.as_view()),

    url(r'^lavlagaa/shugam', ShugamList.as_view(), name='shugam'),
    url(r'^lavlagaa/del_shugam/(\d+)/', ShugamDel.as_view()),
    url(r'^lavlagaa/add_shugam', ShugamAdd.as_view(), name='shugam'),
    url(r'^lavlagaa/edit_shugam/(\d+)/', ShugamEdit.as_view()),

    url(r'^lavlagaa/cable', CableList.as_view(), name='cable'),
    url(r'^lavlagaa/del_cable/(\d+)/', CableDel.as_view()),
    url(r'^lavlagaa/add_cable', CableAdd.as_view(), name='cable'),
    url(r'^lavlagaa/edit_cable/(\d+)/', CableEdit.as_view()),

    url(r'^lavlagaa/relei', ReleiList.as_view(), name='relei'),
    url(r'^lavlagaa/del_relei/(\d+)/', ReleiDel.as_view()),
    url(r'^lavlagaa/add_relei', ReleiAdd.as_view(), name='relei'),
    url(r'^lavlagaa/edit_relei/(\d+)/', ReleiEdit.as_view()),

    url(r'^lavlagaa/huchnii_trans', HuchniiTransList.as_view(), name='huchniin_trans'),
    url(r'^lavlagaa/add_huchnii_trans', HuchniiTransAdd.as_view(), name='huchniin_trans'),
    url(r'^lavlagaa/edit_huchnii_trans/(\d+)/', HuchniiTransEdit.as_view()),
    url(r'^lavlagaa/del_huchnii_trans/(\d+)/', HuchniiTransDel.as_view()),

    url(r'^lavlagaa/battery', BatteryList.as_view(), name='battery'),
    url(r'^lavlagaa/del_battery/(\d+)/', BatteryDel.as_view()),
    url(r'^lavlagaa/add_battery', BatteryAdd.as_view(), name='battery'),
    url(r'^lavlagaa/edit_battery/(\d+)/', BatteryEdit.as_view()),

    url(r'^files', FileControlPage.as_view()),
    url(r'^file/add', FileUpload.as_view()),
    url(r'^file/delete/(\d+)/$', FileDeletePage.as_view()),

    url(r'^ashiglalt/tasralt_list/xls', TasraltList.tasralt_list_xls ,name='tasralt_list_xls'),
    url(r'^ashiglalt/tasralt_list/(\d+)/', TasraltList.as_view()),
    url(r'^ashiglalt/tasralt_add', TasraltAdd.as_view()),
    url(r'^ashiglalt/tasralt_edit/(\d+)/', TasraltEdit.as_view()),
    url(r'^ashiglalt/tasralt_del/(\d+)/', TasraltDel.as_view()),

    url(r'^ashiglalt/taslalt_list/xls', TaslaltList.taslalt_list_xls ,name='taslalt_list_xls'),
    url(r'^ashiglalt/taslalt_list/(\d+)/', TaslaltList.as_view()),
    url(r'^ashiglalt/taslalt_add', TaslaltAdd.as_view()),
    url(r'^ashiglalt/taslalt_edit/(\d+)/', TaslaltEdit.as_view()),
    url(r'^ashiglalt/taslalt_del/(\d+)/', TaslaltDel.as_view()),

    url(r'^ashiglalt/uzleg_shalgalt_list', UzlegShalgaltList.as_view()),
    url(r'^ashiglalt/uzleg_shalgalt_add', UzlegShalgaltAdd.as_view()),
    url(r'^ashiglalt/uzleg_shalgalt_edit/(\d+)/', UzlegShalgaltEdit.as_view()),
    url(r'^ashiglalt/uzleg_shalgalt_del/(\d+)/', UzlegShalgaltDel.as_view()),

    url(r'^ashiglalt/naryad_medeelel_list', NaryadMedeelelList.as_view()),
    url(r'^ashiglalt/naryad_medeelel_add', NaryadMedeelelAdd.as_view()),
    url(r'^ashiglalt/naryad_medeelel_edit/(\d+)/', NaryadMedeelelEdit.as_view()),
    url(r'^ashiglalt/naryad_medeelel_del/(\d+)/', NaryadMedeelelDel.as_view()),

    url(r'^ashiglalt/gemtel_list/xls', GemtelList.gemtel_list_xls, name='gemtel_list_xls'),
    url(r'^ashiglalt/gemtel_list/(\d+)/', GemtelList.as_view()),
    url(r'^ashiglalt/gemtel_add', GemtelAdd.as_view()),
    url(r'^ashiglalt/gemtel_edit/(\d+)/', GemtelEdit.as_view()),
    url(r'^ashiglalt/gemtel_del/(\d+)/', GemtelDel.as_view()),

    url(r'^ashiglalt/shuurhai_ajillagaa_list', ShuurhaiAjillagaaList.as_view()),
    url(r'^ashiglalt/shuurhai_ajillagaa_add', ShuurhaiAjillagaaAdd.as_view()),
    url(r'^ashiglalt/shuurhai_ajillagaa_edit/(\d+)/', ShuurhaiAjillagaaEdit.as_view()),
    url(r'^ashiglalt/shuurhai_ajillagaa_del/(\d+)/', ShuurhaiAjillagaaDel.as_view()),

    url(r'^ashiglalt/zaavarchilgaa_list/taniltsah', AshiglaltZaavarTaniltsah.as_view()),
    url(r'^ashiglalt/zaavarchilgaa_list', AshiglaltZaavarchilgaaList.as_view()),
    url(r'^ashiglalt/zaavarchilgaa_add', AshiglaltZaavarchilgaaAdd.as_view()),
    url(r'^ashiglalt/zaavarchilgaa_edit/(\d+)/', AshiglaltZaavarchilgaaEdit.as_view()),
    url(r'^ashiglalt/zaavarchilgaa_del/(\d+)/', AshiglaltZaavarchilgaaDel.as_view()),

    url(r'^ashiglalt/ded_stants/(\d+)/', AshiglaltDedStants.as_view()),

    url(r'^report/(\d+)/', report.as_view(), name='report'),
    # url(r'^report_builder/', include('report_builder.urls')),

    url(r'^report_geree_1', report_contract_resident, name='report_geree_1'),
    url(r'^report_geree_2', report_contract_org, name='report_geree_2'),
    url(r'^report_geree_3', report_geree_3, name='report_geree_3'),
    url(r'^report_geree_4', report_geree_4, name='report_geree_4'),

    url(r'^report_bichilt_2', report_bichilt_2, name='report_bichilt_2'),
    url(r'^report_bichilt_3', report_bichilt_3, name='report_bichilt_3'),
    url(r'^report_bichilt_4', report_bichilt_4, name='report_bichilt_4'),
    url(r'^report_bichilt_6', report_bichilt_6, name='report_bichilt_6'),
    url(r'^report_bichilt_7', report_bichilt_7, name='report_bichilt_7'),
    url(r'^report_bichilt_9', report_bichilt_9, name='report_bichilt_9'),

    url(r'^report_service_1', report_service_1, name='report_service_1'),
    url(r'^report_service_2', report_service_2, name='report_service_2'),

    url(r'^report_avlaga_1', report_avlaga_1, name='report_avlaga_1'),
    url(r'^report_avlaga_2', report_avlaga_2, name='report_avlaga_2'),
    url(r'^report_avlaga_3', report_avlaga_3, name='report_avlaga_3'),

    url(r'^report_ehzh_1', report_ehzh_1, name='report_ehzh_1'),
    url(r'^report_ehzh_2', report_ehzh_2, name='report_ehzh_2'),
    url(r'^report_ehzh_3', report_ehzh_3, name='report_ehzh_3'),
    url(r'^report_ehzh_4', report_ehzh_4, name='report_ehzh_4'),
    url(r'^report_ehzh_5', report_ehzh_5, name='report_ehzh_5'),
    url(r'^report_ehzh_6', report_ehzh_6, name='report_ehzh_6'),

    url(r'^report_negtgel', report_negtgel, name='report_negtgel'),
    url(r'^report_zaalt', report_zaalt, name='report_zaalt'),

    url(r'^medeeleh/zagvar/(\d+)/', WarningDesign.as_view(), name='medeeleh_zagvar'),
    url(r'^medeeleh/zagvar/edit/(\d+)/(\d+)/', WarningDesignEdit.as_view()),
    url(r'^medeeleh/zagvar/delete/(\d+)/(\d+)/', WarningDesignDelete.as_view()),
    url(r'^medeeleh_email_send', WarningEmailSend.as_view(), name='send_email'),
    url(r'^medeeleh_email', WarningEmail.as_view(), name='medeeleh_email'),
    url(r'^medeeleh_sms_send', WarningSmsSend.as_view(), name='send_sms'),
    url(r'^medeeleh_sms', WarningSms.as_view(), name='medeeleh_sms'),
    url(r'^medeeleh_print_hevleh', WarningPrintHevleh.as_view(), name='print_hevleh'),
    url(r'^medeeleh_print', WarningPrint.as_view(), name='medeeleh_print'),
    url(r'^medeeleh/(\d+)/', Warning.as_view(), name='medeeleh'),
    #url(r'^smart_tooluur', get_tooluur_info),
    url(r'^most_request', most_request),
    # url(r'^khan_request', khan_request),
    url(r'^khan_request', khan_transaction),
    url(r'^golomt_transaction', golomt_transaction),
    url(r'^CheckBillingShort', check_billing),
    url(r'^CheckBillingDetails', check_billing_details),

    url(r'^change_password', ChangePassword.as_view()),

    url(r'^pos_init', pos_init),


]