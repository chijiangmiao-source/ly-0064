from sqlalchemy.orm import Session

from app.database import engine, Base, SessionLocal
from app.models import User, Store, MaterialCategory, Material
from app.security import get_password_hash


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        if not db.query(Store).first():
            store = Store(name="总店", address="北京市朝阳区", phone="13800138000")
            db.add(store)
            db.commit()
            db.refresh(store)
            store_id = store.id
        else:
            store_id = db.query(Store).first().id
        
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                full_name="管理员",
                store_id=store_id,
                is_admin=True
            )
            db.add(admin)
        
        if not db.query(User).filter(User.username == "user").first():
            user = User(
                username="user",
                password_hash=get_password_hash("user123"),
                full_name="普通用户",
                store_id=store_id,
                is_admin=False
            )
            db.add(user)
        
        categories = ["茶叶类", "奶类", "糖类", "粉类", "配料类", "包装类"]
        for cat_name in categories:
            if not db.query(MaterialCategory).filter(MaterialCategory.name == cat_name).first():
                cat = MaterialCategory(name=cat_name)
                db.add(cat)
        
        db.commit()
        print("数据库初始化完成！")
        print("默认账号: admin / admin123")
        print("普通账号: user / user123")
        
    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
