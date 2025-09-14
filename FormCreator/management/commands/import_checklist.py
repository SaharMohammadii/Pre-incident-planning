from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from FormCreator.models import FormTemplate, SectionTemplate, ItemTemplate


checklist = {
    "sections": [
        {
            "title": "1. پلکان‌ها",
            "items": [
                "مجزاسازی باکس پله در طبقات",
                "رعایت فضای فیلتر با متراژ مناسب (S=N+3)",
                "اجرای پله دوم اصولی از همکف تا پشت بام با دسترسی مناسب از فضای عمومی تمام سوئیت‌ها و واحدها",
                "عدم اجرای هر گونه کاربری در فضای فیلتر و پله",
                "نصب تابلوهای راهنمای طبقات و علائم خروج اضطراری",
                "حذف پله خورشیدی در هر طبقه (عدد ...)",
                "جداسازی کاربری (انباری/مسکونی/تجاری/اقامتی)",
                "اجرای دودبند در کلیه طبقات و همکف",
                "اجرای خروجی دوم زیرزمین به طور مجزا و دور از خروجی اول",
                "اجرای پله دوار مطابق بند 3-4-6-3 مبحث سوم مقررات ملی ساختمان (مطابق صفحات 91 تا 95)"
            ]
        },
        {
            "title": "2. نرده و حفاظ‌ها",
            "items": [
                "حفاظ پله",
                "حفاظ پله دوبلکس",
                "حفاظ پله روی بام منتهی به خرپشته",
                "حفاظ پله نیم‌طبقه",
                "جان‌پناه نورگیر (داکت) پشت بام و نصب فنس فلزی",
                "جان‌پناه تراس‌ها و نرده‌های سنگی",
                "جان‌پناه بالکن‌ها",
                "جان‌پناه پشت پنجره‌ها",
                "جان‌پناه نمای شیشه‌ای",
                "جان‌پناه‌ها (دیوارها و سکوها) و حفره‌های پشت بام",
                "جان‌پناه جنب رمپ",
                "جان‌پناه محوطه",
                "جان‌پناه خرپشته (ارتفاع حداقل 110cm با فاصله 11cm)"
            ]
        },
        {
            "title": "3. حفاظ شیشه‌ای",
            "items": [
                "در صورت نصب شیشه نشکن و نریز، لازم است مدارک و استانداردهای آن توسط مهندس ناظر یا مجری ارائه شود (نامه تایید و فاکتور تولید کننده)"
            ]
        },
        {
            "title": "4. درب‌های خروج",
            "items": [
                "درب‌ها از نوع مقاوم در برابر حریق و دارای پلاک شناسه فلزی استاندارد",
                "درب‌ها از نوع چوبی دولایه حداقل",
                "درب‌ها بدون قفل",
                "نصب آرام‌بند پشت درب",
                "جهت بازشو به سمت خروج به طوری که مسیر خروج مسدود نشود (مطابق مرکز تحقیقات مسکن و شهرسازی)"
            ]
        },
        {
            "title": "5. خاموش‌کننده‌ها",
            "items": [
                "نصب در هر واحد مسکونی",
                "نصب در اتاقک موتورخانه آسانسور",
                "نصب در مغازه‌ها و واحدهای تجاری",
                "نصب در پارکینگ (حداقل دو عدد)",
                "نصب در راهروها"
            ]
        },
        {
            "title": "6. سیستم آب آتش‌نشانی",
            "subsections": {
                "6.1 منبع": [
                    "اجرای اتاقک با مصالح بنایی",
                    "عایق‌بندی در برابر یخ‌زدگی و ترکیدگی",
                    "اجرای محفظه مناسب جهت محافظت در برابر یخ‌زدگی و ترکیدگی",
                    "آماده به کار بودن سیستم‌های آتش‌نشانی"
                ],
                "6.2 پمپ": [
                    "نصب الکتروپمپ اتومات با تأمین فشار 4.5 تا 6 بار و دبی حداقل Q=120 L/MIN",
                    "Q=200 L/MIN",
                    "Q=450 L/MIN"
                ]
            }
        },
        {
            "title": "7. لوله‌های آتش‌نشان",
            "subsections": {
                "7.1 سیستم تر": [
                    "سایز لوله‌ها با قطر تأیید شده",
                    "عایق‌بندی در برابر یخ‌زدگی و ترکیدگی"
                ],
                "7.2 سیستم خشک": [
                    "دو عدد شیر سیامی و دو عدد شیر یک‌طرفه 1¼ اینچ با کوپلر استاندارد جهت اتصال خودرو آتش‌نشانی",
                    "نصب شیر ایرونت در بالاترین نقطه رایزر خشک",
                    "نصب شیر تخلیه در پایین‌ترین قسمت رایزر",
                    "نصب شلنگ نواری (برزنتی یا پرولون) با نازل استاندارد"
                ],
                "7.3 جعبه‌های آتش‌نشانی": [
                    "نصب جعبه در محل مناسب با فنر بدون تاخوردگی",
                    "نصب جعبه دوقلو (خشک و تر)",
                    "درج برچسب نحوه استفاده روی جعبه‌ها",
                    "ارتفاع شیر جعبه هوزریل تا کف طبقه 180 سانتی‌متر"
                ]
            }
        },
        {
            "title": "8. اسپرینکلر",
            "items": [
                "فاصله نازل‌ها از یکدیگر و از دیوارها",
                "اجرای اسپرینکلر در کل بنا",
                "اجرای اسپرینکلر در پارکینگ",
                "اجرای اسپرینکلر در انبارهای بزرگ‌تر از 2.5 متر مربع"
            ]
        },
        {
            "title": "9. سیستم فشار مثبت",
            "items": [
                "اجرای سیستم فشار مثبت در پله‌ها با ظرفیت مناسب",
                "اتصال سیستم فشار مثبت به سیستم اعلام حریق"
            ]
        },
        {
            "title": "10. اعلام حریق اتومات",
            "items": [
                "نصب اعلام حریق اتومات در کل ساختمان",
                "استفاده از کابل مقاوم در برابر حریق",
                "نصب ریموت اندیکاتور سر درب واحدها یا فضاهای محصور",
                "نصب شستی اعلام حریق در مسیر خروج",
                "نصب راهنمای دستورالعمل اعلام حریق",
                "نصب پنل اعلام حریق در نگهبانی یا لابی",
                "آماده به کار بودن سیستم (آدرس‌پذیر در ساختمان‌های مسکونی بالای 10000 متر مربع و سقف 10+؛ متعارف در سایر)",
                "فاصله دتکتور دود: 10 متر بین دتکتورها، 5 متر از موانع",
                "نصب دتکتور حرارتی ثابت در آشپزخانه، موتورخانه، تاسیسات (7 متر بین دتکتورها، 3.5 متر از موانع)",
                "نصب دتکتور حرارتی افزایشی در پارکینگ، لاندری"
            ]
        },
        {
            "title": "11. نشت‌یاب گاز",
            "items": [
                "نصب نشت‌یاب گاز در آشپزخانه",
                "نصب نشت‌یاب گاز در اتاق تاسیسات",
                "نصب نشت‌یاب گاز در اتاقک پکیج"
            ]
        },
        {
            "title": "12. روشنایی اضطراری",
            "items": [
                "نصب در مسیر خروج",
                "نصب در زیرزمین",
                "اتصال به برق اصلی با پریز",
                "تعبیه فرش عایق برای تابلوهای برق",
                "نصب ژنراتور برق در محل مجزا",
                "حداکثر حجم مخزن گازوئیل 240 لیتر جهت مصرف روزانه",
                "انتقال منابع گازوئیل به خارج از توده ساختمان"
            ]
        },
        {
            "title": "13. ژنراتور",
            "items": [
                "تعبیه فرش عایق برای تابلوهای برق",
                "نصب ژنراتور برق در محل مناسب و مجزا",
                "حداکثر حجم مخزن گازوئیل 240 لیتر جهت مصرف روزانه",
                "انتقال منابع گازوئیل خارج از توده ساختمان (گروه D)",
                "ضابطه بالابر رعایت یا جمع‌آوری",
                "نصب آسانسور آتش‌نشانی مطابق مبحث 15"
            ]
        },
        {
            "title": "14. پوشش مقاوم حریق",
            "items": [
                "اعمال پوشش مقاوم حرارتی مطابق مقررات"
            ]
        },
        {
            "title": "15. نما",
            "items": [
                "استفاده از مصالح نما مقاوم در برابر حریق مطابق مقررات"
            ]
        },
        {
            "title": "16. سیستم مدیریت دود",
            "items": [
                "اجرای سیستم مدیریت دود",
                "مستقل‌سازی پله و فضای فیلتر آب آتش‌نشانی طبقات",
                "درب‌های مقاوم حریق",
                "خروجی‌های مستقل",
                "خاموش‌کننده‌ها",
                "سیستم آب آتش‌نشانی",
                "رایزر خشک",
                "اسپرینکلر زیرزمین، همکف، طبقات",
                "فشار مثبت پله‌ها",
                "اعلام حریق اتومات",
                "نشت‌یاب گاز",
                "روشنایی اضطراری",
                "دیزل ژنراتور",
                "اعلام حریق موضعی",
                "اعلام حریق آدرس‌پذیر"
            ]
        },
        {
            "title": "17. وضعیت موجود",
            "items": [
                "مستقل‌سازی پله و فضای فیلتر آب آتش‌نشانی طبقات",
                "درب‌های مقاوم حریق",
                "خروجی‌های مستقل",
                "خاموش‌کننده‌ها",
                "سیستم آب آتش‌نشانی",
                "رایزر خشک",
                "اسپرینکلر زیرزمین، همکف، طبقات",
                "فشار مثبت پله‌ها",
                "اعلام حریق اتومات",
                "نشت‌یاب گاز",
                "روشنایی اضطراری",
                "دیزل ژنراتور",
                "اعلام حریق موضعی",
                "اعلام حریق آدرس‌پذیر"
            ]
        }
    ]
}


class Command(BaseCommand):
    help = "Import a raw checklist tree into FormTemplate/SectionTemplate/ItemTemplate."

    def add_arguments(self, parser):
        parser.add_argument("--name", default="Safety Checklist", help="Template name")
        parser.add_argument("--type", default="STANDARD", choices=["STANDARD", "ECO"], help="Template type")
        parser.add_argument("--template-version", type=int, default=1, help="Template version")  # renamed here
        parser.add_argument("--activate", action="store_true", help="Mark this template version as active")
        parser.add_argument("--replace", action="store_true",
                            help="If a template with the same (name,version) exists, delete its sections and re-import")
    
    def _create_section(self, form, title, order, parent=None):
        return SectionTemplate.objects.create(form=form, parent=parent, title=title, order=order)

    def _create_item(self, section, body, order, extra_description="", required=False):
        return ItemTemplate.objects.create(
            section=section, body=body, extra_description=extra_description, required=required, order=order
        )

    def _import_section_node(self, form, node: dict, order: int, parent=None):
        """
        node shape:
          { "title": str, "items": [str|{body, extra_description, required}], "subsections": {title: [items] or dict} }
        """
        title = node.get("title") or f"Section {order}"
        sec = self._create_section(form, title=title, order=order, parent=parent)

        # Items (list of strings or dicts)
        for idx, itm in enumerate(node.get("items", []), start=1):
            if isinstance(itm, str):
                self._create_item(sec, body=itm, order=idx)
            elif isinstance(itm, dict):
                self._create_item(
                    sec,
                    body=itm.get("body", ""),
                    order=idx,
                    extra_description=itm.get("extra_description", "") or "",
                    required=bool(itm.get("required", False)),
                )

        # Subsections (dict preserves insertion order in Py3.7+)
        subs = node.get("subsections", {})
        if isinstance(subs, dict):
            sub_order = 1
            for sub_title, sub_payload in subs.items():
                # normalize subsection into a standard node
                if isinstance(sub_payload, list):
                    sub_node = {"title": sub_title, "items": sub_payload}
                elif isinstance(sub_payload, dict):
                    sub_node = {"title": sub_title, **sub_payload}
                else:
                    continue
                self._import_section_node(form, sub_node, order=sub_order, parent=sec)
                sub_order += 1

        return sec

    @transaction.atomic
    def handle(self, *args, **opts):
        name = opts["name"]
        type_ = opts["type"]
        version = opts["template_version"]
        activate = opts["activate"]
        replace = opts["replace"]

        tpl, created = FormTemplate.objects.get_or_create(
            name=name, version=version, defaults={"type": type_, "is_active": activate}
        )

        if not created:
            # Same (name,version) already exists
            if replace:
                # wipe its sections and re-import
                SectionTemplate.objects.filter(form=tpl).delete()
                self.stdout.write(self.style.WARNING(f"Re-importing into existing template: {tpl}"))
            else:
                raise CommandError(
                    f"A template with name='{name}' and version={version} already exists. "
                    f"Use --replace to overwrite its sections."
                )
        else:
            # If created but type differs from default, update
            if tpl.type != type_:
                tpl.type = type_
            if activate:
                tpl.is_active = True
            tpl.save()

        # Import root sections
        count_sections = 0
        count_items = 0

        for idx, sec_node in enumerate(checklist.get("sections", []), start=1):
            root = self._import_section_node(tpl, sec_node, order=idx, parent=None)
            count_sections += 1

            # Count items under this root (roughly)
            def _count(sec):
                nonlocal count_sections, count_items
                count_items += sec.items.count()
                for ch in sec.children.all():
                    count_sections += 1
                    _count(ch)

            _count(root)

        if activate and not tpl.is_active:
            tpl.is_active = True
            tpl.save()

        self.stdout.write(self.style.SUCCESS(
            f"✔ Imported template '{tpl.name}' v{tpl.version} ({tpl.type}). "
            f"Sections: {SectionTemplate.objects.filter(form=tpl).count()}, "
            f"Items: {ItemTemplate.objects.filter(section__form=tpl).count()}."
        ))