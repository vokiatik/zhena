from sweater.database.base_db import SessionLocal
from sweater.models.auth.User_model import UserModel
from sweater.models.auth.Role_model import RoleModel, UserRoleModel
import uuid, datetime

db = SessionLocal()
ur = UserRoleModel(
    user_id=uuid.UUID('73c0d8b9-a8a7-4080-ade0-1271d521266f'),
    role_id=uuid.UUID('8182657e-da09-44a0-93e4-9540ad01b37c'),
    assigned_at=datetime.datetime(2026, 4, 2, 15, 56, 23)
)
db.add(ur)
db.commit()
print('Inserted successfully')
db.close()