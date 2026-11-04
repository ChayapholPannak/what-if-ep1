# 🧟 WHAT-IF EP.1 — ซอมบี้บุก [ร้าน 24 ชม.] EPB ปทุมธานี

> สั้น 56 วินาที · แนวตั้ง 9:16 (1080×1920) · 30fps
> คลิปสั้นแนว **"ถ้าซอมบี้บุกสถานที่จริงในไทย"** — survival AI cartoon สไตล์ 2D anime ตัดสลับกับภาพ cell-shaded

![genre](https://img.shields.io/badge/genre-2D%20anime%20survival-d6336c)
![format](https://img.shields.io/badge/format-9%3A16%20vertical-14213d)

## 🎬 โครงเรื่อง (56s)

เปิดด้วยมือถือรับ **Cell Broadcast alert "เกิดโรคระบาดซอมบี้"** แล้วหนีขึ้นชั้นสองของร้านสะดวกซื้อ 24 ชม. (EPB) ในปทุมธานี → ขวานอุดประตู อยู่รอดระยะแรก → ต่อมื้อสุดท้ายปิด EP.1 → เท่ออก EP.2

Beat-by-beat breakdown อยู่ใน [`scenario.md`](scenario.md) พร้อม master prompt สำหรับตอนถัดไป

## 🛠 วิธีทำ (Pipeline)

| ขั้นตอน | เครื่องมือ |
|---|---|
| โครงเรื่อง + บท | ร่วมเขียนกับ AI (ดู `scenario.md`, `CLAUDE.md`) |
| ช็อตพื้นหลัง 3D | Blender → ส่งออกมุมกล้องจริง (`blender/`) |
| ถักเรียงต่อเป็นเวลา | [HyperFrames](https://hyperframes.heygen.com) — HTML/GSAP timeline ที่ 1080×1920 → คลาวด์เรนเดอร์เป็น MP4 |
| ส่งออกสุดท้าย | `hyperframes render` → MP4 (ดูตัวอย่างใน `renders/`) |

- **ไฟล์หลัก:** [`index.html`](index.html) — timeline ทั้งคลิป
- **สื่อ:** `assets/` (เสียง, ช็อต Blender ที่ใช้จริง), `refs/` (แบนเนอร์/โลโก้/ภาพมุมกล้องอ้างอิง)
- `blender/out/` ตัดจาก git (3+ GB เรนเดอร์ดิบ) — เก็บเฉพาะจานที่ใช้

## ▶ เรียกใช้งาน

```bash
npm install        # (ไม่จำเป็น, CLI ยิงตรง)
npm run preview    # ดูสด + ไทม์ไลน์
npm run check      # ตรวจผิดพลาดก่อนเรนเดอร์
npm run render     # สร้าง MP4
```

## 📂 โครงโปรเจกต์

```
whatif-ep1/
├─ index.html        # คอมโพจิชั่นหลัก (HTML + GSAP timeline)
├─ scenario.md       # บท + beat table + master prompt
├─ blender/          # ไฟล์ฉาก 3D (outputs ถูก ignore)
├─ assets/           # เสียง + จาน Blender ที่ใช้
├─ refs/             # แบนเนอร์/โลโก้/มุมกล้องอ้างอิง
├─ renders/          # MP4 ตัวสุดท้าย
└─ .media/           # แคตตาล็อกสื่อของ HyperFrames
```

---
*ไม่ได้ตั้งใจให้ใช้แทนการเอาชีวิตรอดจริง 555*
