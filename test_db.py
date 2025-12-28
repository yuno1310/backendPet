from sqlalchemy import text
from database import engine

def test_connection_and_db():
    try:
        # Kết nối tới DB
        with engine.connect() as conn:
            print("✅ 1. Kết nối tới SQL Server thành công!")

            # Kiểm tra xem đang đứng ở database nào
            result_db_name = conn.execute(text("SELECT DB_NAME()")).scalar()
            print(f"✅ 2. Đang kết nối vào database: {result_db_name}")

            if result_db_name == "PETCARE_DB":
                # Thử truy vấn đếm số lượng bản ghi trong bảng ServiceType
                # (Bảng này rỗng nhưng truy vấn phải chạy được không báo lỗi)
                result_count = conn.execute(text("SELECT COUNT(*) FROM Booking")).scalar()
                print(f"✅ 3. Truy vấn bảng 'Booking' thành công. Hiện có {result_count} bản ghi.")
            else:
                print("❌ Cảnh báo: Bạn đang không kết nối vào PETCARE_DB")

    except Exception as e:
        print("\n❌ LỖI KẾT NỐI:")
        print(e)
        print("-" * 30)
        if "Cannot open database" in str(e):
            print("💡 Gợi ý: Có vẻ bạn chưa chạy file SQL để tạo database PetCareX_DB trong SSMS.")

if __name__ == "__main__":
    test_connection_and_db()