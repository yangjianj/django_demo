from django.conf.urls import include, url
from django.contrib import admin
from cmdb import views
#import settings
urlpatterns = [
    # Examples:
    # url(r'^$', 'testdemo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^$', view.hello),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^index/', views.index),
    url(r'^htmlpage/', views.htmlpage),
    url(r'^portal_vlan_connect/', views.portal_vlan_connect),
    url(r'^server_connect_ssid_and_set_ip/', views.server_connect_ssid_and_set_ip),
    url(r'^ping_dstserver/', views.ping_dstserver),
    url(r'^search-post/', views.search_post),
    url(r'^bandwidth_test_both_wireless/', views.bandwidth_test_both_wireless),
    url(r'^bandwidth_test_local_wireless/', views.bandwidth_test_local_wireless),
    url(r'^bandwidth_test_local_wireless_test/', views.bandwidth_test_local_wireless_test),
    url(r'^autolog/', views.autolog),
    url(r'^test/', views.test),
    #url(r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.STATIC_URL}),
]
