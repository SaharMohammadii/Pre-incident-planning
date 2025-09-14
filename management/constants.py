


### WARNINGS

WARNING_LEVEL_1 = "نرمال, پتانسیل خطر کم و قابل پذیرش"
WARNING_LEVEL_2 = "متوسط, پتانسیل خطر متوسط و قابل پذیرش"
WARNING_LEVEL_3 = "بالا, پتانسیل خطر بالا و غیرقابل پذیرش"




### SAFETY LEVEL AND OWNER FUNCTIONALITIES

SAFETY_LEVEL_4 = "اجرا و نصب خاموش کننده دستی, نشت‌یاب گاز, اجرا و اصلاح حفاظ ها و داکت‌ها و سیم‌کشی و کلیه موارد عمومی"
SAFETY_LEVEL_3 = "اجرا سیستم اعلام حریق اتومات, علاوه بر موارد سطح ۴"
SAFETY_LEVEL_2 = "اجرای سیستم اطفاء حریق آبی و اجرای شبکه بازنده کل بنا, علاوه بر سطح ۳"
SAFETY_LEVEL_1 = "تمامی موارد ایمنی از جمله خروج دوم, مستقل سازی پلکان و موارد سطوح قبلی در آن لازم الاجرا است"


WARNINGS = [
    (WARNING_LEVEL_1, WARNING_LEVEL_1),
    (WARNING_LEVEL_2, WARNING_LEVEL_2),
    (WARNING_LEVEL_3, WARNING_LEVEL_3),
]


SAFETY_LEVELS = [
    (SAFETY_LEVEL_4, SAFETY_LEVEL_4),
    (SAFETY_LEVEL_3, SAFETY_LEVEL_3),
    (SAFETY_LEVEL_2, SAFETY_LEVEL_2),
    (SAFETY_LEVEL_1, SAFETY_LEVEL_1),
]


INSPECTION_STATUS = [
    ("done", "انجام شده"),
    ('pending', "در دست انجام"),
]