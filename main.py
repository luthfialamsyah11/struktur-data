import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import csv, os
from datetime import datetime

FILE_CSV = "toko_bangunan.csv"
TRANSAKSI_CSV = "transaksi.csv"
FIELDNAMES = ['ID', 'Nama', 'Kategori', 'Satuan', 'Stok', 'Harga']
FIELDNAMES_TRANSAKSI = ['Waktu', 'ID', 'Nama', 'Jumlah', 'Total']

def format_rupiah(nominal):
    try:
        return f"Rp {int(nominal):,}".replace(",", ".")
    except:
        return "Rp 0"

def load_data():
    if not os.path.exists(FILE_CSV):
        with open(FILE_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
    with open(FILE_CSV, 'r') as f:
        return list(csv.DictReader(f))

def save_data(data):
    with open(FILE_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(data)

def simpan_transaksi(row, jumlah):
    if not os.path.exists(TRANSAKSI_CSV):
        with open(TRANSAKSI_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES_TRANSAKSI)
            writer.writeheader()
    total = int(jumlah) * int(row['Harga'])
    with open(TRANSAKSI_CSV, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES_TRANSAKSI)
        writer.writerow({
            'Waktu': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ID': row['ID'],
            'Nama': row['Nama'],
            'Jumlah': jumlah,
            'Total': total
        })
    return total

def cetak_struk(row, jumlah, total):
    win = tk.Toplevel(root)
    win.title("Struk Transaksi")
    text = tk.Text(win, font=("Consolas", 11), width=45, height=15, bg="#fff8f0", fg="#333", relief="flat")
    text.pack(padx=10, pady=10)
    text.insert(tk.END, f"🧱 TOKO BANGUNAN MAJU JAYA 🧱\n")
    text.insert(tk.END, f"================================\n")
    text.insert(tk.END, f"Waktu  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    text.insert(tk.END, f"Barang : {row['Nama']}\n")
    text.insert(tk.END, f"Jumlah : {jumlah} {row['Satuan']}\n")
    text.insert(tk.END, f"Harga  : {format_rupiah(row['Harga'])}\n")
    text.insert(tk.END, f"Total  : {format_rupiah(total)}\n")
    text.insert(tk.END, f"================================\n")
    text.insert(tk.END, f"Terima kasih telah berbelanja! 🛒\n")

def show_data():
    tree.delete(*tree.get_children())
    data = load_data()
    for row in data:
        total = int(row['Stok']) * int(row['Harga'])
        tree.insert('', 'end', values=(row['ID'], row['Nama'], row['Kategori'], row['Satuan'], row['Stok'], format_rupiah(row['Harga']), format_rupiah(total)))

def tambah_data():
    top = tk.Toplevel(root)
    top.title("Tambah Barang")
    top.configure(bg="#f0f4ff")
    labels = FIELDNAMES
    entries = {}
    for i, label in enumerate(labels):
        tk.Label(top, text=label, font=("Segoe UI", 10), bg="#f0f4ff").grid(row=i, column=0, sticky="w", padx=10, pady=5)
        entry = tk.Entry(top, font=("Segoe UI", 10))
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[label] = entry

    def simpan():
        data = load_data()
        new_item = {label: entries[label].get() for label in labels}
        if any(d['ID'] == new_item['ID'] for d in data):
            messagebox.showerror("Error", "ID sudah ada!")
            return
        data.append(new_item)
        save_data(data)
        show_data()
        top.destroy()

    ttk.Button(top, text="💾 Simpan", command=simpan).grid(row=len(labels), columnspan=2, pady=15)

def update_data():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Peringatan", "Pilih data terlebih dahulu!")
        return
    val = tree.item(sel[0])['values']
    data = load_data()
    for item in data:
        if item['ID'] == val[0]:
            top = tk.Toplevel(root)
            top.title("Update Barang")
            top.configure(bg="#f0f4ff")
            labels = FIELDNAMES
            entries = {}
            for i, label in enumerate(labels):
                tk.Label(top, text=label, font=("Segoe UI", 10), bg="#f0f4ff").grid(row=i, column=0, sticky="w", padx=10, pady=5)
                entry = tk.Entry(top, font=("Segoe UI", 10))
                entry.insert(0, item[label])
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries[label] = entry

            def simpan():
                for label in labels:
                    item[label] = entries[label].get()
                save_data(data)
                show_data()
                top.destroy()

            ttk.Button(top, text="💾 Simpan", command=simpan).grid(row=len(labels), columnspan=2, pady=15)
            return

def hapus_data():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Peringatan", "Pilih data terlebih dahulu!")
        return
    val = tree.item(sel[0])['values']
    data = load_data()
    data = [item for item in data if item['ID'] != val[0]]
    save_data(data)
    show_data()

def transaksi():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Peringatan", "Pilih barang terlebih dahulu!")
        return
    val = tree.item(sel[0])['values']
    jumlah = simpledialog.askinteger("Jumlah", "Masukkan jumlah pembelian:", minvalue=1)
    if not jumlah:
        return
    data = load_data()
    for item in data:
        if item['ID'] == val[0]:
            if int(item['Stok']) < jumlah:
                messagebox.showerror("Gagal", "Stok tidak mencukupi!")
                return
            item['Stok'] = str(int(item['Stok']) - jumlah)
            total = simpan_transaksi(item, jumlah)
            save_data(data)
            show_data()
            cetak_struk(item, jumlah, total)
            return

def tampilkan_transaksi():
    if not os.path.exists(TRANSAKSI_CSV):
        messagebox.showinfo("Info", "Belum ada transaksi.")
        return
    win = tk.Toplevel(root)
    win.title("Riwayat Transaksi")
    tree_trans = ttk.Treeview(win, columns=FIELDNAMES_TRANSAKSI, show="headings")
    for col in FIELDNAMES_TRANSAKSI:
        tree_trans.heading(col, text=col)
        tree_trans.column(col, width=110)
    tree_trans.pack(fill="both", expand=True, padx=10, pady=10)
    with open(TRANSAKSI_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tree_trans.insert('', 'end', values=(row['Waktu'], row['ID'], row['Nama'], row['Jumlah'], format_rupiah(row['Total'])))

def cari_data():
    keyword = entry_cari.get().lower()
    data = load_data()
    hasil = [row for row in data if keyword in row['ID'].lower() or keyword in row['Nama'].lower() or keyword in row['Kategori'].lower()]
    tree.delete(*tree.get_children())
    for row in hasil:
        total = int(row['Stok']) * int(row['Harga'])
        tree.insert('', 'end', values=(row['ID'], row['Nama'], row['Kategori'], row['Satuan'], row['Stok'], format_rupiah(row['Harga']), format_rupiah(total)))

def reset_data():
    entry_cari.delete(0, tk.END)
    show_data()

root = tk.Tk()
root.title("🧱 TOKO BANGUNAN MAJU JAYA | Solusi Kebutuhan Konstruksi Anda 🏗️")
root.geometry("1050x620")
root.configure(bg="#f9f9f9")

style = ttk.Style(root)
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)

frame_header = tk.Frame(root, bg="#4a90e2")
frame_header.pack(fill="x")
title_label = tk.Label(frame_header, text="🧱 TOKO BANGUNAN MAJU JAYA 🏗️", font=("Segoe UI", 20, "bold"), fg="white", bg="#4a90e2", pady=10)
title_label.pack()
subtitle_label = tk.Label(frame_header, text="Solusi Kebutuhan Konstruksi Anda", font=("Segoe UI", 12), fg="white", bg="#4a90e2")
subtitle_label.pack()

frame_cari = ttk.Frame(root)
frame_cari.pack(pady=10)

ttk.Label(frame_cari, text="🔍 Cari Produk: ", font=("Segoe UI", 10)).pack(side="left")
entry_cari = ttk.Entry(frame_cari, width=30)
entry_cari.pack(side="left", padx=5)
ttk.Button(frame_cari, text="Cari", command=cari_data).pack(side="left", padx=5)
ttk.Button(frame_cari, text="Reset", command=reset_data).pack(side="left", padx=5)

frame_btn = tk.Frame(root, bg="#f9f9f9")
frame_btn.pack(pady=15)

button_bg = "#4a90e2"
button_fg = "white"
button_font = ("Segoe UI", 10, "bold")
button_padx = 8

btn_tambah = tk.Button(frame_btn, text="🆕 Tambah", command=tambah_data, bg=button_bg, fg=button_fg, font=button_font, width=18, padx=button_padx)
btn_tambah.pack(side="left", padx=6)

btn_update = tk.Button(frame_btn, text="♻️ Update", command=update_data, bg=button_bg, fg=button_fg, font=button_font, width=18, padx=button_padx)
btn_update.pack(side="left", padx=6)

btn_hapus = tk.Button(frame_btn, text="🗑️ Hapus", command=hapus_data, bg=button_bg, fg=button_fg, font=button_font, width=18, padx=button_padx)
btn_hapus.pack(side="left", padx=6)

btn_transaksi = tk.Button(frame_btn, text="🛒 Transaksi", command=transaksi, bg=button_bg, fg=button_fg, font=button_font, width=18, padx=button_padx)
btn_transaksi.pack(side="left", padx=6)

btn_riwayat = tk.Button(frame_btn, text="📄 Riwayat Transaksi", command=tampilkan_transaksi, bg=button_bg, fg=button_fg, font=button_font, width=18, padx=button_padx)
btn_riwayat.pack(side="left", padx=6)

btn_style = {"padding": 6, "width": 18}



frame_table = ttk.Frame(root)
frame_table.pack(fill="both", expand=True, padx=20, pady=10)

kolom = ['ID', 'Nama', 'Kategori', 'Satuan', 'Stok', 'Harga', 'Total']
tree = ttk.Treeview(frame_table, columns=kolom, show="headings")
for k in kolom:
    tree.heading(k, text=k)
    tree.column(k, width=120, anchor="center")
tree.pack(fill="both", expand=True)

show_data()
root.mainloop()
