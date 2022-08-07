import sensor, image, time,utime
from pyb import RTC
#________________________________定义向量和矩阵运算___________________________________________
class Vector:
    def __init__(self, lis):
        self._values = lis   # 在vector中设置私有变量values存储数组数据

    # 返回 dim 维零向量
    @classmethod
    def zero(cls, dim):
        return cls([0] * dim)

    # 返回向量的模
    def norm(self):
        return math.sqrt(sum(e**2 for e in self))

    # 返回向量的单位向量
    def normalize(self):
        if self.norm() < 1e-8:
            raise ZeroDivisionError("Normalize error! norm is zero.")
        return 1 / self.norm() * Vector(self._values)

    # 向量相加，返回结果向量
    def __add__(self, other):
        assert len(self) == len(other), "error in adding,length of vectors must be same"
        return Vector([a + b for a, b in zip(self, other)])

    # 向量相减，返回结果向量
    def __sub__(self, other):
        assert len(self) == len(other), "error in subbing,length of vectors must be same"
        return Vector([a - b for a, b in zip(self, other)])

    # 向量点乘，返回结果向量
    def dot(self, other):
        assert len(self) == len(other),\
            "error in doting,length of vectors must be same."
        return sum(a * b for a,b in zip(self, other))

    # 向量左乘标量，返回结果向量
    def __mul__(self, k):
        return Vector([a * k for a in self])

    # 向量右乘标量，返回结果向量
    def __rmul__(self, k):
        return Vector([a * k for a in self])

    # 向量数量除法，返回结果向量
    def __truediv__(self, k):
        return 1/k * self

    # 向量取正
    def __pos__(self):
        return 1*self

    # 向量取负
    def __neg__(self):
        return -1*self

    # 取出向量的第index个元素,调用时直接vec[]
    def __getitem__(self, index):
        return self._values[index]

    # 返回向量长度，调用时直接len(vec)
    def __len__(self):
        return len(self._values)

    # 返回向量Vector(...)
    def __repr__(self):  # __repr__和__str__都在调用类时自动执行其中一个，倾向位置在最后一个
        return "Vector({})".format(self._values)

    # 返回向量(...),调用时直接print(vec)
    def __str__(self):
        return "({})".format(",".join(str(e) for e in self._values))



class Matrix:

    def __init__(self, list2d):
        self._values = [row[:] for row in list2d]

    @classmethod
    def zero(cls, r, c):
        """返回一个r行c列的零矩阵"""
        return cls([[0] * c for _ in range(r)])

    def T(self):
        """返回矩阵的转置矩阵"""
        return Matrix([[e for e in self.col_vector(i)]
                       for i in range(self.col_num())])

    def __add__(self, another):
        """返回两个矩阵的加法结果"""
        assert self.shape() == another.shape(), \
            "Error in adding. Shape of matrix must be same."
        return Matrix([[a + b for a, b in zip(self.row_vector(i), another.row_vector(i))]
                       for i in range(self.row_num())])

    def __sub__(self, another):
        """返回两个矩阵的减法结果"""
        assert self.shape() == another.shape(), \
            "Error in subtracting. Shape of matrix must be same."
        return Matrix([[a - b for a, b in zip(self.row_vector(i), another.row_vector(i))]
                       for i in range(self.row_num())])

    def dot(self, another):
        """返回矩阵乘法的结果"""
        if isinstance(another, Vector):
            # 矩阵和向量的乘法
            assert self.col_num() == len(another), \
                "Error in Matrix-Vector Multiplication."
            return Vector([self.row_vector(i).dot(another) for i in range(self.row_num())])

        if isinstance(another, Matrix):
            # 矩阵和矩阵的乘法
            assert self.col_num() == another.row_num(), \
                "Error in Matrix-Matrix Multiplication."
            return Matrix([[self.row_vector(i).dot(another.col_vector(j)) for j in range(another.col_num())]
                           for i in range(self.row_num())])

    def __mul__(self, k):
        """返回矩阵的数量乘结果: self * k"""
        return Matrix([[e * k for e in self.row_vector(i)]
                       for i in range(self.row_num())])

    def __rmul__(self, k):
        """返回矩阵的数量乘结果: k * self"""
        return self * k

    def __truediv__(self, k):
        """返回数量除法的结果矩阵：self / k"""
        return (1 / k) * self

    def __pos__(self):
        """返回矩阵取正的结果"""
        return 1 * self

    def __neg__(self):
        """返回矩阵取负的结果"""
        return -1 * self

    def row_vector(self, index):
        """返回矩阵的第index个行向量"""
        return Vector(self._values[index])

    def col_vector(self, index):
        """返回矩阵的第index个列向量"""
        return Vector([row[index] for row in self._values])

    def __getitem__(self, pos):
        """返回矩阵pos位置的元素"""
        r, c = pos
        return self._values[r][c]

    def ni_matrix(self):
        """返回矩阵的逆（二维矩阵）"""
        a=self._values[0][0]
        b=self._values[0][1]
        c=self._values[1][0]
        d=self._values[1][1]
        ni1 = Matrix(([d,-b],[-c,a]))
        k = 1/(a*d-b*c)
        return Matrix([[e * k for e in ni1.row_vector(i)]
                       for i in range(ni1.row_num())])

    def size(self):
        """返回矩阵的元素个数"""
        r, c = self.shape()
        return r * c

    def row_num(self):
        """返回矩阵的行数"""
        return self.shape()[0]

    __len__ = row_num

    def col_num(self):
        """返回矩阵的列数"""
        return self.shape()[1]

    def shape(self):
        """返回矩阵的形状: (行数， 列数)"""
        return len(self._values), len(self._values[0])

    def __repr__(self):
        return "Matrix({})".format(self._values)

    __str__ = __repr__

#________________________________Apriltags相关系数___________________________________________

f_x = (2.8 / 3.984) * 160 # find_apriltags defaults to this if not set
f_y = (2.8 / 2.952) * 120 # find_apriltags defaults to this if not set
c_x = 160 * 0.5 # find_apriltags defaults to this if not set (the image.w * 0.5)
c_y = 120 * 0.5 # find_apriltags defaults to this if not set (the image.h * 0.5)
K_x  = 23
#________________________________卡尔曼滤波器模型___________________________________________
##预测
#pre_Pk=(A.dot(Pk_1)).dot(A.T())+Q
#pre_Xkhat = A.dot(pre_Xk_1hat)
#pre_Xk_1hat = pre_Xkhat

##校正
#Xk_hat = pre_Xk + Kk.dot(Zk - pre_Xk)
#Kk=pre_Pk.dot((pre_Pk_1+R).ni_matrix())
#Pk = (I -Kk).dot(pre_Pk)
#________________________________初始化噪声、误差协方差矩阵及相关变量___________________________________________

q1 = 1
q2 = 1
r1 = 1
r2 = 1
p1 = 1
p2 = 1

R = Matrix([[r1,0],[0,r2]])#测量噪声协方差矩阵
Q = Matrix([[r1,0],[0,r2]])#过程噪声协方差矩阵
P = Matrix([[p1,0],[0,p2]])#误差协方差矩阵
I = Matrix([[1,0],[0,1]])#单位矩阵

T = 0
A = Matrix([[1,T],[0,1]])
H=  Matrix([[1,0],[0,1]])
pre_Pk =Matrix([[0,0],[0,0]])
pre_Pk_1=Matrix([[0,0],[0,0]])
pre_Xkhat = Matrix([[0],[0]])
Xkhat = Matrix([[0],[0]])
Xk_1hat=Matrix([[0],[1]])
Pk_1=Matrix([[p1,0],[0,p2]])
pre_Xk_1hat=Matrix([[0,0],[0,0]])

pre_YPk =Matrix([[0,0],[0,0]])
pre_YPk_1=Matrix([[0,0],[0,0]])
pre_Ykhat = Matrix([[0],[0]])
Ykhat = Matrix([[0],[0]])
Yk_1hat=Matrix([[0],[1]])
YPk_1=Matrix([[p1,0],[0,p2]])#初始值
pre_Yk_1hat=Matrix([[0,0],[0,0]])
K=0
tag_cx_1=0
tag_cy_1=0
X_est=0
V_est=0
Y_est=0
YV_est=0
MEA_V=0
MEA_cx=0

MEA_YV=0
MEA_cy=0
rect2=0
rect3=0
pre_V=0
pre_YV=0
#________________________________卡尔曼滤波器函数定义___________________________________________
def Kalman_x_filter(cx,vx):
    global A,T,K,pre_Xkhat,pre_Xk_1hat,pre_Pk,Xk_hat,Xk_1hat,Pk_1,pre_Pk_1
    Zk= Matrix([[cx],[vx]])
    pre_Xkhat = (A.dot(Xk_1hat))

    pre_Xk_1hat = pre_Xkhat#保留前一时刻的先验估计值

    pre_Pk=(A.dot(Pk_1)).dot(A.T())+Q
    #print("pre_Pk = {}".format(pre_Pk))
    Kk=pre_Pk.dot((pre_Pk+R).ni_matrix())#卡尔曼系数赋值
    #print("Kk = {}".format(Kk))
    pre_Pk_1 = pre_Pk #更新先验误差协方差矩阵
    Xk_hat = pre_Xkhat + Kk.dot(Zk - H.dot(pre_Xkhat))
    Xk_1hat = Xk_hat #更新后验估计
    Pk_1 = (I-Kk.dot(H)).dot(pre_Pk)
    K=K+1
    #print("K = {}".format(K))
    return Xk_hat.__getitem__([0,0]),Xk_hat.__getitem__([1,0])

def Kalman_y_filter(cy,vy):
    global A,T,K,pre_Ykhat,pre_Yk_1hat,pre_YPk,Yk_hat,Yk_1hat,YPk_1,pre_YPk_1
    YZk= Matrix([[cy],[vy]])
    pre_Ykhat = (A.dot(Yk_1hat))

    pre_Yk_1hat = pre_Ykhat

    pre_YPk=(A.dot(YPk_1)).dot(A.T())+Q
    #print("pre_Pk = {}".format(pre_Pk))
    YKk=pre_YPk.dot((pre_YPk+R).ni_matrix())
    #print("Kk = {}".format(Kk))
    pre_YPk_1 = pre_YPk
    Yk_hat = pre_Ykhat + YKk.dot(YZk - H.dot(pre_Ykhat))
    Yk_1hat = Yk_hat
    YPk_1 = (I-YKk.dot(H)).dot(pre_YPk)
    return Yk_hat.__getitem__([0,0]),Yk_hat.__getitem__([1,0])

#________________________________主函数___________________________________________

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
rtc = RTC()#利用RTC内置函数计时，以便得到模型测量的时间差
rtc.datetime((0,0,0,0,0,0,0,0))
date1=[0,0,0,0,0,0,0,0]

while(True):
    sensor.skip_frames(time = 0)
    sensor.set_auto_gain(False)
    clock = time.clock()
    clock.tick()
    img = sensor.snapshot()
    find_tag = img.find_apriltags() #找APRILTAG
    if find_tag:
      date2 = rtc.datetime()
      for tag in img.find_apriltags(fx=f_x, fy=f_y, cx=0, cy=c_y):

       T =1/255*(date1[7]-date2[7])+date2[6]-date1[6]#date1[7]是1/255*date1[7]秒
       #print("T = {}".format(T))
       date1[7] = date2[7]
       date1[6] = date2[6]
       MEA_V=(tag.cx()-tag_cx_1)/T            #不是直接的x输出，而是和上一次做比较并滤波

       MEA_YV=(tag.cy()-tag_cy_1)/T

       MEA_cx=tag.cx()
       MEA_cy=tag.cy()

       tag_cx_1 = tag.cx()
       tag_cy_1 = tag.cy()
       A = Matrix([[1,T],[0,1]])
       X_est,V_est=Kalman_x_filter(MEA_cx,MEA_V)
       Y_est,YV_est=Kalman_y_filter(MEA_cy,MEA_YV)
       #print("X_est = {}".format(X_est))
       #print("V_est = {}".format(V_est))
       img.draw_rectangle(int(tag.cx()-(tag.rect()[2])/2),int(tag.cy()-(tag.rect()[3])/2),tag.rect()[2],tag.rect()[3],color = (255, 0, 0))
       img.draw_cross(tag.cx(), tag.cy(), color = (255, 0, 0))
       #X_est和Y_est为卡尔曼预测结果
       img.draw_rectangle(int(X_est-(tag.rect()[2])/2),int(Y_est-(tag.rect()[3])/2),tag.rect()[2],tag.rect()[3],color = (0, 0, 255))
       img.draw_cross(int(X_est), int(Y_est), color = (0, 0, 255))
       rect2,rect3=tag.rect()[2],tag.rect()[3]
    #脱离目标，利用卡尔曼滤波器进行预测
    else:
        A = Matrix([[1,T],[0,1]])
        a=1.6
        X_est,V_est=Kalman_x_filter(X_est,a*MEA_V)
        Y_est,YV_est=Kalman_y_filter(Y_est,a*MEA_YV)
        img.draw_rectangle(int(X_est-rect2/2),int(Y_est-rect3/2),rect2,rect3,color = (0, 0, 255))
        img.draw_cross(int(X_est), int(Y_est), color = (0, 0, 255))
        #print("MEA_cx = {}".format(MEA_cx))
        #print("MEA_V = {}".format(MEA_V))
        #print("X_est = {}".format(X_est))
        #print("V_est = {}".format(V_est))


