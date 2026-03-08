import numpy as np
from utils.EOPData import read_eop_data
from utils.SAT_const import SAT_Const
const = SAT_Const()

###### eop = read_eop_data('D:\SoftWare\PythonCode\gongda_mp\missionplan//utils\eop19620101.txt')
eop = read_eop_data('/home/chujiaqing/newpro/gongda_mp/data_file/eop19620101.txt')



def IERS(Mjd_UTC, interp='n'):
    """
    从IERS地球定向参数（EOP）数据中提取指定时刻的参数，支持线性或最近邻插值

    参数:
    eop: EOP数据矩阵（13行×N列，列数=N个数据点），每行含义需与原MATLAB一致：
         - 第4行：数据点对应的修正儒略日（MJD，整数部分，如59947表示2024-01-01）
         - 第5行：x极移（单位：角秒）
         - 第6行：y极移（单位：角秒）
         - 第7行：UT1-UTC时差（单位：秒）
         - 第8行：日长（LOD，单位：秒）
         - 第9行：黄经章动（单位：角秒）
         - 第10行：交角章动（单位：角秒）
         - 第11行：x极移修正（单位：角秒）
         - 第12行：y极移修正（单位：角秒）
         - 第13行：TAI-UTC时差（单位：秒）
    Mjd_UTC: 目标时刻的修正儒略日（UTC，可含小数，如59947.5表示2024-01-01 12:00:00 UTC）
    interp: 插值模式（默认'n'）：
            - 'n'：最近邻插值（取目标时刻所在日期的EOP数据）
            - 'l'：线性插值（在目标时刻前后两个日期的EOP数据间线性插值）
    const: 天文常数对象（需包含Arcs常数，对应SAT_Const类），若为None将自动初始化基础常数

    返回:
    x_pole: x方向极移（单位：弧度）
    y_pole: y方向极移（单位：弧度）
    UT1_UTC: UT1与UTC的时差（单位：秒）
    LOD: 日长（Length of Day，单位：秒）
    dpsi: 黄经章动（单位：弧度）
    deps: 交角章动（单位：弧度）
    dx_pole: x方向极移修正（单位：弧度）
    dy_pole: y方向极移修正（单位：弧度）
    TAI_UTC: TAI与UTC的时差（单位：秒）
    """
    # 若未传入const，初始化基础常数（确保Arcs存在，Arcs=每弧度对应的角秒数）

    # 1. 提取目标时刻的MJD整数部分（对应EOP数据的日期标识）
    mjd_target_int = np.floor(Mjd_UTC).astype(int)
    # 从EOP第4行（MJD整数）中找到匹配的索引（原MATLAB的find(mjd==eop(4,:),1,'first')）
    # 注意：EOP第4行需为整数类型，若为浮点数需先取整
    eop_mjd_int = np.floor(eop[3, :]).astype(int)  # Python索引从0开始，第4行对应索引3
    match_idx = np.where(eop_mjd_int == mjd_target_int)[0]

    if len(match_idx) == 0:
        raise ValueError(f"EOP数据中未找到MJD={mjd_target_int}的记录，请检查EOP数据完整性")
    i = match_idx[0]  # 取第一个匹配索引（与MATLAB的'first'逻辑一致）

    # 2. 根据插值模式计算EOP参数
    if interp == 'l':
        # -------------------------- 线性插值模式 --------------------------
        # 检查是否存在下一个数据点（避免索引越界）
        if i + 1 >= eop.shape[1]:
            raise ValueError(f"MJD={mjd_target_int}为EOP数据最后一个点，无法进行线性插值")

        # 提取前一个和后一个数据点的EOP参数（原MATLAB的preeop和nexteop）
        pre_eop = eop[:, i]  # 前一个数据点（目标日期）
        next_eop = eop[:, i + 1]  # 后一个数据点（目标日期的下一天）

        # 计算时间分数：目标时刻在当天的分钟数 / 1440分钟（1天）
        mfme = 1440 * (Mjd_UTC - mjd_target_int)  # 当天分钟数（0~1440）
        fixf = mfme / 1440.0  # 时间分数（0~1，对应当天00:00到次日00:00）

        # 线性插值计算各参数（角秒单位，后续统一转换为弧度）
        x_pole_arcsec = pre_eop[4] + (next_eop[4] - pre_eop[4]) * fixf  # 第5行→索引4
        y_pole_arcsec = pre_eop[5] + (next_eop[5] - pre_eop[5]) * fixf  # 第6行→索引5
        UT1_UTC = pre_eop[6] + (next_eop[6] - pre_eop[6]) * fixf  # 第7行→索引6（秒）
        LOD = pre_eop[7] + (next_eop[7] - pre_eop[7]) * fixf  # 第8行→索引7（秒）
        dpsi_arcsec = pre_eop[8] + (next_eop[8] - pre_eop[8]) * fixf  # 第9行→索引8（角秒）
        deps_arcsec = pre_eop[9] + (next_eop[9] - pre_eop[9]) * fixf  # 第10行→索引9（角秒）
        dx_pole_arcsec = pre_eop[10] + (next_eop[10] - pre_eop[10]) * fixf  # 第11行→索引10（角秒）
        dy_pole_arcsec = pre_eop[11] + (next_eop[11] - pre_eop[11]) * fixf  # 第12行→索引11（角秒）
        TAI_UTC = pre_eop[12]  # TAI-UTC通常每日不变，取前一个数据点（第13行→索引12）

    elif interp == 'n':
        # -------------------------- 最近邻插值模式 --------------------------
        # 直接取目标日期对应的EOP数据（无需插值）
        target_eop = eop[:, i]

        # 提取各参数（角秒单位，后续统一转换为弧度）
        x_pole_arcsec = target_eop[4]  # 第5行→索引4
        y_pole_arcsec = target_eop[5]  # 第6行→索引5
        UT1_UTC = target_eop[6]  # 第7行→索引6（秒）
        LOD = target_eop[7]  # 第8行→索引7（秒）
        dpsi_arcsec = target_eop[8]  # 第9行→索引8（角秒）
        deps_arcsec = target_eop[9]  # 第10行→索引9（角秒）
        dx_pole_arcsec = target_eop[10]  # 第11行→索引10（角秒）
        dy_pole_arcsec = target_eop[11]  # 第12行→索引11（角秒）
        TAI_UTC = target_eop[12]  # 第13行→索引12（秒）

    else:
        raise ValueError(f"不支持的插值模式 '{interp}'，仅支持 'l'（线性）和 'n'（最近邻）")

    # 3. 单位转换：角秒 → 弧度（除以const.Arcs，即每弧度对应的角秒数）
    x_pole = x_pole_arcsec / const.Arcs
    y_pole = y_pole_arcsec / const.Arcs
    dpsi = dpsi_arcsec / const.Arcs
    deps = deps_arcsec / const.Arcs
    dx_pole = dx_pole_arcsec / const.Arcs
    dy_pole = dy_pole_arcsec / const.Arcs

    return x_pole, y_pole, UT1_UTC, LOD, dpsi, deps, dx_pole, dy_pole, TAI_UTC
