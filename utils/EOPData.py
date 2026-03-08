import numpy as np


def read_eop_data(filename):
    """
    从EOP数据文件中读取地球定向参数，格式与原MATLAB代码兼容

    参数:
    filename: EOP数据文件路径（如'eop19620101.txt'）

    返回:
    eopdata: 13行×N列的numpy数组，每行对应原MATLAB代码中的参数：
             - 行0: 日期（整数，格式如YYYYMMDD）
             - 行1: MJD（修正儒略日，整数部分）
             - 行2: 预留（原格式中的第3列）
             - 行3: 预留（原格式中的第4列）
             - 行4: x极移（角秒）
             - 行5: y极移（角秒）
             - 行6: UT1-UTC时差（秒）
             - 行7: 日长LOD（秒）
             - 行8: 黄经章动dPsi（角秒）
             - 行9: 交角章动dEpsilon（角秒）
             - 行10: dX极移修正（角秒）
             - 行11: dY极移修正（角秒）
             - 行12: DAT（TAI-UTC时差，秒）
    """
    # 打开文件并读取所有数据
    with open(filename, 'r') as fid:
        # 跳过标题行（假设前3行为标题，根据实际文件调整）
        # 读取前3行并忽略（与原MATLAB中跳过注释行的逻辑一致）
        for _ in range(3):
            fid.readline()

        # 读取数据部分，使用与MATLAB相同的格式字符串解析
        # 格式说明：%i %d %d %i %f %f %f %f %f %f %f %f %i
        # 对应13个字段，依次为：
        # 1. 日期（整数）
        # 2. MJD（整数）
        # 3. 第3列（整数）
        # 4. 第4列（整数）
        # 5-12. x, y, UT1-UTC, LOD, dPsi, dEpsilon, dX, dY（浮点数）
        # 13. DAT（整数）
        data = []
        for line in fid:
            # 跳过空行
            if not line.strip():
                continue
            # 解析每行数据，使用split处理空格分隔
            parts = line.strip().split()
            # 确保每行有13个字段
            if len(parts) != 13:
                continue  # 跳过格式错误的行
            # 转换为对应的数据类型
            try:
                row = [
                    int(parts[0]),  # 日期
                    int(parts[1]),  # MJD
                    int(parts[2]),  # 第3列
                    int(parts[3]),  # 第4列
                    float(parts[4]),  # x极移
                    float(parts[5]),  # y极移
                    float(parts[6]),  # UT1-UTC
                    float(parts[7]),  # LOD
                    float(parts[8]),  # dPsi
                    float(parts[9]),  # dEpsilon
                    float(parts[10]),  # dX
                    float(parts[11]),  # dY
                    int(parts[12])  # DAT
                ]
                data.append(row)
            except ValueError:
                # 跳过转换失败的行
                continue

    # 将列表转换为numpy数组，并转置为13行×N列（与MATLAB的eopdata格式一致）
    if not data:
        raise ValueError("未从文件中读取到有效数据")

    eopdata = np.array(data, dtype=np.float64).T

    return eopdata


# 使用示例
if __name__ == "__main__":
    try:
        eopdata = read_eop_data('./eop19620101.txt')
        print(f"成功读取EOP数据，形状为: {eopdata.shape}")
        print("前5列数据预览:")
        print(eopdata[:, :5])  # 打印前5列数据
    except Exception as e:
        print(f"读取EOP数据失败: {str(e)}")
