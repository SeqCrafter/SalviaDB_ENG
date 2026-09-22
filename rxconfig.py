import reflex as rx

config = rx.Config(
    app_name="SalviaDB_ENG",
    show_built_with_reflex=False,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="light",
                has_background=True,
                accent_color="green",
                gray_color="slate",
            )
        ),
    ]
)