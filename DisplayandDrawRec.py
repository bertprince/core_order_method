import cv2
from PIL import Image
from io import BytesIO
# 引入数据
import pymysql

host = '47.93.14.103'
user = 'stu_Liang'
password = 'bertLiang514'
port = 3306
dataset = 'corecatalog_db'
mysql = pymysql.connect(host=host, user=user, password=password, port=port)
cursor = mysql.cursor()
for i in range(172, 502):
    # 159\171
    sql = 'select image,drill_no from corecatalog_db.drill_info where drill_no=' + str(i)+';'
    cursor.execute(sql)
    result = cursor.fetchall()  # tuple数据
    ImgBytes = result[0][0]
    ImgName = result[0][1]
    image = Image.open(BytesIO(ImgBytes))
    image.save('D:\\images\\' + ImgName + '.jpg')
    print('完成了' + str(i) + '/501个图片下载。')
