import struct
from datetime import datetime, timedelta


def parse_satellite_dataframe(dataframe, satinfo_file, output_file):
    """
    解析123字节的卫星数据帧并将其转换为文本文件

    参数:
    dataframe (bytes): 123字节的二进制数据帧
    output_file (str): 输出的文本文件路径
    """
    # 检查数据帧长度
    if len(dataframe) != 123:
        raise ValueError(f"数据帧长度应为123字节，实际为{len(dataframe)}字节")

    # 定义时间起点（2025年1月1日0:0:0 UTC）
    base_time = datetime(2025, 1, 1, 0, 0, 0)

    # 解析各个字段
    offset = 0

    # W0: 指令类型 (1字节)
    command_type = dataframe[offset]
    offset += 1

    # W1-W4: 卫星时间的秒整数 (4字节无符号整数)
    seconds = struct.unpack('>I', dataframe[offset:offset + 4])[0]
    offset += 4

    # W5-W8: 卫星时间的秒小数 (4字节无符号整数，表示微秒)
    microseconds = struct.unpack('>I', dataframe[offset:offset + 4])[0]
    offset += 4

    # 计算完整的卫星时间
    satellite_time = base_time + timedelta(seconds=seconds, microseconds=microseconds)

    # W9-W16: 轨道姿态时 (8字节double)
    orbit_attitude_time = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W17-W24: J2000系X轴速度 (8字节double)
    velocity_x = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W25-W32: J2000系Y轴速度 (8字节double)
    velocity_y = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W33-W40: J2000系Z轴速度 (8字节double)
    velocity_z = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W41-W48: J2000系X轴位置 (8字节double)
    position_x = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W49-W56: J2000系Y轴位置 (8字节double)
    position_y = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W57-W64: J2000系Z轴位置 (8字节double)
    position_z = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W65-W72: 四元数qx (8字节double)
    qx = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W73-W80: 四元数qy (8字节double)
    qy = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W81-W88: 四元数qz (8字节double)
    qz = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W89-W96: 四元数qw (8字节double)
    qw = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W97-W104: J2000系角速度x (8字节double)
    angular_velocity_x = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W105-W112: J2000系角速度y (8字节double)
    angular_velocity_y = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W113-W120: J2000系角速度z (8字节double)
    angular_velocity_z = struct.unpack('>d', dataframe[offset:offset + 8])[0]
    offset += 8

    # W121-W122: 校验和 (2字节无符号)
    checksum = struct.unpack('>H', dataframe[offset:offset + 2])[0]
    offset += 2

    # 写入文本文件
    with open(satinfo_file, 'w') as f:
        f.write("卫星数据帧解析结果\n")
        f.write("=" * 40 + "\n")
        f.write(f"指令类型: {command_type}\n")
        f.write(f"卫星时间: {satellite_time}\n")
        f.write(f"轨道姿态时: {orbit_attitude_time:.6f} 秒\n")
        f.write("\n")
        f.write("J2000坐标系速度 (短整数):\n")
        f.write(f"  X轴速度: {velocity_x}\n")
        f.write(f"  Y轴速度: {velocity_y}\n")
        f.write(f"  Z轴速度: {velocity_z}\n")
        f.write("\n")
        f.write("J2000坐标系位置 (短整数):\n")
        f.write(f"  X轴位置: {position_x}\n")
        f.write(f"  Y轴位置: {position_y}\n")
        f.write(f"  Z轴位置: {position_z}\n")
        f.write("\n")
        f.write("四元数 (短整数):\n")
        f.write(f"  qx: {qx}\n")
        f.write(f"  qy: {qy}\n")
        f.write(f"  qz: {qz}\n")
        f.write(f"  qw: {qw}\n")
        f.write("\n")
        f.write("J2000坐标系角速度 (短整数):\n")
        f.write(f"  X轴角速度: {angular_velocity_x}\n")
        f.write(f"  Y轴角速度: {angular_velocity_y}\n")
        f.write(f"  Z轴角速度: {angular_velocity_z}\n")
        f.write(f"  校验和: {checksum}\n")

    print(f"成功解析数据帧并保存到 {satinfo_file}")

    position_x_km = position_x / 1000
    position_y_km = position_y / 1000
    position_z_km = position_z / 1000
    velocity_x_kms = velocity_x / 1000
    velocity_y_kms = velocity_y / 1000
    velocity_z_kms = velocity_z / 1000

    # 生成只包含J2000坐标系位置和速度的文件datarv.txt
    with open(output_file, 'w') as f:
        f.write(f"{position_x_km} {position_y_km} {position_z_km} {velocity_x_kms} {velocity_y_kms} {velocity_z_kms}\n")

    print(f"成功解析数据帧并保存到 {output_file}")
    print(f"成功生成包含J2000坐标系位置和速度的文件 datarv.txt")
def read_hex_file(hex_file_path):
    """从十六进制文件读取数据并转换为字节"""
    try:
        with open(hex_file_path, 'rb') as f:
            binary_data = f.read()
        # 将二进制数据转换为十六进制字符串
        hex_content = binary_data.hex()

        # with open(hex_file_path, 'r') as f:
        #     # 读取文件内容并移除所有空白字符
        #     hex_content = f.read().replace(' ', '').replace('\n', '').replace('\r', '')

        # 将十六进制字符串转换为字节
        print(bytes.fromhex(hex_content))
        return bytes.fromhex(hex_content)
    except FileNotFoundError:
        print(f"错误：找不到文件 {hex_file_path}")
        return None
    except ValueError as e:
        print(f"错误：十六进制文件格式不正确 - {e}")
        return None
    except Exception as e:
        print(f"发生未知错误：{e}")
        return None


# 示例用法
def read_satinfo(hex_file, satinfo_file, output_file):
    # 读取十六进制文件
    dataframe = read_hex_file(hex_file)

    if dataframe:
        # 检查数据长度
        if len(dataframe) != 123:
            print(f"错误：数据长度应为123字节，但读取到{len(dataframe)}字节")
        else:
            # 解析并保存到文本文件
            parse_satellite_dataframe(dataframe, satinfo_file, output_file)

if __name__ == "__main__":
    main()