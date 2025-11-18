import os
import shutil
from imagededup.methods import CNN
from pathlib import Path

# ================= CẤU HÌNH =================
INPUT_FOLDER = '/Users/nguyentaman/Downloads/YOLO11_Vietnamese_license_plate/Dataset_Bien_So_Xe/images'
TRASH_FOLDER = 'trash_bin'     
THRESHOLD = 0.95                
REPORT_FILE = 'review_report.html' 

# --- CẤU HÌNH XÓA LABEL ---
DELETE_LABELS = True   # Set False nếu chỉ muốn xóa ảnh, giữ label
LABEL_FOLDER = '/Users/nguyentaman/Downloads/YOLO11_Vietnamese_license_plate/Dataset_Bien_So_Xe/labels'
LABEL_EXT = '.txt'     # Đuôi file label (YOLO là .txt, VOC là .xml)
# ============================================

def get_file_size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return 0

def create_html_report(data_log):
    """Hàm tạo file HTML để xem lại ảnh"""
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f0f0f0; padding: 20px; }
            h1 { text-align: center; color: #333; }
            .container { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }
            .card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); width: 90%; max-width: 800px; display: flex; align-items: center; }
            .image-box { flex: 1; text-align: center; }
            .image-box img { max-width: 100%; max-height: 300px; border: 1px solid #ddd; }
            .arrow { font-size: 24px; padding: 0 20px; color: #888; font-weight: bold; }
            .label { margin-top: 5px; font-size: 12px; color: #555; word-break: break-all;}
            .kept { color: green; font-weight: bold; }
            .deleted { color: red; font-weight: bold; }
            .sub-info { font-size: 11px; color: #888; font-style: italic; }
        </style>
    </head>
    <body>
        <h1>Báo Cáo Dọn Dẹp Dataset</h1>
        <p style="text-align:center">Cột trái: Ảnh giữ lại | Cột phải: Ảnh (và Label) đã chuyển vào Trash</p>
        <div class="container">
    """

    for item in data_log:
        kept_rel = os.path.relpath(item['kept_path'], os.path.dirname(os.path.abspath(REPORT_FILE)))
        deleted_rel = os.path.relpath(item['deleted_path'], os.path.dirname(os.path.abspath(REPORT_FILE)))
        
        label_msg = f"<br><span class='sub-info'>(Label: {item['label_status']})</span>" if DELETE_LABELS else ""

        html_content += f"""
            <div class="card">
                <div class="image-box">
                    <div class="label kept">GIỮ LẠI ({item['kept_name']})</div>
                    <img src="{kept_rel}" alt="Kept Image">
                </div>
                <div class="arrow">➔</div>
                <div class="image-box">
                    <div class="label deleted">ĐÃ XÓA ({item['deleted_name']}){label_msg}</div>
                    <img src="{deleted_rel}" alt="Deleted Image">
                </div>
            </div>
        """

    html_content += "</div></body></html>"

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    

def main():
    if not os.path.exists(TRASH_FOLDER):
        os.makedirs(TRASH_FOLDER)

    cnn_encoder = CNN()

    encodings = cnn_encoder.encode_images(image_dir=INPUT_FOLDER)
    duplicates = cnn_encoder.find_duplicates(encoding_map=encodings, 
                                             min_similarity_threshold=THRESHOLD,
                                             scores=False)


    processed_files = set()
    moved_count = 0
    report_log = []

    for filename, duplicate_list in duplicates.items():
        if not duplicate_list:
            continue

        raw_cluster = [filename] + duplicate_list
        
        valid_cluster = []
        for f in raw_cluster:
            f_path = os.path.join(INPUT_FOLDER, f)
            if os.path.exists(f_path) and f not in processed_files:
                valid_cluster.append((f, f_path))
        
        if len(valid_cluster) < 2:
            continue

        for f_name, _ in valid_cluster:
            processed_files.add(f_name)

        sorted_cluster = sorted(valid_cluster, key=lambda x: get_file_size(x[1]), reverse=True)
        
        best_file_name = sorted_cluster[0][0]
        best_file_path = sorted_cluster[0][1]
        files_to_remove = sorted_cluster[1:]

        
        for file_name, file_path in files_to_remove:
            try:
                label_status = "Không check"
                if os.path.exists(file_path):
                    # 1. Di chuyển Ảnh
                    dst_path = os.path.join(TRASH_FOLDER, file_name)
                    shutil.move(file_path, dst_path)
                    
                    # 2. Xử lý Label (Nếu bật cờ)
                    if DELETE_LABELS:
                        # Tách tên file (bỏ đuôi .jpg) và ghép đuôi label (.txt)
                        base_name = os.path.splitext(file_name)[0]
                        label_name = base_name + LABEL_EXT
                        label_src = os.path.join(LABEL_FOLDER, label_name)
                        label_dst = os.path.join(TRASH_FOLDER, label_name)

                        if os.path.exists(label_src):
                            try:
                                shutil.move(label_src, label_dst)
                                label_status = "Đã xóa kèm"
                            except Exception as e:
                                print(f"      ❌ Lỗi khi move label {label_name}: {e}")
                                label_status = "Lỗi khi xóa"
                        else:
                            print(f"      ⚠️ Không tìm thấy file label: {label_name}")
                            label_status = "Không tìm thấy"

                    moved_count += 1
                    
                    # Ghi log
                    report_log.append({
                        'kept_name': best_file_name,
                        'kept_path': best_file_path,
                        'deleted_name': file_name,
                        'deleted_path': dst_path,
                        'label_status': label_status
                    })

            except Exception as e:
                print(f"   ❌ Lỗi khi di chuyển {file_name}: {e}")

    if report_log:
        create_html_report(report_log)
    else:
        print("Không có file trùng lặp nào được tìm thấy.")

    print("-" * 30)
    print(f"🎉 Hoàn tất! Tổng cộng đã lọc {moved_count} cặp ảnh/label.")

if __name__ == "__main__":
    main()