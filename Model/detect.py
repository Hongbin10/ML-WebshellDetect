# -*- coding: utf8 -*-

import re
import subprocess
import os


def get_file_opcode(fp):
    php_vld_cmd = ['php', '-dvld.active=1', '-dvld.execute=0', '-dvld.dump_paths=0', '-f', fp]

    try:
        raw_out = subprocess.check_output(php_vld_cmd,
                                          stderr=subprocess.STDOUT)
        opcodes = re.findall(r'\*       (\b[A-Z_]+\b) ', raw_out.decode())
        return ' '.join(opcodes)
    except Exception as e:
        import traceback
        traceback.print_exc()
        # print(fp, raw_out)
        return None


def extract_opcodes_for_detect(ind, verberos=False):
    fps = []
    opcodes = []
    count = 0

    # 检查是文件还是目录
    if os.path.isfile(ind):
        # 单文件处理
        if not ind.lower().endswith('.php'):
            return None, None
            
        try:
            opcode_str = get_file_opcode(ind)
            if opcode_str:
                fps.append(ind)
                opcodes.append(opcode_str)
                count += 1
                if verberos:
                    print(count, os.path.basename(ind), len(opcode_str))
                print(f'Parse {ind}\'s opcode.')
        except Exception as e:
            import traceback
            traceback.print_exc()
            pass
    else:
        # 目录处理
        g = os.walk(ind)
        for path, dir_list, file_list in g:
            for fn in file_list:
                if not fn.lower().endswith('.php'): continue

                fp = os.path.join(path, fn)
                try:
                    opcode_str = get_file_opcode(fp)
                    if opcode_str:
                        fps.append(fp)
                        opcodes.append(opcode_str)
                        count += 1
                        if verberos:
                            print(count, fn, len(opcode_str))
                        print(f'Parse {fp}\'s opcode.')
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    pass

    if count == 0:
        return None, None

    return fps, opcodes

def get_feature_from_loaded_model(cv, tfidf, opcodes):
    covec_mat = cv.transform(opcodes).toarray()
    tfidf_mat = tfidf.transform(covec_mat).toarray()

    return tfidf_mat


def delete_files(file_paths):
    successfully_deleted = []
    failed_to_delete = []
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                successfully_deleted.append(file_path)
                print(f"[INFO] 已成功删除文件: {file_path}")
            else:
                failed_to_delete.append(file_path)
                print(f"[WARN] 文件不存在，无法删除: {file_path}")
        except Exception as e:
            failed_to_delete.append(file_path)
            print(f"[ERROR] 删除文件 {file_path} 时出错: {str(e)}")
    return successfully_deleted, failed_to_delete