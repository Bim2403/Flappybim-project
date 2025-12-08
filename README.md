🐦 FLAPPY BIM
Flappy Bim là một tựa game giải trí được lấy cảm hứng từ Flappy Bird huyền thoại, được phát triển bằng ngôn ngữ Python và thư viện Pygame. Game đưa người chơi điều khiển chú chim "Bim" bay lượn qua những chướng ngại vật tại bối cảnh Hồ Gươm (Hà Nội).

👥 Tác giả
Dự án được thực hiện bởi:

Hiền Anh

Nam Khánh

🎮 Tính năng nổi bật
3 Chế độ khó (Difficulty Levels): Người chơi có thể tùy chỉnh độ khó ngay tại Menu.

EASY: Khe hở rộng (200px), tốc độ chậm.

NORMAL: Tốc độ vừa phải, trọng lực chuẩn.

HARD: Khe hẹp (120px), tốc độ nhanh, trọng lực mạnh.

Chu kỳ Ngày/Đêm: Background thay đổi (Hồ Gươm Sáng/Tối) tự động sau mỗi 5 điểm ghi được, tăng sự thú vị cho thị giác.

Hệ thống điểm số: Ghi nhận điểm hiện tại và lưu điểm cao nhất (High Score) trong phiên chơi.

Cơ chế Fallback an toàn: Nếu thiếu file hình ảnh, game tự động tạo các khối hình màu thay thế (hình vuông đỏ) để không bị lỗi crash.

🛠️ Cài đặt và Chạy game
1. Yêu cầu hệ thống
Python 3.x đã được cài đặt trên máy tính.

Thư viện pygame.

2. Cài đặt thư viện
Mở terminal (Command Prompt hoặc PowerShell) và chạy lệnh sau để cài đặt Pygame:

Bash

pip install pygame
3. Chuẩn bị tài nguyên (Assets)
Để game hiển thị đẹp nhất, hãy đảm bảo các file ảnh sau nằm cùng thư mục với file code flappybim.py:

bim.png (hoặc bim.jpg): Ảnh nhân vật chú chim Bim.

hoguomsang.jpg: Ảnh nền Hồ Gươm ban ngày.

hoguomtoi.jpeg: Ảnh nền Hồ Gươm ban đêm.

(Lưu ý: Nếu bạn chưa có ảnh, code đã được lập trình để tự vẽ các khối màu thay thế, game vẫn chơi được bình thường).

4. Chạy game
Tại thư mục chứa game, chạy lệnh:

Bash

python flappybim.py
🕹️ Hướng dẫn chơi
SPACE (Phím cách): Giúp Bim vỗ cánh bay lên.

Chuột trái: Sử dụng để nhấn các nút trên Menu (Start, Difficulty, Retry, Quit).

Mục tiêu: Khéo léo điều khiển Bim bay qua khe hở giữa các cặp ống nước xanh.

Game Over: Trò chơi kết thúc nếu Bim chạm vào ống nước, chạm đất hoặc bay đụng trần.

📂 Cấu trúc dự án
Plaintext

FlappyBim/
├── flappybim.py      # Source code chính của trò chơi
├── bim.png           # Hình ảnh nhân vật (ưu tiên png, fallback sang jpg)
├── hoguomsang.jpg    # Hình nền ban ngày
├── hoguomtoi.jpeg    # Hình nền ban đêm
└── README.md         # File hướng dẫn sử dụng
Chúc bạn chơi game vui vẻ! 🚀
