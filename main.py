from datetime import date
from typing import List, Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
import json 
from datetime import datetime
from pathlib import Path
from database import SessionDep
from sqlalchemy import text

OUTPUT_DIR = Path("E:\\Web_For_CSDLNC\\backendPet\\result")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()

origins = [
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

### Scenario 1 ###
@app.get("/scenario1/customer_check")
def customer_check(phone_number: str, session: SessionDep):
    result = session.execute(
        text("EXEC sp_customer_check :phone"), {"phone": phone_number}
    ).fetchone()

    if not result.CustomerID:
        return {"exists": False}

    return {"exists": True, "customer": dict(result._mapping)}


@app.post("/scenario1/create_manual")
def create_manual(
    branch_id: int,
    receptionist_id: int,
    customer_name: str,
    phone_number: str,
    note: str,
    session: SessionDep,
):
    result = session.execute(
        text("""
        DECLARE @BookingID INT;

        EXEC dbo.SP_Booking_CreateManual
            @BranchID = :branchid,
            @ReceptionistID = :receptionistid,
            @CustomerName = :customername,
            @PhoneNumber = :phonenumber,
            @Note = :note;

        SELECT @BookingID AS booking_id;
        """),
        {
            "branchid": branch_id,
            "receptionistid": receptionist_id,
            "customername": customer_name,
            "phonenumber": phone_number,
            "note": note,
        },
    ).fetchone()
    session.commit()
    return {"booking_id": result[0]}


@app.post("/scenario1/create_detailed")
def create_detailed(
    customer_id: int,
    branch_id: int,
    receptionist_id: int,
    details: list[dict],
    note: str,
    session: SessionDep,
):
    conn = session.connection().connection  #
    cursor = conn.cursor()

    tvp_rows = [(d["service_id"], d["petid"], d["note"]) for d in details]

    booking_id = cursor.execute("SELECT 0").fetchone()[0]
    try:
        row = cursor.execute(
            """
            DECLARE @BookingID INT;

            EXEC dbo.SP_Booking_CreateDetailed
                @CustomerID = ?,
                @BranchID = ?,
                @ReceptionistID = ?,
                @Details = ?,
                @Note = ?,
                @BookingID = @BookingID OUTPUT;

            SELECT @BookingID AS booking_id;
            """,
            customer_id,
            branch_id,
            receptionist_id,
            tvp_rows,
            note,
        ).fetchone()

        if not row or row[0] is None:
            raise HTTPException(status_code=400, detail="Booking creation failed")

        return {"booking_id": row[0]}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario1/pet_add")
def add_pet(
    customer_id: int,
    pet_name: str,
    species: str,
    breed: str,
    date_of_birth: str,  # YYYY-MM-DD
    gender: str,
    health_status: str,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            DECLARE @RC INT;

            EXECUTE @RC = dbo.sp_Pet_Add
                @CustomerID = :customer_id,
                @PetName = :pet_name,
                @Species = :species,
                @Breed = :breed,
                @DateOfBirth = :date_of_birth,
                @Gender = :gender,
                @HealthStatus = :health_status;

            SELECT @RC AS return_code;
            """),
            {
                "customer_id": customer_id,
                "pet_name": pet_name,
                "species": species,
                "breed": breed,
                "date_of_birth": date_of_birth,
                "gender": gender,
                "health_status": health_status,
            },
        ).fetchone()

        session.commit()

        if result is None:
            raise HTTPException(500, "No result returned from stored procedure")

        return {"PetID": result[0]}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

### Scenario 2 ###
@app.post("/scenario2/booking_find")
def booking_find(
    phone_number: str,
    branch_id: int,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            DECLARE @RC INT;

            EXECUTE @RC = dbo.sp_Booking_Find
                @PhoneNumber = :phone_number,
                @BranchID = :branch_id;

            SELECT @RC AS return_code;
            """),
            {
                "phone_number": phone_number,
                "branch_id": branch_id,
            },
        ).fetchone()

        if result is None:
            raise HTTPException(status_code=500, detail="No result returned")

        print(type(result))

        return {
            "return_code": {
                "bookingID": result[0],
                "branchID": result[1],
                "bookingTime": result[2],
                "status": result[3],
                "petid": result[4],
                "serviceID": result[5],
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario2/customer_register")
def customer_register(
    name: str,
    phone_number: str,
    email: str,
    citizen_id: str,
    gender: str,
    date_of_birth: date,
    membership_tier: str,
    pet_name: List[str],
    species: List[str],
    breed: List[str],
    pet_dob: List[date],
    pet_gender: List[str],
    health_status: List[str],
    session: SessionDep,
):
    try:
        if not (
            len(pet_name)
            == len(species)
            == len(breed)
            == len(pet_dob)
            == len(pet_gender)
            == len(health_status)
        ):
            raise HTTPException(400, "Pet lists length mismatch")

        sql = """
        SET NOCOUNT ON;
        DECLARE @RC INT;
        DECLARE @Pets dbo.PetList;
        """

        for i in range(len(pet_name)):
            sql += f"""
            INSERT INTO @Pets (
                PetName, Species, Breed, DateOfBirth, Gender, HealthStatus
            ) VALUES (
                :pet_name_{i},
                :species_{i},
                :breed_{i},
                :pet_dob_{i},
                :pet_gender_{i},
                :health_status_{i}
            );
            """

        sql += """
        EXEC @RC = dbo.sp_Customer_RegisterNew
            @Name = :name,
            @PhoneNumber = :phone_number,
            @Email = :email,
            @CitizenID = :citizen_id,
            @Gender = :gender,
            @DateOfBirth = :date_of_birth,
            @MembershipTier = :membership_tier,
            @Pets = @Pets;

        SELECT @RC AS return_code;
        """

        params = {
            "name": name,
            "phone_number": phone_number,
            "email": email,
            "citizen_id": citizen_id,
            "gender": gender,
            "date_of_birth": date_of_birth,
            "membership_tier": membership_tier,
        }
        for i in range(len(pet_name)):
            params.update(
                {
                    f"pet_name_{i}": pet_name[i],
                    f"species_{i}": species[i],
                    f"breed_{i}": breed[i],
                    f"pet_dob_{i}": pet_dob[i],
                    f"pet_gender_{i}": pet_gender[i],
                    f"health_status_{i}": health_status[i],
                }
            )

        result = session.execute(text(sql), params)
        result.fetchone()
        session.commit()
        success = True
        return {"return_code": success}

    except Exception as e:
        success = False
        print(e)
        return {"return_code": success}


@app.post("/scenario2/visit_auto_create")
def visit_auto_create(
    booking_id: int,
    receptionist_id: int,
    branch_id: int,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            DECLARE @RC INT;

            EXEC @RC = dbo.sp_Visit_AutoCreateFromBooking
                @BookingID = :booking_id,
                @ReceptionistID = :receptionist_id,
                @BranchID = :branch_id;

            SELECT @RC AS return_code;
            """),
            {
                "booking_id": booking_id,
                "receptionist_id": receptionist_id,
                "branch_id": branch_id,
            },
        ).fetchone()
        session.commit()
        if result is not None:
            return {"flag": True}
        else:
            return {"flag": False}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario2/visit_create")
def visit_create(
    customer_id: int,
    receptionist_id: int,
    branch_id: int,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            DECLARE @RC INT;

            EXEC @RC = dbo.sp_Visit_Create
                @CustomerID = :customer_id,
                @ReceptionistID = :receptionist_id,
                @BranchID = :branch_id;

            SELECT @RC AS return_code;
            """),
            {
                "customer_id": customer_id,
                "receptionist_id": receptionist_id,
                "branch_id": branch_id,
            },
        ).fetchone()
        session.commit()
        return {"return_code": result[0] if result else None}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario2/service_order_add")
def service_order_add(
    visit_id: int,
    employee_id: int,
    service_id: List[int],
    pet_id: List[int],
    discount: List[float],
    note: List[str],
    session: SessionDep,
):
    try:
        order_count = len(service_id)

        if not all(len(lst) == order_count for lst in [pet_id, discount, note]):
            raise HTTPException(400, "Service order lists length mismatch")

        sql = """
        DECLARE @RC INT;
        DECLARE @Orders dbo.ServiceOrderList;
        """

        # populate dbo.ServiceOrderList
        for i in range(order_count):
            sql += f"""
            INSERT INTO @Orders (
                ServiceID,
                PetID,
                Discount,
                Note
            ) VALUES (
                :service_id_{i},
                :pet_id_{i},
                :discount_{i},
                :note_{i}
            );
            """

        sql += """
        EXEC @RC = dbo.sp_ServiceOrder_Add
            @VisitID = :visit_id,
            @EmployeeID = :employee_id,
            @Orders = @Orders;

        SELECT @RC AS return_code;
        """

        params = {
            "visit_id": visit_id,
            "employee_id": employee_id,
        }

        for i in range(order_count):
            params.update(
                {
                    f"service_id_{i}": service_id[i],
                    f"pet_id_{i}": pet_id[i],
                    f"discount_{i}": discount[i],
                    f"note_{i}": note[i],
                }
            )

        result = session.execute(text(sql), params)
        session.commit()  # Lưu dữ liệu vào database
        
        # Kiểm tra xem result có rows hay không
        try:
            row = result.fetchone()
            return {"return_code": row[0] if row else 1}
        except:
            # Nếu không có result set, return thành công
            return {"return_code": 1}

    except Exception as e:
        session.rollback()  # Rollback nếu có lỗi
        print(f"Error in service_order_add: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

### Scenario 3 ###
@app.post("/scenario3/service_order_pending")
def get_pending_service_orders(
    branch_id: int,
    session: SessionDep,    
):
    try:
        result = session.execute(
            text("""
            DECLARE @RC INT;

            EXEC @RC = dbo.SP_ServiceOrder_GetPending
                @BranchID = :branch_id;

            SELECT @RC AS return_code;
            """),
            {
                "branch_id": branch_id,
            },
        ).fetchone()

        return {"return_code": result.return_code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario3/medical_record_create")
def medical_record_create(
    order_id: int,
    vet_id: int,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            DECLARE @RC INT;

            EXEC @RC = dbo.SP_MedicalRecord_Create
                @OrderID = :order_id,
                @VetID = :vet_id;

            SELECT @RC AS return_code;
            """),
            {
                "order_id": order_id,
                "vet_id": vet_id,
            },
        ).fetchone()

        return {"return_code": result.return_code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario3/medical_record_update")
def medical_record_update(
    medical_id: int,
    symptoms: str,
    diagnosis: str,
    re_exam_date: date,
    notes: str,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            DECLARE @RC INT;

            EXEC @RC = dbo.SP_MedicalRecord_Update
                @MedicalID = :medical_id,
                @Symptoms = :symptoms,
                @Diagnosis = :diagnosis,
                @ReExamDate = :re_exam_date,
                @Notes = :notes;

            SELECT @RC AS return_code;
            """),
            {
                "medical_id": medical_id,
                "symptoms": symptoms,
                "diagnosis": diagnosis,
                "re_exam_date": re_exam_date,
                "notes": notes,
            },
        ).fetchone()

        return {"return_code": result.return_code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario3/prescription_create")
def prescription_create(
    medical_id: int,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            DECLARE @RC INT;

            EXEC @RC = dbo.SP_Prescription_Create
                @MedicalID = :medical_id;

            SELECT @RC AS return_code;
            """),
            {
                "medical_id": medical_id,
            },
        ).fetchone()

        return {"return_code": result.return_code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario3/prescription_detail_add")
def prescription_detail_add(
    prescription_id: int,
    medicine_id: List[int],
    quantity: List[int],
    dosage: List[str],
    note: List[str],
    session: SessionDep,
):
    try:
        detail_count = len(medicine_id)

        if not all(len(lst) == detail_count for lst in [quantity, dosage, note]):
            raise HTTPException(400, "Prescription detail lists length mismatch")

        sql = """
        DECLARE @RC INT;
        DECLARE @Details dbo.PrescriptionDetailList;
        """

        # populate TVP
        for i in range(detail_count):
            sql += f"""
            INSERT INTO @Details (
                MedicineID,
                Quantity,
                Dosage,
                Note
            ) VALUES (
                :medicine_id_{i},
                :quantity_{i},
                :dosage_{i},
                :note_{i}
            );
            """

        sql += """
        EXEC @RC = dbo.SP_PrescriptionDetail_Add
            @PrescriptionID = :prescription_id,
            @Details = @Details;

        SELECT @RC AS return_code;
        """

        params = {
            "prescription_id": prescription_id,
        }

        for i in range(detail_count):
            params.update(
                {
                    f"medicine_id_{i}": medicine_id[i],
                    f"quantity_{i}": quantity[i],
                    f"dosage_{i}": dosage[i],
                    f"note_{i}": note[i],
                }
            )

        result = session.execute(text(sql), params).fetchone()
        return {"return_code": result.return_code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario3/service_order_complete")
def service_order_complete(
    order_id: int,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            DECLARE @RC INT;

            EXEC @RC = dbo.SP_ServiceOrder_Complete
                @OrderID = :order_id;

            SELECT @RC AS return_code;
            """),
            {
                "order_id": order_id,
            },
        ).fetchone()

        return {"return_code": result.return_code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### Scenario 4 ###
@app.post("/scenario4/visit_pending_payment")
def visit_get_pending_payment_all(
    branch_id: int,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            DECLARE @RC INT;

            EXEC @RC = dbo.SP_Visit_GetPendingPayment_All
                @BranchID = :branch_id;

            SELECT @RC AS return_code;
            """),
            {
                "branch_id": branch_id,
            },
        ).fetchone()

        return {"return_code": result.return_code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario4/visit_details")
def visit_get_details(
    visit_id: int,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            DECLARE @RC INT;

            EXEC @RC = dbo.SP_Visit_GetDetails
                @VisitID = :visit_id;

            SELECT @RC AS return_code;
            """),
            {"visit_id": visit_id},
        ).fetchone()

        return {"return_code": result.return_code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario4/invoice_preview")
def invoice_preview(
    visit_id: int,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            DECLARE @RC INT;

            EXEC @RC = dbo.SP_Invoice_Preview
                @VisitID = :visit_id;

            SELECT @RC AS return_code;
            """),
            {"visit_id": visit_id},
        ).fetchone()

        return {"return_code": result.return_code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario4/invoice_create")
def invoice_create(
    visit_id: int,
    receptionist_id: int,
    discount_rate: float,
    payment_method: str,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            DECLARE @RC INT;

            EXEC @RC = dbo.SP_Invoice_Create
                @VisitID = :visit_id,
                @ReceptionistID = :receptionist_id,
                @DiscountRate = :discount_rate,
                @PaymentMethod = :payment_method;

            SELECT @RC AS return_code;
            """),
            {
                "visit_id": visit_id,
                "receptionist_id": receptionist_id,
                "discount_rate": discount_rate,
                "payment_method": payment_method,
            },
        ).fetchone()

        return {"return_code": result.return_code}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### Scenario 5 ###
@app.get("/scenario5/pet_medical_history")
def pet_medical_history(
    pet_id: int,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            EXEC dbo.SP_Pet_GetMedicalHistory
                @PetID = :pet_id;
            """),
            {"pet_id": pet_id},
        )

        rows = result.mappings().all()

        return {"data": rows}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### Scenario 6 ###
@app.get("/scenario6/report_annual_revenue")
def report_annual_revenue(
    target_year: int,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            EXEC dbo.SP_Report_AnnualRevenue
                @TargetYear = :target_year;
            """),
            {"target_year": target_year},
        )

        rows = result.mappings().all()

        return {"year": target_year, "data": rows}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### Scenario 7 ###
@app.get("/scenario7/inventory_low_stock")
def inventory_low_stock(
    current_branch_id: int,
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            EXEC dbo.SP_Inventory_GetLowStock
                @CurrentBranchID = :branch_id;
            """),
            {"branch_id": current_branch_id},
        )

        rows = result.mappings().all()

        return {"branch_id": current_branch_id, "data": rows}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### Scenario 8 ###
@app.get("/scenario8/report_churn_customers")
def report_churn_customers(session: SessionDep):
    try:
        # 1) chạy SP
        result = session.execute(text("EXEC dbo.SP_Report_ChurnCustomers;"))

        # 2) tạo tên file theo timestamp
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = OUTPUT_DIR / f"churn_customers_{ts}.json"

        # 3) ghi JSON dạng mảng: [ {...}, {...}, ... ]
        count = 0
        with out_path.open("w", encoding="utf-8") as f:
            f.write("[\n")
            first = True

            for row in result.mappings().yield_per(1000):
                # row là RowMapping -> convert sang dict
                obj = dict(row)

                # json.dump 1 object/lần (stream)
                if not first:
                    f.write(",\n")
                else:
                    first = False

                json.dump(obj, f, ensure_ascii=False, default=str)
                count += 1

            f.write("\n]\n")

        return {
            "message": "Saved churn customers to json file",
            "file": str(out_path),
            "count": count,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
