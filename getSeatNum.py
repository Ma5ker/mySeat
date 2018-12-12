import requests
import datetime
from bs4 import BeautifulSoup
def getHomePage(sess,headers):
    url = 'http://seat.lib.whu.edu.cn'
    home_page = sess.get(url,headers = headers)
    return home_page

def loginPage(sess,token,synuri,headers):
    url2= 'http://seat.lib.whu.edu.cn/auth/signIn'
    payload = {
        'SYNCHRONIZER_TOKEN': token,
        'SYNCHRONIZER_URI':synuri,
        # 'username':'2015301500199',
        # 'password':'010019',
        'username':'2015301500200',
        'password':'013313',
        'authid':'-1',
        'appId':'a3a5c1faff9e41c2b2447a52c5bd7ea0',
        'appAuthKey':'a109981dd38540d5b20b4af760d7f6f1'
        }
    main_page = sess.post(url2,data=payload,headers=headers)
    return main_page

def getSeatNum(seat_dict,roomNum,sess,headers,timeNow):
    url = 'http://seat.lib.whu.edu.cn/mapBook/getSeatsByRoom?room='+roomNum+'&date='+timeNow
    page_seat = sess.get(url,headers=headers)
    while(page_seat.status_code!=200):
        page_seat = sess.get(url,headers=headers)
    soup_seat = BeautifulSoup(page_seat.text,"html.parser")
    for liTag in soup_seat.find_all('li'):
        if liTag.get('id')!= None:
            #seat_list.append( liTag.get('id')[5:])
            seat_id = liTag.get('id')[5:]
            seatNum = liTag.find('a',"idle").text
            seat_dict[seatNum] = seat_id




if __name__=='__main__':
    timeVal = datetime.date.today() + datetime.timedelta(days=1)
    timeNow = timeVal.strftime('%Y-%m-%d')

    #房间名对应数字 用于下载座位号
    room_dict = {}
    # room_dict['3C创客空间'] = '4'
    # room_dict['创新学习讨论区'] = '5'
    room_dict['西自然科学区'] = '6'
    room_dict['东自然科学区'] = '7'
    room_dict['西社会科学区'] = '8'
    room_dict['西图书阅览区'] = '9'
    room_dict['东社会科学区'] = '10'
    room_dict['东图书阅览区'] = '11'
    room_dict['自主学习区'] = '12'
    # room_dict['3C创客电子阅读'] = '13'
    # room_dict['3C创客双屏电脑'] = '14'
    room_dict['创新学习苹果区'] = '15'
    room_dict['创新学习云桌面'] = '16'
    fl = open('./room_name.txt','w',encoding='utf-8')
    fl.write(str(room_dict))
    fl.close()

    #房间座位号key的所有座位,二维字典
    roomNum_dict = {}
    for i in [6,7,8,9,10,11,12,15,16]:
        roomNum_dict[str(i)]={}

    sess=requests.session()
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0' }

    #获取登陆页面
    home_page = getHomePage(sess,headers)
    while home_page.status_code !=200:
        home_page = getHomePage(sess,headers)
    #bp4解析 得到token
    soup = BeautifulSoup(home_page.text,"html.parser")
    token = soup.find('input',id = 'SYNCHRONIZER_TOKEN')['value']
    synuri = soup.find('input',id = 'SYNCHRONIZER_URI')['value']

    #登陆操作
    main_page = loginPage(sess,token,synuri,headers)
    while main_page.status_code !=200:
        main_page = loginPage(sess,token,synuri,headers)
    #bp4解析 得到token
    soup = BeautifulSoup(main_page.text,"html.parser")
    final_token = soup.find('input',id = 'SYNCHRONIZER_TOKEN')['value']
    final_synuri = soup.find('input',id = 'SYNCHRONIZER_URI')['value']

    #获取所有座位号
    for i in [6,7,8,9,10,11,12,15,16]:
        getSeatNum( roomNum_dict[str(i)],str(i), sess,headers,timeNow)

    #存入文件
    f = open('./seat_dict.txt','w')
    f.write(str(roomNum_dict))
    f.close()
    #文件读出
    f = open('./seat_dict.txt','r')
    a = f.read()
    dict_name = eval(a)
    if(dict_name == roomNum_dict):
        print('yes')
    else:
        print('no')