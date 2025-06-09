import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import json
import os
import shutil

class App:
    def __init__(self):
        self.config = self.load_config()
        self.password = self.config.get('password', 'admin123')
        self.init_db()
        self.login()

    def load_config(self):
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_config(self):
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass

    def init_db(self):
        self.conn = sqlite3.connect('data.db')
        self.cursor = self.conn.cursor()
        
        # 기존 테이블 구조 확인
        self.cursor.execute('PRAGMA table_info(records)')
        columns = {col[1]: col[2] for col in self.cursor.fetchall()}
        
        # 테이블이 없으면 생성
        if not columns:
            self.cursor.execute('''
                CREATE TABLE records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    points INTEGER NOT NULL,
                    point_type TEXT NOT NULL DEFAULT "상점",
                    timestamp TEXT NOT NULL
                )
            ''')
        else:
            # 구버전 스키마 호환성
            if 'point_type' not in columns:
                self.cursor.execute('ALTER TABLE records ADD COLUMN point_type TEXT DEFAULT "상점"')
                # 기존 데이터의 point_type 업데이트
                self.cursor.execute('UPDATE records SET point_type = "상점" WHERE points > 0 AND point_type IS NULL')
                self.cursor.execute('UPDATE records SET point_type = "벌점" WHERE points < 0 AND point_type IS NULL')
            
            if 'timestamp' not in columns and 'time' in columns:
                self.cursor.execute('ALTER TABLE records ADD COLUMN timestamp TEXT')
                self.cursor.execute('UPDATE records SET timestamp = time WHERE timestamp IS NULL')
        
        self.conn.commit()

    def login(self):
        self.login_win = tk.Tk()
        self.login_win.title("상벌점 관리 로그인")
        self.login_win.geometry("300x180")
        
        frame = tk.Frame(self.login_win, padx=30, pady=30)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="상벌점 관리", font=('맑은 고딕', 16, 'bold')).pack(pady=(0, 20))
        
        tk.Label(frame, text="비밀번호").pack(anchor='w')
        self.pwd_entry = tk.Entry(frame, show="*", font=('맑은 고딕', 11))
        self.pwd_entry.pack(fill='x', pady=(5, 15))
        self.pwd_entry.bind('<Return>', lambda e: self.check_pwd())

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill='x')
        
        tk.Button(btn_frame, text="로그인", command=self.check_pwd).pack(side='left', fill='x', expand=True)
        tk.Button(btn_frame, text="비밀번호 변경", command=self.change_pwd).pack(side='right', padx=(10, 0))
        
        self.pwd_entry.focus()
        self.login_win.mainloop()

    def check_pwd(self):
        if self.pwd_entry.get() == self.password:
            self.login_win.destroy()
            self.main()
        else:
            messagebox.showerror("오류", "잘못된 비밀번호입니다")
            self.pwd_entry.delete(0, tk.END)

    def change_pwd(self):
        new = simpledialog.askstring("비밀번호 변경", "새 비밀번호를 입력하세요:", show='*')
        if new and len(new) >= 3:
            self.password = new
            self.config['password'] = new
            self.save_config()
            messagebox.showinfo("완료", "비밀번호가 변경되었습니다")
        elif new is not None:
            messagebox.showerror("오류", "비밀번호는 최소 3자 이상이어야 합니다")

    def main(self):
        self.root = tk.Tk()
        self.root.title("상벌점 관리")
        self.root.geometry("1000x700")

        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 헤더
        header = tk.Frame(main_frame)
        header.pack(fill=tk.X, pady=(0, 20))

        tk.Label(header, text="상벌점 관리", font=('맑은 고딕', 18, 'bold')).pack(side='left')
        
        header_btn = tk.Frame(header)
        header_btn.pack(side='right')
        
        tk.Button(header_btn, text="데이터 초기화", command=self.reset_data).pack(side='left', padx=(0, 10))
        tk.Button(header_btn, text="로그아웃", command=self.logout).pack(side='left')

        # 입력 섹션
        input_frame = tk.LabelFrame(main_frame, text="정보 입력", font=('맑은 고딕', 11, 'bold'), padx=15, pady=15)
        input_frame.pack(fill=tk.X, pady=(0, 20))

        # 첫 번째 행
        row1 = tk.Frame(input_frame)
        row1.pack(fill=tk.X, pady=(0, 10))

        tk.Label(row1, text="학번", width=8).pack(side='left')
        self.e1 = tk.Entry(row1, width=15)
        self.e1.pack(side='left', padx=(0, 20))

        tk.Label(row1, text="이름", width=8).pack(side='left')
        self.e2 = tk.Entry(row1, width=12)
        self.e2.pack(side='left', padx=(0, 20))

        tk.Label(row1, text="점수", width=8).pack(side='left')
        self.e3 = tk.Entry(row1, width=8)
        self.e3.pack(side='left')

        # 두 번째 행
        row2 = tk.Frame(input_frame)
        row2.pack(fill=tk.X, pady=(0, 15))

        tk.Label(row2, text="사유", width=8).pack(side='left')
        self.e4 = tk.Entry(row2)
        self.e4.pack(side='left', fill='x', expand=True)

        # 버튼들
        btn_frame = tk.Frame(input_frame)
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="상점 추가", command=lambda: self.add("상점")).pack(side='left', padx=(0, 10))
        tk.Button(btn_frame, text="벌점 추가", command=lambda: self.add("벌점")).pack(side='left', padx=(0, 10))
        tk.Button(btn_frame, text="상쇄점 추가", command=lambda: self.add("상쇄점")).pack(side='left', padx=(0, 10))
        tk.Button(btn_frame, text="입력 초기화", command=self.clear).pack(side='left', padx=(20, 0))

        # 검색 및 보기 옵션
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(control_frame, text="검색").pack(side='left')
        self.search = tk.Entry(control_frame, width=20)
        self.search.pack(side='left', padx=(5, 20))
        self.search.bind('<KeyRelease>', self.search_data)

        self.view_mode = tk.StringVar(value="summary")
        tk.Radiobutton(control_frame, text="학생별 요약", variable=self.view_mode, value="summary", command=self.load_data).pack(side='left', padx=(0, 10))
        tk.Radiobutton(control_frame, text="전체 기록", variable=self.view_mode, value="detail", command=self.load_data).pack(side='left', padx=(0, 10))
        tk.Button(control_frame, text="새로고침", command=self.load_data).pack(side='left', padx=(10, 0))

        # 테이블
        table_frame = tk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(table_frame, show='headings', height=15)
        
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.bind('<Double-1>', self.show_detail)
        
        self.setup_columns()
        self.load_data()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def setup_columns(self):
        if self.view_mode.get() == "summary":
            columns = ("학번", "이름", "상점", "벌점", "상쇄점", "총점", "최근활동")
            widths = (100, 80, 60, 60, 60, 70, 140)
        else:
            columns = ("학번", "이름", "유형", "사유", "점수", "일시")
            widths = (100, 80, 70, 220, 60, 140)
        
        self.tree.configure(columns=columns)
        
        for i, col in enumerate(columns):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[i], anchor='center' if col != "사유" else 'w')

    def add(self, point_type):
        try:
            sid = self.e1.get().strip()
            name = self.e2.get().strip()
            points = int(self.e3.get().strip())
            reason = self.e4.get().strip()
            
            if not all([sid, name, reason]) or points <= 0:
                messagebox.showerror("입력 오류", "모든 항목을 올바르게 입력하세요")
                return
            
            if point_type == "벌점":
                points = -points
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            self.cursor.execute('''
                INSERT INTO records (student_id, name, reason, points, point_type, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (sid, name, reason, points, point_type, timestamp))
            self.conn.commit()
            
            messagebox.showinfo("완료", f"{name} 학생 {point_type} {abs(points)}점이 추가되었습니다")
            self.clear()
            self.load_data()
            
        except ValueError:
            messagebox.showerror("입력 오류", "점수는 숫자로 입력하세요")
        except Exception as e:
            messagebox.showerror("오류", f"저장 중 오류가 발생했습니다: {e}")

    def clear(self):
        for e in [self.e1, self.e2, self.e3, self.e4]:
            e.delete(0, tk.END)

    def backup_data(self):
        try:
            os.makedirs('backups', exist_ok=True)
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = os.path.join('backups', backup_name)
            shutil.copy2('data.db', backup_path)
            return backup_path
        except Exception:
            return None

    def reset_data(self):
        result = messagebox.askyesno("데이터 초기화", 
                                   "정말로 모든 데이터를 초기화하시겠습니까?\n\n백업이 생성되고 모든 기록이 삭제됩니다.",
                                   icon='warning')
        
        if result:
            try:
                backup_path = self.backup_data()
                if backup_path:
                    self.cursor.execute('DELETE FROM records')
                    self.conn.commit()
                    self.load_data()
                    messagebox.showinfo("완료", f"데이터가 초기화되었습니다.\n백업: {backup_path}")
                else:
                    messagebox.showerror("오류", "백업 생성에 실패했습니다. 초기화를 중단합니다.")
            except Exception as e:
                messagebox.showerror("오류", f"초기화에 실패했습니다: {e}")

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.setup_columns()
        
        try:
            if self.view_mode.get() == "summary":
                self.cursor.execute('''
                    SELECT student_id, name,
                           SUM(CASE WHEN point_type = "상점" THEN points ELSE 0 END) as merit,
                           SUM(CASE WHEN point_type = "벌점" THEN ABS(points) ELSE 0 END) as demerit,
                           SUM(CASE WHEN point_type = "상쇄점" THEN points ELSE 0 END) as offset,
                           SUM(points) as total,
                           MAX(timestamp) as last_activity
                    FROM records 
                    GROUP BY student_id, name 
                    ORDER BY last_activity DESC
                ''')
                
                for row in self.cursor.fetchall():
                    total_display = f"+{row[5]}" if row[5] > 0 else str(row[5])
                    self.tree.insert('', 'end', values=(*row[:5], total_display, row[6]))
            else:
                self.cursor.execute('''
                    SELECT student_id, name, point_type, reason, points, timestamp 
                    FROM records ORDER BY timestamp DESC
                ''')
                
                for row in self.cursor.fetchall():
                    points_display = f"+{row[4]}" if row[4] > 0 else str(row[4])
                    self.tree.insert('', 'end', values=(*row[:4], points_display, row[5]))

        except Exception as e:
            messagebox.showerror("오류", f"데이터 로드에 실패했습니다: {e}")

    def search_data(self, event=None):
        term = self.search.get().strip().lower()
        if not term:
            self.load_data()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            if self.view_mode.get() == "summary":
                self.cursor.execute('''
                    SELECT student_id, name,
                           SUM(CASE WHEN point_type = "상점" THEN points ELSE 0 END) as merit,
                           SUM(CASE WHEN point_type = "벌점" THEN ABS(points) ELSE 0 END) as demerit,
                           SUM(CASE WHEN point_type = "상쇄점" THEN points ELSE 0 END) as offset,
                           SUM(points) as total,
                           MAX(timestamp) as last_activity
                    FROM records 
                    WHERE LOWER(student_id) LIKE ? OR LOWER(name) LIKE ?
                    GROUP BY student_id, name 
                    ORDER BY last_activity DESC
                ''', (f'%{term}%', f'%{term}%'))
                
                for row in self.cursor.fetchall():
                    total_display = f"+{row[5]}" if row[5] > 0 else str(row[5])
                    self.tree.insert('', 'end', values=(*row[:5], total_display, row[6]))
            else:
                self.cursor.execute('''
                    SELECT student_id, name, point_type, reason, points, timestamp 
                    FROM records 
                    WHERE LOWER(student_id) LIKE ? OR LOWER(name) LIKE ? OR LOWER(reason) LIKE ?
                    ORDER BY timestamp DESC
                ''', (f'%{term}%', f'%{term}%', f'%{term}%'))
                
                for row in self.cursor.fetchall():
                    points_display = f"+{row[4]}" if row[4] > 0 else str(row[4])
                    self.tree.insert('', 'end', values=(*row[:4], points_display, row[5]))

        except Exception as e:
            messagebox.showerror("오류", f"검색에 실패했습니다: {e}")

    def show_detail(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        if self.view_mode.get() == "summary" and len(values) >= 2:
            sid = values[0]
            name = values[1]
            
            detail_win = tk.Toplevel(self.root)
            detail_win.title(f"{name}({sid}) 상세 기록")
            detail_win.geometry("700x500")
            
            frame = tk.Frame(detail_win, padx=20, pady=20)
            frame.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(frame, text=f"{name} 학생 상세 기록", font=('맑은 고딕', 14, 'bold')).pack(pady=(0, 15))
            
            table_frame = tk.Frame(frame)
            table_frame.pack(fill=tk.BOTH, expand=True)
            
            detail_tree = ttk.Treeview(table_frame, show='headings', height=12)
            detail_tree.configure(columns=("일시", "유형", "점수", "사유"))
            
            for col, width in [("일시", 140), ("유형", 80), ("점수", 60), ("사유", 250)]:
                detail_tree.heading(col, text=col)
                detail_tree.column(col, width=width, anchor='center' if col != "사유" else 'w')
            
            detail_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=detail_tree.yview)
            detail_tree.configure(yscrollcommand=detail_scrollbar.set)
            
            detail_tree.pack(side='left', fill=tk.BOTH, expand=True)
            detail_scrollbar.pack(side='right', fill='y')
            
            self.cursor.execute("SELECT timestamp, point_type, points, reason FROM records WHERE student_id=? ORDER BY timestamp DESC", (sid,))
            
            for row in self.cursor.fetchall():
                points_display = f"+{row[2]}" if row[2] > 0 else str(row[2])
                detail_tree.insert('', 'end', values=(row[0], row[1], points_display, row[3]))

    def logout(self):
        self.root.destroy()
        self.login()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        try:
            self.conn.close()
        except:
            pass
        self.root.quit()

if __name__ == "__main__":
    App()