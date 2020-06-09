#coding:utf-8
# running with python 3.x
import json
from typing import List, Any
import math

def ReorderCoreJason(json_str):
    data0 = json_str['results']
    # 确定第一个矩形框，距离远点最近的
    length_2_Ori=float("inf")
    NotCardNum = 0
    NotCardSum = 0
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
    NotCardHeightMean = 0
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
                if emptyLoopFactor > 0:
                    emptyLoopFactor = 0

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
                for i in range(0,len(RowList)-1):
                    for j in range(0,len(RowList)-i-1):
                        if float(RowList[j]["location"]["left"]) > float(RowList[j+1]["location"]["left"]):
                            RowList[j],RowList[j+1] = RowList[j+1],RowList[j]
                RowGroup.extend(RowList)
                RowListIsEmpty = False
                # 移除已归行（类）数据
                for j in range(len(RowList)):
                    data0.remove(RowList[j])
            else:
                RowListIsEmpty = True
                emptyLoopFactor += 0.5
                print ("已删除数据为：%s，本次minY= %s,mean= %s， 剩余数据为： %s" % (RowGroup,minY,NotCardHeightMean,data0))
                break
    json_str['results'] = RowGroup
    return json_str

jsondata = []#引入识别后的json数据
reorderedData = ReorderCoreJason(jsondata)
print (reorderedData)