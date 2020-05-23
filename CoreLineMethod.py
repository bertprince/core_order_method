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
b = 40
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
    for i in range(len(data0)):
        # 获取并赋值点的模长
        m=float(math.sqrt(float(data0[i]['location']['left'])**2 + float(data0[i]['location']['top'])**2))
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

    NotCardHeightMean = 0
    HeightMax = max(HeightList)
    MinY = min(YList)
    if NotCardNum != 0:
        NotCardHeightMean = NotCardSum / NotCardNum
    # ------------------------------------20200212----------------平均值效果更好------------------------------
    # 遍历获得行分组
    RowGroup: List[Any] = []
    groupNum = 0
    while len(data0) > 0:
        PopIndex: List[int] = []
        RowList: List[Any] = []
        for i in range(len(data0)):
            if (float(data0[i]['location']['top'])+float(data0[i]['location']['height']/2)) > (MinY + groupNum * NotCardHeightMean) and (float(data0[i]['location']['top'])+(float(data0[i]['location']['height'])/2)) < (MinY + (groupNum+1) * NotCardHeightMean):
                RowList.append(data0[i])
        if len(RowList) != 0:
            RowGroup += [RowList]
        for j in range(len(RowList)):
            data0.remove(RowList[j])
        groupNum += 1

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
    image = cv2.imread('D:\\images\\' + str(count) + '.jpg')
    font = cv2.FONT_HERSHEY_SIMPLEX

    for i in range(len(RowGroup)):
        for j in range(len(RowGroup[i])):
            xmin = float(RowGroup[i][j]['location']['left'])
            ymin = float(RowGroup[i][j]['location']['top'])
            xmax = xmin + float(RowGroup[i][j]['location']['width'])
            ymax = ymin + float(RowGroup[i][j]['location']['height'])
            cv2.rectangle(image, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color[i], 5)
            cv2.putText(image, str(i+1), (int(xmin), int(ymin)), font, 2, (255, 255, 255), 5)
    dir = 'D:\\images\\' + str(str(count) + 'marked.jpg')
    cv2.imwrite(dir, image)

    # print('%.2f' % NotCardHeightMean)
    # print(groupNum)
    # print(result)
    print('完成了' + str(count) + '/' + str(b) + '张图片的标记')
