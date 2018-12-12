# coding=utf-8
import requests
#import datetime
from bs4 import BeautifulSoup
import time

def getSeatDict():
    #数据库读出所有座位
    f = open('./seat_dict.txt','r',encoding='utf-8')
    a = f.read()
    dict_name = eval(a)
    return dict_name

def getRoomName():
    #数据库读出所有房间名
    f = open('./room_name.txt','r',encoding='utf-8')
    a = f.read()
    room_dict = eval(a)
    return room_dict

#手动改信息 暂时不管交互
# def getRequireInfo():
#     #timeVal = datetime.date.today() + datetime.timedelta(days=1)
#     timeVal = datetime.date.today()
#     timeNow = timeVal.strftime('%Y-%m-%d')
#     print('-------------------------------')
#     print('|       今日：'+timeNow+'       |')
#     print('-------------------------------')
#     flag=int(input("抢座1 ，订座0："))
#     timeN = input("日期(格式:2018-12-10,未作格式检查):")
#     room_Name = input("房间名: ")
#     while (room_Name in room_dict.keys())!=True:
#         room_Name = input("Room name not found, try again: ")
#     #房间号
#     roomNum = room_dict[room_Name]
#     seatNum = input("座位号(格式:001): ")
#     while (seatNum in seat_dict[roomNum].keys())!=True:
#         seatNum = input("seat in this room not found, try again: ")
#     #座位号
#     seatId = seat_dict[roomNum][seatNum]
#     #开始和结束时间
#     start_time = float(input("开始时间(8-22，未作当前时间检查): "))
#     end_time = float(input("结束时间(8.5-22.5): "))
#     #返回所有参数
#     return flag,timeN,roomNum,seatId,start_time,end_time



def getHomePage(sess,headers ):
    url = 'http://seat.lib.whu.edu.cn'
    home_page = sess.get(url,headers = headers)
    return home_page

def loginPage(sess,token,synuri,headers,username,password ):
    url2= 'http://seat.lib.whu.edu.cn/auth/signIn'
    payload = {
        'SYNCHRONIZER_TOKEN': token,
        'SYNCHRONIZER_URI':synuri,
        'username':username,
        'password':password,
        'authid':'-1',
        'appId':'a3a5c1faff9e41c2b2447a52c5bd7ea0',
        'appAuthKey':'a109981dd38540d5b20b4af760d7f6f1'
        }
    main_page = sess.post(url2,data=payload,headers=headers)
    return main_page

def loginFunc(sess,username,password):
    #获取登陆页面
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0' }
    home_page = getHomePage(sess,headers )
    while home_page.status_code !=200:
        home_page = getHomePage(sess,headers )
    #bp4解析 得到token
    soup = BeautifulSoup(home_page.text,"html.parser")
    token = soup.find('input',id = 'SYNCHRONIZER_TOKEN')['value']
    synuri = soup.find('input',id = 'SYNCHRONIZER_URI')['value']
    #登陆操作
    main_page = loginPage(sess,token,synuri,headers,username,password )
    while main_page.status_code !=200:
        main_page = loginPage(sess,token,synuri,headers,username,password )
    #bp4解析 得到token
    soup = BeautifulSoup(main_page.text,"html.parser")
    final_token = soup.find('input',id = 'SYNCHRONIZER_TOKEN')['value']
    final_synuri = soup.find('input',id = 'SYNCHRONIZER_URI')['value']
    return final_token,final_synuri


#发送预约包
def sentFunc(sess,seatId,final_token,final_synuri,start_time,end_time,timeNow ):
    url3 = 'http://seat.lib.whu.edu.cn/selfRes'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'}
    payload2 = {
        'SYNCHRONIZER_TOKEN': final_token,
        'SYNCHRONIZER_URI': final_synuri,
        'date': timeNow,
        'start': str(int(start_time*60)),
        'end': str(int(end_time*60)),
        'authid': '-1',
        'appId':'a3a5c1faff9e41c2b2447a52c5bd7ea0',
        'appAuthKey':'a109981dd38540d5b20b4af760d7f6f1',
        'seat': seatId
        }
    ret = sess.post(url3,data=payload2,headers = headers,timeout=0.5)
    if ret.text.find("系统已经为您")!=-1:
        print('抢座成功,座位id: '+seatId)
        return True
    else:
        return False

# #定义子进程
# def myfunc(seatId,start_time,end_time,timeNow):
#     sess = requests.Session()
#     final_token,final_synuri = loginFunc(sess)
#     succ=sentFunc(sess, seatId ,final_token,final_synuri,start_time,end_time,timeNow)
#     return succ
    
if __name__=='__main__':
    '''
    脚本目前因为只录入了信图的座位id，只能用在信图；不过把getSeatNum.py中building参数改一下，应该差不多
    '''
    #读入数据库信息
    seat_dict = getSeatDict()
    room_dict = getRoomName()
    # 配置信息
    # 下面几项分别为：
    # 订座的时间，一般是抢第二日，填第二日日期
    # 座位号，可以通过 python getSeatNum.py获取到存入seat_dict.txt文件中，其中字典索引对应房间名参考room_name.txt(不要某些房间，所以去掉了)
    # 开始时间和结束时间，对于半小时的用.5表示
    # 用户名 密码
    timeNow= '2018-12-13'
    seatId = '9390'
    start_time = 8
    end_time = 22
    username = 'username'
    password = 'password'
    time_now = time.strftime("%H:%M:%S", time.localtime())
    ##默认先抢指定,然后抢同房间的所有座,然后抢所有座
    while True:
        time_now = time.strftime("%H:%M:%S", time.localtime())
        print('\r当前时间：'+time_now,end = '')
        if(time_now >= '22:45:00'):
            print('\n开始抢座..')
            break
    sess = requests.Session()
    final_token,final_synuri = loginFunc(sess,username,password)

    ##默认先抢指定,然后抢同房间的所有座,然后抢所有座
    sorf = sentFunc(sess,seatId,final_token,final_synuri,start_time,end_time,timeNow)
    if sorf == True:
        exit(0)
    print('指定座位没了，尝试抢其他座位...')
    ecp_seat = []
    count = 0 
    for i in room_dict:
        for j in seat_dict[room_dict[i]]:
            count += 1
            try:
                sess = requests.Session()
                final_token,final_synuri = loginFunc(sess,username,password)
                succ=sentFunc(sess, seat_dict[room_dict[i]][j] ,final_token,final_synuri,start_time,end_time,timeNow)
                print('\r当前扫描座位数:'+str(count),end='')
                if succ==True:
                    exit(0)
                count += 1
            except:
                ecp_seat.append(seat_dict[room_dict[i]][j])
                continue
    # #对出错的再次遍历
    # for i in ecp_seat:
    #     try:
    #         succ=sentFunc(sess, i,final_token,final_synuri,start_time,end_time,timeNow)
    #         if succ==True:
    #             exit(0)
    #     except:
    #         continue
    print('\n完事了')




