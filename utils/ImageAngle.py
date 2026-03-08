from utils.LLA2P_WGS84 import LLA2P_WGS84
from utils.PV_WGS84_J2000 import PV_WGS84_J2000
import numpy as np

def ImageAngle(jd, sat_r_J2000, sat_v_J2000, lla):
    # 将列表转换为数组
    sat_r_J2000 = np.array(sat_r_J2000).reshape((3, 1))
    sat_v_J2000 = np.array(sat_v_J2000).reshape((3, 1))

    # 定义Z轴（偏航轴）为位置矢量反方向
    sat_z_J2000 = -sat_r_J2000

    # 定义Y轴（俯仰轴）指向轨道面法向
    sat_y_J2000 = np.cross(sat_z_J2000.flatten(), sat_v_J2000.flatten()).reshape((3, 1))

    # X轴（滚动轴）由Y轴与Z轴叉乘得到
    sat_x_J2000 = np.cross(sat_y_J2000.flatten(), sat_z_J2000.flatten()).reshape((3, 1))

    # 目标矢量
    tar_r_WGS84 = LLA2P_WGS84(lla)
    tar_v_WGS84 = np.array([0, 0, 0]).reshape((3, 1))
    tar_r_J2000, _ = PV_WGS84_J2000(jd, tar_r_WGS84, tar_v_WGS84)

    # 卫星指向目标矢量(观测矢量)
    st_J2000 = tar_r_J2000 - sat_r_J2000

    # 观测矢量在本体系三轴投影
    st_x_J2000 = np.dot(st_J2000.flatten(), sat_x_J2000.flatten()) / np.linalg.norm(sat_x_J2000)
    st_y_J2000 = np.dot(st_J2000.flatten(), sat_y_J2000.flatten()) / np.linalg.norm(sat_y_J2000)
    st_z_J2000 = np.dot(st_J2000.flatten(), sat_z_J2000.flatten()) / np.linalg.norm(sat_z_J2000)

    # 滚转角及俯仰角
    roll_angle = -np.arctan(st_y_J2000 / st_z_J2000)
    pitch_angle = np.arctan(st_x_J2000 / st_z_J2000)

    return roll_angle, pitch_angle
