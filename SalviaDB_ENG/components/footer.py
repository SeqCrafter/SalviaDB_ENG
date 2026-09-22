import reflex as rx

# Theme colors aligned with SalviaDB design system
GREEN = "#006d4d"
MINT = "#a7f3d0"
PALE_MINT = "#ecfdf5"
INK = "#17201f"
MUTED = "#677472"
LINE = "#e8ecec"


def media(name: str, href: str, icon: str = "") -> rx.Component:
    children = []
    if icon:
        children.append(rx.icon(icon, size=13))
    children.append(rx.text(name, font_size="15px", font_weight="600"))

    return rx.link(
        rx.flex(
            *children,
            spacing="1",
            align="center",
        ),
        href=href,
        target="_blank",
        rel="noopener noreferrer",
        underline="none",
        color="#3f4d4a",
        padding="5px 10px",
        border_radius="8px",
        border=f"1px solid {LINE}",
        background="#ffffff",
        transition="all 0.15s ease",
        _hover={
            "background": PALE_MINT,
            "color": GREEN,
            "border_color": MINT,
            "transform": "translateY(-1px)",
            "box_shadow": "0 2px 6px rgba(0, 108, 76, 0.08)",
        },
    )


def footer_v2() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.box(
                rx.flex(
                    rx.text(
                        "© 2026",
                        font_size="16px",
                        font_weight="600",
                        color=INK,
                    ),
                    rx.text(
                        "·",
                        font_size="16px",
                        color=MUTED,
                    ),
                    rx.text(
                        "Shandong Academy of Chinese Medicine",
                        font_size="15px",
                        color=MUTED,
                    ),
                    align="center",
                    spacing="2",
                    wrap="wrap",
                ),
                rx.text(
                    "Salvia Molecular Identification System · Salvia Molecular Identification Database",
                    font_size="14px",
                    color="#879693",
                    margin_top="3px",
                ),
            ),
            rx.flex(
                media("GitHub", "https://github.com/SeqCrafter", "git-fork"),
                media("Blog", "https://blog.xiaohanys.top", "globe"),
                media("Zhihu", "https://www.zhihu.com/people/luo-tian-bao-92", "message-square"),
                spacing="2",
                align="center",
                wrap="wrap",
            ),
            justify="between",
            align="center",
            width="100%",
            max_width="1120px",
            margin="0 auto",
            padding="16px 20px",
            wrap="wrap",
            gap="14px",
        ),
        width="100%",
        background="rgba(255, 255, 255, 0.92)",
        border_top=f"1px solid {LINE}",
        backdrop_filter="blur(10px)",
        margin_top="32px",
    )
