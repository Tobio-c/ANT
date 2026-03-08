hex16_data = """
3C000003CD00055730408E67999999999A
0000000000000000
0000000000001DEC
0000000000000000
0000000000676C90
0000000000000000
0000000000000000
""" + "00"*58  # 65-122 的58个零

# 移除空白字符
clean_hex = hex16_data.replace("\n", "").replace(" ", "")
bytes_data = bytes.fromhex(clean_hex)
print(f"生成字节数: {len(bytes_data)}")
assert len(bytes_data) == 123, "字节数错误，应为123字节"
output_path = r"D:\SoftWare\PythonCode\gongda_mp\data_file\data_123bytes.bin"
with open(output_path, "wb") as f:
    f.write(bytes_data)
print(f"文件已生成: {output_path}")