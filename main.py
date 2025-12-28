from datetime import date
from typing import List, Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException

from database import SessionDep
from sqlalchemy import text

from pydantic import BaseModel
from decimal import Decimal
from schemas import MedicalHistoryResponse, AnnualRevenueResponse
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
            @Note = :note,
            @BookingID = @BookingID OUTPUT;

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
    try:
        sql = text(
            """
            DECLARE @RC int;
            DECLARE @BookingID int;
            DECLARE @Details [dbo].[BookingDetailList];
            
            -- Insert booking details into table variable
            """
            + "\n".join(
                [
                    f"INSERT INTO @Details (ServiceID, PetID, Note) VALUES ({d['service_id']}, {d['petid']}, {repr(d.get('note'))});"
                    for d in details
                ]
            )
            + """
            
            -- Execute stored procedure
            EXEC @RC = [dbo].[SP_Booking_CreateDetailed]
                @CustomerID = :customer_id,
                @BranchID = :branch_id,
                @ReceptionistID = :receptionist_id,
                @Details = @Details,
                @Note = :note,
                @BookingID = @BookingID OUTPUT;
        """
        )

        session.execute(
            sql,
            {
                "customer_id": customer_id,
                "branch_id": branch_id,
                "receptionist_id": receptionist_id,
                "note": note,
            },
        )

        session.commit()

    except Exception as e:
        session.rollback()
        raise e


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
                @Species = :spPetID@Breed = :breed,
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

        if result is not None:
            return {"success": True}
        else:
            return {"success": False}
    except Exception as e:
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

        result = session.execute(text(sql), params).fetchone()
        print(result)
        return {"return_code": result.VisitID}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        ).fetchall()
        orders = []
        for item in result:
            orders.append(
                {
                    "orderID": item[0],
                    "PetName": item[1],
                    "ServiceName": item[2],
                    "TimeIn": item[3],
                    "Note": item[4],
                }
            )
        return orders

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
        session.commit()
        if result is not None:
            return {"success": True}
        else:
            return {"success": False}
    except Exception as e:
        print(e)
        return {"success": False}


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
        ).fetchall()
        orders = []
        for item in result:
            orders.append(
                {
                    "VisitID": item[0],
                    "CustomerName": item[1],
                    "TimeIn": item[2],
                    "ReceptionistName": item[3],
                }
            )
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenario4/visit_details/{visit_id}")
def visit_get_details(
    visit_id: int,
    session: SessionDep,
):
    try:
        # Get visit basic info
        visit_result = session.execute(
            text("""
            EXEC dbo.SP_Visit_GetDetails @VisitID = :visit_id;
            """),
            {"visit_id": visit_id},
        ).fetchone()

        if not visit_result:
            raise HTTPException(status_code=404, detail="Visit not found")

        # Get service orders for this visit
        orders_result = session.execute(
            text("""
            SELECT 
                SO.OrderID,
                SO.ServiceName,
                P.PetName,
                SO.Status,
                SO.Price,
                SO.Discount,
                SO.Note
            FROM ServiceOrder SO
            LEFT JOIN Pet P ON SO.PetID = P.PetID
            WHERE SO.VisitID = :visit_id
            ORDER BY SO.OrderID;
            """),
            {"visit_id": visit_id},
        ).fetchall()

        service_orders = []
        for row in orders_result:
            service_orders.append(
                {
                    "ServiceOrderID": row[0],
                    "ServiceName": row[1],
                    "PetName": row[2],
                    "Status": row[3],
                    "Price": float(row[4]) if row[4] else 0,
                    "Discount": float(row[5]) if row[5] else 0,
                    "Note": row[6],
                }
            )

        return {
            "VisitID": visit_result[0],
            "TimeIn": str(visit_result[1]) if visit_result[1] else None,
            "CustomerID": visit_result[2],
            "CustomerName": visit_result[3],
            "PhoneNumber": visit_result[4].strip() if visit_result[4] else "",
            "LoyaltyPoints": visit_result[5] if visit_result[5] else 0,
            "MembershipTier": visit_result[6],
            "BranchID": visit_result[7],
            "ServiceOrders": service_orders,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario4/invoice_preview")
def invoice_preview(
    visit_id: int,
    session: SessionDep,
):
    try:
        # Get the raw connection
        connection = session.connection()
        cursor = connection.connection.cursor()

        # Execute the stored procedure
        cursor.execute("EXEC dbo.SP_Invoice_Preview @VisitID = ?", (visit_id,))

        # First result set: Line items
        line_items = []
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            line_items.append(
                {
                    "OrderID": row[0],
                    "PetName": row[1],
                    "ServiceName": row[2],
                    "BasePrice": float(row[3]) if row[3] else 0,
                    "DiscountAmount": float(row[4]) if row[4] else 0,
                    "FinalItemPrice": float(row[5]) if row[5] else 0,
                }
            )

        # Move to second result set: Totals
        totals = {
            "SubTotal_Base_All": 0,
            "ServiceOrderDiscount_Total": 0,
            "TotalAmount_Net_Before_Final_Discount": 0,
        }

        if cursor.nextset():
            totals_row = cursor.fetchone()
            if totals_row:
                totals = {
                    "SubTotal_Base_All": float(totals_row[0]) if totals_row[0] else 0,
                    "ServiceOrderDiscount_Total": float(totals_row[1])
                    if totals_row[1]
                    else 0,
                    "TotalAmount_Net_Before_Final_Discount": float(totals_row[2])
                    if totals_row[2]
                    else 0,
                }

        cursor.close()

        return {"line_items": line_items, "totals": totals}

    except Exception as e:
        # Check if it's the warning about existing invoice
        error_message = str(e)
        if "Cảnh báo" in error_message or "đã được tạo" in error_message:
            raise HTTPException(
                status_code=400, detail="Invoice for this VisitID already exists"
            )
        raise HTTPException(status_code=500, detail=error_message)


@app.post("/scenario4/invoice_create")
def invoice_create(
    visit_id: int,
    receptionist_id: int,
    discount_rate: float,
    payment_method: str,
    session: SessionDep,
):
    try:
        # Get the raw connection
        connection = session.connection()
        cursor = connection.connection.cursor()

        # Execute the stored procedure
        cursor.execute(
            "EXEC dbo.SP_Invoice_Create @VisitID = ?, @ReceptionistID = ?, @DiscountRate = ?, @PaymentMethod = ?",
            (visit_id, receptionist_id, discount_rate, payment_method),
        )

        # Fetch the result (NewInvoiceID, TotalPaid, PointsEarned)
        result_row = cursor.fetchone()

        if result_row:
            response = {
                "NewInvoiceID": result_row[0],
                "TotalPaid": float(result_row[1]) if result_row[1] else 0,
                "PointsEarned": result_row[2] if result_row[2] else 0,
            }
        else:
            response = {"NewInvoiceID": None, "TotalPaid": 0, "PointsEarned": 0}

        cursor.close()

        # Commit the transaction
        session.commit()

        return response

    except Exception as e:
        # Rollback on error
        session.rollback()

        error_message = str(e)

        # Handle specific error cases
        if "Tỷ lệ giảm giá phải nằm trong khoảng" in error_message:
            raise HTTPException(
                status_code=400, detail="Discount rate must be between 0.0 and 1.0"
            )
        elif "VisitID không hợp lệ" in error_message:
            raise HTTPException(
                status_code=404, detail="Invalid VisitID or Visit already paid"
            )
        elif "Không có dịch vụ/sản phẩm nào đã hoàn thành" in error_message:
            raise HTTPException(
                status_code=400, detail="No completed services/products to pay for"
            )

        raise HTTPException(status_code=500, detail=error_message)


@app.get("/scenario5/pet_medical_history", response_model=List[MedicalHistoryResponse])
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

        return rows

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenario6/report_annual_revenue", response_model=List[AnnualRevenueResponse])
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

        return rows

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenario7/report_churn_customers")
def report_churn_customers(
    session: SessionDep,
):
    try:
        result = session.execute(
            text("""
            EXEC dbo.SP_Report_ChurnCustomers;
            """)
        )

        rows = result.mappings().all()

        return {"data": rows}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scenario8/inventory_low_stock")
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
