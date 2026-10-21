"""More > Backup: create, export, restore (merge / replace)."""
import os
from datetime import datetime

import flet as ft

import json

from .. import backup, export, paths
from ..history import Histories
from . import kit, theme as T
from .rows import empty_state, page_frame, small_btn


def _restore_dialog(ui, path, name):
    def run(mode):
        ui.page.close(dlg)
        res = ui.guard(backup.restore_file, ui.repo, path, mode)
        if res is not None:
            ui.toast("تم الاسترجاع")
            ui.refresh()

    def as_history(e):
        ui.page.close(dlg)

        def run():
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, ValueError):
                raise backup.AppError("ما كدرت أقرأ ملف النسخة الاحتياطية")
            hs = Histories(paths.history_dir())
            meta = hs.create()
            arch = hs.open(meta["id"])
            try:
                backup._import_tables(arch, data, "replace")
            except Exception:
                arch.conn.close()
                hs.delete(meta["id"])
                raise
            arch.conn.close()
            return meta["name"]
        name = ui.guard(run)
        if name:
            ui.toast(f"انحفظت كـ «{name}» بدون أي تأثير على التطبيق")
            ui.more_page = "history"
            ui.refresh()

    def replace(e):
        ui.page.close(dlg)
        kit.confirm(ui.page, "استبدال كل البيانات؟", "كل بياناتك الحالية تنحذف وتنستبدل بمحتوى النسخة. (تُحفظ نسخة أمان قبلها)",
                    lambda: (backup.create_backup(ui.repo, paths.backup_dir(), keep=5, prefix="pre-restore"), run("replace")),
                    yes_label="استبدال")

    def opt(title, hint, fn, outline=True, color=None):
        return kit.col([kit.big_button(title, fn, outline=outline, **({"bg": color} if color else {})),
                        kit.txt(hint, 12, color=T.MUTED)], spacing=4)

    dlg = ft.AlertDialog(
        title=ft.Text("استرجاع: " + name),
        content=ft.Container(kit.col([
            opt("هستوري معزول (الأنسب للبيانات القديمة)",
                "يحفظها كأرشيف له فئاته ومحافظه وأشخاصه الخاصة، ولا يختلط بشي من التطبيق. للعرض والإحصائيات فقط.",
                as_history, outline=False),
            opt("دمج مع بياناتي", "يضيف الناقص لتطبيقك، والفئات تندمج مع فئاتك بنفس الاسم.", lambda e: run("merge")),
            opt("استبدال كل شي", "يمسح بياناتك الحالية ويرجع النسخة كاملة (مع الهستوري المحفوظ فيها).", replace, outline=False, color=T.EXPENSE)],
            spacing=12, scroll=True), width=320),
        actions=[ft.TextButton("إلغاء", on_click=lambda e: ui.page.close(dlg))])
    ui.page.open(dlg)


def build_backup(ui):
    repo, folder = ui.repo, paths.backup_dir()

    def now(e):
        p = ui.guard(backup.create_backup, repo, folder, 7)
        if p:
            export.mirror_backup(p)
            ui.toast("تم إنشاء النسخة")
            ui.refresh()

    def export(e):
        data = json.dumps(backup.export_full(repo), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        kit.save_bytes(ui, f"masarif-{datetime.now():%Y%m%d-%H%M}.json", data, ["json"], "تصدير نسخة احتياطية", "تم تصدير النسخة")

    def from_file(e):
        kit.pick_file(ui, lambda p: _restore_dialog(ui, p, os.path.basename(p)), ["json"], "اختر ملف نسخة احتياطية")

    rows = []
    for b in backup.list_backups(folder):
        when = datetime.fromtimestamp(b["mtime"]).strftime("%Y-%m-%d %H:%M")
        rows.append(kit.box(kit.between(kit.col([kit.txt(b["name"], 13, True), kit.txt(f"{when} · {b['size'] // 1024 + 1} KB", 12, color=T.MUTED)], spacing=2),
                                        small_btn("restore", lambda e, b=b: _restore_dialog(ui, b["path"], b["name"]), "استرجاع", T.PRIMARY))))
    return page_frame(ui, "النسخ الاحتياطي", [
        kit.row([ft.Container(kit.big_button("نسخة الآن", now), expand=True),
                 ft.Container(kit.big_button("تصدير لملف", export, outline=True), expand=True)], spacing=10),
        kit.big_button("استرجاع من ملف", from_file, outline=True),
        kit.txt("النسخ التلقائية محفوظة داخل التطبيق:", 12, color=T.MUTED), kit.txt(folder, 11, color=T.FAINT, selectable=True),
        *(rows or [empty_state("ما في نسخ بعد")]),
    ])
