import asyncio
from functools import partial

import reflex as rx

from .function import IdentificationResult, identify_salvia_sequence

from .about import about
from .components.footer import footer_v2

### backend code
class IndexState(rx.State):
    its_seq: rx.Field[str] = rx.field("AACCCCCGTCATGT....")
    d1_seq: rx.Field[str] = rx.field("TTGATTTTATCAAAAA....")
    evalue: rx.Field[str] = rx.field("1e-5")
    task: rx.Field[str] = rx.field("megablast")
    mode: rx.Field[str] = rx.field("direct")
    is_identifying: rx.Field[bool] = rx.field(False)
    identification_progress: rx.Field[int] = rx.field(0)
    elapsed_seconds: rx.Field[int] = rx.field(0)
    show_identification_result: rx.Field[bool] = rx.field(False)
    has_no_identification_result: rx.Field[bool] = rx.field(False)
    identification_error: rx.Field[str] = rx.field("")
    matched_species: rx.Field[str] = rx.field("")
    result_identity: rx.Field[float] = rx.field(0.0)
    result_bit_score: rx.Field[float] = rx.field(0.0)
    result_evalue: rx.Field[str] = rx.field("")
    result_its_genbank_id: rx.Field[str] = rx.field("")
    result_d1_genbank_id: rx.Field[str] = rx.field("")
    match_results: rx.Field[list[dict[str, str | float | int]]] = rx.field(
        default_factory=list
    )

    @rx._x.hybrid_property
    def advanced_parameter_summary(self) -> str:
        """Build the compact parameter summary directly in the browser."""
        return f"{self.evalue} · {self.task} · {self.mode}"

    @rx.event
    def example_seq(self):
        self.its_seq = "AACCCCCGTCATGTACTCGGTCCCCCGCCGGCGCGCGTCCTCGGGCAGTGTCGTGCGGGCTAACGAACCCCGGCGCGGAATGCGCCAAGGAAAACTAATCGAAGCGTCCGCCCCTCGTGCCCCGTTCGCGGTGCGCGCGGGGGGATTGGATGTCTATCAAATGTCAAAACGACTCTCGGCAACGGATATCTCGGCTCTCGCATCGATGAAGAACGTAGCGAAATGCGATACTTGGTGTGAATTGCAGAATCCCGTGAACCATCGAGTCTTTGAACGCAAGTTGCGCCCGAAGCCATTAGGCCGAGGGCACGTCTGCCTGGGCGTCACGCATCGCGTCGCCCCCCTCCCCGCGCATAGCGTGGGCTGCGGGGGCGGAAACTGGCCTCCCGTGCGCCCCGGCGCGCGGCTGGCCCAAATGCGATCCCTCGGCGACTCGTGTCGCGACAAGTGGTGGTTGAACAACTCACTTTCATG"
        self.d1_seq = "TTGATTTTATCAAAAAAATCGAAATATTTCATGTCTTTGTTGACCTGACCAGGAAAAAAGAAGTTATCCTTTTTTTTTTTATTTTAACATATACATATTAATTTAATTGAATTTGAATGAATCGGGATGATTTGGATTGATGTAAATACAGGACTGCTTTTTTTTTGTTTCGAAAGCAAAGGTTAAAACTTTATCTTTATATTTTATATTATTACATTATTCGAATAGAAAGTCATTTTAAATGAAAATCAAGCCACGACCCTCACCAACTAACCGTTTTTYTGTATTCACCAAGCAAAAACCTGATCCCTTTAACTCCAAAAAATTTCAAAAGCTTTTTTTTTTTTGAATTTATAAATGTTTTGTAAAGCGAGAGTTTTATACATTGTTGAGTTGAGGTA"
    
    @rx.event
    def clean_data(self):
        self.its_seq = ""
        self.d1_seq = ""
        self.identification_progress = 0
        self.elapsed_seconds = 0
        self.show_identification_result = False
        self.has_no_identification_result = False
        self.identification_error = ""
        self.match_results = []
        
    @rx.event
    def set_its_seq(self, value: str):
        self.its_seq = value
    
    @rx.event
    def set_d1_seq(self, value: str):
        self.d1_seq = value

    @rx.event
    def set_evalue(self, value: str):
        self.evalue = value

    @rx.event
    def set_task(self, value: str):
        if value in {"megablast", "blastn", "dc-megablast", "blastn-short"}:
            self.task = value

    @rx.event
    def set_mode(self, value: str):
        if value in {"direct", "all"}:
            self.mode = value

    @rx.event(background=True)
    async def run_identification(self):
        """Run the synchronous identification pipeline in a worker thread."""
        async with self:
            # Background events may be triggered more than once, so guard against
            # starting a duplicate identification while one is already active.
            if self.is_identifying:
                return
            self.is_identifying = True
            self.show_identification_result = False
            self.has_no_identification_result = False
            self.identification_progress = 0
            self.elapsed_seconds = 0
            self.identification_error = ""
            its_sequence = self.its_seq
            d1_sequence = self.d1_seq
            evalue = self.evalue
            task = self.task
            mode = self.mode

        worker = asyncio.create_task(
            rx.run_in_thread(
                partial(
                    identify_salvia_sequence,
                    its_sequence,
                    d1_sequence,
                    evalue,
                    task,
                    mode,
                )
            )
        )

        try:
            # The real BLAST runtime is unknown. Present a virtual 30-second
            # timeline and hold at 95% if the worker takes longer.
            while not worker.done():
                await asyncio.sleep(1)
                async with self:
                    self.elapsed_seconds += 1
                    self.identification_progress = min(
                        int(self.elapsed_seconds / 30 * 100), 95
                    )

            result: IdentificationResult | None = await worker
            if not result or not result.get("matches") or not result.get("species_name"):
                async with self:
                    self.match_results = []
                    self.identification_progress = 100
                    self.is_identifying = False
                    self.show_identification_result = False
                    self.has_no_identification_result = True
                return

            async with self:
                self.matched_species = result["species_name"]
                self.result_identity = result["identity"]
                self.result_bit_score = result["bit_score"]
                self.result_evalue = result["evalue"]
                self.result_its_genbank_id = result["its_genbank_id"]
                self.result_d1_genbank_id = result["d1_genbank_id"]
                self.match_results = result["matches"]
                self.identification_progress = 100
                self.is_identifying = False
                self.has_no_identification_result = False
                self.show_identification_result = True
        except Exception as exc:
            async with self:
                self.identification_error = str(exc)
                self.is_identifying = False
                self.has_no_identification_result = False
                self.show_identification_result = False
    
    @rx.var(cache=False)
    def its_seq_len(self) -> int:
        return len(self.its_seq)
    
    @rx.var(cache=False)
    def d1_seq_len(self) -> int:
        return len(self.d1_seq)

### Front code

GREEN = "#006d4d"
MINT = "#a7f3d0"
PALE_MINT = "#ecfdf5"
LAVENDER = "#f1f2ff"
INK = "#17201f"
MUTED = "#677472"
LINE = "#e8ecec"
NCBI_NUCCORE_BASE = "https://www.ncbi.nlm.nih.gov/nuccore/"


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
                        href="https://github.com/SeqCrafter/SalviaDB_ENG",
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


def pill(text: str, icon: str, **style) -> rx.Component:
    return rx.flex(
        rx.icon(icon, size=13),
        rx.text(text, font_size="14px", font_weight="700"),
        spacing="1",
        align="center",
        width="fit-content",
        padding="5px 10px",
        border_radius="999px",
        **style,
    )


def intro() -> rx.Component:
    return rx.box(
        rx.flex(
            pill(
                "Powered by NCBI BLAST",
                "arrow-right",
                background="#b7f4d5",
                color="#00664a",
            ),
            rx.text(
                "Database version: SalviaDB-v1.0",
                font_size="13px",
                color="#4d5b59",
                font_family="monospace",
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        rx.heading(
            "Salvia Molecular Identification System",
            size="5",
            font_weight="800",
            color=INK,
            margin_top="9px",
        ),
        rx.text(
            "Enter the nuclear ribosomal ITS and chloroplast D-1 sequences to rapidly identify cultivated varieties and wild forms of S. miltiorrhiza using BLAST.",
            font_size="15px",
            color="#53605e",
            margin_top="5px",
        ),
        rx.flex(
            rx.button(
                rx.icon("cloud-download", size=14),
                "Load example: Ludan No. 1 sequences",
                height="34px",
                flex="1",
                background=MINT,
                color="#064e3b",
                font_size="15px",
                font_weight="700",
                border_radius="8px",
                cursor="pointer",
                _hover={"background": "#8cebbf"},
                on_click=IndexState.example_seq
            ),
            rx.button(
                rx.icon("rotate-ccw", size=13),
                "Clear",
                height="34px",
                background="#eef0ff",
                color="#46505d",
                font_size="14px",
                border_radius="8px",
                cursor="pointer",
                variant="soft",
                on_click=IndexState.clean_data
            ),
            spacing="2",
            width="100%",
            margin_top="14px",
        ),
        padding="0 4px",
    )


def field_header(label: str, length: int) -> rx.Component:
    return rx.flex(
        rx.text(
            label,
            rx.text.span(" *", color="#ef4444"),
            font_size="14px",
            font_weight="700",
            color="#263230",
        ),
        rx.text(
            f"{length} bases (bp)",
            font_size="13px",
            color="#4e5b58",
            font_family="monospace",
        ),
        justify="between",
        align="center",
        width="100%",
        margin_bottom="6px",
    )


def sequence_field(
    label: str,
    length: int,
    value:str,
    change_data:rx.EventHandler,
    placeholder: str,
) -> rx.Component:
    return rx.box(
        field_header(label, length),
        rx.box(
            rx.text_area(
                placeholder=placeholder,
                width="100%",
                height="74px",
                resize="none",
                border="none",
                outline="none",
                box_shadow="none",
                background="transparent",
                color="#52605e",
                font_family="monospace",
                font_size="13px",
                line_height="1.45",
                padding="12px 12px 22px",
                _focus={"box_shadow": "none", "outline": "none"},
                value=value,
                on_change=change_data
            ),
            rx.text(
                "Paste sequence",
                position="absolute",
                right="10px",
                bottom="7px",
                font_size="12px",
                color="#8a9593",
            ),
            position="relative",
            background=LAVENDER,
            border_radius="8px",
            overflow="hidden",
        ),
        width="100%",
    )


def parameter_control(label: str, control: rx.Component) -> rx.Component:
    return rx.box(
        rx.text(
            label,
            font_size="14px",
            color="#43504e",
            font_weight="600",
            margin_bottom="6px",
        ),
        control,
        width="100%",
    )


def advanced_parameters() -> rx.Component:
    return rx.el.details(
        rx.el.summary(
            rx.flex(
                rx.flex(
                    rx.icon("sliders-horizontal", size=14, color=GREEN),
                    rx.text(
                        "Advanced Alignment Parameters (BLASTn)",
                        font_size="14px",
                        font_weight="700",
                    ),
                    rx.text(
                        IndexState.advanced_parameter_summary,
                        font_size="12px",
                        color="#7a8583",
                        font_family="monospace",
                        display=["none", "block"],
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.icon(
                    "chevron-down",
                    class_name="advanced-parameters-chevron",
                    size=14,
                    color="#64716f",
                    transition="transform .2s ease",
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            cursor="pointer",
            list_style="none",
            padding="10px 12px",
            css={"&::-webkit-details-marker": {"display": "none"}},
        ),
        rx.box(
            rx.grid(
                parameter_control(
                    "E-value threshold",
                    rx.input(
                        value=IndexState.evalue,
                        on_change=IndexState.set_evalue,
                        placeholder="For example: 1e-5",
                        width="100%",
                        height="35px",
                        background="white",
                        border="1px solid #e4e8e7",
                        border_radius="6px",
                        font_family="monospace",
                        font_size="14px",
                        box_shadow="none",
                    ),
                ),
                parameter_control(
                    "Alignment task",
                    rx.select(
                        ["megablast", "blastn", "dc-megablast", "blastn-short"],
                        value=IndexState.task,
                        on_change=IndexState.set_task,
                        width="100%",
                        size="2",
                    ),
                ),
                parameter_control(
                    "Concatenation mode",
                    rx.select(
                        ["direct", "all"],
                        value=IndexState.mode,
                        on_change=IndexState.set_mode,
                        width="100%",
                        size="2",
                    ),
                ),
                width="100%",
                grid_template_columns="repeat(auto-fit, minmax(190px, 1fr))",
                gap="12px",
            ),
            padding="12px",
            border_top="1px solid #dfe4f1",
        ),
        width="100%",
        background=LAVENDER,
        border_radius="8px",
        margin_top="13px",
        overflow="hidden",
        css={
            "&[open] .advanced-parameters-chevron": {
                "transform": "rotate(180deg)"
            }
        },
    )


def input_card() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                rx.center(
                    rx.icon("flask-conical", size=14, color="white"),
                    width="24px",
                    height="24px",
                    border_radius="999px",
                    background=GREEN,
                ),
                rx.text("Molecular Sequence Input", font_size="17px", font_weight="800"),
                spacing="2",
                align="center",
            ),
            rx.badge(
                "FASTA / Plain sequence",
                color_scheme="gray",
                variant="soft",
                size="1",
                font_family="monospace",
                font_size="12px",
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        rx.vstack(
            sequence_field(
                "Nuclear Ribosomal ITS Sequence",
                IndexState.its_seq_len,
                IndexState.its_seq,
                IndexState.set_its_seq,
                "AGCATGGCAT...",
            ),
            sequence_field(
                "Chloroplast D-1 Sequence",
                IndexState.d1_seq_len,
                IndexState.d1_seq,
                IndexState.set_d1_seq,
                "CTTT...",
            ),
            spacing="3",
            width="100%",
            margin_top="14px",
        ),
        advanced_parameters(),
        rx.button(
            rx.icon("microscope", size=16),
            rx.cond(
                IndexState.is_identifying,
                "Running BLAST identification...",
                "Start BLAST Identification",
            ),
            on_click=IndexState.run_identification,
            disabled=IndexState.is_identifying,
            loading=IndexState.is_identifying,
            width="100%",
            height="45px",
            background=GREEN,
            color="white",
            font_size="17px",
            font_weight="800",
            border_radius="7px",
            margin_top="10px",
            box_shadow="0 5px 11px rgba(0,109,77,.2)",
            cursor="pointer",
            _hover={"background": "#005c41", "transform": "translateY(-1px)"},
            _disabled={"cursor": "not-allowed", "opacity": ".82"},
        ),
        background="white",
        border="1px solid #e9edec",
        border_radius="14px",
        padding="16px",
        margin_top="16px",
        box_shadow="0 3px 13px rgba(30,58,50,.035)",
    )


def stat(label: str, value) -> rx.Component:
    return rx.box(
        rx.text(label, font_size="12px", color="#52605d", font_family="monospace"),
        rx.text(
            value,
            font_size="14px",
            color="#123c31",
            font_weight="800",
            font_family="monospace",
            margin_top="2px",
        ),
    )


def genbank_link(accession) -> rx.Component:
    return rx.link(
        rx.flex(
            rx.text(accession),
            rx.icon("external-link", size=10),
            spacing="1",
            align="center",
        ),
        href=rx.Var.create(NCBI_NUCCORE_BASE) + accession.to(str),
        target="_blank",
        rel="noopener noreferrer",
        color=GREEN,
        font_size="13px",
        font_weight="800",
        font_family="monospace",
        underline="hover",
    )


def genbank_stat(label: str, accession) -> rx.Component:
    return rx.box(
        rx.text(label, font_size="12px", color="#52605d", font_family="monospace"),
        genbank_link(accession),
        margin_top="2px",
    )


def result_card() -> rx.Component:
    return rx.box(
        rx.flex(
            pill(
                "High-Confidence Identification",
                "badge-check",
                background=GREEN,
                color="white",
            ),
            rx.text(
                "BLASTn · Best hit",
                font_size="13px",
                color=GREEN,
                font_weight="700",
                font_family="monospace",
            ),
            justify="between",
            align="center",
        ),
        rx.flex(
            rx.box(
                rx.heading(
                    IndexState.matched_species,
                    size="5",
                    font_weight="800",
                    font_style="italic",
                    color="#173a31",
                ),
                rx.text(
                    "NCBI nucleotide reference match",
                    font_size="13px",
                    color="#66736f",
                    margin_top="4px",
                ),
            ),
            rx.box(
                rx.text(
                    IndexState.result_identity,
                    "%",
                    font_size="24px",
                    color=GREEN,
                    font_weight="900",
                ),
                rx.text("Sequence identity", font_size="12px", color="#53615e"),
                text_align="right",
            ),
            justify="between",
            align="end",
            margin_top="14px",
        ),
        rx.grid(
            stat("Bit-Score", IndexState.result_bit_score),
            stat("E-value", IndexState.result_evalue),
            genbank_stat("ITS GenBank ID", IndexState.result_its_genbank_id),
            genbank_stat("D1 GenBank ID", IndexState.result_d1_genbank_id),
            width="100%",
            grid_template_columns="repeat(auto-fit, minmax(130px, 1fr))",
            gap="12px",
            padding_top="9px",
            margin_top="8px",
            border_top="1px solid rgba(13,109,78,.11)",
        ),
        background="linear-gradient(110deg, #e8fff5 0%, #f9fffc 75%)",
        border="1px solid #dff4ea",
        border_radius="14px",
        padding="15px 16px 13px",
        margin_top="16px",
    )


def identification_progress_card() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                rx.center(
                    rx.icon("dna", size=15, color="white"),
                    width="27px",
                    height="27px",
                    border_radius="999px",
                    background=GREEN,
                ),
                rx.box(
                    rx.text(
                        "Aligning sequences",
                        font_size="16px",
                        font_weight="800",
                        color="#173a31",
                    ),
                    rx.text(
                        "Running BLAST. Please wait (30-second estimated progress cycle).",
                        font_size="13px",
                        color="#63716e",
                        margin_top="2px",
                    ),
                ),
                spacing="2",
                align="center",
            ),
            rx.text(
                IndexState.identification_progress,
                "%",
                color=GREEN,
                font_size="15px",
                font_weight="800",
                font_family="monospace",
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        rx.progress(
            value=IndexState.identification_progress,
            max=100,
            size="2",
            color_scheme="jade",
            radius="full",
            width="100%",
            margin_top="14px",
        ),
        rx.flex(
            rx.text(
                "Searching the S. miltiorrhiza reference database...",
                font_size="12px",
                color="#6a7774",
            ),
            rx.text(
                "Elapsed: ",
                IndexState.elapsed_seconds,
                " s",
                font_size="12px",
                color="#6a7774",
                font_family="monospace",
            ),
            justify="between",
            width="100%",
            margin_top="7px",
        ),
        background="linear-gradient(110deg, #ecfff7 0%, #ffffff 80%)",
        border="1px solid #dff4ea",
        border_radius="14px",
        padding="16px",
        margin_top="16px",
        box_shadow="0 3px 13px rgba(30,58,50,.035)",
    )


def match_row(
    match: dict[str, str | float | int],
) -> rx.Component:
    is_best = match["rank"] == 1
    return rx.flex(
        rx.flex(
            rx.center(
                match["rank"],
                width="20px",
                height="20px",
                border_radius="999px",
                background=rx.cond(is_best, GREEN, "#e4e7fb"),
                color=rx.cond(is_best, "white", "#6d7590"),
                font_size="13px",
                font_weight="800",
                flex_shrink="0",
            ),
            rx.box(
                rx.flex(
                    rx.text(
                        match["species_name"],
                        font_size="14px",
                        font_weight="800",
                        font_style="italic",
                        color="#24312f",
                    ),
                    rx.cond(
                        is_best,
                        rx.badge(
                            "Best match",
                            background=GREEN,
                            color="white",
                            font_size="11px",
                            height="20px",
                            padding="0 7px",
                        ),
                        rx.fragment(),
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.flex(
                    rx.text(
                        "ITS:",
                        font_size="12px",
                        color="#667270",
                        font_family="monospace",
                    ),
                    genbank_link(match["its_genbank_id"]),
                    rx.text("·", font_size="12px", color="#8a9491"),
                    rx.text(
                        "D1:",
                        font_size="12px",
                        color="#667270",
                        font_family="monospace",
                    ),
                    genbank_link(match["d1_genbank_id"]),
                    spacing="1",
                    align="center",
                    wrap="wrap",
                    margin_top="3px",
                ),
            ),
            spacing="2",
            align="center",
        ),
        rx.box(
            rx.text(
                match["identity"],
                "%",
                font_size="14px",
                font_weight="800",
                color="#163d33",
            ),
            rx.text(
                "Score: ",
                match["bit_score"],
                "  |  E: ",
                match["evalue"],
                font_size="12px",
                color="#53615e",
                font_family="monospace",
                margin_top="3px",
            ),
            text_align="right",
        ),
        justify="between",
        align="center",
        width="100%",
        min_height="54px",
        padding="8px 10px",
        background=rx.cond(is_best, "#e9fff5", LAVENDER),
        border_radius="8px",
        border=rx.cond(is_best, "1px solid #e1f5eb", "1px solid #edf0fb"),
    )


def matches_card() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                rx.icon("list-tree", size=15, color=GREEN),
                rx.text(
                    "Top 5 BLAST Matches",
                    font_size="16px",
                    font_weight="800",
                ),
                spacing="2",
                align="center",
            ),
            rx.text("Sorted by bit score", font_size="12px", color="#64706e"),
            justify="between",
            align="center",
        ),
        rx.vstack(
            rx.foreach(IndexState.match_results, match_row),
            spacing="1",
            width="100%",
            margin_top="12px",
        ),
        background="white",
        border="1px solid #e9edec",
        border_radius="14px",
        padding="15px 16px",
        margin_top="10px",
        box_shadow="0 3px 13px rgba(30,58,50,.025)",
    )


def identification_error_card() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.icon("triangle-alert", size=16, color="#b42318"),
            rx.box(
                rx.text("Identification could not be completed", font_size="16px", font_weight="800"),
                rx.text(
                    IndexState.identification_error,
                    font_size="13px",
                    color="#7a3731",
                    margin_top="3px",
                ),
            ),
            spacing="2",
            align="center",
        ),
        background="#fff4f2",
        border="1px solid #ffd6d1",
        border_radius="14px",
        padding="15px 16px",
        margin_top="16px",
    )


def no_identification_result_card() -> rx.Component:
    return rx.box(
        rx.center(
            rx.center(
                rx.icon("search-x", size=20, color="#5f6d69"),
                width="38px",
                height="38px",
                border_radius="999px",
                background="#eef2f1",
            ),
            rx.text(
                "No matches found",
                font_size="17px",
                font_weight="800",
                color="#263330",
                margin_top="10px",
            ),
            rx.text(
                "The sequences did not match the internal S. miltiorrhiza reference database. Check sequence quality or adjust the advanced alignment parameters, then try again.",
                font_size="13px",
                color="#697572",
                text_align="center",
                max_width="520px",
                margin_top="5px",
            ),
            direction="column",
        ),
        background="white",
        border="1px dashed #d5ddda",
        border_radius="14px",
        padding="24px 16px",
        margin_top="16px",
        box_shadow="0 3px 13px rgba(30,58,50,.025)",
    )


def academic_disclaimer() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.icon("info", size=15, color="#246da8"),
            rx.text(
                "Academic and Database Notice",
                font_size="15px",
                font_weight="800",
                color="#263442",
            ),
            spacing="2",
            align="center",
        ),
        rx.text(
            "This system's reference database is for academic and educational use only. Identification results are for reference only.",
            font_size="13px",
            color="#65717c",
            line_height="1.6",
            margin_top="6px",
        ),
        background="#f0f2ff",
        border="1px solid #e8eafd",
        border_radius="10px",
        padding="13px 15px",
        margin_top="14px",
    )


def identification_output() -> rx.Component:
    return rx.cond(
        IndexState.is_identifying,
        identification_progress_card(),
        rx.cond(
            IndexState.identification_error != "",
            identification_error_card(),
            rx.cond(
                IndexState.has_no_identification_result,
                no_identification_result_card(),
                rx.cond(
                    IndexState.show_identification_result,
                    rx.fragment(result_card(), matches_card()),
                    rx.fragment(),
                ),
            ),
        ),
    )


def index() -> rx.Component:
    return rx.flex(
        header(),
        rx.box(
            intro(),
            input_card(),
            identification_output(),
            academic_disclaimer(),
            width="100%",
            max_width="1120px",
            margin="0 auto",
            padding="14px 20px 22px",
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


app = rx.App(
    stylesheets=[
        "https://font.webcache.cn/google/css2?family=Inter:wght@400;500;600;700;800&display=swap"
    ]
)
app.add_page(index, title="Salvia Molecular Identification System")
app.add_page(about, route="/about", title="User Guide | Salvia Molecular Identification System")
