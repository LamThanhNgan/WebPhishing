# Quy trình coding

## Nhánh chính: **Main**
Chứa các đoạn code mới nhất và hoạt động ổn định. 
-> Tránh đụng vào bằng cách push thẳng commit lên trên nhánh (Cần setup protect branch để đảm bảo)

**Lưu ý** Luôn tạo nhánh mới từ Main để thực hiện coding

## Các nhánh dùng để dev

```shell
# Tạo nhánh mới từ main (giả sử tên nhánh là: feature/letonnhan/ui)
git checkout -b feature/letonnhan/ui
```

### Trong quá trình code

Thực hiện commit code bằng cách 

```shell
git add . # đưa toàn bộ file đang ở folder hiện tại (os.pwd()) vào trong stages changed
git commit -m "Example commands" # thêm command để nhận biết
```

Sau khi đã hoàn tất các chức năng cần thiết trong nhánh. Thực hiện lệnh `git push` để đưa code lên remote (github repository) tương ứng với tên nhánh đang thực hiện `feature/letonnhan/ui`

```shell
git push -u origin feature/letonnhan/ui
```

### Thực hiện tạo PR trên Github console

Step 1: Mở github trên trình duyệt web.

Step 2: Truy cập repository https://github.com/Le-Ton-Nhan/WebPhishing

Step 3: Bấm vào tab Pull requests

Step 4: Bấm nút `New Pull Request`

Step 5: Chọn `base:main` và `compare:feature/lamthanhngan/pedia` để thực hiện tạo merge request từ `compare` vào `base`

Step 6: Bấm nút `Create pull request`

Step 7: Điền thông tin của PR và bấm `Create pull request`

Step 7.1(Optional): Kiểm tra lại các file đã thay đổi ở tab `Files changed` để đảm bảo không bị sót file hoặc miss commit

Step 8: Hoàn tất merge request bằng cách bấm `Merge pull request`






