import sqlite3
import tkinter as tk
from tkinter import messagebox

# --- DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect("prices.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS phones(model TEXT, price REAL, stars INTEGER)")
    conn.commit()
    conn.close()

def insert_data(model, price, stars):
    if not model or not price:
        messagebox.showwarning("Input Error", "Model and Price cannot be empty!")
        return

    try:
        price_value = float(price)
        stars_value = int(stars)
    except ValueError:
        messagebox.showwarning("Input Error", "Price must be a number and stars must be an integer.")
        return

    conn = sqlite3.connect("prices.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO phones (model, price, stars) VALUES (?, ?, ?)",
        (model, price_value, stars_value),
    )
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"{model} added!")

# --- ADD NEW WINDOW ---
def open_add_window():
    new_window = tk.Toplevel(app)
    new_window.title("Add New Phone")
    new_window.geometry("350x400")

    # Model Girişi ve Otomatik Arama
    tk.Label(new_window, text="Model Name:").pack(pady=5)
    model_var = tk.StringVar() # Metni izlemek için değişken
    ent_model = tk.Entry(new_window, textvariable=model_var)
    ent_model.pack(pady=5)

    # Tahmini Fiyat Etiketi
    lbl_est = tk.Label(new_window, text="Estimated Price: None", fg="blue")
    lbl_est.pack(pady=5)
    suggested_price = {"value": None}

    tk.Label(new_window, text="Actual Price:").pack(pady=5)
    ent_price = tk.Entry(new_window)
    ent_price.pack(pady=5)

    # Veritabanında Fiyat Arama Fonksiyonu
    def check_price(*args):
        search_term = model_var.get()
        if len(search_term) > 2: # En az 3 harf yazınca ara
            conn = sqlite3.connect("prices.db")
            cur = conn.cursor()
            cur.execute("SELECT price FROM phones WHERE model LIKE ? LIMIT 1", (f"%{search_term}%",))
            result = cur.fetchone()
            conn.close()
            
            if result:
                suggested_price["value"] = float(result[0])
                lbl_est.config(text=f"Suggested Price: {result[0]}")
            else:
                suggested_price["value"] = None
                lbl_est.config(text="Suggested Price: Not found")
        else:
            suggested_price["value"] = None
            lbl_est.config(text="Estimated Price: None")

    # Yazı yazıldığında check_price fonksiyonunu çalıştır
    model_var.trace_add("write", check_price)

    tk.Label(new_window, text="Stars (1-5):").pack(pady=5)
    ent_stars = tk.Scale(new_window, from_=1, to=5, orient=tk.HORIZONTAL)
    ent_stars.pack(pady=5)

    def submit():
        # O an kutularda yazılı olan değerleri alıyoruz
        selected_model = ent_model.get()
        selected_price = ent_price.get()
        selected_stars = ent_stars.get()

        if not selected_model or not selected_price:
            messagebox.showwarning("Input Error", "Model and Price cannot be empty!")
            return

        try:
            actual_price = float(selected_price)
        except ValueError:
            messagebox.showwarning("Input Error", "Actual Price must be a number.")
            return

        profit = None
        if suggested_price["value"] is not None:
            profit = actual_price - suggested_price["value"]

        # 'receipt.txt' dosyasına bu verileri kaydediyoruz
        with open(f"{selected_model}receipt.txt", "w", encoding="utf-8") as f:
            f.write("--- PURCHASE RECEIPT ---\n")
            f.write(f"Model: {selected_model}\n")
            f.write(f"Price: ${actual_price:.2f}\n")
            f.write(f"Rating: {selected_stars} Stars\n")
            if profit is None:
                f.write("Owner Profit: N/A\n")
            else:
                f.write(f"Owner Profit: ${profit:.2f}\n")
                f.write("IF OWNER PROFIT IS IN THE NEGATIVES YOU HAVE AN HIGH CHANCE OF BEING SCAMMED")
            f.write("------------------------")
            f.write("Made using Device Bill")
        # Veritabanına da kaydetmek istersen (isteğe bağlı)
        insert_data(selected_model, actual_price, selected_stars)
        
        messagebox.showinfo("Saved", "Receipt generated and data saved!")
        new_window.destroy()



    tk.Button(new_window, text="Save to Database", command=submit, bg="lightblue").pack(pady=20)

# --- MAIN UI SETUP ---
app = tk.Tk()
app.title("DeviceBill")
app.geometry("400x400")

init_db()

tk.Button(app, text="Add New Device", command=open_add_window, width=20).pack(pady=10)
# (Diğer butonları buraya ekleyebilirsin...)

app.mainloop()
