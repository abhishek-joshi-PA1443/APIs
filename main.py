from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2AuthorizationCodeBearer
from sqlalchemy.orm import Session
from .db_connection import create_schema, get_db
from .models import Employee, EmployeeCreate, EmployeeResponse, EmployeeUpdate
from .logging import get_logger, LoggingMiddleware


app = FastAPI()

oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl="token")

logger = get_logger(__name__)

app.add_middleware(LoggingMiddleware)

async def get_current_user(token : str = Depends(oauth2_scheme), db : Session = Depends(get_db)):
    db_emp = db.query(Employee).filter(Employee.email == token).first()
    if not db_emp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
            headers={"WWW-Authenticate":"Bearer"}
        )
    return db_emp

async def get_admin(token : str = Depends(oauth2_scheme),db:Session=Depends(get_db)):
    db_emp = db.query(Employee).filter(Employee.email == token).first()
    if db_emp.role != "admin" or db_emp is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_emp


@app.post("/token")
async def login(form_data : OAuth2PasswordRequestForm = Depends(),db:Session = Depends(get_db)):
    db_emp = db.query(Employee).filter(form_data.username == Employee.email).first()
    if db_emp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid username or password")
    if db_emp.password != form_data.password:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid username or password")
    # if db_emp.role != "admin":
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid username or password")
    return {"access_token": db_emp.email, "token_type": "bearer"}


@app.post("/token/admin")
async def login_admin(form_data : OAuth2PasswordRequestForm = Depends(),db:Session = Depends(get_db)):
    db_emp = db.query(Employee).filter(form_data.username == Employee.email).first()
    if db_emp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid username or password")
    if db_emp.password != form_data.password:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid username or password")
    if db_emp.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Invalid username or password")
    return {"access_token": db_emp.email, "token_type": "bearer"}

@app.on_event("startup")
def on_startup():
    create_schema()


# current_user:EmployeeResponse = Depends(get_current_user)

# current_admin:EmployeeResponse = Depends(get_admin)

@app.post("/employee",response_model=EmployeeResponse)
async def create_employee(emp:EmployeeCreate,db:Session = Depends(get_db)):
    db_emp = Employee(name=emp.name,email=emp.email,password=emp.password,role=emp.role,manager_id=emp.manager_id)
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp


@app.get("/employees",response_model=list[EmployeeResponse])
async def read_employees(db:Session=Depends(get_db)):
    employees = db.query(Employee).all()
    return employees

@app.get("/emp",response_model=EmployeeResponse)
async def read_specific_employee(current_user : EmployeeResponse = Depends(get_current_user)):
    return current_user

@app.get("/manager/employees",response_model=dict())
async def read_manager_employees(current_user : EmployeeResponse = Depends(get_current_user),db:Session=Depends(get_db)):
    # sample_emp = db.query(Employee).filter(current_user.id == Employee.manager_id).first()
    emp_list = db.query(Employee).filter(current_user.id == Employee.manager_id).all()
    # new_emps = db.query(Employee).filter(Employee.manager_id == sample_emp.id).all()
    all_emps = {}
    for emps in emp_list:
        all_emps[emps.name] = []
        new_emps = db.query(Employee).filter(emps.id == Employee.manager_id).all()
        for emp in new_emps:
            all_emps[emps.name].append(emp)
    return all_emps


@app.delete("/employee/{emp_id}",response_model=EmployeeResponse)
async def delete_employee(emp_id:int,db:Session = Depends(get_db)):
    db_emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if db_emp is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No data for the employee")
    else:
        del_emp = db_emp
        db.delete(db_emp)
        db.commit()
        return del_emp
        # db.refresh(db_emp)
        # return f"Employee with id {emp_id} is deleted"


@app.put("/manager/update-employee/{emp_id}",response_model=EmployeeResponse)
async def update_managers_employee(emp_id : int,update_data:EmployeeUpdate,current_user : EmployeeResponse = Depends(get_current_user),db:Session=Depends(get_db)):
    if current_user.role == "manager" or current_user.role == "deputy_manager":
        db_emp = db.query(Employee).filter(current_user.id == Employee.manager_id).filter(Employee.id == emp_id).first()
        # if emp_list:
        #     for emp in emp_list:
        #         if emp.id == emp_id:
        #             # emp.id = emp.id
        #             # emp.name = emp.name
        #             # emp.email = emp.email
        #             emp.role = update_data.role
        #             emp.manager_id = update_data.manager_id
        #             # emp = EmployeeResponse(name=emp.name,email=emp.email,role=update_data.role,manager_id=update_data.manager_id)
        #             return emp           
        if not db_emp:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,detail="Sorry this employee is not in your team")
        else:
            db_emp.role = update_data.role
            db_emp.manager_id = update_data.manager_id
            db.commit()
            db.refresh(db_emp)
            return db_emp
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Sorry you are not authorized to this api")   
