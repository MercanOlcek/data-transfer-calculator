"""Terminal UI app for transfer time calculation and IP tracking (curses)."""

from __future__ import annotations

import curses
from dataclasses import dataclass, field
from datetime import datetime

from get_ip import get_local_ip, get_public_ip_info
from trans import aktarim_suresi


@dataclass
class AppState:
    mode: str = "menu"  # menu, calc_tb, calc_speed, result
    input_buffer: str = ""
    pending_tb: float | None = None
    calc_result: str = ""
    status_message: str = "Hazır"
    local_ip: str = "Unavailable"
    public_info: dict = field(default_factory=dict)
    history: list[str] = field(default_factory=list)


def format_duration(veri_tb: float, hiz_mbit: float) -> str:
    gun, saat, dakika, saniye = aktarim_suresi(veri_tb, hiz_mbit)
    return f"{gun} gün, {saat} saat, {dakika} dakika, {saniye} saniye"


def refresh_ip(state: AppState) -> None:
    state.local_ip = get_local_ip()
    state.public_info = get_public_ip_info()
    ts = datetime.now().strftime("%H:%M:%S")
    public_ip = state.public_info.get("public_ip", "Unavailable")
    status = state.public_info.get("status", "error")
    entry = f"[{ts}] local={state.local_ip} public={public_ip} ({status})"
    state.history.insert(0, entry)
    state.history = state.history[:8]
    if status == "success":
        state.status_message = "IP bilgileri güncellendi."
    else:
        msg = state.public_info.get("message") or "Bilinmeyen hata"
        state.status_message = f"IP takibi güncellendi (hata: {msg})."


def clipped(text: str, width: int) -> str:
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    if width <= 1:
        return text[:width]
    return text[: width - 1] + "…"


def safe_addstr(stdscr, y: int, x: int, text: str, attr: int = 0) -> None:
    h, w = stdscr.getmaxyx()
    if y < 0 or y >= h or x < 0 or x >= w:
        return
    max_len = w - x
    if max_len <= 0:
        return
    try:
        stdscr.addnstr(y, x, text, max_len, attr)
    except curses.error:
        pass


def draw_box(stdscr, y: int, x: int, w: int, h: int, title: str = "", attr: int = 0) -> None:
    max_h, max_w = stdscr.getmaxyx()
    if w < 4 or h < 3:
        return
    if y >= max_h or x >= max_w:
        return
    # Clamp
    w = min(w, max_w - x)
    h = min(h, max_h - y)
    if w < 4 or h < 3:
        return

    top = "┌" + ("─" * (w - 2)) + "┐"
    bottom = "└" + ("─" * (w - 2)) + "┘"
    safe_addstr(stdscr, y, x, top, attr)
    for i in range(1, h - 1):
        safe_addstr(stdscr, y + i, x, "│" + (" " * (w - 2)) + "│", attr)
    safe_addstr(stdscr, y + h - 1, x, bottom, attr)
    if title:
        label = f" {title} "
        label_x = x + 2
        if label_x + len(label) < x + w - 1:
            safe_addstr(stdscr, y, label_x, label, attr | curses.A_BOLD)


def init_colors() -> dict[str, int]:
    colors = {
        "default": curses.A_NORMAL,
        "title": curses.A_BOLD,
        "box": curses.A_NORMAL,
        "status": curses.A_REVERSE,
        "help": curses.A_REVERSE,
        "bold": curses.A_BOLD,
    }
    if curses.has_colors():
        try:
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_GREEN, -1)
            curses.init_pair(3, curses.COLOR_WHITE, -1)
            curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)
            curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)
            colors["box"] = curses.color_pair(1)
            colors["title"] = curses.color_pair(2) | curses.A_BOLD
            colors["text"] = curses.color_pair(3)
            colors["status"] = curses.color_pair(5) | curses.A_BOLD
            colors["help"] = curses.color_pair(4) | curses.A_BOLD
            colors["bold"] = curses.color_pair(3) | curses.A_BOLD
        except curses.error:
            colors["text"] = curses.A_NORMAL
    else:
        colors["text"] = curses.A_NORMAL
    return colors


def render(stdscr, state: AppState, colors: dict[str, int]) -> None:
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    width = max(40, width)
    height = max(16, height)

    note = "This app tool developed by Mercan Ölçek"
    subtitle = "Data Transfer Time Calculator"
    safe_addstr(
        stdscr,
        0,
        max(0, (width - len(clipped(note, width - 1))) // 2),
        clipped(note, width - 1),
        colors["title"],
    )
    safe_addstr(
        stdscr,
        1,
        max(0, (width - len(clipped(subtitle, width - 1))) // 2),
        clipped(subtitle, width - 1),
        colors.get("text", 0),
    )

    # IP panel
    ip_w = min(width - 4, 90)
    ip_h = 10
    ip_x = max(2, (width - ip_w) // 2)
    ip_y = 3
    draw_box(stdscr, ip_y, ip_x, ip_w, ip_h, "IP Tracker", colors["box"])
    info = state.public_info or {}
    lines = [
        f"Yerel IP : {state.local_ip}",
        f"Genel IP : {info.get('public_ip', 'Bilinmiyor')}",
        f"Konum    : {info.get('city', '-')}, {info.get('region', '-')} / {info.get('country', '-')}",
        f"ISP      : {info.get('isp', '-')}",
        f"Saat Dil.: {info.get('timezone', '-')}",
        f"Son Kont.: {info.get('checked_at', '-')}",
    ]
    if info.get("status") == "error" and info.get("message"):
        lines.append(f"Durum    : Hata - {info.get('message')}")
    else:
        lines.append(f"Durum    : {info.get('status', 'bilinmiyor')}")
    for i, line in enumerate(lines[: ip_h - 2]):
        safe_addstr(stdscr, ip_y + 1 + i, ip_x + 2, clipped(line, ip_w - 4), colors.get("text", 0))

    # Calculator panel
    main_w = min(width - 4, 90)
    main_h = 8
    main_x = max(2, (width - main_w) // 2)
    main_y = ip_y + ip_h + 1
    draw_box(stdscr, main_y, main_x, main_w, main_h, "Veri Aktarım Hesaplayıcı", colors["box"])
    row = main_y + 1
    inner_w = main_w - 4
    text_attr = colors.get("text", 0)
    bold_attr = colors.get("bold", curses.A_BOLD)

    if state.mode == "menu":
        safe_addstr(stdscr, row, main_x + 2, clipped("Hesaplama için 'c' tuşuna basın.", inner_w), text_attr)
        safe_addstr(stdscr, row + 1, main_x + 2, clipped("IP bilgilerini yenilemek için 'r' tuşuna basın.", inner_w), text_attr)
        safe_addstr(stdscr, row + 2, main_x + 2, clipped("Çıkmak için 'q' tuşuna basın.", inner_w), text_attr)
        if state.calc_result:
            safe_addstr(stdscr, row + 4, main_x + 2, clipped(f"Son sonuç: {state.calc_result}", inner_w), bold_attr)
    elif state.mode == "calc_tb":
        prompt = f"Veri miktarı (TB): {state.input_buffer}"
        safe_addstr(stdscr, row, main_x + 2, clipped(prompt, inner_w), bold_attr)
        safe_addstr(stdscr, row + 2, main_x + 2, clipped("Sayı girin, Enter ile onaylayın, Esc ile iptal.", inner_w), text_attr)
    elif state.mode == "calc_speed":
        safe_addstr(stdscr, row, main_x + 2, clipped(f"Veri miktarı: {state.pending_tb} TB", inner_w), text_attr)
        prompt = f"İnternet hızı (Mbit/s): {state.input_buffer}"
        safe_addstr(stdscr, row + 1, main_x + 2, clipped(prompt, inner_w), bold_attr)
        safe_addstr(stdscr, row + 3, main_x + 2, clipped("Sayı girin, Enter ile hesapla, Esc ile iptal.", inner_w), text_attr)
    elif state.mode == "result":
        safe_addstr(stdscr, row, main_x + 2, clipped("Tahmini aktarım süresi:", inner_w), bold_attr)
        safe_addstr(stdscr, row + 1, main_x + 2, clipped(state.calc_result, inner_w), text_attr)
        safe_addstr(stdscr, row + 3, main_x + 2, clipped("Menüye dönmek için herhangi bir tuşa basın.", inner_w), text_attr)

    # History panel
    hist_w = min(width - 4, 90)
    hist_h = max(5, min(10, height - (main_y + main_h + 4)))
    hist_x = max(2, (width - hist_w) // 2)
    hist_y = main_y + main_h + 1
    if hist_y + hist_h <= height - 2:
        draw_box(stdscr, hist_y, hist_x, hist_w, hist_h, "IP Takip Geçmişi", colors["box"])
        if not state.history:
            safe_addstr(stdscr, hist_y + 1, hist_x + 2, clipped("Henüz kayıt yok.", hist_w - 4), text_attr)
        else:
            for i, entry in enumerate(state.history[: hist_h - 2]):
                safe_addstr(stdscr, hist_y + 1 + i, hist_x + 2, clipped(entry, hist_w - 4), text_attr)

    # Status/help bars
    status_y = height - 2
    help_y = height - 1
    if status_y >= 0:
        status_line = clipped(f" Durum: {state.status_message}", width - 1)
        safe_addstr(stdscr, status_y, 0, status_line.ljust(max(0, width - 1)), colors["status"])
    if help_y >= 0:
        help_line = clipped(" [C] Hesapla  [R] IP Yenile  [Q] Çıkış  |  This app tool developed by Mercan Ölçek", width - 1)
        safe_addstr(stdscr, help_y, 0, help_line.ljust(max(0, width - 1)), colors["help"])

    # Cursor for input
    if state.mode == "calc_tb":
        cursor_x = min(main_x + 2 + len("Veri miktarı (TB): ") + len(state.input_buffer), main_x + main_w - 2)
        cursor_y = main_y + 1
        try:
            curses.curs_set(1)
            stdscr.move(cursor_y, cursor_x)
        except curses.error:
            pass
    elif state.mode == "calc_speed":
        cursor_x = min(main_x + 2 + len("İnternet hızı (Mbit/s): ") + len(state.input_buffer), main_x + main_w - 2)
        cursor_y = main_y + 2
        try:
            curses.curs_set(1)
            stdscr.move(cursor_y, cursor_x)
        except curses.error:
            pass
    else:
        try:
            curses.curs_set(0)
        except curses.error:
            pass

    stdscr.noutrefresh()
    curses.doupdate()


def parse_positive_float(text: str) -> float | None:
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    if value <= 0:
        return None
    return value


def handle_input_char(state: AppState, ch: int) -> bool:
    if 48 <= ch <= 57:  # digits
        char = chr(ch)
        if len(state.input_buffer) < 24:
            state.input_buffer += char
            return True
    elif ch in (ord('.'), ord(',')):
        if '.' not in state.input_buffer and len(state.input_buffer) < 24:
            state.input_buffer += '.'
            return True
    elif ch in (curses.KEY_BACKSPACE, 127, 8):
        if state.input_buffer:
            state.input_buffer = state.input_buffer[:-1]
            return True
    return False


def run_tui(stdscr) -> None:
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)
    colors = init_colors()

    state = AppState()
    state.local_ip = get_local_ip()
    state.public_info = {
        "status": "loading",
        "public_ip": "Yükleniyor...",
        "city": "-",
        "region": "-",
        "country": "-",
        "isp": "-",
        "timezone": "-",
        "checked_at": "-",
        "message": "",
    }
    state.status_message = "IP bilgileri alınıyor..."

    render(stdscr, state, colors)
    refresh_ip(state)
    render(stdscr, state, colors)

    while True:
        ch = stdscr.getch()

        if ch == curses.KEY_RESIZE:
            render(stdscr, state, colors)
            continue

        if state.mode == "menu":
            if ch in (ord('q'), ord('Q')):
                break
            if ch in (ord('r'), ord('R')):
                state.status_message = "IP bilgileri yenileniyor..."
                render(stdscr, state, colors)
                refresh_ip(state)
                render(stdscr, state, colors)
                continue
            if ch in (ord('c'), ord('C')):
                state.mode = "calc_tb"
                state.input_buffer = ""
                state.pending_tb = None
                state.status_message = "Veri miktarını girin (TB)."
                render(stdscr, state, colors)
                continue
            render(stdscr, state, colors)
            continue

        if state.mode in ("calc_tb", "calc_speed"):
            if ch == 27:  # ESC
                state.mode = "menu"
                state.input_buffer = ""
                state.pending_tb = None
                state.status_message = "İşlem iptal edildi."
                render(stdscr, state, colors)
                continue

            if ch in (curses.KEY_ENTER, 10, 13):
                value = parse_positive_float(state.input_buffer)
                if value is None:
                    state.status_message = "Geçerli, sıfırdan büyük bir sayı girin."
                    render(stdscr, state, colors)
                    continue
                if state.mode == "calc_tb":
                    state.pending_tb = value
                    state.mode = "calc_speed"
                    state.input_buffer = ""
                    state.status_message = "İnternet hızını girin (Mbit/s)."
                else:
                    assert state.pending_tb is not None
                    state.calc_result = format_duration(state.pending_tb, value)
                    state.mode = "result"
                    state.input_buffer = ""
                    state.status_message = "Hesaplama tamamlandı."
                render(stdscr, state, colors)
                continue

            if handle_input_char(state, ch):
                render(stdscr, state, colors)
                continue

            render(stdscr, state, colors)
            continue

        if state.mode == "result":
            state.mode = "menu"
            state.status_message = "Hazır"
            render(stdscr, state, colors)
            continue


def main() -> None:
    import sys

    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print(
            "Bu uygulama etkileşimli bir terminal (TTY) gerektirir.\n"
            "Lütfen gerçek bir terminal emülatöründe çalıştırın:\n"
            "  cd /home/mercan/mega && ./megagigawhat/bin/python app.py",
            file=sys.stderr,
        )
        raise SystemExit(1)

    try:
        curses.wrapper(run_tui)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
