__author__ = 'likangwei'
import urllib
import lxml
import lxml.html
from util import md5util
import os
import urllib2
from urlparse import urlsplit


def get_html_str(tran_page_url):
    if not tran_page_url:
        return ''
    url_md5 = md5util.get_md5_value(tran_page_url)
    html_tmp_file_name = "tmp/%s.html" %url_md5
    print os.path.abspath(html_tmp_file_name)

    if os.path.exists(html_tmp_file_name):
        print 'reload from cache %s' %tran_page_url
        return open(html_tmp_file_name).read()
    else:
        uss = urlsplit(tran_page_url)
        refer = '%s://%s' %(uss.scheme, uss.netloc)
        req = urllib2.Request(tran_page_url)
        req.add_header('Referer', refer)
        try:
            r = urllib2.urlopen(req)
            html_str = r.read()
            open(html_tmp_file_name, 'w').write(html_str)
            return html_str
        except Exception, e:
            error_msg = '%s ===>  %s' % (tran_page_url, str(e))
            return error_msg


def get_html_element(tran_page_url):
    html_str = get_html_str(tran_page_url)
    html_element = lxml.html.fromstring(html_str)
    return html_element


if __name__ == '__main__':

    req = urllib2.Request('https://docs.djangoproject.com/xxx/1.8/')
    req.add_header('Referer', 'https://docs.djangoproject.com')
    try:
        r = urllib2.urlopen(req)
    except Exception,e:
        print 1
    print r.read()