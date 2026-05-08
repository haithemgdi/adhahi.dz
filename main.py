import customtkinter as ctk
from tkinter import messagebox
import requests
from PIL import Image
import io
import base64

# إعدادات المظهر العام
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AdhahiProApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # إعدادات النافذة الرئيسية
        self.title("Adhahi DZ - Professional Registration Tool")
        self.geometry("500x800")
        
        # إدارة الجلسة والبيانات
        self.session = requests.Session()
        self.captcha_id = ""

        # --- العنوان الرئيسي ---
        self.header_label = ctk.CTkLabel(self, text="نظام التسجيل - أضحي", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack(pady=(20, 10))

        # --- حاوية الحقول (قابلة للتمرير) ---
        self.form_frame = ctk.CTkScrollableFrame(self, width=460, height=450)
        self.form_frame.pack(pady=5, padx=20, fill="both", expand=True)

        self.fields = {}
        # قائمة الحقول المطلوبة مع القيم الافتراضية
        input_data = [
            ("Wilaya ID", "wilayaId", "10"),
            ("Commune Code", "communeCode", "1038"),
            ("NIN (National ID)", "nin", "100000352003170001"),
            ("Card Number (CNIBE)", "cnibe", "412477591"),
            ("Phone Number", "phoneNumber", "0782884708"),
            ("Email Address", "email", "haithemdon62@gmail.com"),
            ("Password", "password", "Haithem2015+")
        ]

        for label_text, key, default in input_data:
            self.create_input_field(label_text, key, default)

        # --- حاوية الكابتشا والزر (ثابتة في الأسفل) ---
        self.bottom_sticky_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_sticky_frame.pack(side="bottom", fill="x", pady=20, padx=20)

        # عرض صورة الكابتشا
        self.captcha_img_label = ctk.CTkLabel(self.bottom_sticky_frame, text="صورة التحقق ستظهر هنا", text_color="gray")
        self.captcha_img_label.pack(pady=5)

        # أزرار التحكم في الكابتشا
        self.captcha_entry_row = ctk.CTkFrame(self.bottom_sticky_frame, fg_color="transparent")
        self.captcha_entry_row.pack(fill="x", pady=5)

        self.btn_refresh = ctk.CTkButton(self.captcha_entry_row, text="تحديث ↻", width=100,
                                          command=self.get_captcha, fg_color="#3498db", hover_color="#2980b9")
        self.btn_refresh.pack(side="left", padx=(0, 10))

        self.ent_captcha = ctk.CTkEntry(self.captcha_entry_row, placeholder_text="أدخل رمز التحقق", height=40)
        self.ent_captcha.pack(side="left", fill="x", expand=True)

        # زر الإرسال النهائي
        self.btn_submit = ctk.CTkButton(self.bottom_sticky_frame, text="إتمام عملية التسجيل الآن", 
                                         command=self.submit_registration,
                                         height=50, font=ctk.CTkFont(size=18, weight="bold"),
                                         fg_color="#2ecc71", hover_color="#27ae60")
        self.btn_submit.pack(pady=(15, 0), fill="x")

    def create_input_field(self, label_text, key, default_value):
        """دالة مساعدة لإنشاء الحقول بتنسيق احترافي"""
        frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        frame.pack(pady=8, padx=10, fill="x")
        
        label = ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=13, weight="bold"))
        label.pack(side="top", anchor="w", padx=5)
        
        entry = ctk.CTkEntry(frame, height=38, placeholder_text=f"Enter {label_text}...")
        entry.insert(0, default_value)
        entry.pack(side="top", fill="x", padx=5, pady=2)
        
        if key == "password":
            entry.configure(show="*")
            
        self.fields[key] = entry

    def get_captcha(self):
        """جلب الكابتشا مع Headers كاملة لتفادي الحظر"""
        url = "https://adhahi.dz/api/v1/captcha/generate"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://adhahi.dz/register",
            "Origin": "https://adhahi.dz"
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                self.captcha_id = data['captchaId']
                img_b64 = data['captchaImage'].split(",")[1]
                
                img_data = base64.b64decode(img_b64)
                img_raw = Image.open(io.BytesIO(img_data))
                
                # تحويل الصورة لتناسب واجهة CTK
                img_ctk = ctk.CTkImage(light_image=img_raw, dark_image=img_raw, size=(180, 60))
                
                self.captcha_img_label.configure(image=img_ctk, text="")
                self.ent_captcha.delete(0, 'end')
            else:
                messagebox.showerror("خطأ", f"فشل السيرفر: {response.status_code}")
        except Exception as e:
            messagebox.showerror("خطأ في الاتصال", f"لا يمكن الوصول للسيرفر:\n{e}")

    def submit_registration(self):
        """إرسال بيانات التسجيل النهائية"""
        if not self.captcha_id:
            messagebox.showwarning("تنبيه", "يرجى تحديث الكابتشا أولاً!")
            return

        captcha_answer = self.ent_captcha.get().strip()
        if not captcha_answer:
            messagebox.showwarning("تنبيه", "يرجى إدخال رمز التحقق!")
            return

        url = "https://adhahi.dz/api/v2/citizens/register"
        
        # تجميع البيانات من المدخلات
        payload = {k: v.get() for k, v in self.fields.items()}
        
        # تعديل أنواع البيانات لتناسب API
        payload["wilayaId"] = int(payload["wilayaId"])
        payload["categoryId"] = 1
        payload["paymentMethod"] = "TPE"

        headers = {
            "Content-Type": "application/json",
            "X-Captcha-Id": self.captcha_id,
            "X-Captcha-Answer": captcha_answer,
            "Referer": "https://adhahi.dz/register",
            "Origin": "https://adhahi.dz",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=20)
            
            if response.status_code in [200, 201]:
                messagebox.showinfo("نجاح", "تمت عملية التسجيل بنجاح!")
            else:
                # محاولة قراءة رسالة الخطأ من السيرفر إن وجدت
                error_msg = response.text
                messagebox.showwarning("فشل التسجيل", f"رد السيرفر ({response.status_code}):\n{error_msg}")
                
        except Exception as e:
            messagebox.showerror("خطأ فادح", f"فشل إرسال الطلب:\n{e}")

if __name__ == "__main__":
    app = AdhahiProApp()
    app.mainloop()
