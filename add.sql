USE PETCARE_DB;
GO

-- =============================================
-- 1. DATA NỀN TẢNG (Chi nhánh, Dịch vụ, Sản phẩm)
-- =============================================

-- 1.1 Chi nhánh (Branch)
INSERT INTO Branch (Name, Address, Phone, OpenTime, CloseTime)
VALUES 
(N'PetCare Quận 1', N'123 Nguyễn Huệ, Q1, HCM', '0901111222', '08:00', '20:00'),
(N'PetCare Thủ Đức', N'456 Võ Văn Ngân, TĐ, HCM', '0903333444', '07:30', '21:00');

-- 1.2 Loại Dịch vụ (ServiceType)
INSERT INTO ServiceType (TypeName) VALUES (N'Khám Chữa Bệnh'), (N'Spa & Grooming'), (N'Tiêm Chủng');

-- 1.3 Dịch vụ (Service)
-- Giả sử TypeID: 1=Khám, 2=Spa, 3=Tiêm
INSERT INTO Service (TypeID, Name, Price)
VALUES 
(1, N'Khám Tổng Quát', 150000),
(1, N'Siêu Âm Ổ Bụng', 300000),
(2, N'Cắt Tỉa Lông Chó < 5kg', 250000),
(3, N'Tiêm Vaccine Dại', 100000);

-- Map Dịch vụ vào Chi nhánh (Branch_Service)
-- Chi nhánh 1 có tất cả dịch vụ
INSERT INTO Branch_Service (BranchID, ServiceID, IsAvailable, EffectiveDate)
SELECT 1, ServiceID, 1, '2023-01-01' FROM Service;

-- 1.4 Sản phẩm (Product) & Vaccine
-- Lưu ý: Vaccine là subtype của Product, phải insert Product trước

-- Sản phẩm thường (Food)
INSERT INTO Product (ProductName, RetailPrice, ProductType) 
VALUES (N'Royal Canin Puppy', 180000, 'Food');

-- Sản phẩm thuốc (Drug)
INSERT INTO Product (ProductName, RetailPrice, ProductType) 
VALUES (N'Amoxicillin 50mg', 20000, 'Drug');

-- Sản phẩm Vaccine (Insert vào Product -> Lấy ID -> Insert vào Vaccine)
INSERT INTO Product (ProductName, RetailPrice, ProductType) 
VALUES (N'Vaccine 7 Bệnh (Zoetis)', 500000, 'Vaccine');

DECLARE @VacProdID INT = SCOPE_IDENTITY(); -- Lấy ID vừa tạo
INSERT INTO Vaccine (VaccineID, VaccineName, VaccineType, Manufacturer, ManufactureDate, ExpiryDate)
VALUES (@VacProdID, N'Vanguard Plus 5/L', N'Nhược độc', N'Zoetis', '2023-01-01', '2025-12-31');

-- Kho hàng (Inventory)
INSERT INTO Inventory (BranchID, ProductID, Quantity)
VALUES (1, 1, 50), (1, 2, 100), (1, @VacProdID, 20);

-- =============================================
-- 2. NHÂN SỰ (Employee)
-- =============================================
-- Branch 1
INSERT INTO Employee (BranchID, Name, DateOfBirth, StartDate, Gender, Salary, Position)
VALUES 
(1, N'Nguyễn Văn An', '1985-05-10', '2020-01-01', N'Nam', 20000000, 'Vet'), -- Bác sĩ
(1, N'Trần Thị Bích', '1995-08-20', '2021-06-15', N'Nữ', 8000000, 'Receptionist'), -- Lễ tân
(1, N'Lê Hoàng Cường', '1990-12-01', '2019-03-01', N'Nam', 25000000, 'Manager'); -- Quản lý

-- =============================================
-- 3. KHÁCH HÀNG & THÚ CƯNG
-- =============================================
INSERT INTO Customer (Name, PhoneNumber, Email, CitizenID, Gender, DateOfBirth, MembershipTier)
VALUES 
(N'Phạm Minh Duy', '0912345678', 'duy@email.com', '079123456789', N'Nam', '1998-01-01', 'VIP'),
(N'Hoàng Thị Hoa', '0987654321', 'hoa@email.com', '079987654321', N'Nữ', '2000-05-05', 'Basic');

-- Thú cưng
INSERT INTO Pet (CustomerID, PetName, Species, Breed, DateOfBirth, Gender, HealthStatus)
VALUES 
(1, N'Milu', N'Chó', N'Poodle', '2022-02-01', N'Đực', N'Bình thường'),
(2, N'Mimi', N'Mèo', N'Anh Lông Ngắn', '2023-06-10', N'Cái', N'Đã triệt sản');

-- =============================================
-- 4. FLOW TEST: ĐẶT LỊCH -> KHÁM -> THANH TOÁN
-- =============================================

-- 4.1 Tạo Booking (Khách hẹn trước)
INSERT INTO Booking (CustomerID, BranchID, ReceptionistID, BookingTime, CustomerName, Species, PhoneNumber, Status, Note)
VALUES 
(1, 1, 2, GETDATE(), N'Phạm Minh Duy', N'Chó', '0912345678', 'Confirmed', N'Khám da liễu');

DECLARE @BookingID INT = SCOPE_IDENTITY();

-- Chi tiết Booking (Book dịch vụ Khám tổng quát)
INSERT INTO BookingDetails (BookingID, ServiceID, PetID, Status)
VALUES (@BookingID, 1, 1, 'Pending');

-- 4.2 Khách đến nơi -> Tạo Visit (Check-in)
INSERT INTO Visit (BookingID, BranchID, CustomerID, ReceptionistID, TimeIn)
VALUES (@BookingID, 1, 1, 2, GETDATE());

DECLARE @VisitID INT = SCOPE_IDENTITY();

-- 4.3 Tạo Service Order (Chỉ định dịch vụ thực tế)
-- Giả sử bác sĩ chỉ định thêm Siêu âm (ServiceID = 2) ngoài việc khám
INSERT INTO ServiceOrder (VisitID, ServiceID, PetID, ServiceName, Price, Status, Note)
VALUES 
(@VisitID, 1, 1, N'Khám Tổng Quát', 150000, 'Completed', N'Đã khám xong'),
(@VisitID, 2, 1, N'Siêu Âm Ổ Bụng', 300000, 'Completed', N'Phát hiện dị vật');

-- Lấy OrderID của ca khám để tạo bệnh án
DECLARE @OrderExamID INT = (SELECT TOP 1 OrderID FROM ServiceOrder WHERE VisitID = @VisitID AND ServiceID = 1);

-- 4.4 Bác sĩ ghi bệnh án (Medical Record)
-- Insert Supertype trước
INSERT INTO ServiceRecord (ServiceRecordID, CreatedDate) VALUES (@OrderExamID, GETDATE());

-- Insert Subtype (MedicalRecord) - Bác sĩ ID = 1
INSERT INTO MedicalRecord (MedicalID, VetID, PetID, Symptoms, Diagnosis, ReExamDate, Notes)
VALUES 
(@OrderExamID, 1, 1, N'Ngứa nhiều vùng lưng', N'Viêm da dị ứng', DATEADD(DAY, 7, GETDATE()), N'Cần kiêng ăn gà');


-- 4.5 Kê đơn thuốc (Prescription)
INSERT INTO Prescription (MedicalID, Note) VALUES (@OrderExamID, N'Uống thuốc sau ăn');
DECLARE @PrescriptionID INT = SCOPE_IDENTITY();

-- Kê thuốc Amoxicillin (DrugID = 2)
INSERT INTO PrescriptionDetail (PrescriptionID, DrugID, Dosage, Quantity, UsageInstruction)
VALUES (@PrescriptionID, 2, N'1 viên/lần', 10, N'Sáng 1 viên, Tối 1 viên');

-- 4.6 Thanh toán (Invoice)
-- Tính tổng tiền = 150k (Khám) + 300k (Siêu âm) = 450k
INSERT INTO Invoice (VisitID, CustomerID, ReceptionistID, SubTotal, DiscountAmount, TotalAmount, PaymentMethod, CreateDate)
VALUES 
(@VisitID, 1, 2, 450000, 0, 450000, N'Chuyển khoản', GETDATE());

-- =============================================
-- 5. TEST DATA GÓI VẮC XIN (Package)
-- =============================================
INSERT INTO VaccinePackage (Name, Description, Duration, TotalShots, Price)
VALUES (N'Gói Tiêm Chủng Chó Con (Cơ bản)', N'Bao gồm 3 mũi 7 bệnh', 3, 3, 1200000);

-- Đăng ký gói cho Mèo Mimi (PetID=2)
INSERT INTO PackageSubscription (PetID, PackageID, StartDate, RemainingShots)
VALUES (2, 1, GETDATE(), 3);
GO

SELECT p.PetName, m.Diagnosis, m.Symptoms, e.Name as VetName
FROM MedicalRecord m
JOIN Pet p ON m.PetID = p.PetID
JOIN Employee e ON m.VetID = e.EmployeeID
WHERE p.PetName = N'Milu';

SELECT * FROM Invoice 
WHERE CreateDate >= '2025-01-01'; -- Kiểm tra xem có nằm đúng partition năm nay không

SELECT * FROM MedicalRecord

USE PETCARE_DB;
GO

-- ============================================================
-- BƯỚC 1: CHUẨN BỊ DỮ LIỆU (Thêm thú cưng mới để đa dạng bệnh án)
-- ============================================================
-- Thêm 2 khách hàng và thú cưng mới để có dữ liệu phong phú hơn
INSERT INTO Customer (Name, PhoneNumber, Email, CitizenID, Gender, DateOfBirth)
VALUES 
(N'Lê Thị Cúc', '0998887776', 'cuc@email.com', '079888777666', N'Nữ', '1995-12-12'),
(N'Trần Văn Dũng', '0911223344', 'dung@email.com', '079112233445', N'Nam', '1990-03-03');

INSERT INTO Pet (CustomerID, PetName, Species, Breed, DateOfBirth, Gender, HealthStatus)
VALUES 
((SELECT CustomerID FROM Customer WHERE PhoneNumber='0998887776'), N'Lu', N'Mèo', N'Ba Tư', '2021-01-01', N'Cái', N'Yếu'),
((SELECT CustomerID FROM Customer WHERE PhoneNumber='0911223344'), N'Lucky', N'Chó', N'Golden', '2020-05-05', N'Đực', N'Khỏe');

-- ============================================================
-- BƯỚC 2: INSERT 10 MEDICAL RECORDS (KÈM VISIT & ORDER)
-- ============================================================
-- Lưu ý: Giả sử VetID = 1 (Bs. An), ServiceID = 1 (Khám tổng quát)
-- Chúng ta dùng biến bảng để xử lý insert hàng loạt cho gọn

DECLARE @MedData TABLE (
    RowID INT IDENTITY(1,1),
    PetName NVARCHAR(50),
    Symptoms NVARCHAR(MAX),
    Diagnosis NVARCHAR(MAX),
    TreatmentNote NVARCHAR(MAX),
    ReExamDays INT
);

INSERT INTO @MedData (PetName, Symptoms, Diagnosis, TreatmentNote, ReExamDays) VALUES
(N'Milu', N'Nôn mửa, bỏ ăn 2 ngày', N'Viêm dạ dày cấp', N'Truyền dịch, nhịn ăn 24h', 3),
(N'Mimi', N'Gãi tai liên tục, có vảy đen', N'Viêm tai do rận', N'Vệ sinh tai, nhỏ thuốc trị rận', 7),
(N'Lu', N'Mắt đỏ, chảy ghèn xanh', N'Viêm kết mạc', N'Nhỏ mắt kháng sinh', 5),
(N'Lucky', N'Đi khập khiễng chân sau phải', N'Giãn dây chằng nhẹ', N'Hạn chế vận động, uống giảm đau', 14),
(N'Milu', N'Ho khạc như hóc xương', N'Viêm phế quản', N'Uống kháng sinh và long đờm', 7),
(N'Mimi', N'Đi tiểu ra máu, rên rỉ', N'Viêm bàng quang', N'Cần siêu âm thêm, uống kháng viêm', 3),
(N'Lu', N'Rụng lông mảng tròn, da đỏ', N'Nấm da (Ringworm)', N'Bôi thuốc nấm, tắm lá chè', 10),
(N'Lucky', N'Sốt cao 40 độ, mệt mỏi', N'Sốt virus (nghi ngờ)', N'Hạ sốt, theo dõi tại nhà', 2),
(N'Milu', N'Hôi miệng, nướu sưng đỏ', N'Viêm nướu / Cao răng', N'Lấy cao răng, bôi gel nha khoa', 30),
(N'Mimi', N'Bụng to bất thường, ăn nhiều', N'Mang thai tuần thứ 4', N'Bổ sung canxi và dinh dưỡng thai kỳ', 14);

-- BIẾN HỖ TRỢ LOOP
DECLARE @i INT = 1;
DECLARE @Total INT = (SELECT COUNT(*) FROM @MedData);
DECLARE @CurrentPetID INT;
DECLARE @CurrentVisitID INT;
DECLARE @CurrentOrderID INT;
DECLARE @RecID INT = (SELECT ISNULL(MAX(EmployeeID), 0) FROM Employee WHERE Position = 'Receptionist'); -- Lấy đại 1 lễ tân
DECLARE @VetID INT = (SELECT TOP 1 EmployeeID FROM Employee WHERE Position = 'Vet'); -- Lấy đại 1 bác sĩ

WHILE @i <= @Total
BEGIN
    -- 1. Lấy thông tin từ bảng tạm
    DECLARE @PName NVARCHAR(50), @Sym NVARCHAR(MAX), @Dia NVARCHAR(MAX), @Note NVARCHAR(MAX), @ReDate INT;
    SELECT @PName = PetName, @Sym = Symptoms, @Dia = Diagnosis, @Note = TreatmentNote, @ReDate = ReExamDays
    FROM @MedData WHERE RowID = @i;

    SELECT TOP 1 @CurrentPetID = PetID FROM Pet WHERE PetName = @PName;

    -- 2. Tạo Visit (Giả lập khách đến hôm nay hoặc vài ngày trước)
    INSERT INTO Visit (BranchID, CustomerID, ReceptionistID, TimeIn)
    SELECT TOP 1 1, CustomerID, @RecID, DATEADD(DAY, -@i, GETDATE()) -- Ngày lùi dần để data trông tự nhiên
    FROM Pet WHERE PetID = @CurrentPetID;
    
    SET @CurrentVisitID = SCOPE_IDENTITY();

    -- 3. Tạo ServiceOrder (Order dịch vụ Khám - ServiceID=1)
    INSERT INTO ServiceOrder (VisitID, ServiceID, PetID, ServiceName, Price, Status)
    VALUES (@CurrentVisitID, 1, @CurrentPetID, N'Khám Tổng Quát', 150000, 'Completed');
    
    SET @CurrentOrderID = SCOPE_IDENTITY();

    -- 4. Tạo ServiceRecord (Supertype)
    INSERT INTO ServiceRecord (ServiceRecordID, CreatedDate)
    VALUES (@CurrentOrderID, DATEADD(DAY, -@i, GETDATE()));

    -- 5. Tạo MedicalRecord (Subtype - Đích đến cuối cùng)
    INSERT INTO MedicalRecord (MedicalID, VetID, PetID, Symptoms, Diagnosis, ReExamDate, Notes)
    VALUES (
        @CurrentOrderID, 
        @VetID, 
        @CurrentPetID, 
        @Sym, 
        @Dia, 
        DATEADD(DAY, @ReDate, GETDATE()), -- Ngày tái khám = hôm nay + số ngày hẹn
        @Note
    );

    SET @i = @i + 1;
END;
GO

-- ============================================================
-- KIỂM TRA KẾT QUẢ
-- ============================================================
SELECT 
    mr.MedicalID,
    p.PetName,
    e.Name AS VetName,
    mr.Diagnosis,
    mr.Symptoms,
    mr.Notes AS Treatment,
    mr.ReExamDate
FROM MedicalRecord mr
JOIN Pet p ON mr.PetID = p.PetID
JOIN Employee e ON mr.VetID = e.EmployeeID
ORDER BY mr.MedicalID DESC;

----------------------------------------------------------------------------------------------------------------------------

USE PETCARE_DB;
GO

-- ============================================================
-- TỰ ĐỘNG SINH DỮ LIỆU HÓA ĐƠN & DOANH THU (2023-2025)
-- ============================================================
SET NOCOUNT ON;

DECLARE @i INT = 1;
DECLARE @TotalRows INT = 500; -- Số lượng hóa đơn muốn tạo thêm

-- Các biến tạm
DECLARE @RandBranchID INT;
DECLARE @RandCustomerID INT;
DECLARE @RandRecID INT;
DECLARE @RandYear INT;
DECLARE @RandMonth INT;
DECLARE @RandDay INT;
DECLARE @RandDate DATETIME;
DECLARE @RandAmount DECIMAL(18,0);
DECLARE @NewVisitID INT;

-- Lấy ID nhân viên lễ tân (để gán vào hóa đơn)
SELECT TOP 1 @RandRecID = EmployeeID FROM Employee WHERE Position = 'Receptionist';

WHILE @i <= @TotalRows
BEGIN
    -- 1. Random Chi nhánh (1 hoặc 2)
    SET @RandBranchID = (ABS(CHECKSUM(NEWID())) % 2) + 1;

    -- 2. Random Khách hàng (Lấy ngẫu nhiên từ bảng Customer)
    SELECT TOP 1 @RandCustomerID = CustomerID FROM Customer ORDER BY NEWID();

    -- 3. Random Năm (2023, 2024, 2025) - Tương ứng với Partition
    -- Logic: 0 -> 2023, 1 -> 2024, 2 -> 2025
    SET @RandYear = 2023 + (ABS(CHECKSUM(NEWID())) % 3);

    -- 4. Random Ngày tháng
    SET @RandMonth = (ABS(CHECKSUM(NEWID())) % 12) + 1;
    SET @RandDay = (ABS(CHECKSUM(NEWID())) % 28) + 1; -- Lấy max 28 để tránh lỗi tháng 2
    SET @RandDate = DATEFROMPARTS(@RandYear, @RandMonth, @RandDay);

    -- 5. Random Tiền (Từ 100k đến 5 triệu)
    SET @RandAmount = (ABS(CHECKSUM(NEWID())) % 50 + 1) * 100000;

    -- BƯỚC A: Tạo Visit trước (Do Invoice tham chiếu Visit)
    INSERT INTO Visit (BranchID, CustomerID, ReceptionistID, TimeIn, IsPaid)
    VALUES (@RandBranchID, @RandCustomerID, @RandRecID, @RandDate, 1);
    
    SET @NewVisitID = SCOPE_IDENTITY();

    -- BƯỚC B: Tạo Invoice
    INSERT INTO Invoice (VisitID, CreateDate, CustomerID, ReceptionistID, SubTotal, DiscountAmount, TotalAmount, PaymentMethod)
    VALUES (
        @NewVisitID, 
        @RandDate, -- Quan trọng: Ngày này quyết định Partition và Report
        @RandCustomerID, 
        @RandRecID, 
        @RandAmount, 
        0, 
        @RandAmount, 
        N'Tiền mặt'
    );

    SET @i = @i + 1;
END;

PRINT N'Đã thêm xong 500 hóa đơn mẫu vào hệ thống!';
GO

EXEC dbo.SP_Report_AnnualRevenue @TargetYear = 2023;
EXEC dbo.SP_Report_AnnualRevenue @TargetYear = 2024;
EXEC dbo.SP_Report_AnnualRevenue @TargetYear = 2024;
SELECT 
    b.Name, 
    YEAR(i.CreateDate) as [Year], 
    SUM(i.TotalAmount) as TotalRevenue,
    COUNT(i.InvoiceID) as TotalInvoices
FROM Invoice i
JOIN Branch b ON i.BranchID = b.BranchID
GROUP BY b.Name, YEAR(i.CreateDate)
ORDER BY [Year], b.Name;

-------------------------------------------------------------
USE PETCARE_DB;
GO

-- ============================================================
-- TẠO DỮ LIỆU TEST CHURN CUSTOMERS (KHÁCH HÀNG RỜI BỎ)
-- ============================================================
SET NOCOUNT ON;

-- 1. Lấy thông tin phụ trợ (Chi nhánh, Lễ tân) để tạo Visit hợp lệ
DECLARE @BranchID INT = (SELECT TOP 1 BranchID FROM Branch);
DECLARE @RecID INT = (SELECT TOP 1 EmployeeID FROM Employee WHERE Position = 'Receptionist');

-- Biến tạm để lưu ID khách hàng vừa tạo
DECLARE @CusID INT;

-- ------------------------------------------------------------
-- CASE 1: KHÁCH HÀNG "CHURN" THỰC SỰ (Sẽ hiện trong báo cáo)
-- ------------------------------------------------------------

-- [Khách A] Chỉ đến 1 lần duy nhất cách đây 8 tháng -> Cần chăm sóc lại
INSERT INTO Customer (Name, PhoneNumber, Email, CitizenID, Gender, DateOfBirth, MembershipTier)
VALUES (N'Nguyễn Văn Cũ', '0901000001', 'cu1@mail.com', '001099000001', N'Nam', '1990-01-01', 'Basic');
SET @CusID = SCOPE_IDENTITY();

INSERT INTO Visit (BranchID, CustomerID, ReceptionistID, TimeIn)
VALUES (@BranchID, @CusID, @RecID, DATEADD(MONTH, -8, GETDATE())); -- Lần cuối: 8 tháng trước


-- [Khách B] Khách VIP nhưng đã 1 năm không quay lại -> Cần báo động đỏ
INSERT INTO Customer (Name, PhoneNumber, Email, CitizenID, Gender, DateOfBirth, MembershipTier)
VALUES (N'Trần Thị Lãng Quên', '0901000002', 'quen@mail.com', '001099000002', N'Nữ', '1985-05-05', 'VIP');
SET @CusID = SCOPE_IDENTITY();

INSERT INTO Visit (BranchID, CustomerID, ReceptionistID, TimeIn)
VALUES (@BranchID, @CusID, @RecID, DATEADD(YEAR, -1, GETDATE())); -- Lần cuối: 1 năm trước


-- ------------------------------------------------------------
-- CASE 2: KHÁCH HÀNG "TRUNG THÀNH" (KHÔNG được hiện trong báo cáo)
-- Mục đích: Test xem logic lấy "TOP 1 ... ORDER BY DESC" có đúng không
-- ------------------------------------------------------------

-- [Khách C] Từng đến cách đây 2 năm, NHƯNG tháng trước mới quay lại -> Vẫn là khách Active
INSERT INTO Customer (Name, PhoneNumber, Email, CitizenID, Gender, DateOfBirth, MembershipTier)
VALUES (N'Lê Tái Ngộ', '0901000003', 'taingo@mail.com', '001099000003', N'Nam', '1992-02-02', 'Loyal');
SET @CusID = SCOPE_IDENTITY();

-- Visit cũ (2 năm trước)
INSERT INTO Visit (BranchID, CustomerID, ReceptionistID, TimeIn)
VALUES (@BranchID, @CusID, @RecID, DATEADD(YEAR, -2, GETDATE()));

-- Visit mới (1 tháng trước) -> Đây là mốc quyết định
INSERT INTO Visit (BranchID, CustomerID, ReceptionistID, TimeIn)
VALUES (@BranchID, @CusID, @RecID, DATEADD(MONTH, -1, GETDATE()));


-- ------------------------------------------------------------
-- CASE 3: KHÁCH HÀNG MỚI (KHÔNG được hiện trong báo cáo)
-- ------------------------------------------------------------

-- [Khách D] Mới đến hôm qua
INSERT INTO Customer (Name, PhoneNumber, Email, CitizenID, Gender, DateOfBirth, MembershipTier)
VALUES (N'Phạm Mới Tanh', '0901000004', 'moi@mail.com', '001099000004', N'Nữ', '2000-10-10', 'Basic');
SET @CusID = SCOPE_IDENTITY();

INSERT INTO Visit (BranchID, CustomerID, ReceptionistID, TimeIn)
VALUES (@BranchID, @CusID, @RecID, DATEADD(DAY, -1, GETDATE()));

PRINT N'Đã thêm dữ liệu test Churn thành công!';
GO

------------------------------------------------------------------------
USE PETCARE_DB;
GO

-- ============================================================
-- DATA TEST CHO SP_Inventory_GetLowStock
-- ============================================================

-- 1. Tạo thêm một số sản phẩm mới để test cho rõ ràng
INSERT INTO Product (ProductName, RetailPrice, ProductType) VALUES 
(N'Vitamin Gel Nutri-Plus', 150000, 'Drug'),      -- Sẽ set tồn kho THẤP
(N'Cát Vệ Sinh Mèo 5L', 80000, 'Accessory'),      -- Sẽ set HẾT HÀNG (0)
(N'Bánh Thưởng Pedigree', 30000, 'Food'),         -- Sẽ set tồn kho CAO
(N'Vòng Cổ Chống Rận', 120000, 'Accessory');      -- Sẽ set tồn kho BIÊN (10)

-- Lấy ID của các sản phẩm vừa tạo
DECLARE @P_Low INT = (SELECT Top 1 ProductID FROM Product WHERE ProductName = N'Vitamin Gel Nutri-Plus');
DECLARE @P_Zero INT = (SELECT Top 1 ProductID FROM Product WHERE ProductName = N'Cát Vệ Sinh Mèo 5L');
DECLARE @P_High INT = (SELECT Top 1 ProductID FROM Product WHERE ProductName = N'Bánh Thưởng Pedigree');
DECLARE @P_Border INT = (SELECT Top 1 ProductID FROM Product WHERE ProductName = N'Vòng Cổ Chống Rận');

-- 2. Thiết lập Tồn kho cho Chi nhánh 1 (Chi nhánh mục tiêu test)
-- CASE 1: Tồn kho thấp (<10) -> KỲ VỌNG: HIỆN
INSERT INTO Inventory (BranchID, ProductID, Quantity) VALUES (1, @P_Low, 3);

-- CASE 2: Hết hàng (=0) -> KỲ VỌNG: HIỆN
INSERT INTO Inventory (BranchID, ProductID, Quantity) VALUES (1, @P_Zero, 0);

-- CASE 3: Tồn kho cao (>10) -> KỲ VỌNG: ẨN
INSERT INTO Inventory (BranchID, ProductID, Quantity) VALUES (1, @P_High, 50);

-- CASE 4: Ngay tại biên (=10) -> KỲ VỌNG: ẨN (Vì điều kiện là < 10)
INSERT INTO Inventory (BranchID, ProductID, Quantity) VALUES (1, @P_Border, 10);

-- 3. Thiết lập Tồn kho cho Chi nhánh 2 (Để test việc lọc chi nhánh)
-- Sản phẩm này ở Chi nhánh 2 chỉ còn 1 cái (Rất thấp), nhưng khi chạy SP cho Chi nhánh 1 thì KHÔNG được hiện.
INSERT INTO Inventory (BranchID, ProductID, Quantity) VALUES (2, @P_Low, 1); 

GO