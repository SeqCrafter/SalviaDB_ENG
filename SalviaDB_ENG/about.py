import reflex as rx

from .components.footer import footer_v2


GREEN = "#006d4d"
MINT = "#a7f3d0"
PALE_MINT = "#ecfdf5"
LAVENDER = "#f1f2ff"
INK = "#17201f"
MUTED = "#677472"
LINE = "#e8ecec"


def brand_mark() -> rx.Component:
    return rx.center(
        rx.icon("sprout", size=20, color="white", stroke_width=2.2),
        width="36px",
        height="36px",
        border_radius="11px",
        background="linear-gradient(145deg, #168563, #006947)",
        box_shadow="0 5px 12px rgba(0, 108, 76, .18)",
        flex_shrink="0",
    )


def nav_link(label: str, href: str, icon: str) -> rx.Component:
    return rx.link(
        rx.flex(
            rx.icon(icon, size=13),
            rx.text(label, font_size="14px", font_weight="700"),
            spacing="1",
            align="center",
        ),
        href=href,
        underline="none",
        color="#3f4d4a",
        padding="7px 9px",
        border_radius="9px",
        _hover={"background": PALE_MINT, "color": GREEN},
    )


def header() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                brand_mark(),
                rx.box(
                    rx.flex(
                        rx.text(
                            "Salvia Molecular Identification System",
                            font_size="20px",
                            font_weight="800",
                            color=GREEN,
                            letter_spacing=".01em",
                        ),
                        rx.text(
                            "Sequence Identification",
                            font_size="13px",
                            color="#687470",
                            padding_left="10px",
                            border_left="1px solid #d9dfdc",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    rx.flex(
                        rx.box(
                            width="6px",
                            height="6px",
                            background="#21b97c",
                            border_radius="999px",
                        ),
                        rx.text(
                            "SalviaDB v1.0 Online",
                            font_size="13px",
                            color="#238363",
                            font_weight="600",
                        ),
                        spacing="1",
                        align="center",
                        margin_top="2px",
                    ),
                ),
                spacing="3",
                align="center",
            ),
            rx.flex(
                rx.flex(
                    nav_link("Identification", "/", "search"),
                    nav_link("User Guide", "/about", "book-open"),
                    spacing="1",
                    align="center",
                ),
                rx.center(
                    rx.link(
                        rx.icon("git-fork", size=16, color="white"),
                        href="https://github.com/SeqCrafter/SalviaDB",
                        target="_blank",
                        rel="noopener noreferrer",
                        underline="none",
                    ),
                    width="34px",
                    height="34px",
                    border_radius="11px",
                    background=GREEN,
                    box_shadow="0 4px 12px rgba(0, 108, 76, .14)",
                ),
                spacing="2",
                align="center",
            ),
            justify="between",
            align="center",
            width="100%",
            gap="12px",
            wrap="wrap",
        ),
        background="rgba(255,255,255,.96)",
        border_bottom="1px solid #edf0ef",
        padding="12px 22px",
        position="sticky",
        top="0",
        z_index="20",
        backdrop_filter="blur(10px)",
    )


def pill(text: str, icon: str) -> rx.Component:
    return rx.flex(
        rx.icon(icon, size=13),
        rx.text(text, font_size="14px", font_weight="700"),
        spacing="1",
        align="center",
        width="fit-content",
        padding="5px 10px",
        border_radius="999px",
        background=PALE_MINT,
        color=GREEN,
        border="1px solid #ccefe0",
    )


def hero() -> rx.Component:
    return rx.box(
        rx.flex(
            pill("ITS + D-1 · Standard Operating Procedure", "flask-conical"),
            rx.text(
                "SOP · DNA Extraction, Amplification, Sequencing, and Combined Identification",
                font_size="13px",
                color="#4d5b59",
                font_family="monospace",
            ),
            justify="between",
            align="center",
            width="100%",
            wrap="wrap",
            gap="8px",
        ),
        rx.heading(
            "Molecular Identification Protocol for Salvia Species, Including S. miltiorrhiza",
            size="5",
            font_weight="800",
            color=INK,
            margin_top="12px",
        ),
        rx.text(
            "A standardized workflow from sample DNA preparation to combined identification, using the ribosomal DNA marker ITS and D-1, a Salvia-specific barcode selected by our team.",
            font_size="15px",
            color=MUTED,
            line_height="1.75",
            margin_top="7px",
            max_width="820px",
        ),
        background="linear-gradient(135deg, #ffffff 0%, #f4fff9 58%, #f1f2ff 100%)",
        border="1px solid #e5eee9",
        border_radius="14px",
        padding="20px",
        box_shadow="0 8px 24px rgba(23, 32, 31, .04)",
    )


def section_title(number: str, title: str, icon: str) -> rx.Component:
    return rx.flex(
        rx.center(
            rx.text(number, font_size="14px", font_weight="800", color="white"),
            width="26px",
            height="26px",
            border_radius="8px",
            background=GREEN,
            flex_shrink="0",
        ),
        rx.icon(icon, size=16, color=GREEN),
        rx.heading(title, size="3", font_weight="800", color=INK),
        spacing="2",
        align="center",
    )


def section_card(number: str, title: str, icon: str, *children, **style) -> rx.Component:
    return rx.box(
        section_title(number, title, icon),
        rx.box(*children, margin_top="13px"),
        background="white",
        border=f"1px solid {LINE}",
        border_radius="13px",
        padding="18px",
        box_shadow="0 6px 20px rgba(23, 32, 31, .035)",
        **style,
    )


def body_text(*children, **style) -> rx.Component:
    return rx.text(
        *children,
        font_size="14px",
        color=MUTED,
        line_height="1.8",
        **style,
    )


def metric(label: str, value: str, note: str) -> rx.Component:
    return rx.box(
        rx.text(label, font_size="13px", color="#53615e", font_weight="700"),
        rx.text(value, font_size="20px", color=GREEN, font_weight="800", margin_top="3px"),
        rx.text(note, font_size="12px", color="#7a8583", margin_top="2px"),
        background=PALE_MINT,
        border="1px solid #d9f1e6",
        border_radius="10px",
        padding="12px",
    )


def data_table(headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...]) -> rx.Component:
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    *[
                        rx.table.column_header_cell(
                            header,
                            font_size="13px",
                            font_weight="800",
                            color="#33413f",
                            background="#edf5f1",
                            white_space="nowrap",
                        )
                        for header in headers
                    ]
                )
            ),
            rx.table.body(
                *[
                    rx.table.row(
                        *[
                            rx.table.cell(
                                cell,
                                font_size="13px",
                                color="#566360",
                                line_height="1.55",
                            )
                            for cell in row
                        ]
                    )
                    for row in rows
                ]
            ),
            width="100%",
            variant="surface",
            size="1",
        ),
        width="100%",
        overflow_x="auto",
        border_radius="10px",
    )


def step_item(number: str, title: str, description: str) -> rx.Component:
    return rx.flex(
        rx.center(
            number,
            width="24px",
            height="24px",
            border_radius="999px",
            background=LAVENDER,
            color="#545aa7",
            font_size="13px",
            font_weight="800",
            flex_shrink="0",
        ),
        rx.box(
            rx.text(title, font_size="14px", font_weight="800", color=INK),
            rx.text(description, font_size="13px", color=MUTED, line_height="1.7", margin_top="2px"),
        ),
        spacing="3",
        align="start",
    )


def about() -> rx.Component:
    return rx.flex(
        header(),
        rx.box(
            hero(),
            rx.grid(
                section_card(
                    "01",
                    "Scope",
                    "circle-check-big",
                    body_text(
                        "For molecular identification of Salvia species, including S. miltiorrhiza. ITS is a ribosomal DNA marker; D-1 is a Salvia-specific barcode selected by our team."
                    ),
                ),
                section_card(
                    "02",
                    "DNA Extraction and PCR Template Requirements",
                    "dna",
                    body_text(
                        "Extract total genomic DNA from approximately 100 mg of dried leaves using a modified CTAB method. Assess DNA purity and concentration with an ND-2000 spectrophotometer and 0.8% agarose gel electrophoresis."
                    ),
                    body_text(
                        "Dilute DNA to 20–30 ng/μL with TE buffer (10 mM Tris-HCl, pH 8.0; 1 mM EDTA). Add 20–30 ng of template DNA to each 25 μL PCR reaction; this corresponds to 1 μL at the working concentration above.",
                        margin_top="7px",
                    ),
                ),
                columns="repeat(auto-fit, minmax(300px, 1fr))",
                gap="14px",
                margin_top="14px",
            ),
            section_card(
                "03",
                "ITS and D-1 Primer Information",
                "scan-search",
                data_table(
                    ("Target", "Primer", "Sequence (5′→3′)", "Annealing temperature"),
                    (
                        ("ITS", "ITS 1F", "TCCGTAGGTGAACCTGCGG", "55°C"),
                        ("ITS", "ITS 4R", "TCCTCCGCTTATTGATATGC", "55°C"),
                        ("D-1", "D-F-1", "TAATACTACTGCCAGACTTCCTAAT", "53°C"),
                        ("D-1", "D-R-1", "TCAATGTCCGAAGAATATGAGCT", "53°C"),
                    ),
                ),
                rx.grid(
                    metric("D-1 candidate region", "Approx. 360 bp", "40 bp at the 3′ end of ndhI + 320 bp of intergenic region"),
                    metric("Reference genome position", "116,365–116,724 bp", "S. miltiorrhiza chloroplast genome"),
                    metric("ITS amplicon", "Approx. 470 bp", "Ribosomal DNA marker"),
                    columns="repeat(auto-fit, minmax(190px, 1fr))",
                    gap="10px",
                    margin_top="12px",
                ),
                margin_top="14px",
            ),
            rx.grid(
                section_card(
                    "04",
                    "PCR Reaction Mixture",
                    "test-tube-diagonal",
                    body_text(
                        "Set up separate ITS and D-1 reactions for each sample using the corresponding primers. The following is an example 25 μL reaction mixture using AmpliTaq DNA polymerase and a GeneAmp PCR System 9700.",
                        margin_bottom="10px",
                    ),
                    data_table(
                        ("Component", "Amount or final concentration per reaction"),
                        (
                            ("Template DNA", "20–30 ng"),
                            ("AmpliTaq DNA polymerase", "0.625 U"),
                            ("PCR buffer", "1×"),
                            ("MgCl₂", "1.5 mM"),
                            ("dNTP", "0.2 mM"),
                            ("Forward primer", "0.3 μM"),
                            ("Reverse primer", "0.3 μM"),
                            ("ddH₂O", "Bring to 25 μL"),
                        ),
                    ),
                ),
                section_card(
                    "05",
                    "PCR Cycling Program",
                    "timer",
                    data_table(
                        ("Stage", "Temperature", "Duration", "Cycles"),
                        (
                            ("Initial denaturation", "95°C", "4 min", "1"),
                            ("Denaturation", "94°C", "30 s", "40 cycles for these three stages"),
                            ("Annealing", "ITS 55°C; D-1 53°C", "1 min", "Same as above"),
                            ("Extension", "72°C", "1.5 min", "Same as above"),
                            ("Final extension", "72°C", "10 min", "1"),
                        ),
                    ),
                ),
                columns="repeat(auto-fit, minmax(420px, 1fr))",
                gap="14px",
                margin_top="14px",
            ),
            section_card(
                "06",
                "Product Assessment and Sanger Sequencing",
                "microscope",
                rx.grid(
                    step_item("1", "Gel electrophoresis", "Check PCR products by electrophoresis on a 1% agarose gel in TAE buffer."),
                    step_item("2", "Quality assessment", "Proceed to Sanger sequencing if bands are clear, at the expected positions, and free of nonspecific amplification."),
                    step_item("3", "Bidirectional sequencing", "Use ITS 1F/ITS 4R for ITS and D-F-1/D-R-1 for D-1."),
                    step_item("4", "Sequence assembly", "Assemble the forward and reverse reads after they are obtained."),
                    columns="repeat(auto-fit, minmax(210px, 1fr))",
                    gap="14px",
                ),
                margin_top="14px",
            ),
            section_card(
                "07",
                "Sequence Processing and Combined ITS + D-1 Identification",
                "workflow",
                rx.grid(
                    step_item("1", "Generate consensus sequences", "Assemble Sanger reads with CodonCode Aligner v.3.7. Generate separate ITS and D-1 consensus sequences, both linked to the same sample ID."),
                    step_item("2", "Enter sequences", "Enter the ITS and D-1 sequences from the same sample into their respective fields."),
                    step_item("3", "Set BLASTn parameters", "The default E-value is 1e-5; lower it to filter for higher-confidence results. The default Task is megablast."),
                    step_item("4", "Select concatenation mode", "direct concatenates the input ITS and D-1 sequences as entered; all also tries combinations using their reverse complements."),
                    step_item("5", "Start identification", "After setting the parameters, click “Start BLAST Identification” and wait for the results."),
                    columns="repeat(auto-fit, minmax(250px, 1fr))",
                    gap="14px",
                ),
                rx.box(
                    rx.flex(
                        rx.icon("info", size=14, color="#545aa7"),
                        rx.text("Parameter Notes", font_size="14px", font_weight="800", color="#394070"),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        "Task sets the initial word size, scoring matrix, and extension threshold to balance speed against sensitivity to distant homologs. blastn is more sensitive than megablast and detects more distant matches, but can run several times slower.",
                        font_size="13px",
                        color="#606784",
                        line_height="1.7",
                        margin_top="5px",
                    ),
                    background=LAVENDER,
                    border="1px solid #e2e4fa",
                    border_radius="10px",
                    padding="12px 14px",
                    margin_top="14px",
                ),
                margin_top="14px",
            ),
            section_card(
                "08",
                "Reference",
                "library-big",
                body_text(
                    "[1] Cui, N., Liao, B. S., Liang, C. L., Li, S. F., Zhang, H., Xu, J., Li, X. W., & Chen, S. L. (2020). Complete chloroplast genome of Salvia plebeia: organization, specific barcode and phylogenetic analysis. Chinese Journal of Natural Medicines, 18(8), 563–572."
                ),
                rx.link(
                    rx.flex(
                        rx.text("DOI 10.1016/S1875-5364(20)30068-6", font_size="13px", font_weight="700"),
                        rx.icon("external-link", size=11),
                        spacing="1",
                        align="center",
                    ),
                    href="https://doi.org/10.1016/S1875-5364(20)30068-6",
                    target="_blank",
                    rel="noopener noreferrer",
                    color=GREEN,
                    underline="hover",
                    display="inline-block",
                    margin_top="8px",
                ),
                margin_top="14px",
            ),
            width="100%",
            max_width="1120px",
            margin="0 auto",
            padding="14px 20px 28px",
            flex="1",
        ),
        footer_v2(),
        direction="column",
        width="100%",
        min_height="100vh",
        background="#f8f7ff",
        color=INK,
        font_family="Inter, 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif",
    )
