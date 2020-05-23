#coding:utf-8
# running with python 3.x
import json
from typing import List, Any
import math
import cv2
import pymysql

host = '47.93.14.103'
user = 'stu_Liang'
password = 'bertLiang514'
port = 3306
dataset = 'corecatalog_db'
mysql = pymysql.connect(host=host, user=user, password=password, port=port)
cursor = mysql.cursor()
a = 1
b = 130
for count in range(a, b):
    sql = 'select image_data from corecatalog_db.drill_info where drill_no=' + str(count) + ';'
    cursor.execute(sql)
    result = cursor.fetchall()  # tuple数据
    image_dataStr = result[0][0]
    json_str = json.loads(image_dataStr)
    # print(json_str)
    # print(type(json_str))
    # data0为原始数据组，未经过排序和处理
    data0 = json_str['results']
    # 确定第一个矩形框，距离远点最近的
    length_2_Ori=float("inf")
    NotCardNum = 0
    NotCardSum = 0
    HeightList = []
    YList = []
    XList = []
    DropItem = []
    for m in range(len(data0)):
        if data0[m]['location']['height']<=50 or data0[m]['location']['width']<=20:
            DropItem.append(data0[m])
    if  len(DropItem)!=0:
        for i in range(len(DropItem)):
            data0.remove(DropItem[i])
    for i in range(len(data0)):
        # 获取并赋值点的模长
        m=float(math.sqrt(float(data0[i]['location']['left'])**2 + float(data0[i]['location']['top'])**2))
        # 将模长复制给score，原json数据中score是置信度，本算法中无用
        data0[i]['score'] = m
        if length_2_Ori>m:
            length_2_Ori=m
        # print(data0[i]['score'])
        # 获得识别框（除回次卡）的高度均值
        if data0[i]['name']!="card":
            NotCardNum += 1
            NotCardSum += float(data0[i]['location']['height'])

        # 获得所有Height值和top（y）值
        HeightList += [data0[i]['location']['height']]
        YList += [data0[i]['location']['top']]
        # 修正Xlisyt，现在为3倍数据，应该为两倍
        XList += [data0[i]['location']['left']]
        XList += [data0[i]['location']['left']]+[data0[i]['location']['width']]
    NotCardHeightMean = 0
    # HeightMax = max(HeightList)#未用到
    # MinY_ori = min(YList)
    MinX = min(XList)
    MaxX = max(XList)
    ListYmin = []
    if NotCardNum != 0:
        NotCardHeightMean = NotCardSum / NotCardNum
        # ---20200212---平均值效果更好---
        # 遍历获得行分组
        RowGroup: List[Any] = []  # 需要py3.x以上
        RowListIsEmpty = False#用于在while循环中判断行数据是否为空数据
        emptyLoopFactor = 0#空循环加成系数
        # MinY_changed = MinY_ori
        while len(data0) > 0:
            #
            # PopIndex: List[int] = []
            if not RowListIsEmpty:
                # 每次换行重新计算行开始坐标
                ylist = []
                for k in range(len(data0)):
                    ylist += [data0[k]['location']['top']]
                minY = min(ylist)
                ListYmin.append(minY)

            RowList: List[Any] = []
            for i in range(len(data0)):
                # 如果数据的矩形框的中心点Y坐标在根据平均高度计算的行之间，则归入该行
                if not RowListIsEmpty:
                    if (float(data0[i]['location']['top']) + float(data0[i]['location']['height'] / 2)) > (
                            minY) and (
                            float(data0[i]['location']['top']) + (float(data0[i]['location']['height']) / 2 )) < (
                            minY + NotCardHeightMean):
                        RowList.append(data0[i])
                else:
                    if (float(data0[i]['location']['top']) + float(data0[i]['location']['height'] * 2 / 3)) > (
                            minY) and (
                            float(data0[i]['location']['top']) + (float(data0[i]['location']['height']) * 2 / 3)) < (
                            minY + NotCardHeightMean*(emptyLoopFactor+1)):
                        RowList.append(data0[i])
            # 成行
            if len(RowList) != 0:
                RowGroup += [RowList]
                RowListIsEmpty = False
                # 移除已归行（类）数据
                for j in range(len(RowList)):
                    data0.remove(RowList[j])
            else:
                RowListIsEmpty = True
                emptyLoopFactor += 0.5
                print ("已删除数据为：%s，本次minY= %s,mean= %s， 剩余数据为： %s" % (RowGroup,minY,NotCardHeightMean,data0))
                break


    # 引入数据
    # host = '47.93.14.103'
    # user = 'stu_Liang'
    # password = 'bertLiang514'
    # port = 3306
    # dataset = 'corecatalog_db'
    # mysql = pymysql.connect(host=host, user=user, password=password, port=port)
    # cursor = mysql.cursor()
    # sql = 'select image from corecatalog_db.drill_info where drill_no = "1";'
    #
    # cursor.execute(sql)
    # result = cursor.fetchall() # tuple数据

    # bytes_stream = BytesIO(result[0][0]) #result[0][0]为bytes类型数据
    # byte_array = numpy.frombuffer(bytes_stream)
    # Displayimg = Image.open(bytes_stream)
    # lena = mpimg.imread('001.jpg')
    # image = cv2.imread(lena)
    # plt.imshow(image)
    # plt.axis('off')
    # plt.show()
    color = [(0, 255, 2), (255, 0, 0), (0, 0, 255), (0, 100, 0), (100, 100, 0), (20, 30, 50), (0, 0, 20)]
    # 需要优化，没有对应图片的化，需要自动从数据库读取
    image = cv2.imread('F:\\Py Files\\PyProjects\\CoreLineModification\\images\\' + str(count) + '.jpg')
    font = cv2.FONT_HERSHEY_SIMPLEX

    for i in range(len(RowGroup)):
        cv2.line(image,(int(MinX),int(ListYmin[i]+i*NotCardHeightMean)),(int(MaxX),int(ListYmin[i]+i*NotCardHeightMean)),color[i],5)
        for j in range(len(RowGroup[i])):
            xmin = float(RowGroup[i][j]['location']['left'])
            ymin = float(RowGroup[i][j]['location']['top'])
            xmax = xmin + float(RowGroup[i][j]['location']['width'])
            ymax = ymin + float(RowGroup[i][j]['location']['height'])
            cv2.rectangle(image, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color[i], 5)
            cv2.putText(image, str(i+1)+"-"+str(j+1), (int(xmin), int(ymin)), font, 2, (255, 255, 255), 5)
    dir = 'F:\\Py Files\\PyProjects\\CoreLineModification\\images\\' + str(str(count) + '_marked.jpg')
    cv2.imwrite(dir, image)

    # print('%.2f' % NotCardHeightMean)
    # print(groupNum)
    # print(result)
    print('完成了' + str(count-a) + '/' + str(b-a) + '张图片的标记')
