"""Build the Thar vs Escape Velocity production script as a print-ready PDF."""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, Image, KeepTogether,
                                PageBreak, NextPageTemplate)
from reportlab.lib.enums import TA_LEFT

HERE = os.path.dirname(os.path.abspath(__file__))
SB = os.path.join(HERE, "storyboard")

INK = colors.HexColor("#111111")
RED = colors.HexColor("#B3141E")
GREY = colors.HexColor("#5A5A5A")
LIGHT = colors.HexColor("#E8E8E8")

PAGE_W, PAGE_H = A4
M = 0.72 * inch
CONTENT_W = PAGE_W - 2 * M

base = dict(fontName="Helvetica", textColor=INK, fontSize=10.5, leading=15)


def st(name, **kw):
    d = dict(base)
    d.update(kw)
    return ParagraphStyle(name, **d)


S = {
    "kicker": st("kicker", fontName="Helvetica-Bold", fontSize=8.5, leading=11,
                 textColor=GREY, spaceAfter=4),
    "title": st("title", fontName="Helvetica-Bold", fontSize=34, leading=37, spaceAfter=2),
    "subtitle": st("subtitle", fontName="Helvetica-Bold", fontSize=17, leading=21,
                   textColor=RED, spaceAfter=10),
    "meta": st("meta", fontSize=10.5, leading=15, textColor=GREY),
    "deck": st("deck", fontSize=10.5, leading=15),
    "lead": st("lead", fontName="Helvetica-Bold", fontSize=13.5, leading=17),
    "label": st("label", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=RED),
    "body": st("body", fontSize=10, leading=14.5, spaceAfter=2),
    "small": st("small", fontSize=8, leading=10, textColor=GREY),
    "dialogue": st("dialogue", fontName="Helvetica-Bold", fontSize=10, leading=14),
    "field": st("field", fontSize=9.7, leading=13.6, spaceAfter=3),
    "prompt": st("prompt", fontSize=8.8, leading=12.6, leftIndent=10),
    "note": st("note", fontName="Helvetica-Oblique", fontSize=9.4, leading=13, textColor=GREY),
}


def field(label, body):
    return Paragraph(f'<font name="Helvetica-Bold" size="7.8" color="#B3141E">{label}</font>&nbsp;&nbsp;{body}',
                     S["field"])


def rule(color="#B3141E", weight=1.1, space_before=2, space_after=8):
    t = Table([[""]], colWidths=[CONTENT_W], rowHeights=[0.6])
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), weight, colors.HexColor(color)),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return [Spacer(1, space_before), t, Spacer(1, space_after)]


def shot_head(num, tc, title):
    return Paragraph(
        f'<font name="Helvetica-Bold" size="12.5" color="#B3141E">{num}</font>&nbsp;&nbsp;'
        f'<font name="Helvetica-Bold" size="10.5">{tc}</font>&nbsp;&nbsp;'
        f'<font name="Helvetica-Bold" size="12.5">{title.upper()}</font>',
        st("sh", fontSize=12.5, leading=16, spaceBefore=2, spaceAfter=5))


def frame_row(frames):
    cells, caps = [], []
    n = len(frames)
    w = (CONTENT_W - 0.14 * inch * (n - 1)) / n
    for fn, cap in frames:
        path = os.path.join(SB, "web", os.path.splitext(fn)[0] + ".jpg")
        if not os.path.exists(path):
            path = os.path.join(SB, fn)
        items = []
        if os.path.exists(path):
            iw, ih = ImageReader(path).getSize()
            img = Image(path, width=w, height=w * ih / iw)
            items.append(img)
        else:
            ph = Table([[Paragraph('<font color="#B3141E" name="Helvetica-Bold" size="7.5">FRAME TO RENDER</font>',
                                   S["small"])]],
                       colWidths=[w], rowHeights=[w * 0.56])
            ph.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.6, LIGHT),
                                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
            items.append(ph)
        items.append(Spacer(1, 3))
        items.append(Paragraph(cap, st("cap", fontSize=7.2, leading=9, textColor=GREY,
                                       alignment=TA_LEFT)))
        cells.append(items)

    row_tbl = Table([cells], colWidths=[w] * n)
    row_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0.14 * inch),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return row_tbl


SHOTS = [
    dict(num="01", tc="0:00 – 0:10", title="The Setup & The Drop",
         frames=[("01_setup_kneeling.png", "1A · Jira in devotion, empty white void"),
                 ("02_thar_drop.png", "1B · Impact — the Thar lands, crimson shadow flash")],
         board="Pure white. Jira kneels, hands folded, eyes shut, one bead of devotional sweat. "
               "The frame is 80% empty air above him — that emptiness is the setup.",
         action="A massive solid-black Thar drops in from the top edge of frame. Ground contact: screen-shake, "
                "dust plume, a dark crimson shadow flashing under the tyres, white radial impact lines punching "
                "outward. The jeep bounces once and settles. Jira does not move.",
         camera="Locked static wide on the void. On impact, a 2-frame upward jolt plus a 6% scale punch-in keyed "
                "to the bass hit. Let the shake decay over 8 frames — do not ease it out.",
         audio="The trending track enters clean and devotional — “Hey Bhagwan, ek lambi ek Thar de do…” — with a "
               "divine reverb tail and a low sub-bass swell underneath.",
         cut="Hard cut on the beat. No dissolve anywhere in this film.",
         which="Lands the premise in one image and one sound."),
    dict(num="02", tc="0:10 – 0:18", title="The Demand",
         frames=[("03_eyes_snap.png", "2A · Eyes snap open, speed lines"),
                 ("04_point_to_sky.png", "2B · Finger to the sky, full attitude")],
         board="Jira's eyes snap open. Extreme close-up first, then a violent pull back as he stands. Horizontal "
               "black speed lines rush behind him in alternating directions.",
         action="He rises, smirks, and points one finger straight at the sky — the shonen hero pose played "
                "completely straight. The Thar sits behind him, still radiating heat.",
         camera="Close-up (100mm feel) on the eyes, then a whip-pan out to a low-angle hero shot. Two cuts in "
                "eight seconds. Add a 3-frame white flash on the eye snap.",
         audio="The song is guillotined by a hard record scratch at 0:10.5. One beat of room tone, then Jira.",
         dialogue=[("JIRA", "Thank you Prabhu! Par isme aisi speed do ki dharti pe mujhe koi pakad na paye! "
                            "Ekdum Rocket!")],
         vo="audio/02_jira_demand.mp3",
         cut="Snap cut on “Rocket!” — mid-word if possible. Trim the last consonant.",
         which="Turns gratitude into a demand. The engine of the whole joke."),
    dict(num="03", tc="0:18 – 0:28", title="The Launch",
         frames=[("05_cockpit_speedo.png", "3A · Cockpit — dash crimson, needle buried"),
                 ("06_speedbreaker_launch.png", "3B · The breaker — 90° vertical launch"),
                 ("07_sonic_boom.png", "3C · Sonic boom, scale reveal")],
         board="Inside the Thar. The dash glows crimson; the speedometer needle slams past the end of the scale "
               "and stops on exactly 11.2 km/s. Outside, a bright red speed breaker.",
         action="The Thar rockets forward, hits the breaker — and instead of bouncing, it tilts ninety degrees "
                "and shoots straight off the top of the frame. Thick red exhaust lines trail it like an anime "
                "missile. Pull wide: a tiny dot, a huge shockwave cone.",
         camera="Three cuts. (1) Over-the-shoulder cockpit, speedo dead centre, hold 1.5s while the needle buries. "
                "(2) Low tracking shot on the breaker, the 90° tilt as a hard 2-frame snap. (3) Ultra-wide on the "
                "boom, held a beat too long for comedy.",
         audio="Divine ting. Heavy supercar rev layering into an aggressive jet takeoff roar at the bump, "
               "resolving in a full sonic boom with a sub drop.",
         dialogue=[("JIRA", "Ab aayega na asli mazaa! Let's gooo!")],
         vo="audio/03_jira_launch_scream.mp3",
         cut="The boom cuts to nothing. Absolute black, absolute silence.",
         which="The physical joke: a Thar treated as a launch vehicle, no questions asked."),
    dict(num="04", tc="0:28 – 0:45", title="Zero Gravity",
         frames=[("08_zero_gravity.png", "4A · Thar adrift, Jira flailing outside"),
                 ("09_sweat_drop.png", "4B · Giant sweat drop, deadpan dread")],
         board="Instant cut to pitch-black space, glowing stars, faint crimson nebula. The Thar floats helplessly, "
               "rotating a slow 360°. Headlamps still on, pointing at nothing.",
         action="Jira is outside the window, arms and legs flailing in slow motion. A massive anime sweat drop "
                "forms on his head — hold on it half a second longer than is comfortable.",
         camera="Slow orbit around the drifting Thar, then a push to a close-up on Jira's face. Everything is slow. "
                "The cut from hyper-speed into this is the gag — make the contrast brutal.",
         audio="Two full seconds of terrifying silence. Then a single, awkward cricket chirp. Nothing else — no "
               "music, no reverb wash.",
         dialogue=[("JIRA", "Arey bhai bhai bhai! Highway pe nikalna tha, sidha orbit mein phek diya!")],
         vo="audio/04_jira_zero_g.mp3",
         note="Jira's voice should feel small and thin here. Echo it, but keep it quiet — he is a long way from home.",
         cut="Smash cut on the last syllable into the phonk drop.",
         which="The tonal floor drops out. Comedy is allowed to breathe here."),
    dict(num="05", tc="0:45 – 0:54", title="The Realization",
         frames=[("10_facepalm.png", "5A · Slow-motion facepalm, total regret")],
         board="Dramatic slow-motion facepalm. Every frame is a small tragedy.",
         action="Jira and the Thar slowly drift upward, beginning to fade into the cosmic void.",
         camera="120fps, tight on the palm meeting the forehead, then a slow pull back to reveal how small he is "
                "against the black.",
         audio="Heavy, comedic phonk beat drops and carries into the final shot.",
         dialogue=[("JIRA", "Escape velocity de di! Physics ne aukaat dikha di.")],
         vo="audio/05_jira_realization.mp3",
         note="Read the sigh before the line. Half the joke is the exhale.",
         cut="Beat-matched cut into the giant hand.",
         which="Names the film: escape velocity, delivered as a curse."),
    dict(num="06", tc="0:54 – 1:00", title="The Verdict",
         frames=[("11_giant_hand.png", "6A · Giant crimson hand points down — to render"),
                 ("12_drift_into_void.png", "6B · Fade into the void — to render")],
         board="A giant glowing crimson manga hand slides down from the top edge of frame and points directly at "
               "Jira. Scale contrast does all the work: gods are big, Jira is a pixel.",
         action="Jira and the Thar fade into the dark cosmic void while the phonk keeps running.",
         camera="Static. Huge negative space. The hand enters on the phonk downbeat.",
         audio="Phonk continues, then ducks under the divine voice. Cathedral reverb, sub-harmonic under the words.",
         dialogue=[("BHAGWAN", "Vats, ab orbit mein hi ghoomo… aur haan, jaate-jaate baaki bachchon ko bolna "
                               "Sansi Sir ko zaroor follow karein!")],
         vo="audio/06_bhagwan_booming.mp3",
         note="Deliver the CTA as a blessing, not an ad. Comic sincerity is the whole brand.",
         cut="Hard cut to black on “follow karein”. One second of black. Logo card. Done.",
         which="The verdict plus the punchline CTA — the last thing the viewer hears."),
]

PROMPTS = [
    ("1A", "Pure infinite white background with no detail, anime manga cel-shaded look, bold black ink outlines, "
           "crimson black and white palette. A young Indian man in an oversized white t-shirt kneels on the white "
           "ground in the lower third of the frame, hands folded in intense prayer, eyes shut, a single small "
           "devotional sweat drop, faint holy glow behind him. The camera is locked static and the vast white space "
           "above him stays completely empty and waiting."),
    ("1B", "Pure infinite white background, anime manga cel-shaded look, bold black ink outlines, crimson black and "
           "white palette. A massive solid-black boxy Indian off-road SUV with round headlamps and chunky tyres "
           "crashes down from the top edge of frame and slams onto the white ground with a violent impact: a dark "
           "crimson shadow flashes under the tyres, white radial impact lines and debris explode outward, dust "
           "plumes, screen-shaking camera jolt and a fast scale punch-in, then the jeep bounces once and settles "
           "while a tiny praying young man in a white t-shirt stays motionless at the bottom of frame."),
    ("2A", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. An extreme "
           "close-up of a young Indian man's eyes snapping wide open with a crimson glint and a tiny reflection of "
           "a black SUV in the irises. Horizontal black anime speed lines rush behind him across a pure white "
           "background as the camera aggressively pushes in, thick eyebrows drawn tight, a small sweat bead at the "
           "temple, three frames of white flash on the snap."),
    ("2B", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. A young Indian "
           "man in an oversized white t-shirt rises on a pure white ground and smirks with pure attitude, one "
           "finger pointed straight up at the sky, low-angle shonen hero framing. Horizontal speed lines explode "
           "outward behind him, crimson rim light on his hair and shoulders, and a solid-black boxy Indian "
           "off-road SUV sits blurred in the background still radiating heat. The camera whips out from a close-up "
           "into this low heroic angle."),
    ("3A", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. Over-the-shoulder "
           "view from the back seat of a black boxy Indian off-road SUV interior, the dashboard glowing crimson "
           "red, an analog speedometer dial dead centre with the needle buried past the end of the scale on exactly "
           "11.2 km/s, a young man's hands gripping the steering wheel with white knuckles, extreme speed blur "
           "streaking past the windshield. The camera holds steady on the speedometer for a beat too long while the "
           "needle overshoots."),
    ("3B", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. A black boxy "
           "Indian off-road SUV hits a bright red-and-white striped speed breaker on a white road and instead of "
           "bouncing it snaps ninety degrees upwards, nose to the sky, shooting vertically out of frame. Thick red "
           "exhaust lines and a jet flame trail behind it like an anime missile, a massive radiating shockwave, "
           "cracked asphalt and flying debris. The camera tracks low alongside, then the tilt to vertical is a hard "
           "two-frame snap."),
    ("3C", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. Ultra-wide shot "
           "of a tiny black boxy Indian off-road SUV rocketing up through a clean white sky as a bright dot, "
           "leaving a colossal white and crimson sonic boom cone and a huge expanding shockwave ring. Bold "
           "hand-drawn manga sound effect shapes burst around the shockwave, ink splatter at the frame edges, "
           "enormous negative space, the camera holding one beat too long for comedy."),
    ("4A", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. Pitch-black outer "
           "space filled with glowing white stars and a faint crimson nebula. A black boxy Indian off-road SUV "
           "floats helplessly in the middle of frame, slowly rotating three hundred and sixty degrees, headlamps "
           "still casting two beams into the void, dust particles drifting out. A young Indian man in a white "
           "t-shirt floats just outside the driver window with arms and legs flailing in slow motion and his mouth "
           "open in panic. The camera orbits slowly, everything in extreme slow motion."),
    ("4B", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. Close-up of a "
           "young Indian man's face in zero gravity, messy black hair floating in strands, brown skin, eyes wide "
           "with dread, lips pressed together, one hand flat against the SUV window glass with his reflection "
           "doubled behind it. A giant oversized glossy anime sweat drop hangs huge on the side of his head. "
           "Pitch-black starry space behind. The camera pushes in slowly and holds on the sweat drop a half second "
           "too long."),
    ("5A", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. Dramatic "
           "slow-motion medium shot of a young Indian man in a white t-shirt floating in pitch-black starry space, "
           "eyes closed in defeat, palm slowly meeting his forehead in a facepalm, long elegant manga impact lines "
           "behind him, hair drifting, a small crimson sparkle of shame. The black boxy SUV drifts blurred in the "
           "background. The camera is tight on the palm, then pulls back slowly to reveal how small he is against "
           "the void."),
    ("6A", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. A giant glowing "
           "crimson manga-style disembodied hand slides down from the top edge of frame, index finger pointing "
           "straight down, glowing outline and ink hatching, dripping light particles. Tiny below it, a young Indian "
           "man in a white t-shirt and a black boxy Indian off-road SUV float in pitch-black starry space. Static "
           "low-angle camera with enormous negative space as the hand enters on the beat."),
    ("6B", "Anime manga cel-shaded look, bold black ink outlines, crimson black and white palette. Final quiet wide: "
           "a tiny black boxy Indian off-road SUV and a tiny human silhouette drift upward into a deep black cosmic "
           "void, half dissolving into stars and crimson particles, headlamps dimming. Vast empty black space, one "
           "faint glowing crimson ring far in the distance like the curve of an orbit. The camera holds completely "
           "still as they fade, then hard cut to black."),
]


def cover(story):
    story += [Paragraph("PRODUCTION SCRIPT · V1 · 13 NOV 2026", S["kicker"]),
              Paragraph("THAR vs<br/>ESCAPE VELOCITY", S["title"]),
              Paragraph("Anime / Manga Edition", S["subtitle"]),
              Paragraph("Runtime 60s &nbsp;·&nbsp; 6 shots &nbsp;·&nbsp; 12 storyboard frames &nbsp;·&nbsp; "
                        "6 voice lines", S["meta"]),
              Paragraph("Vibe: extreme dramatic tension, fast cuts, high-impact comedy.", S["meta"]),
              Spacer(1, 4)]
    story += rule()
    story += [Paragraph("THE SIX-WORD PITCH", S["label"]),
              Paragraph("A man prays for a Thar. God delivers it with orbital velocity. Phyzix does the rest, and "
                        "the last word goes to a booming voice from the heavens with a follow-the-founder "
                        "punchline.", S["deck"]),
              Spacer(1, 12)]

    spec = [
        ["HERO — JIRA", "Young Indian man, early 20s. Messy spiky black hair, thick brows, white oversized tee, "
                        "dark track pants. Always slightly too confident."],
        ["THE THAR", "Solid-black Mahindra Thar-style hardtop. Round headlamps, chunky tyres, black-on-black. "
                     "Sits like a tank, moves like a missile."],
        ["THE DIVINE", "Unseen. Booming echo, white void, and one giant glowing crimson hand."],
        ["PALETTE", "Pure white void → crimson + black → pitch black space with crimson nebula. Three colours. "
                    "Never more."],
        ["TYPE / SFX", "Bold hand-drawn manga lettering, red fill or black outline. Sound effects are physical "
                       "objects in frame, not overlays."],
        ["FORMAT", "16:9, 1080p, 24fps. Shoot 60fps for the launch beat and 120fps for the facepalm."],
    ]
    rows = [[Paragraph(k, st("k", fontName="Helvetica-Bold", fontSize=7.6, leading=10, textColor=RED)),
             Paragraph(v, S["small"])] for k, v in spec]
    t = Table(rows, colWidths=[1.25 * inch, CONTENT_W - 1.25 * inch])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, LIGHT),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))
    story += rule(color="#DDDDDD", weight=0.6)
    story.append(Paragraph("Asset register", S["label"]))
    story.append(Paragraph("storyboard/ — 10 rendered frames (2 still to render for shot 06)<br/>"
                           "audio/ — 6 Hindi VO lines: Jira (hyper, young) and Bhagwan (booming, divine)<br/>"
                           "build_pdf.py — regenerates this document", S["small"]))


def shot_flow(sh):
    flow = [shot_head(sh["num"], sh["tc"], sh["title"]), frame_row(sh["frames"])]
    body = [field("BOARD", sh["board"]),
            field("ACTION", sh["action"]),
            field("CAMERA", sh["camera"]),
            field("AUDIO", sh["audio"])]
    if sh.get("dialogue"):
        for who, line in sh["dialogue"]:
            body.append(Paragraph(
                f'<font name="Helvetica-Bold" size="8" color="#B3141E">&nbsp;&nbsp;{who}&nbsp;&nbsp;</font>'
                f'<font name="Helvetica-Bold" size="10" color="#111111">“{line}”</font>',
                st("dl", fontSize=10, leading=14, spaceBefore=2, spaceAfter=2, leftIndent=4)))
        body.append(Paragraph(f"<font name='Courier' size='7.4' color='#5A5A5A'>VO FILE&nbsp;&nbsp;{sh['vo']}</font>",
                              st("vo", fontSize=7.4, leading=11, leftIndent=14, spaceAfter=3)))
    if sh.get("note"):
        body.append(field("NOTE", f'<i>{sh["note"]}</i>'))
    body.append(field("CUT", sh["cut"]))
    flow.append(KeepTogether(body))
    flow += rule(color="#E2E2E2", weight=0.5, space_before=4, space_after=6)
    return flow


def edit_notes(story):
    story.append(Paragraph("EDIT NOTES", S["label"]))
    story.append(Paragraph("The rhythm is the film. Six rules, no exceptions.", S["lead"]))
    story += rule()
    notes = [
        ("01", "Cut on sound, never on movement.",
         "Every transition here is attached to an audio event: a record scratch, a sonic boom, a single cricket "
         "chirp, a phonk downbeat. If picture and sound do not land on the same frame, move the picture."),
        ("02", "Protect the silence.",
         "0:28 to 0:30 has no music at all. Resist the urge to fill it. That silence is what makes the rest of the "
         "film sound expensive."),
        ("03", "Speed is a shape, not a number.",
         "Fast beats use hard cuts, two-frame snaps and no motion blur on cut points. Slow beats use 120fps and "
         "long holds. Never mix the two inside one shot."),
        ("04", "Type lives in the frame.",
         "Manga SFX are drawn objects, not overlays. They should be occluded by the Thar when it passes in front "
         "of them."),
        ("05", "Three colours only.",
         "White, crimson, black. The moment a fourth appears, the film stops looking like a manga and starts "
         "looking like a mood board."),
        ("06", "The CTA is the punchline.",
         "The divine voice is funny because it is completely sincere about the follow. Cut to black on the last "
         "word — do not let the joke breathe, let the silence do it."),
    ]
    rows = []
    for n, head, body in notes:
        rows.append([Paragraph(n, st("n", fontName="Courier-Bold", fontSize=10, leading=13, textColor=RED)),
                     [Paragraph(head, st("nh", fontName="Helvetica-Bold", fontSize=10.5, leading=14,
                                         spaceAfter=1)),
                      Paragraph(body, st("nb", fontSize=9.4, leading=13.2, textColor=GREY))]])
    t = Table(rows, colWidths=[0.4 * inch, CONTENT_W - 0.4 * inch])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, LIGHT),
    ]))
    story.append(t)


def prompts_page(story):
    story.append(Paragraph("HELIOS SHOT PROMPTS", S["label"]))
    story.append(Paragraph("Twelve single-action prompts, one per storyboard frame.", S["lead"]))
    story.append(Paragraph("Feed each as its own generation rather than one minute-long prompt — the model holds "
                           "character, palette and lighting far better across short, single-action takes. "
                           "Every prompt is written as one flowing paragraph, in the style the repository's own "
                           "example prompts use.", S["deck"]))
    story += rule()
    for tag, text in PROMPTS:
        story.append(KeepTogether([
            Paragraph(tag, st("pt", fontName="Courier-Bold", fontSize=8.6, leading=11, textColor=RED,
                              spaceBefore=3)),
            Paragraph(text, S["prompt"]),
        ]))
    story.append(Spacer(1, 8))
    story += rule(color="#DDDDDD", weight=0.6)
    story.append(Paragraph("RENDER NOTES", S["label"]))
    story.append(Paragraph("Keep the negative prompt constant across all twelve: <i>photorealistic, extra limbs, "
                           "text artefacts, watermarks, colour fringing, fourth accent colour</i>. Render 1A and 1B "
                           "first and lock the character sheet from them; every later frame should reference that "
                           "same face and the same black Thar, or the film will read as twelve different shorts.",
                           S["small"]))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#DDDDDD"))
    canvas.setLineWidth(0.5)
    canvas.line(M, 0.52 * inch, PAGE_W - M, 0.52 * inch)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(GREY)
    canvas.drawString(M, 0.38 * inch, "THAR vs ESCAPE VELOCITY  ·  production script v1")
    canvas.drawRightString(PAGE_W - M, 0.38 * inch, f"{doc.page:02d}")
    canvas.restoreState()


def build():
    out = os.path.join(HERE, "Thar_vs_Escape_Velocity_Production_Script.pdf")
    doc = BaseDocTemplate(out, pagesize=A4,
                          leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=0.75 * inch,
                          title="Thar vs Escape Velocity — Production Script",
                          author="Arena", subject="Anime/Manga short production script")
    frame = Frame(M, 0.75 * inch, CONTENT_W, PAGE_H - M - 0.75 * inch, id="main",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=footer)])

    story = []
    cover(story)
    story.append(PageBreak())

    story.append(Paragraph("SHOT BREAKDOWN", S["label"]))
    story.append(Paragraph("Six shots. Every cut lands on a sound — a record scratch, a sonic boom, or dead "
                           "silence. Silence is the loudest cut in this film; protect it.", S["deck"]))
    story += rule()

    for i, sh in enumerate(SHOTS):
        story += shot_flow(sh)
        if i == 1 or i == 3 or i == 4:
            story.append(PageBreak())

    story.append(PageBreak())
    edit_notes(story)
    story.append(PageBreak())
    prompts_page(story)

    doc.build(story)
    print("saved", out)


if __name__ == "__main__":
    build()
