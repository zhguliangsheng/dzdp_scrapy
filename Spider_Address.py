# coding: UTF-8
import xlwt

'''
爬取网页时直接出现403，意思是没有访问权限
'''
from bs4 import BeautifulSoup
import urllib
# 入口网页
start_url = 'https://www.dianping.com/changsha/ch10'  #长沙美食


def get_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Cookie':'cy=1; cye=shanghai; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_cuid=164c9e2cad2c8-0881b9c09552e6-5b193413-100200-164c9e2cad4c8; _lxsdk=164c9e2cad2c8-0881b9c09552e6-5b193413-100200-164c9e2cad4c8; _hc.v=b4246e94-470f-1aa8-cf98-df323c97ad13.1532395442; s_ViewType=10; _lxsdk_s=164c9e2cad4-387-e39-c15%7C%7C112'
        }
    req = urllib.request.Request(url=url, headers=headers)
    html = urllib.request.urlopen(req).read().decode("utf-8")
    return html

'''
    获取所有行政区的url
'''


def region_url(html):
    soup = BeautifulSoup(html, 'lxml')  # lxml解析器
    # <div id="region-nav" class="nc-items ">
    #   <a href="/search/category/344/10/r299"><span>芙蓉区</span></a>
    # 列表推导式

    region_url_list = [i['href'] for i in soup.find('div', id="region-nav").find_all('a')]
    return region_url_list


# 获取商户的详情页的url地址
# find:取第一个(返回一个具体的元素，没有为null)       find_all:匹配所有(返回列表，没有返回[])
def get_shop_url(html):
    soup = BeautifulSoup(html, 'lxml')  # lxml解析器
    shop_url_list = [i.find('a')['href'] for i in soup.find_all('div', class_='tit')]
    return shop_url_list


# 获取所得信息(店名，价格，评分)。。。解析页面
def get_detail(html):
    soup = BeautifulSoup(html, 'lxml')  # lxml解析器
    # <h1 class="shop-name">1911牛肉烤串</h1>
    title = soup.find('div', class_='breadcrumb').find('span').text
    # <span id="avgPriceTitle" class="item">人均：-</span>
    price = soup.find('span', id="avgPriceTitle").text
    # <span id="comment_score"><span class="item">口味：7.6</span><span class="item">环境：7.4</span><span class="item">服务：7.5</span></span>
    evaluation = soup.find('span', id="comment_score").find_all('span', class_="item")  # 评分的list
    # <span id="reviewCount" class="item">3条评论</span>
    comments = soup.find('span', id="reviewCount").text  # 评论的数量
    #     <div class="expand-info address" itemprop="street-address">
    #         <span class="item" itemprop="street-address" title="麓松路南丰港安置小区12栋">
    #                      麓松路南丰港安置小区12栋
    #         </span>
    #     </div>
    address = soup.find('span', class_="item", itemprop="street-address").text.strip()

    #     print u'店名'+title
    #     for ev in evaluation:
    #         print ev.text
    #     print u'价格'+price
    #     print u'评论数量'+comments
    #     print u'地址'+address
    return (title, evaluation[0].text, evaluation[1].text, evaluation[2].text, price, comments, address)


# 文件作为脚本直接执行，而import到其他脚本中是不会被执行的。
if __name__ == '__main__':
    items = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Cookie': '__guid=169583271.1366018690068634000.1532332838354.5256; _lxsdk_cuid=164c62792dec8-0af620d87c03ba-6b1b1279-100200-164c62792dfc8; _lxsdk=164c62792dec8-0af620d87c03ba-6b1b1279-100200-164c62792dfc8; _hc.v=48e5f4dc-11fb-1b35-9255-74c8078901f5.1532332840; s_ViewType=10; monitor_count=14; Hm_lvt_df17baab2895cc586cda96cfc3bb3f95=1532332840; Hm_lpvt_df17baab2895cc586cda96cfc3bb3f95=1532335073; _lxsdk_s=164c62792e1-65e-6b2-b9%7C%7C169'
    }
    html = get_content(start_url)
    region_url_list = region_url(html)
    # 遍历所有行政区的所有商户
    for url in region_url_list:  # 遍历所有的行政区
        # 简单的出错处理，有错则略过
        try:
            for n in range(1, 51):  # 遍历所有的50页
                html=get_content(url + 'p' + str(n))
                # 所有商户的详情页
                shop_url_list = get_shop_url(html)
                for shop_url in shop_url_list:
                    #                 print shop_url
                    # 提取数据，获取
                    detail_html = get_content(shop_url)
                    '''
                    #403 Forbidden（没有访问权限）:
                                            （1）直接出现：
                                            （2）爬取一会儿出现403：可以通过代理ip解决
                    referer   防盗链
                    Host域名
                    Cookie
                    '''
                    items.append(get_detail(detail_html))
        except:
            continue
    new_table = 'dzdp.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('test1')
    headData = ['商户名字', '口味评分', '环境评分', '服务评分', '人均价格', '评论数量', '地址']
    for colnum in range(0, 7):
        ws.write(0, colnum, headData[colnum], xlwt.easyxf('font:bold on'))
    index = 1
    lens = len(items)
    for j in range(0, lens):
        for i in range(0, 7):
            ws.write(index, i, items[j][i])
        index = index + 1

    wb.save(new_table)

