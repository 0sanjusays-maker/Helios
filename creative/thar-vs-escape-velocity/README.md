# Thar vs Escape Velocity — Anime/Manga Edition

60-second short. A man prays for a Thar, gets it, asks for rocket speed, and Physics
bills him for the full escape velocity. Production pack.

## What's here

| File | What it is |
| --- | --- |
| `Thar_vs_Escape_Velocity_Production_Script.pdf` | Print/review version of the full script (9 pages) |
| `Thar_vs_Escape_Velocity_Production_Script.docx` | Same doc, editable |
| `storyboard/web/*.jpg` | 10 rendered storyboard frames (shots 1–5 + the drift beat) |
| `storyboard/*.png` | Full-resolution masters of the same frames |
| `audio/*.mp3` | 6 Hindi VO lines — Jira (hyper, young) and Bhagwan (booming, divine) |

Google Doc: **Thar vs Escape Velocity — Production Script (v2)**
<https://docs.google.com/document/d/1O7qfclqyT3KdB_DylRm-ldt4l9npYEExWhb4Tg8R17A/edit>

## Structure

| Shot | Time | Title | Beats |
| --- | --- | --- | --- |
| 01 | 0:00–0:10 | The Setup & The Drop | 1A kneeling · 1B impact |
| 02 | 0:10–0:18 | The Demand | 2A eyes snap · 2B finger to sky |
| 03 | 0:18–0:28 | The Launch | 3A cockpit · 3B breaker · 3C sonic boom |
| 04 | 0:28–0:45 | Zero Gravity | 4A adrift · 4B sweat drop |
| 05 | 0:45–0:54 | The Realization | 5A facepalm |
| 06 | 0:54–1:00 | The Verdict | 6A giant hand · 6B fade to void |

The script carries BOARD / ACTION / CAMERA / AUDIO / NOTE / CUT for every shot, the six
edit rules, and twelve Helios-ready single-action prompts (one per frame).

## Voiceover

| File | Character | Line |
| --- | --- | --- |
| `01_jira_prayer.mp3` | Jira | Hey Bhagwan… ek lambi, ek Thar de do… |
| `02_jira_demand.mp3` | Jira | Thank you Prabhu! Par isme aisi speed do ki dharti pe mujhe koi pakad na paye! Ekdum Rocket! |
| `03_jira_launch_scream.mp3` | Jira | Ab aayega na asli mazaa! Let's gooo! |
| `04_jira_zero_g.mp3` | Jira | Arey bhai bhai bhai! Highway pe nikalna tha, sidha orbit mein phek diya! |
| `05_jira_realization.mp3` | Jira | Escape velocity de di! Physics ne aukaat dikha di. |
| `06_bhagwan_booming.mp3` | Bhagwan | Vats, ab orbit mein hi ghoomo… aur haan, jaate-jaate baaki bachchon ko bolna Sansi Sir ko zaroor follow karein! |

## Regenerating

```bash
python3 -m pip install --break-system-packages python-docx reportlab pillow
python3 build_doc.py   # -> .docx
python3 build_pdf.py   # -> .pdf
```

Frames 6A (giant crimson hand) and 6B (fade into the void) are still unrendered —
their prompts are in the script and the layout shows them as placeholders.
