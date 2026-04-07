"""摄像头测试脚本 - 快速验证摄像头是否可用"""
import cv2
import sys

def test_camera(camera_id=0):
    """测试指定摄像头"""
    print(f"正在测试摄像头 {camera_id}...")
    
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"❌ 摄像头 {camera_id} 无法打开")
        return False
    
    # 设置分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # 读取一帧
    ret, frame = cap.read()
    
    if not ret:
        print(f"❌ 摄像头 {camera_id} 无法读取画面")
        cap.release()
        return False
    
    print(f"✅ 摄像头 {camera_id} 工作正常!")
    print(f"   分辨率: {frame.shape[1]}x{frame.shape[0]}")
    
    # 显示测试画面
    print("\n按 'q' 键关闭测试窗口...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 添加提示文字
        cv2.putText(frame, f"Camera {camera_id} - Press 'q' to quit", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Camera Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return True

def find_all_cameras(max_id=10):
    """查找所有可用的摄像头"""
    print("正在扫描可用摄像头...\n")
    available_cameras = []
    
    for i in range(max_id):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            print(f"✅ 找到摄像头: /dev/video{i} (ID: {i})")
            cap.release()
    
    if not available_cameras:
        print("❌ 未找到任何摄像头!")
    else:
        print(f"\n总共找到 {len(available_cameras)} 个摄像头")
    
    return available_cameras

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--scan":
        # 扫描所有摄像头
        find_all_cameras()
    else:
        # 测试默认摄像头(设备ID 0)
        test_camera(0)