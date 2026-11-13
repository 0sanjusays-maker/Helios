"""Build the Thar vs Escape Velocity production script as a .docx (then PDF)."""

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Inches
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SB = os.path.join(HERE, "storyboard")

INK = RGBColor(0x11, 0x11, 0x11)
RED = RGBColor(0xB3, 0x14, 0x1E)
GREY = RGBColor(0x5A, 0x5A, 0x5A)


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def cell_text(cell, text, size=9.5, bold=False, color=INK, mono=False, space_after=2):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(1)
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Consolas" if mono else "Inter"
    return p


def add_para(doc, text, size=11, bold=False, italic=False, color=INK,
             space_before=0, space_after=6, align=None, style=None):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = "Inter"
    return p


def label_para(doc, label, body, size=10.5):
    """A field line like 'CAMERA — text' with the label in red caps."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(label + "  ")
    r.font.size = Pt(size - 1)
    r.font.bold = True
    r.font.color.rgb = RED
    r.font.name = "Inter"
    r2 = p.add_run(body)
    r2.font.size = Pt(size)
    r2.font.color.rgb = INK
    r2.font.name = "Inter"
    return p


def rule(doc, color="B3141E", size=12):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(8)
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    pbdr.append(bottom)
    pPr.append(pbdr)


def shot_heading(doc, num, timecode, title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(f"{num}  ")
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RED
    r.font.name = "Inter"
    r2 = p.add_run(f"{timecode}  ")
    r2.font.size = Pt(11)
    r2.font.bold = True
    r2.font.color.rgb = INK
    r2.font.name = "Consolas"
    r3 = p.add_run(title.upper())
    r3.font.size = Pt(13)
    r3.font.bold = True
    r3.font.color.rgb = INK
    r3.font.name = "Inter"
    return p


def build():
    doc = Document()

    # page setup
    for s in doc.sections:
        s.page_width = Inches(8.27)
        s.page_height = Inches(11.69)
        s.left_margin = Inches(0.72)
        s.right_margin = Inches(0.72)
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)

    st = doc.styles["Normal"]
    st.font.name = "Inter"
    st.font.size = Pt(10.5)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.12

    # ---------------------------------------------------------------- COVER
    add_para(doc, "PRODUCTION SCRIPT  ·  V1  ·  13 NOV 2026", size=9, bold=True, color=GREY, space_after=4)
    add_para(doc, "THAR vs\nESCAPE VELOCITY", size=34, bold=True, color=INK, space_after=2)
    add_para(doc, "Anime / Manga Edition", size=16, bold=True, color=RED, space_after=10)
    add_para(doc, "Runtime 60s  ·  6 shots  ·  12 storyboard frames  ·  6 voice lines",
             size=10.5, color=GREY, space_after=2)
    add_para(doc, "Vibe: extreme dramatic tension, fast cuts, high-impact comedy.",
             size=10.5, italic=True, color=GREY, space_after=10)
    rule(doc)
    add_para(doc, "THE SIX-WORD PITCH", size=9, bold=True, color=RED, space_after=2)
    add_para(doc, "A man prays for a Thar. God delivers it with orbital velocity. "
                  "Phyzix does the rest, and the last word goes to a booming voice from "
                  "the heavens with a follow-the-founder punchline.", size=10.5, space_after=12)

    # spec table
    spec = [
        ("Hero (Jira)", "Young Indian man, early 20s. Messy spiky black hair, thick brows, white oversized tee, dark track pants. Always slightly too confident."),
        ("The Thar", "Solid-black Mahindra Thar-style hardtop. Round headlamps, chunky tyres, black-on-black. Sits like a tank, moves like a missile."),
        ("The Divine", "Unseen. Booming echo, white void, and one giant glowing crimson hand."),
        ("Palette", "Pure white void  →  crimson + black  →  pitch black space with crimson nebula. Three colours. Never more."),
        ("Type / SFX", "Bold hand-drawn manga lettering, red fill or black outline. Sound effects as physical objects in frame."),
        ("Aspect", "16:9. Shoot for 1080p at 24fps; speed-ramp on 60fps for the launch beat."),
    ]
    t = doc.add_table(rows=0, cols=2)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for k, v in spec:
        row = t.add_row()
        row.cells[0].width = Inches(1.35)
        row.cells[1].width = Inches(5.4)
        cell_text(row.cells[0], k.upper(), size=8.5, bold=True, color=RED)
        cell_text(row.cells[1], v, size=9.5)
    doc.add_page_break()

    # ---------------------------------------------------------------- SHOTS
    add_para(doc, "SHOT BREAKDOWN", size=9, bold=True, color=GREY, space_after=2)
    add_para(doc, "Six shots. Every cut lands on a sound — a record scratch, a sonic boom, "
                  "or dead silence. Silence is the loudest cut in this film; protect it.",
             size=10.5, color=GREY, space_after=6)
    rule(doc)

    shots = [
        {
            "num": "01", "tc": "0:00 – 0:10", "title": "The Setup & The Drop",
            "frames": [("01_setup_kneeling.png", "1A — Jira in devotion, white void"),
                       ("02_thar_drop.png", "1B — Impact: the Thar lands, red shadow flash")],
            "board": "PURE WHITE. Jira kneels, hands folded, eyes shut, one bead of devotional sweat. "
                     "The frame is 80% empty air above him — the emptiness is the joke's setup.",
            "action": "A massive solid-black Thar drops in from the top edge of frame. Ground contact: "
                      "screen-shake, dust plume, a dark crimson shadow flashing directly under the tyres, "
                      "white radial impact lines punching outward. The jeep bounces once, settles. Jira does not move.",
            "camera": "Locked static wide on the white void. On impact, a 2-frame upward jolt plus a 6% "
                      "scale punch-in keyed to the bass hit. Let the shake decay over 8 frames — do not ease it out.",
            "audio": "The trending track enters clean and devotional: \"Hey Bhagwan, ek lambi ek Thar de do...\" "
                     "Divine reverb tail on the vocal, low sub-bass swell underneath.",
            "transition": "Hard cut on the beat. No dissolve, ever, in this film.",
        },
        {
            "num": "02", "tc": "0:10 – 0:18", "title": "The Demand",
            "frames": [("03_eyes_snap.png", "2A — Eyes snap open, speed lines"),
                       ("04_point_to_sky.png", "2B — Finger to the sky, full attitude")],
            "board": "Jira's eyes snap open. Extreme close-up, then a violent pull back as he stands. "
                     "Horizontal black speed lines rush behind him in alternating directions.",
            "action": "He rises, smirks, and points one finger straight at the sky — the shonen hero pose, "
                      "played completely straight. The Thar sits behind him, still radiating heat.",
            "camera": "Close-up (100mm feel) on the eyes, then a whip-pan out to a low-angle hero shot. "
                      "Two cuts inside eight seconds keeps the rhythm aggressive. Add a 3-frame white flash on the eye snap.",
            "audio": "The song is guillotined by a hard record scratch at 0:10.5. One beat of room tone, then Jira.",
            "dialogue": [("JIRA", "Thank you Prabhu! Par isme aisi speed do ki dharti pe mujhe koi pakad na paye! Ekdum Rocket!")],
            "vo": "02_jira_demand.mp3",
            "transition": "Snap cut on \"Rocket!\" — mid-word if possible. Trim the last consonant.",
        },
        {
            "num": "03", "tc": "0:18 – 0:28", "title": "The Launch",
            "frames": [("05_cockpit_speedo.png", "3A — Cockpit: dash crimson, needle buried"),
                       ("06_speedbreaker_launch.png", "3B — The breaker: 90° vertical launch"),
                       ("07_sonic_boom.png", "3C — Sonic boom, scale reveal")],
            "board": "Inside the Thar. Dash glows crimson; the speedometer needle slams past the end of the "
                     "scale and stops on exactly 11.2 km/s. Outside, a bright red speed breaker.",
            "action": "The Thar rockets forward, hits the breaker — and instead of bouncing, it tilts ninety "
                      "degrees and shoots straight off the top of the frame. Thick red exhaust lines trail it "
                      "like an anime missile. Pull wide: a tiny dot, a huge shockwave cone.",
            "camera": "Three cuts. (1) Over-the-shoulder cockpit, speedo dead centre, hold 1.5s while the needle "
                      "buries. (2) Low tracking shot on the breaker, 90° tilt as a hard snap — 2 frames, no ease. "
                      "(3) Ultra-wide on the boom, hold a beat too long for comedy.",
            "audio": "Divine *ting*. Heavy supercar rev layering into an aggressive jet takeoff roar at the bump, "
                     "resolving in a full sonic boom with a sub drop.",
            "dialogue": [("JIRA", "Ab aayega na asli mazaa! Let's gooo!")],
            "vo": "03_jira_launch_scream.mp3",
            "transition": "Boom cuts to nothing. Absolute black, absolute silence.",
        },
        {
            "num": "04", "tc": "0:28 – 0:45", "title": "Zero Gravity",
            "frames": [("08_zero_gravity.png", "4A — Thar adrift, Jira outside flailing"),
                       ("09_sweat_drop.png", "4B — Giant sweat drop, deadpan dread")],
            "board": "Instant cut to pitch-black space, glowing stars, faint crimson nebula. The Thar floats "
                     "helplessly, rotating a slow 360°. Headlamps still on, pointing at nothing.",
            "action": "Jira is outside the window, arms and legs flailing in slow motion. A massive anime sweat "
                      "drop appears on his head — hold on it a half-second longer than is comfortable.",
            "camera": "Slow orbit around the drifting Thar, then push to a close-up on Jira's face. Everything is "
                      "slow. The cut from hyper-speed to this is the whole gag — make the contrast brutal.",
            "audio": "Two full seconds of terrifying silence. Then a single, awkward cricket chirp. Nothing else. "
                     "No music, no reverb wash — just the chirp and the void.",
            "dialogue": [("JIRA", "Arey bhai bhai bhai! Highway pe nikalna tha, sidha orbit mein phek diya!")],
            "vo": "04_jira_zero_g.mp3",
            "note": "Jira's VO should feel small and thin here. Echo it, but keep it quiet — he is a long way from home.",
            "transition": "Smash cut on the last syllable into the phonk drop.",
        },
        {
            "num": "05", "tc": "0:45 – 0:54", "title": "The Realization",
            "frames": [("10_facepalm.png", "5A — Slow-motion facepalm")],
            "board": "Dramatic slow-motion facepalm. Every frame is a small tragedy.",
            "action": "Jira and the Thar slowly drift upward, beginning to fade into the cosmic void. The regret is total.",
            "camera": "120fps, tight on the palm meeting the forehead, then a slow pull back to reveal how small "
                      "he is against the black.",
            "audio": "Heavy, comedic phonk beat drops and carries into the final shot.",
            "dialogue": [("JIRA", "Escape velocity de di! Physics ne aukaat dikha di.")],
            "vo": "05_jira_realization.mp3",
            "note": "Read the sigh before the line. Half the joke is the exhale.",
            "transition": "Beat-matched cut into the giant hand.",
        },
        {
            "num": "06", "tc": "0:54 – 1:00", "title": "The Verdict",
            "frames": [("11_giant_hand.png", "* — Giant crimson hand points down (to render)"),
                       ("12_drift_into_void.png", "* — Fade into the void (to render)")],
            "board": "A giant glowing crimson manga hand slides down from the top edge of frame and points "
                     "directly at Jira. Scale contrast does all the work: gods are big, Jira is a pixel.",
            "action": "Jira and the Thar fade into the dark cosmic void as the phonk keeps running.",
            "camera": "Static. Huge negative space. The hand enters on the phonk downbeat.",
            "audio": "Phonk continues, then ducks under the divine voice. Add cathedral reverb, sub-harmonic under the words.",
            "dialogue": [
                ("BHAGWAN", "Vats, ab orbit mein hi ghoomo... aur haan, jaate-jaate baaki bachchon ko bolna Sansi Sir ko zaroor follow karein!"),
            ],
            "vo": "06_bhagwan_booming.mp3",
            "note": "Deliver the CTA as a blessing, not an ad. Comic sincerity is the whole brand.",
            "transition": "Hard cut to black on \"follow karein\". One second of black. Logo card. Done.",
        },
    ]

    for sh in shots:
        shot_heading(doc, sh["num"], sh["tc"], sh["title"])

        # storyboard frames
        frames = sh["frames"]
        ft = doc.add_table(rows=1, cols=len(frames))
        ft.alignment = WD_TABLE_ALIGNMENT.CENTER
        ft.autofit = True
        for i, (fn, cap) in enumerate(frames):
            c = ft.rows[0].cells[i]
            c.text = ""
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(1)
            path = os.path.join(SB, "web", os.path.splitext(fn)[0] + ".jpg")
            if not os.path.exists(path):
                path = os.path.join(SB, fn)
            if os.path.exists(path):
                p.add_run().add_picture(path, width=Inches(2.05 if len(frames) == 3 else 2.55))
                c2 = c.add_paragraph()
                c2.alignment = WD_ALIGN_PARAGRAPH.CENTER
                c2.paragraph_format.space_after = Pt(4)
                r = c2.add_run(cap)
                r.font.size = Pt(7.5)
                r.font.italic = True
                r.font.color.rgb = GREY
            else:
                r = p.add_run("[ FRAME TO RENDER ]")
                r.font.size = Pt(8)
                r.font.bold = True
                r.font.color.rgb = RED
                c2 = c.add_paragraph()
                c2.alignment = WD_ALIGN_PARAGRAPH.CENTER
                c2.paragraph_format.space_after = Pt(4)
                r = c2.add_run(cap)
                r.font.size = Pt(7.5)
                r.font.italic = True
                r.font.color.rgb = GREY

        label_para(doc, "BOARD", sh["board"])
        label_para(doc, "ACTION", sh["action"])
        label_para(doc, "CAMERA", sh["camera"])
        label_para(doc, "AUDIO", sh["audio"])
        if "dialogue" in sh:
            for who, line in sh["dialogue"]:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.left_indent = Inches(0.18)
                r = p.add_run(who + ":  ")
                r.font.size = Pt(10)
                r.font.bold = True
                r.font.color.rgb = RED
                r2 = p.add_run("\u201c" + line + "\u201d")
                r2.font.size = Pt(10.5)
                r2.font.bold = True
                r2.font.color.rgb = INK
            if "vo" in sh:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.18)
                p.paragraph_format.space_after = Pt(2)
                r = p.add_run("VO FILE  ")
                r.font.size = Pt(8.5)
                r.font.bold = True
                r.font.color.rgb = GREY
                r2 = p.add_run("audio/" + sh["vo"])
                r2.font.size = Pt(8.5)
                r2.font.name = "Consolas"
                r2.font.color.rgb = GREY
        if "note" in sh:
            label_para(doc, "NOTE", sh["note"])
        label_para(doc, "CUT", sh["transition"])
        rule(doc, color="DDDDDD", size=6)

    doc.add_page_break()

    # ---------------------------------------------------------------- EDIT NOTES
    add_para(doc, "EDIT NOTES", size=9, bold=True, color=GREY, space_after=2)
    add_para(doc, "The rhythm is the film. Six rules, no exceptions.", size=13, bold=True, space_after=8)
    rule(doc)

    notes = [
        ("01", "Cut on sound, never on movement.",
         "Every transition in this script is attached to an audio event: a record scratch, a sonic boom, a "
         "single cricket chirp, a phonk downbeat. If the picture and the sound do not land on the same frame, "
         "move the picture."),
        ("02", "Protect the silence.",
         "0:28 to 0:30 has no music at all. Resist the urge to fill it. That silence is what makes the rest of "
         "the film sound expensive."),
        ("03", "Speed is a shape, not a number.",
         "Fast beats use hard cuts, 2-frame snaps and no motion blur on the cut points. Slow beats use 120fps and "
         "long holds. Never mix the two inside a single shot."),
        ("04", "Type lives in the frame.",
         "Manga SFX are drawn objects, not overlays on top of the picture. They should get occluded by the Thar "
         "when it passes in front of them."),
        ("05", "Three colours only.",
         "White, crimson, black. The moment a fourth appears, the film stops looking like a manga and starts "
         "looking like a mood board."),
        ("06", "The CTA is the punchline.",
         "The divine voice is funny because it is completely sincere about the follow. Cut to black immediately "
         "on the last word — do not let the joke breathe, let the silence do it."),
    ]
    for n, head, body in notes:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(n + "   ")
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RED
        r.font.name = "Consolas"
        r2 = p.add_run(head)
        r2.font.size = Pt(11)
        r2.font.bold = True
        r2.font.color.rgb = INK
        add_para(doc, body, size=10, color=GREY, space_after=6)

    rule(doc)

    # ---------------------------------------------------------------- PROMPTS
    add_para(doc, "HELIOS SHOT PROMPTS", size=9, bold=True, color=GREY, space_after=2)
    add_para(doc, "Twelve single-action prompts, one per storyboard frame.", size=13, bold=True, space_after=4)
    add_para(doc, "Feed each as its own generation rather than one minute-long prompt — the model holds character, "
                  "palette and lighting far better across short, single-action takes. Every prompt is written as "
                  "one flowing paragraph, in the style the repository's own example prompts use. Keep the negative "
                  "prompt constant across all twelve: photorealistic, extra limbs, text artefacts, watermarks, "
                  "colour fringing, fourth accent colour. Render 1A and 1B first and lock the character sheet from "
                  "them; every later frame should reference that same face and the same black Thar, or the film "
                  "will read as twelve different shorts.", size=10, color=GREY, space_after=8)
    rule(doc)

    prompts = [
        ("1A", "Pure infinite white background with no detail, anime manga cel-shaded look, bold black ink outlines, "
               "crimson black and white palette. A young Indian man in an oversized white t-shirt kneels on the white "
               "ground in the lower third of the frame, hands folded in intense prayer, eyes shut, a single small "
               "devotional sweat drop, faint holy glow behind him. The camera is locked static and the vast white "
               "space above him stays completely empty and waiting."),
        ("1B", "Pure infinite white background, anime manga cel-shaded look, bold black ink outlines, crimson black "
               "and white palette. A massive solid-black boxy Indian off-road SUV with round headlamps and chunky "
               "tyres crashes down from the top edge of frame and slams onto the white ground with a violent impact: "
               "a dark crimson shadow flashes under the tyres, white radial impact lines and debris explode outward, "
               "dust plumes, screen-shaking camera jolt and a fast scale punch-in, then the jeep bounces once and "
               "settles while a tiny praying young man in a white t-shirt stays motionless at the bottom of frame."),
        ("2A", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. An extreme "
               "close-up of a young Indian man's eyes snapping wide open with a crimson glint and a tiny reflection "
               "of a black SUV in the irises. Horizontal black anime speed lines rush behind him across a pure white "
               "background as the camera aggressively pushes in, thick eyebrows drawn tight, a small sweat bead at "
               "the temple, three frames of white flash on the snap."),
        ("2B", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. A young Indian "
               "man in an oversized white t-shirt rises on a pure white ground and smirks with pure attitude, one "
               "finger pointed straight up at the sky, low-angle shonen hero framing. Horizontal speed lines explode "
               "outward behind him, crimson rim light on his hair and shoulders, and a solid-black boxy Indian "
               "off-road SUV sits blurred in the background still radiating heat. The camera whips out from a "
               "close-up into this low heroic angle."),
        ("3A", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. Over-the-"
               "shoulder view from the back seat of a black boxy Indian off-road SUV interior, the dashboard glowing "
               "crimson red, an analog speedometer dial dead centre with the needle buried past the end of the scale "
               "on exactly 11.2 km/s, a young man's hands gripping the steering wheel with white knuckles, extreme "
               "speed blur streaking past the windshield. The camera holds steady on the speedometer for a beat too "
               "long while the needle overshoots."),
        ("3B", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. A black boxy "
               "Indian off-road SUV hits a bright red-and-white striped speed breaker on a white road and instead of "
               "bouncing it snaps ninety degrees upwards, nose to the sky, shooting vertically out of frame. Thick "
               "red exhaust lines and a jet flame trail behind it like an anime missile, a massive radiating "
               "shockwave, cracked asphalt and flying debris. The camera tracks low alongside, then the tilt to "
               "vertical is a hard two-frame snap."),
        ("3C", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. Ultra-wide "
               "shot of a tiny black boxy Indian off-road SUV rocketing up through a clean white sky as a bright "
               "dot, leaving a colossal white and crimson sonic boom cone and a huge expanding shockwave ring. Bold "
               "hand-drawn manga sound effect shapes burst around the shockwave, ink splatter at the frame edges, "
               "enormous negative space, the camera holding one beat too long for comedy."),
        ("4A", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. Pitch-black "
               "outer space filled with glowing white stars and a faint crimson nebula. A black boxy Indian off-road "
               "SUV floats helplessly in the middle of frame, slowly rotating three hundred and sixty degrees, "
               "headlamps still casting two beams into the void, dust particles drifting out. A young Indian man in "
               "a white t-shirt floats just outside the driver window with arms and legs flailing in slow motion and "
               "his mouth open in panic. The camera orbits slowly, everything in extreme slow motion."),
        ("4B", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. Close-up of a "
               "young Indian man's face in zero gravity, messy black hair floating in strands, brown skin, eyes wide "
               "with dread, lips pressed together, one hand flat against the SUV window glass with his reflection "
               "doubled behind it. A giant oversized glossy anime sweat drop hangs huge on the side of his head. "
               "Pitch-black starry space behind. The camera pushes in slowly and holds on the sweat drop a half "
               "second too long."),
        ("5A", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. Dramatic slow-"
               "motion medium shot of a young Indian man in a white t-shirt floating in pitch-black starry space, "
               "eyes closed in defeat, palm slowly meeting his forehead in a facepalm, long elegant manga impact "
               "lines behind him, hair drifting, a small crimson sparkle of shame. The black boxy SUV drifts blurred "
               "in the background. The camera is tight on the palm, then pulls back slowly to reveal how small he is "
               "against the void."),
        ("6A", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. A giant "
               "glowing crimson manga-style disembodied hand slides down from the top edge of frame, index finger "
               "pointing straight down, glowing outline and ink hatching, dripping light particles. Tiny below it, a "
               "young Indian man in a white t-shirt and a black boxy Indian off-road SUV float in pitch-black starry "
               "space. Static low-angle camera with enormous negative space as the hand enters on the beat."),
        ("6B", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. Final quiet "
               "wide: a tiny black boxy Indian off-road SUV and a tiny human silhouette drift upward into a deep "
               "black cosmic void, half dissolving into stars and crimson particles, headlamps dimming. Vast empty "
               "black space, one faint glowing crimson ring far in the distance like the curve of an orbit. The "
               "camera holds completely still as they fade, then hard cut to black."),
    ]
    for tag, text in prompts:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(tag)
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RED
        r.font.name = "Consolas"
        b = doc.add_paragraph()
        b.paragraph_format.space_after = Pt(6)
        b.paragraph_format.left_indent = Inches(0.14)
        rb = b.add_run(text)
        rb.font.size = Pt(9)
        rb.font.color.rgb = INK

    rule(doc)
    add_para(doc, "ASSETS IN THIS PACK", size=9, bold=True, color=RED, space_after=3)
    add_para(doc, "storyboard/  10 rendered frames (2 still to render for shot 06)\n"
                  "audio/  6 Hindi VO lines — Jira (hyper, young) and Bhagwan (booming, divine)\n"
                  "build_doc.py  regenerates this document", size=9.5, color=GREY, space_after=0)

    out_docx = os.path.join(HERE, "Thar_vs_Escape_Velocity_Production_Script.docx")
    doc.save(out_docx)
    print("saved", out_docx)


if __name__ == "__main__":
    build()
