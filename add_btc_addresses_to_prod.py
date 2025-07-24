#!/usr/bin/env python3
import sqlite3

DB_PATH = '/opt/pocketflow/data/users.db'
ADMIN_EMAIL = 'admin@klasholmgren.se'
NEW_ADDRESSES = [
    "bc1q9hnp3v4gcm2mjfg6ay2zpf9us9gg43zs8992ng",
    "bc1qlaqrmujm0r5y845s5n37jaumael5fatfxjpzfs",
    "bc1qdjhc9wnac0hqf0fhsplx7kr3rk2twjg0qcdtst",
    "bc1q5g7m5spm88d7kq6jcv6c2gn8zk9l8wj6774rjy",
    "bc1q3pdlj7hn4rslzdxmuekgna334dduf7shlql906",
    "bc1qv2uhey2km5nsf3g83a62zavqkvdpnrvzt0t2gx",
    "bc1qaew00m3wnv85kf8d4kfn7z3z67u6z0mhep9k37",
    "bc1qayrk9swkmnp8en7kzke9df02g0rz6v3y67gmyc",
    "bc1q52mded0ct5jzqs3qelf2sfrvw3k76kwdtdfuv0",
    "bc1q0qqt9mqslux8neyk06s7pjf0ma95ae2saza5dc",
    "bc1qvgegfxcqs6fmc9mlzdcmz2v2x24xnpa2nkpyv2",
    "bc1qwff979f78n8qdwgqd6rlcphgxc4lyr6rshr2cv",
    "bc1qf82d735vy0mn63jkkz8guguv6z86n753ez33r9",
    "bc1q3nkfgtguas6yvf75zfy8ttyrvlxfq295p0a436",
    "bc1qs9an84vcgr9gmscuuqeqkp3jtystwjggdyz2xj",
    "bc1qt0wklf6l4zvy4xjq9lvshn20y73mlzwk7xl5lr",
    "bc1qwaxfg7em4ka9zmtvq2rw27ez9trft6mhnxdp2a",
    "bc1q4xnwc4jmck0weskq6vhvdpeul06q0wu39dal57",
    "bc1qk8q4skv4utngs2ezz5kmgdhl2ke9hzmnsv8qfu",
    "bc1q89tpdjg8k7nc09g8ucqxdm2qzh7jed0ulnxz2f"
]

def add_addresses(db_path, email, addresses):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    added = 0
    for addr in addresses:
        try:
            cursor.execute("INSERT INTO btc_addresses (email, address) VALUES (?, ?)", (email, addr))
            added += 1
        except Exception as e:
            print(f"Error adding {addr}: {e}")
    conn.commit()
    conn.close()
    return added

def main():
    added = add_addresses(DB_PATH, ADMIN_EMAIL, NEW_ADDRESSES)
    print(f"✅ Added {added} new BTC addresses to {ADMIN_EMAIL} in {DB_PATH}")

if __name__ == "__main__":
    main() 