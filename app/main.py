import sqlite3
import pandas as pd


def get_average_order_value(conn) -> float:
    try:
        query = """
            SELECT AVG(order_total) FROM (
                SELECT order_id, SUM(price * quantity) as order_total
                FROM order_items
                GROUP BY order_id
            )
        """
        res = pd.read_sql(query, conn)
        return float(res.iloc[0, 0]) if not res.empty and pd.notna(res.iloc[0, 0]) else 0.0
    except Exception:
        return 0.0


def get_top_products(conn, n=5) -> dict:
    try:
        query = """
            SELECT p.name, SUM(oi.quantity) as total_qty, SUM(oi.price * oi.quantity) as total_rev
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            GROUP BY p.name
        """
        df = pd.read_sql(query, conn)
        if df.empty:
            return {"by_qty": {}, "by_revenue": {}}
        
        by_qty = df.sort_values(by="total_qty", ascending=False).head(n).set_index("name")["total_qty"].to_dict()
        by_revenue = df.sort_values(by="total_rev", ascending=False).head(n).set_index("name")["total_rev"].to_dict()
        return {"by_qty": by_qty, "by_revenue": by_revenue}
    except Exception:
        return {"by_qty": {}, "by_revenue": {}}


def get_category_breakdown(conn) -> dict:
    try:
        query = """
            SELECT p.category, SUM(oi.quantity * oi.price) as revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            GROUP BY p.category
        """
        df = pd.read_sql(query, conn)
        if df.empty:
            return {}
        return df.set_index("category")["revenue"].to_dict()
    except Exception:
        return {}


def get_daily_order_counts(conn) -> dict:
    try:
        query = "SELECT order_date, COUNT(*) as count FROM orders GROUP BY order_date"
        df = pd.read_sql(query, conn)
        if df.empty:
            return {}
        return df.set_index("order_date")["count"].to_dict()
    except Exception:
        return {}


def get_weekly_trends(conn) -> dict:
    try:
        query = "SELECT strftime(\x27%Y-%W\x27, order_date) as week, COUNT(*) as count FROM orders GROUP BY week"
        df = pd.read_sql(query, conn)
        if df.empty or df["week"].isna().all():
            return {}
        return df.dropna().set_index("week")["count"].to_dict()
    except Exception:
        return {}


def analyze_restaurant_data() -> dict:
    conn = sqlite3.connect("db.sqlite3")
    
    try:
        orders_df = pd.read_sql("SELECT * FROM orders", conn)
    except Exception:
        orders_df = pd.DataFrame()
        
    try:
        order_items_df = pd.read_sql("SELECT * FROM order_items", conn)
    except Exception:
        order_items_df = pd.DataFrame()
        
    total_orders = len(orders_df) if not orders_df.empty else 0
    total_items = int(order_items_df["quantity"].sum()) if not order_items_df.empty and "quantity" in order_items_df.columns else len(order_items_df)
    
    total_revenue = 0.0
    if not order_items_df.empty:
        price_col = next((c for c in ["price", "unit_price"] if c in order_items_df.columns), None)
        qty_col = next((c for c in ["quantity", "qty"] if c in order_items_df.columns), None)
        if price_col and qty_col:
            total_revenue = float((order_items_df[price_col] * order_items_df[qty_col]).sum())
        elif price_col:
            total_revenue = float(order_items_df[price_col].sum())

    avg_order_value = get_average_order_value(conn)
    top_products = get_top_products(conn)
    category_breakdown = get_category_breakdown(conn)
    daily_orders = get_daily_order_counts(conn)
    weekly_trends = get_weekly_trends(conn)
    
    conn.close()

    return {
        "total_orders": total_orders,
        "total_items": total_items,
        "total_revenue": total_revenue,
        "avg_order_value": avg_order_value,
        "top_products_by_qty": top_products.get("by_qty", {}),
        "top_products_by_revenue": top_products.get("by_revenue", {}),
        "category_breakdown": category_breakdown,
        "daily_orders": daily_orders,
        "weekly_trends": weekly_trends
    }


if __name__ == "__main__":
    print(analyze_restaurant_data())

