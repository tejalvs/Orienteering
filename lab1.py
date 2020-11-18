'''
Terrain type	    Color on map	Photo (legend)
Open land	         #F89412 (248,148,18)	A
Rough meadow	     #FFC000 (255,192,0)	B
Easy movement forest #FFFFFF (255,255,255)	C · D
Slow run forest	     #02D03C (2,208,60)	    E
Walk forest	         #028828 (2,136,40)	F
Impassible vegetation #054918 (5,73,24)	G
Lake/Swamp/Marsh	  #0000FF (0,0,255)	H · I · J
Paved road	          #473303 (71,51,3)	K · L
Footpath	          #000000 (0,0,0)	M · N
Out of bounds	      #CD0065 (205,0,101)	'''

import math
import sys

from PIL import Image
class Point():
    def __init__(self,previous,position):
        self.previous=previous
        self.position=position

        self.cost=0
        self.heuristic=0
        self.fn=0

    def __eq__(self,other):
        return self.position==other.position



finalpath=[]
inputPoints=[]
elevations=[]
img_RGB=None
img_OUT=None
img_ht=0
img_wd=0
oFileName = ""
terrainSpeedRelation = {"#F89412":10,"#FFC000":2,"#FFFFFF":7,"#02D03C":6,"#028828":5,"#054918":0,"#0000FF":0,"#473303":10,"#000000":9,"#CD0065":0,"#F5F542":4,"#42BFF5":7}

def getRGBValues(x,y):
    global img_RGB
    R,G,B=img_RGB.getpixel((x,y))
    return "#{:02X}{:02X}{:02X}".format(R,G,B)

def getTerrain(Terrain):
    global img_RGB
    global img_ht
    global img_wd
    global img_OUT
    img = Image.open(Terrain, 'r')
    img_RGB = img.convert('RGB')
    img_wd, img_ht = img.size
    img_OUT=img_RGB.copy()


def getElevation(Elevation):
    global elevations
    file=open(Elevation,'r')
    for line in file:
        elevations.append([float(j) for j in line.split()])


def getPathPoints(Points):
    global inputPoints
    f=open(Points,'r')
    for line in f:
        nums=line.split()
        inputPoints.append((int(nums[0]),int(nums[1])))


def pathFinder(src,destination):
    srcPt=Point(None,src)
    srcPt.cost = 0
    srcPt.heuristic = 0
    srcPt.fn = 0
    destinationPt = Point(None,destination)
    destinationPt.cost = 0
    destinationPt.heuristic = 0
    destinationPt.fn = 0
    openList = []
    closedList = []
    openList.append(srcPt)
    while len(openList)>0:
        currentPoint=openList[0]
        currentIndex=0
        for index,value in enumerate(openList):
            if value.fn < currentPoint.fn:
                currentPoint=value
                currentIndex=index
        openList.pop(currentIndex)
        closedList.append(currentPoint)
        if currentPoint==destinationPt:
            route=[]
            current=currentPoint
            while current is not None:
                route.append(current.position)
                current=current.previous
            return route[::-1],currentPoint.cost
        surroundingPts=[]
        for nextPt in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            newXpos = currentPoint.position[0]+nextPt[0]
            newYpos = currentPoint.position[1]+nextPt[1]
            PointPosition = (newXpos,newYpos)
            if PointPosition[0]>= (img_ht) or PointPosition[0]<= 0 or PointPosition[1]>=(img_wd) or PointPosition[1]<= 0:
                continue
            if getRGBValues(PointPosition[0],PointPosition[1]) == "#CD0065":
                continue
            if getRGBValues(PointPosition[0],PointPosition[1]) == "#0000FF":
                continue
            if getRGBValues(PointPosition[0],PointPosition[1]) == "#054918":
                continue
            newPt = Point(currentPoint,PointPosition)
            surroundingPts.append(newPt)
        for points in surroundingPts:
            gotPoint = False
            for closedPts in closedList:
                if points == closedPts:
                    gotPoint = True
                    continue
            points.cost = currentPoint.cost + getCostFunctionValue(currentPoint.position,points.position)
            points.heuristic = getHeuristicFunctionValue(currentPoint.position,points.position,destination)
            points.fn = points.cost+points.heuristic
            for openPts in openList:
                if points == openPts and points.fn>openPts.fn:
                    gotPoint = True
                    continue
            if(gotPoint == False):
                openList.append(points)

def getCostFunctionValue(curr,destPt):
    elevation = getElevDiff(curr, destPt)
    pixDist = abs(curr[0] - destPt[0]) + abs(curr[1] - destPt[1])
    disp = math.sqrt(pixDist ** 2 + elevation ** 2)
    return disp

def getElevDiff(points,destinationPt):
    return abs(elevations[points[0]][points[1]] - elevations[destinationPt[0]][destinationPt[1]])

def getHeuristicFunctionValue(points,destinationPt,finalPoint):
    distance = abs(destinationPt[0]-finalPoint[0])+abs(destinationPt[1]-finalPoint[1])
    if(terrainSpeedRelation[getRGBValues(points[0],points[1])]>0):
        speed = distance/terrainSpeedRelation[getRGBValues(destinationPt[0],destinationPt[1])]
        elevation = getElevDiff(points,destinationPt)
        pixDist = abs(points[0]-destinationPt[0])+abs(points[1]-destinationPt[1])
        disp = math.sqrt(pixDist**2+elevation**2)
        return (distance*10)+(speed*30)+(disp*40)

def markPath(Path):
    global img_OUT
    for x in range(len(Path)):
        img_OUT.putpixel(Path[x],(245,66,66))
    img_OUT.save(oFileName,"PNG")

def Fall():
    global terrainSpeedRelation
    terrainSpeedRelation["#FFFFFF"] = terrainSpeedRelation["#FFFFFF"] - 2
    terrainSpeedRelation["#02D03C"] = terrainSpeedRelation["#02D03C"] - 2
    terrainSpeedRelation["#028828"] = terrainSpeedRelation["#028828"] - 2


def Spring():
    global img_RGB
    global img_ht
    global img_wd
    lakeEdge = []
    queue = []
    marshPoints = set()
    layer = {}
    WaterMap = img_RGB.copy()
    for x in range(img_wd - 1):
        for y in range(img_ht - 1):
            if getRGBValues(x, y) == "#0000FF":
                currentPoint = Point(None, (x, y))
                for nextPt in [(0, -1), (-1, 1), (1, -1), (1, 0), (-1, -1), (1, 1), (0, 1), (-1, 0)]:
                    newXpos = currentPoint.position[0] + nextPt[0]
                    newYpos = currentPoint.position[1] + nextPt[1]
                    PointPosition = (newXpos, newYpos)
                    if getRGBValues(PointPosition[0], PointPosition[1]) != "#0000FF":
                        temp = (x, y)
                        lakeEdge.append(temp)
                        break
    for x in range(len(lakeEdge)):
        queue.append(lakeEdge[x])
        layer[lakeEdge[x]] = 0
        while(len(queue)!=0):
            currentPoint=queue.pop()
            for nextPt in [(0, -1), (-1, 1), (1, -1), (1, 0), (-1, -1), (1, 1), (0, 1), (-1, 0)]:
                newXpos = currentPoint[0] + nextPt[0]
                newYpos = currentPoint[1] + nextPt[1]
                PointPosition = (newXpos, newYpos)
                if PointPosition[0]<img_wd and PointPosition[1] < img_ht and PointPosition[0]>=0 and PointPosition[1]>=0:
                    if getRGBValues(PointPosition[0], PointPosition[1]) != "#0000FF" and layer[currentPoint]<=15 and getRGBValues(PointPosition[0], PointPosition[1]) != "#CD0065":
                        queue.append(PointPosition)
                        marshPoints.add(PointPosition)
                        layer[PointPosition]=layer[currentPoint]+1

    for x in (marshPoints):
        img_OUT.putpixel(x, (245, 245, 66))

def Winter():
    global img_RGB
    global  img_ht
    global img_wd
    lakeEdge=[]
    WaterMap=img_RGB.copy()
    for x in range(img_wd-1):
        for y in range(img_ht-1):
            if getRGBValues(x,y)=="#0000FF":
                currentPoint= Point(None,(x,y))
                for nextPt in [(0, -1),  (-1, 1), (1, -1), (1, 0), (-1, -1), (1, 1),(0, 1), (-1, 0)]:
                    newXpos = currentPoint.position[0] + nextPt[0]
                    newYpos = currentPoint.position[1] + nextPt[1]
                    PointPosition = (newXpos, newYpos)
                    if getRGBValues(PointPosition[0],PointPosition[1])!="#0000FF":
                        temp=(x,y)
                        lakeEdge.append(temp)
                        break
    BFS(lakeEdge)

def BFS(lakeedge):
    global img_OUT
    queue=[]
    freezePoint= set()
    layer={}
    for x in range(len(lakeedge)):
        queue.append(lakeedge[x])
        layer[lakeedge[x]] = 0
        while(len(queue)!=0):
            currentPoint=queue.pop()
            for nextPt in [(0, -1), (-1, 1), (1, -1), (1, 0), (-1, -1), (1, 1), (0, 1), (-1, 0)]:
                newXpos = currentPoint[0] + nextPt[0]
                newYpos = currentPoint[1] + nextPt[1]
                PointPosition = (newXpos, newYpos)
                if PointPosition[0]<img_wd and PointPosition[1] < img_ht and PointPosition[0]>=0 and PointPosition[1]>=0:
                    if getRGBValues(PointPosition[0], PointPosition[1]) == "#0000FF" and layer[currentPoint]<=7:
                        queue.append(PointPosition)
                        freezePoint.add(PointPosition)
                        layer[PointPosition]=layer[currentPoint]+1

    for x in (freezePoint):
        img_OUT.putpixel(x, (66, 191, 245))



# lab1.py terrain.png mpp.txt red.txt winter redWinter.png
def main():
    global inputPoints
    global finalpath
    global oFileName
    getTerrain(sys.argv[1])
    getElevation(sys.argv[2])
    getPathPoints(sys.argv[3])
    season=sys.argv[4].lower()
    oFileName=sys.argv[5]
    if(season=="winter"):
        Winter()
    elif (season == "fall"):
        Fall()
    elif (season == "spring"):
        Spring()
    totalDist = 0
    for pt in range(len(inputPoints)-1):
        p,dist = pathFinder(inputPoints[pt],inputPoints[pt+1])
        totalDist = dist+totalDist
        finalpath.extend(p)
    print("Total Distance",totalDist)
    markPath(finalpath)





main()