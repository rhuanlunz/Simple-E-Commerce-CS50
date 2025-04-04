from datetime           import datetime
from json               import loads

from sqlalchemy.orm     import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy         import Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.sql     import func


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    creation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cart = relationship("Cart", back_populates="user")


    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"


class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(254), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(254), nullable=False)
    image_path: Mapped[str] = mapped_column(String(254), nullable=False)

    cart = relationship("Cart", back_populates="product")

    
    def __repr__(self):
        return f"Products(id={self.id}, name='{self.name}', description='{self.description}', price='{self.price}', category='{self.category}', img='{self.image_path}')"


    def initialize(self, session):
        with open("products.json", "r") as f:
            products = loads(f.read())

        for i in products["products"]:
            table = self.__class__

            product = table(
                name=i["name"], 
                description=i["description"],
                price=i["price"],
                category=i["category"],
                image_path=i["image_path"]
            )
            
            result = session.query(table).filter_by(
                name=product.name, 
                description=product.description, 
                price=product.price,
                category=product.category,
                image_path=product.image_path
            ).first()

            if not result:
                session.add(product)
        session.commit()


class Cart(Base):
    __tablename__ = "users_cart"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    
    user = relationship("User", back_populates="cart")
    product = relationship("Products", back_populates="cart")


    def __repr__(self):
        return f"Cart(id='{self.id}', user_id='{self.user_id}', product_id='{self.product_id}')"

