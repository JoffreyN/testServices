"""testServices URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from django.conf.urls import include, url

from . import views
from django.views.generic.base import TemplateView
from django.views.static import serve
from django.conf import settings



urlpatterns = [
    path('admin/',admin.site.urls),#admin aaaa1111
    url(r'^$',views.index),
    url('index/',views.index),
    url('index-old/',views.index_old),

    url('login/',views.accLogin),
    url('logout/',views.accLogout),
    url(r'^changepwd/',views.changepwd),
    url(r'^createuser/',views.createuser),
    url(r'^resetpwd/',views.resetpwd),

    url(r'^hello',views.hello),
    url(r'^echo',views.echo),
    url(r'^ttl_resetPwd',views.ttl_resetPwd),
    url(r'^abc_resetPwd',views.abc_resetPwd),
    url(r'^ttl_inMoney',views.ttl_inMoney),
    url(r'^get_ttl_checkId',views.get_ttl_checkId),
    url(r'^ttl_checkInMoney',views.ttl_checkInMoney),
    url(r'^getTestAccount',views.getTestAccount),
    url(r'^queryClientInfo',views.queryClientInfo),
    url(r'^unlockAccount',views.unlockAccount),
    url(r'^grayControl',views.grayControl),
    url(r'^rpqTest',views.rpqTest),
    # url(r'^getKafkalog',views.getKafkalog),
    url(r'^parsePB2',views.parsePB2),
    url(r'^addHold',views.addHold),
    url(r'^ttl_addHold',views.ttl_addHold),
    url(r'^addMoney',views.addMoney),
    url(r'^cms_createUesr',views.cms_createUesr),
    url(r'^TTLgrayControl',views.TTLgrayControl),
    url(r'^UIAutoControl',views.UIAutoControl),
    url(r'^getStockList',views.getStockList),
    url(r'^regByApi',views.regByApi),
    url(r'^bankSecuritiesAddMoney',views.bankSecuritiesAddMoney),
    url(r'^addIPO',views.addIPO),
    url(r'^accountLogout',views.accountLogout),
    url(r'^portfolio',views.portfolio),
    url(r'^uploadPDF',views.uploadPDF),
    url(r'^openmarket',views.openmarket),
    url(r'^getViewXY',views.getViewXY),
    url(r'^saveViewXY',views.saveViewXY),
    url(r'^unBinding',views.unBinding),
    url(r'^getTTLsessionID',views.getTTLsessionID),

    # url('health',views.health),
    # url('show', TemplateView.as_view(template_name="show.html")), 
    # url('statistics/',include('apiStatistics.urls')),
    # re_path(r'^report/(?P<path>.*)$', serve, {'document_root':settings.REPORT_DIR})
]