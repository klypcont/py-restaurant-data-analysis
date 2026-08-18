import sqlite3
import pandas as pd


def analyze_restaurant_data() -> dict:
    conn = sqlite3.connect("db.sqlite3")
    
    try:
        products_df = pd.read_sql("SELECT * FROM products", conn)
    except Exception:
        products_df = pd.DataFrame()
        
    try:
        orders_df = pd.read_sql("SELECT * FROM orders", conn)
    except Exception:
        orders_df = pd.DataFrame()
        
    try:
        order_items_df = pd.read_sql("SELECT * FROM order_items", conn)
    except Exception:
        order_items_df = pd.DataFrame()
        
    conn.close()
    
    total_orders = len(orders_df) if not orders_df.empty else 0
    total_items = len(order_items_df) if not order_items_df.empty else 0
    
    total_revenue = 0.0
    if not order_items_df.empty:
        price_col = next((c for c in ["price", "unit_price", "cost"] if c in order_items_df.columns), None)
        qty_col = next((c for c in ["quantity", "qty", "amount"] if c in order_items_df.columns), None)
        if price_col and qty_col:
            total_revenue = float((order_items_df[price_col] * order_items_df[qty_col]).sum())
        elif price_col:
            total_revenue = float(order_items_df[price_col].sum())

    return {
        "total_orders": total_orders,
        "total_items": total_items,
        "total_revenue": total_revenue
    }


if __name__ == "__main__":
    print(analyze_restaurant_data())

